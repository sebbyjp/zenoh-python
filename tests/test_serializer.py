from dataclasses import dataclass

import pytest

from zenoh import ZBytes, deserializer, serializer


@pytest.mark.parametrize(
    "tp, value",
    [
        (bytes, b"foo"),
        (str, "foo"),
        (int, 42),
        (float, 0.5),
        (bool, True),
        (list[int], [0, 1, 2]),
        (dict[str, str], {"foo": "bar"}),
        (tuple[int, int], (0, 1)),
        (list[tuple[int, int]], [(0, 1), (2, 3)]),
        (ZBytes, ZBytes(b"foo")),
        (list, [ZBytes(0), ZBytes(1)]),
        (dict, {ZBytes("foo"): ZBytes("bar")}),
    ],
)
def test_default_serializer(tp, value):
    assert ZBytes(value).deserialize(tp) == value


def test_registered_serializer():
    @dataclass
    class Foo:
        bar: int

    @deserializer
    def deserialize_foo(zbytes: ZBytes) -> Foo:
        return Foo(zbytes.deserialize(int))

    @serializer
    def serialize_foo(foo: Foo) -> ZBytes:
        return ZBytes(foo.bar)

    foo = Foo(42)
    assert ZBytes(foo).deserialize(Foo) == foo


def test_registered_serializer_with_target():
    @dataclass
    class Foo:
        bar: int

    @deserializer(target=Foo)
    def deserialize_foo(zbytes):
        return Foo(zbytes.deserialize(int))

    @serializer(target=Foo)
    def serialize_foo(foo):
        return ZBytes(foo.bar)

    foo = Foo(42)
    assert ZBytes(foo).deserialize(Foo) == foo
