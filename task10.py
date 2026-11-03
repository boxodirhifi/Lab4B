# Lab 4B - Task 10: Choosing the class from a string
#
# Answers:
# 10.1 One registry: PAYMENT_METHODS maps the name to the class.
#      create_payment_method(name) returns the instance.
# 10.2 An unknown name raises UnknownPaymentMethodError; the message lists
#      the supported names so the caller knows what to send.
# 10.3 The name is normalised once with strip().lower(), so " Payme ",
#      "PAYME" and "payme" are the same entry.
# 10.4 One string->class mapping at the edge of the system is acceptable
#      because HTTP requests carry strings and somebody must translate them -
#      better in exactly one audited, tested place. The if/elif inside
#      Checkout was not acceptable because it mixed transport details with
#      business logic and was duplicated across three disagreeing modules.
# 10.5 Adding BankTransfer to the registry = 1 line changed (plus the class
#      itself, which already existed from Task 1). No other module touched.
from task01 import (
    PaymentMethod,
    BankTransfer,
    CardPayment,
    CashPayment,
    ClickPayment,
    PaymePayment,
)
import pytest


class UnknownPaymentMethodError(Exception):
    pass


PAYMENT_METHODS: dict[str, type[PaymentMethod]] = {
    "card": CardPayment,
    "click": ClickPayment,
    "payme": PaymePayment,
    "cash": CashPayment,
    "bank_transfer": BankTransfer,
}


def create_payment_method(name: str) -> PaymentMethod:
    key = name.strip().lower()
    try:
        return PAYMENT_METHODS[key]()
    except KeyError:
        supported = ", ".join(sorted(PAYMENT_METHODS))
        raise UnknownPaymentMethodError(
            f"unknown payment method: {name!r}. Supported: {supported}"
        ) from None


def test_create_known_methods():
    assert isinstance(create_payment_method("card"), CardPayment)
    assert isinstance(create_payment_method("click"), ClickPayment)
    assert isinstance(create_payment_method("payme"), PaymePayment)
    assert isinstance(create_payment_method("cash"), CashPayment)
    assert isinstance(create_payment_method("bank_transfer"), BankTransfer)


def test_normalisation():
    assert isinstance(create_payment_method(" Payme "), PaymePayment)
    assert isinstance(create_payment_method("PAYME"), PaymePayment)
    assert isinstance(create_payment_method("payme"), PaymePayment)


def test_unknown_name_lists_supported():
    with pytest.raises(UnknownPaymentMethodError) as err:
        create_payment_method("bitcoin")
    msg = str(err.value)
    assert "bitcoin" in msg
    for name in ["bank_transfer", "card", "cash", "click", "payme"]:
        assert name in msg
