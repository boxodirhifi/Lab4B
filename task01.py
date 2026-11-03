# Lab 4B - Task 1: A new payment method must not touch Checkout
#
# Answers:
# 1.1 PaymentMethod is an ABC with an abstract fee(amount) method and a
#     refundable flag (property).
# 1.2 Percentage-fee methods share PercentFeePayment, configured per provider.
#     ClickPayment and PaymePayment are separate classes and neither inherits
#     from the other, so one provider can change without coupling the other.
# 1.3 Checkout.pay now takes a PaymentMethod object. No if/elif/isinstance.
# 1.4 Adding BankTransfer changed 0 lines of Checkout (only a new class was
#     added).
from abc import ABC, abstractmethod
import inspect


class PaymentMethod(ABC):
    @abstractmethod
    def fee(self, amount: int) -> int:
        """Fee in minor units (sum/tiyin) for a payment of `amount`."""
        ...

    @property
    @abstractmethod
    def refundable(self) -> bool: ...
class PercentFeePayment(PaymentMethod):
    """Shared implementation for payment methods charged by a percentage fee."""

    refundable = True

    def __init__(self, fee_per_mille: int):
        self.fee_per_mille = fee_per_mille

    def fee(self, amount: int) -> int:
        return amount * self.fee_per_mille // 1000


class CardPayment(PercentFeePayment):
    def __init__(self):
        super().__init__(15)


class ClickPayment(PercentFeePayment):
    def __init__(self):
        super().__init__(10)


class PaymePayment(PercentFeePayment):
    def __init__(self):
        super().__init__(10)


class CashPayment(PaymentMethod):
    def fee(self, amount: int) -> int:
        return 0

    refundable = False


class BankTransfer(PaymentMethod):
    FIXED_FEE = 5_000

    def fee(self, amount: int) -> int:
        return self.FIXED_FEE

    refundable = True


class Checkout:
    def pay(self, method: PaymentMethod, amount: int) -> dict:
        return {"charged": amount + method.fee(amount), "refundable": method.refundable}


def test_checkout_has_no_method_branches():
    source = inspect.getsource(Checkout)
    assert " if " not in source
    assert "elif" not in source
    assert "isinstance" not in source


def test_card_fee_and_refundable():
    assert Checkout().pay(CardPayment(), 10_000) == {"charged": 10_150, "refundable": True}


def test_percent_fee_methods_share_implementation_without_coupling():
    assert issubclass(ClickPayment, PercentFeePayment)
    assert issubclass(PaymePayment, PercentFeePayment)
    assert not issubclass(PaymePayment, ClickPayment)
    assert not issubclass(ClickPayment, PaymePayment)
    assert ClickPayment().fee(10_000) == PaymePayment().fee(10_000)


def test_click_and_payme():
    assert Checkout().pay(ClickPayment(), 10_000)["charged"] == 10_100
    assert Checkout().pay(PaymePayment(), 10_000)["charged"] == 10_100


def test_cash_not_refundable():
    assert Checkout().pay(CashPayment(), 10_000) == {"charged": 10_000, "refundable": False}


def test_bank_transfer_fixed_fee():
    assert Checkout().pay(BankTransfer(), 10_000) == {"charged": 15_000, "refundable": True}
    assert Checkout().pay(BankTransfer(), 1_000_000)["charged"] == 1_005_000
