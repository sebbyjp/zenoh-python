#
# Copyright (c) 2024 ZettaScale Technology
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors:
#   ZettaScale Zenoh Team, <zenoh@zettascale.tech>
#
<<<<<<< HEAD
from typing import Any

from .closures import Closure, Handler, IClosure, IHandler, IntoClosure, IntoHandler, ListCollector, Queue
from .config import Config
from .enums import CongestionControl, Encoding, Priority, QueryConsolidation, QueryTarget, Reliability, SampleKind
from .keyexpr import IntoKeyExpr, IntoSelector, KeyExpr, Selector
from .queryable import Query, Queryable
from .session import Info, Publisher, PullSubscriber, Session, Subscriber
from .value import Hello, IntoSample, IntoValue, IValue, Reply, Sample, Timestamp, Value, ZenohId
from .zenoh import init_logger
from .zenoh import scout as _scout


def open(*args, **kwargs):
    """Open a Zenoh session.

    :param config: The configuration of the Zenoh session
    :type config: Config
    :rtype: Session

    :Example:

    >>> import zenoh
    >>> s = zenoh.open(zenoh.Config())
    """
    return Session(*args, **kwargs)

class Scout:
    def __init__(self, inner, receiver) -> None:
        self._inner_ = inner
        self.receiver = receiver

    def stop(self) -> None:
        self._inner_ = None

def scout(handler: IntoHandler[Hello, Any, Any] = None, what: str | None = None, config: Config = None, timeout=None):
    """Scout for routers and/or peers.

    This spawns a task that periodically sends scout messages for a specified duration and returns
    a list of received :class:`Hello` messages.

    :param what: The kind of zenoh process to scout for
    :param config: The configuration to use for scouting
    :param timeout: the duration of scout (in seconds)
    :param handler:
    :rtype: list of :class:`Hello`

    :Example:

    >>> import zenoh
    >>> for hello in zenoh.scout(what = "peer|router", timeout=1.0).receiver():
    ...     print(hello)
    """
    from threading import Timer
    if handler is None:
        handler = ListCollector()
    handler = Handler(handler, lambda x: Hello._upgrade_(x))
    scout = _scout(handler.closure, config, what)
    scout = Scout(scout, handler.receiver)
    if timeout:
        Timer(timeout, lambda: scout.stop()).start()
    return scout
=======
from .zenoh import *
>>>>>>> aa19e083bfe32cdae7545c9aea8e29ae6614b657
