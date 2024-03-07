// Copyright (c) 2017, 2022 ZettaScale Technology Inc.

// This program and the accompanying materials are made available under the
// terms of the Eclipse Public License 2.0 which is available at
// http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
// which is available at https://www.apache.org/licenses/LICENSE-2.0.

// SPDX-License-Identifier: EPL-2.0 OR Apache-2.0

// Contributors:
//   ZettaScale Zenoh team, <zenoh@zettascale.tech>

use pyo3::{prelude::*, types::PyBytes, PyObject};
use uhlc::Timestamp;
use zenoh::{
    prelude::{Encoding, KeyExpr, Sample, Value, ZenohId},
    query::Reply,
    sample::QoS,
    scouting::Hello,
};
use zenoh_buffers::{buffer::SplitBuffer, ZBuf};

use crate::{
    enums::{_CongestionControl, _Encoding, _Priority, _SampleKind},
    keyexpr::_KeyExpr,
    ToPyErr,
};

#[pyclass(subclass)]
#[derive(Clone)]
pub struct _ZBuf {
    inner: Payload,
}
fn memoryview(slice: &[u8], py: Python) -> PyObject {
    unsafe {
        let memview = pyo3::ffi::PyMemoryView_FromMemory(
            slice.as_ptr().cast_mut().cast(),
            slice.len() as isize,
            100,
        );
        PyObject::from_owned_ptr(py, memview)
    }
}
#[pymethods]
impl _ZBuf {
    #[new]
    pub fn pynew(this: Self) -> Self {
        this
    }
    #[staticmethod]
    pub fn new(bytes: PyObject, py: Python) -> PyResult<Self> {
        if let Ok(this) = bytes.downcast::<PyBytes>(py) {
            return Ok(Self {
                inner: Payload::Python(Py::from(this)),
            });
        }
        bytes.extract(py)
    }
    pub fn contiguous(&mut self, py: Python) -> PyObject {
        match &mut self.inner {
            Payload::Zenoh(buf) => match buf.contiguous() {
                std::borrow::Cow::Borrowed(slice) => memoryview(slice, py),
                std::borrow::Cow::Owned(vec) => {
                    *buf = vec.into();
                    let slice = buf.slices().next().unwrap();
                    memoryview(slice, py)
                }
            },
            Payload::Python(buf) => buf.to_object(py),
        }
    }
    fn n_slices(&self) -> usize {
        match &self.inner {
            Payload::Zenoh(buf) => buf.slices().len(),
            Payload::Python(_) => 1,
        }
    }
    fn __getitem__(&self, index: usize, py: Python) -> PyResult<PyObject> {
        match &self.inner {
            Payload::Python(buf) => {
                if index == 0 {
                    return Ok(buf.to_object(py));
                }
            }
            Payload::Zenoh(buf) => {
                if let Some(slice) = buf.slices().nth(index) {
                    return Ok(memoryview(slice, py));
                }
            }
        }
        Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(format!(
            "index: {index}, n_slices: {}",
            self.n_slices()
        )))
    }
}

#[derive(Clone)]
pub(crate) enum Payload {
    Zenoh(ZBuf),
    Python(Py<PyBytes>),
}
impl From<_ZBuf> for ZBuf {
    fn from(value: _ZBuf) -> ZBuf {
        match value.inner {
            Payload::Zenoh(buf) => buf,
            Payload::Python(buf) => Python::with_gil(|py| ZBuf::from(buf.as_bytes(py).to_owned())),
        }
    }
}
impl From<ZBuf> for _ZBuf {
    fn from(buf: ZBuf) -> Self {
        _ZBuf {
            inner: Payload::Zenoh(buf),
        }
    }
}
impl From<Py<PyBytes>> for _ZBuf {
    fn from(buf: Py<PyBytes>) -> Self {
        _ZBuf {
            inner: Payload::Python(buf),
        }
    }
}
impl core::fmt::Debug for _ZBuf {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match &self.inner {
            Payload::Zenoh(arg0) => {
                for slice in arg0.slices() {
                    for byte in slice {
                        write!(f, "{byte:02x}")?
                    }
                }
            }
            Payload::Python(arg0) => {
                for byte in arg0.as_bytes(unsafe { Python::assume_gil_acquired() }) {
                    write!(f, "{byte:02x}")?
                }
            }
        };
        Ok(())
    }
}
#[pyclass(subclass)]
#[derive(Clone, Debug)]
pub struct _Value {
    pub(crate) payload: _ZBuf,
    pub(crate) encoding: Encoding,
}
#[pymethods]
impl _Value {
    #[new]
    pub fn pynew(this: Self) -> Self {
        this
    }
    #[staticmethod]
    pub fn new(bytes: PyObject, encoding: Option<_Encoding>, py: Python) -> PyResult<Self> {
        Ok(Self {
            payload: _ZBuf::new(bytes, py)?,
            encoding: encoding.map(|e| e.0).unwrap_or(Encoding::EMPTY),
        })
    }
    #[getter]
    pub fn payload(&self) -> _ZBuf {
        self.payload.clone()
    }
    pub fn with_payload(&mut self, payload: _ZBuf) {
        self.payload = payload
    }
    #[getter]
    pub fn encoding(&self) -> _Encoding {
        _Encoding(self.encoding.clone())
    }
    pub fn with_encoding(&mut self, encoding: _Encoding) {
        self.encoding = encoding.0;
    }
    pub fn __str__(&self) -> String {
        format!("{self:?}")
    }
}
impl From<Value> for _Value {
    fn from(value: Value) -> Self {
        _Value {
            payload: value.payload.into(),
            encoding: value.encoding,
        }
    }
}
impl From<_Value> for Value {
    fn from(value: _Value) -> Self {
        Value::new(value.payload.into()).encoding(value.encoding)
    }
}

pub(crate) trait PyAnyToValue {
    fn to_value(self) -> PyResult<Value>;
}
impl PyAnyToValue for &PyAny {
    fn to_value(self) -> PyResult<Value> {
        let encoding: _Encoding = self.getattr("encoding")?.extract()?;
        let payload: &PyBytes = self.getattr("payload")?.extract()?;
        Ok(Value::new(ZBuf::from(payload.as_bytes().to_owned())).encoding(encoding.0))
    }
}

#[pyclass(subclass)]
#[derive(Clone, Debug, Default)]
pub struct _QoS(pub(crate) QoS);

#[pymethods]
impl _QoS {
    #[new]
    pub fn pynew(this: Self) -> Self {
        this
    }
    #[getter]
    pub fn priority(&self) -> _Priority {
        _Priority(self.0.priority())
    }
    #[getter]
    pub fn congestion_control(&self) -> _CongestionControl {
        _CongestionControl(self.0.congestion_control())
    }
    #[getter]
    pub fn express(&self) -> bool {
        self.0.express()
    }
    #[staticmethod]
    pub fn new() -> Self {
        Self::default()
    }
}

#[pyclass(subclass)]
#[derive(Clone, Debug)]
pub struct _Sample {
    key_expr: KeyExpr<'static>,
    value: _Value,
    kind: _SampleKind,
    timestamp: Option<_Timestamp>,
    qos: _QoS,
}
impl From<Sample> for _Sample {
    fn from(sample: Sample) -> Self {
        let Sample {
            key_expr,
            value,
            kind,
            timestamp,
            qos,
            ..
        } = sample;
        _Sample {
            key_expr,
            value: value.into(),
            kind: _SampleKind(kind),
            timestamp: timestamp.map(_Timestamp),
            qos: _QoS(qos),
        }
    }
}

#[pyclass(subclass)]
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct _ZenohId(pub(crate) ZenohId);
impl core::fmt::Debug for _ZenohId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        core::fmt::Debug::fmt(&self.0, f)
    }
}
#[pymethods]
impl _ZenohId {
    #[new]
    pub fn pynew(this: Self) -> Self {
        this
    }
    pub fn __str__(&self) -> String {
        self.0.to_string()
    }
}

#[pyclass(subclass)]
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct _Timestamp(Timestamp);
#[pymethods]
impl _Timestamp {
    #[new]
    pub fn pynew(this: Self) -> Self {
        this
    }
    fn __richcmp__(&self, other: &Self, op: pyo3::pyclass::CompareOp) -> bool {
        match op {
            pyo3::pyclass::CompareOp::Lt => self < other,
            pyo3::pyclass::CompareOp::Le => self <= other,
            pyo3::pyclass::CompareOp::Eq => self == other,
            pyo3::pyclass::CompareOp::Ne => self != other,
            pyo3::pyclass::CompareOp::Gt => self > other,
            pyo3::pyclass::CompareOp::Ge => self >= other,
        }
    }
    #[getter]
    pub fn get_time(&self) -> u64 {
        self.0.get_time().0
    }
    #[getter]
    pub fn seconds_since_unix_epoch(&self) -> f64 {
        self.0.get_time().as_secs_f64()
    }
}
impl core::fmt::Debug for _Timestamp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        core::fmt::Debug::fmt(&self.0, f)
    }
}

#[pymethods]
impl _Sample {
    #[new]
    pub fn pynew(this: Self) -> Self {
        this
    }
    #[getter]
    pub fn value(&self) -> _Value {
        self.value.clone()
    }
    #[getter]
    pub fn key_expr(&self) -> _KeyExpr {
        _KeyExpr(self.key_expr.clone())
    }
    #[getter]
    pub fn payload(&self) -> _ZBuf {
        self.value.payload()
    }
    #[getter]
    pub fn encoding(&self) -> _Encoding {
        _Encoding(self.value.encoding.clone())
    }
    #[getter]
    pub fn qos(&self) -> _QoS {
        self.qos.clone()
    }
    #[getter]
    pub fn kind(&self) -> _SampleKind {
        self.kind.clone()
    }
    #[getter]
    pub fn timestamp(&self) -> Option<_Timestamp> {
        self.timestamp
    }
    #[staticmethod]
    pub fn new(
        key_expr: _KeyExpr,
        value: _Value,
        qos: _QoS,
        kind: _SampleKind,
        timestamp: Option<_Timestamp>,
    ) -> Self {
        _Sample {
            key_expr: key_expr.0,
            value,
            qos,
            kind,
            timestamp,
        }
    }
    fn __str__(&self) -> String {
        format!("{self:?}")
    }
}

impl From<_Sample> for Sample {
    fn from(sample: _Sample) -> Self {
        let _Sample {
            key_expr,
            value,
            kind,
            timestamp,
            qos,
        } = sample;
        let mut sample = Sample::new(key_expr, value);
        sample.kind = kind.0;
        sample.timestamp = timestamp.map(|t| t.0);
        sample.qos = qos.0;
        sample
    }
}

#[pyclass(subclass)]
#[derive(Clone, Debug)]
pub struct _Reply {
    #[pyo3(get)]
    pub replier_id: _ZenohId,
    pub reply: Result<_Sample, _Value>,
}
#[pymethods]
impl _Reply {
    #[new]
    pub fn pynew(this: Self) -> Self {
        this
    }
    #[getter]
    pub fn ok(&self) -> PyResult<_Sample> {
        match &self.reply {
            Ok(o) => Ok(o.clone()),
            Err(_) => Err(zenoh_core::zerror!("Called `Reply.ok` on a non-ok reply.").to_pyerr()),
        }
    }
    #[getter]
    pub fn err(&self) -> PyResult<_Value> {
        match &self.reply {
            Err(o) => Ok(o.clone()),
            Ok(_) => Err(zenoh_core::zerror!("Called `Reply.err` on a non-err reply.").to_pyerr()),
        }
    }
    #[getter]
    pub fn is_ok(&self) -> bool {
        self.reply.is_ok()
    }
    fn __str__(&self) -> String {
        format!("{self:?}")
    }
}
impl From<Reply> for _Reply {
    fn from(reply: Reply) -> Self {
        _Reply {
            replier_id: _ZenohId(reply.replier_id),
            reply: match reply.sample {
                Ok(o) => Ok(o.into()),
                Err(e) => Err(e.into()),
            },
        }
    }
}

#[pyclass(subclass)]
#[derive(Clone)]
pub struct _Hello(pub(crate) Hello);
#[pymethods]
impl _Hello {
    #[new]
    pub fn pynew(this: Self) -> Self {
        this
    }
    #[getter]
    pub fn zid(&self) -> Option<_ZenohId> {
        Some(_ZenohId(self.0.zid))
    }
    #[getter]
    pub fn whatami(&self) -> Option<&'static str> {
        match self.0.whatami {
            zenoh::config::WhatAmI::Client => Some("client"),
            zenoh::config::WhatAmI::Peer => Some("peer"),
            zenoh::config::WhatAmI::Router => Some("router"),
        }
    }
    #[getter]
    pub fn locators(&self) -> Vec<String> {
        self.0.locators.iter().map(|l| l.to_string()).collect()
    }
    pub fn __str__(&self) -> String {
        self.0.to_string()
    }
}
impl From<Hello> for _Hello {
    fn from(h: Hello) -> Self {
        _Hello(h)
    }
}
