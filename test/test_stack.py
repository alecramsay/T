#!/usr/bin/env python3
#
# TEST PROGRAM HELPERS - STACK & NAMESPACE
#

from T.stack import *


def sample_stack() -> Stack:
    s: Stack = Stack()
    s.push("foo")
    s.push("bar")
    s.push("bas")

    return s


class TestStacks:
    def test_new(self) -> None:
        s: Stack = Stack()
        assert s.isempty()

    def test_push(self) -> None:
        s: Stack = sample_stack()

        assert list(s._queue_) == ["bas", "bar", "foo"]
        assert s.len() == len(["bas", "bar", "foo"])

    def test_pop(self) -> None:
        s: Stack = sample_stack()

        assert s.pop() == "bas"

    def test_clear(self) -> None:
        s: Stack = sample_stack()

        s.clear()
        assert s.isempty()

    def test_top(self) -> None:
        s: Stack = sample_stack()

        assert s.first() == "bas"
        assert list(s._queue_) == ["bas", "bar", "foo"]

    def test_replace_top(self) -> None:
        s: Stack = sample_stack()

        s.replace_top("bat")
        assert list(s._queue_) == ["bat", "bar", "foo"]

    def test_swap(self):
        s = sample_stack()

        s.swap()
        assert list(s._queue_) == ["bar", "bas", "foo"]

    def test_reverse(self) -> None:
        s: Stack = sample_stack()

        s.reverse()
        assert list(s._queue_) == ["foo", "bar", "bas"]

    def test_rotate(self) -> None:
        s: Stack = sample_stack()

        s.rotate()
        assert list(s._queue_) == ["foo", "bas", "bar"]


### END ###
