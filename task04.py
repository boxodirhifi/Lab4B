# Lab 4B - Task 4: The audit log that could be erased
#
# Answers:
# 4.1 No, an AuditLog is not a list - it only holds entries. Inheriting from
#     list exposes clear(), sort(), pop(), insert(), remove(), append(),
#     __setitem__ ... any of these breaks the append-only rule. Three examples
#     that break it: clear(), sort(), pop().
# 4.2 AuditLog now *has* a list (composition). Public interface:
#     record(user, action), len(log), iter(log), last(n).
# 4.3 One entry is a plain tuple (user, action) - tuples are immutable, so a
#     recorded entry cannot be changed.
# 4.4 Overriding clear() and pop() is worse: dir(list) returns 48 names,
#     11 of them public non-dunder methods (clear, sort, pop, insert, ...),
#     and dunder methods such as __setitem__, __delitem__, __iadd__ can
#     also break the rule. You would have to remember every one forever.
#     Composition simply does not offer those methods.
#     last(n) returns the newest n entries; last(0) returns [], and a
#     negative n raises ValueError.
import pytest


class AuditLog:
    def __init__(self):
        self._entries: list[tuple[str, str]] = []

    def record(self, user: str, action: str) -> None:
        self._entries.append((user, action))

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def last(self, n: int) -> list[tuple[str, str]]:
        if n < 0:
            raise ValueError("n must be >= 0")
        if n == 0:
            return []
        return self._entries[-n:]


def test_record_and_len():
    log = AuditLog()
    log.record("admin", "approve_loan#77")
    assert len(log) == 1


def test_iteration_and_last():
    log = AuditLog()
    log.record("a", "one")
    log.record("b", "two")
    log.record("c", "three")
    assert list(log) == [("a", "one"), ("b", "two"), ("c", "three")]
    assert log.last(2) == [("b", "two"), ("c", "three")]
    assert log.last(10) == [("a", "one"), ("b", "two"), ("c", "three")]


def test_last_zero():
    log = AuditLog()
    log.record("admin", "approve_loan#77")
    assert log.last(0) == []


def test_last_negative_raises():
    log = AuditLog()
    log.record("admin", "approve_loan#77")
    with pytest.raises(ValueError):
        log.last(-1)


def test_destructive_list_methods_are_gone():
    log = AuditLog()
    assert not hasattr(log, "clear")
    assert not hasattr(log, "sort")
    assert not hasattr(log, "pop")
    with pytest.raises(TypeError):
        log[0] = ("x", "y")


def test_entries_are_immutable():
    log = AuditLog()
    log.record("admin", "approve_loan#77")
    entry = next(iter(log))
    assert isinstance(entry, tuple)
