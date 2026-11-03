# Lab 4B - Task 7: Dollars added to sums
#
# Answers:
# 7.1 @dataclass(order=True) is wrong because it compares fields in order of
#     definition (amount first, then currency), so Money(100, 'USD') >
#     Money(1, 'UZS') would be True - it compares amounts across different
#     currencies and ignores the currency. Money only supports < for equal
#     currencies; mixed currencies raise CurrencyMismatchError, while
#     non-Money operands are left to Python's normal typing rules.
# 7.2 sum() starts with 0 and calls 0 + Money(...); int has no __add__ for
#     Money, so it fails with TypeError. For production I choose explicit
#     sum(items, start=Money(0, 'UZS')) because it shows which currency the
#     starting zero has. __radd__ accepting 0 is also provided so plain
#     sum(items) works, and both styles are tested.
# 7.3 __add__ and __eq__ must return NotImplemented (not False, not an
#     exception) when the other object is not a Money, so Python can try the
#     other operand's reflected method.
# 7.4 Money * Money - no (tiyin squared is meaningless). Money / Money -
#     no for now: a ratio is the only sensible result and it is a plain
#     number, not Money; if ever needed, add it deliberately. Rule: only add
#     operators whose meaning is obvious.
from dataclasses import dataclass, FrozenInstanceError
import pytest


class CurrencyMismatchError(Exception):
    pass


@dataclass(frozen=True)
class Money:
    """amount is an int in minor units (tiyin, cents). Never changes."""

    amount: int
    currency: str

    def __post_init__(self):
        if not isinstance(self.amount, int):
            raise TypeError("amount must be an int")
        if not isinstance(self.currency, str):
            raise TypeError("currency must be a str")
        cur = self.currency.upper()
        if len(cur) != 3 or not cur.isalpha():
            raise ValueError("currency must be a 3-letter code like 'UZS'")
        object.__setattr__(self, "currency", cur)

    def _check_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(f"{self.currency} != {other.currency}")

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._check_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __radd__(self, other):
        if isinstance(other, int) and other == 0:
            return self
        return NotImplemented

    def __mul__(self, n):
        if not isinstance(n, int):
            return NotImplemented
        return Money(self.amount * n, self.currency)

    __rmul__ = __mul__

    def __lt__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._check_same_currency(other)
        return self.amount < other.amount


def test_add_same_currency():
    assert Money(100, "UZS") + Money(250, "UZS") == Money(350, "UZS")


def test_add_different_currency_raises():
    with pytest.raises(CurrencyMismatchError):
        Money(100, "USD") + Money(100, "UZS")


def test_mul_both_sides():
    assert Money(100, "UZS") * 3 == Money(300, "UZS")
    assert 3 * Money(100, "UZS") == Money(300, "UZS")


def test_eq_with_int_is_false_not_error():
    assert (Money(500, "UZS") == 500) is False


def test_ordering_same_currency():
    assert Money(100, "UZS") < Money(200, "UZS")
    with pytest.raises(CurrencyMismatchError):
        Money(100, "USD") < Money(200, "UZS")


def test_non_money_operands_are_returned_to_python():
    m = Money(1, "UZS")
    assert m.__add__(500) is NotImplemented
    assert m.__eq__(500) is NotImplemented
    assert m.__radd__(500) is NotImplemented
    assert m.__mul__(1.5) is NotImplemented
    assert m.__lt__("<") is NotImplemented


def test_sum_works():
    items = [Money(100, "UZS"), Money(200, "UZS"), Money(300, "UZS")]
    assert sum(items) == Money(600, "UZS")
    assert sum(items, start=Money(0, "UZS")) == Money(600, "UZS")


def test_money_is_hashable_dict_key():
    assert hash(Money(100, "uzs")) == hash(Money(100, "UZS"))
    d = {Money(100, "UZS"): "ok"}
    assert d[Money(100, "UZS")] == "ok"


def test_money_never_changes():
    with pytest.raises(FrozenInstanceError):
        Money(1, "UZS").amount = 2


def test_invalid_types_are_rejected():
    with pytest.raises(TypeError):
        Money("1", "UZS")
    with pytest.raises(TypeError):
        Money(1, 500)


def test_invalid_currency_code_raises():
    with pytest.raises(ValueError):
        Money(1, "US")


def test_currency_is_normalised():
    assert Money(1, "uzs").currency == "UZS"
