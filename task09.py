# Lab 4B - Task 9: Invoices that were never saved
#
# Answers:
# 9.1 Expected (naive): all four lines print - updated_at, validate,
#     INSERT, audit. Actual MRO: Invoice -> TimestampMixin -> ValidateMixin
#     -> AuditMixin -> Model. ValidateMixin does NOT call super().save(),
#     so AuditMixin and Model.save are never reached. Only two lines print:
#     "TimestampMixin: set updated_at" and "ValidateMixin: validate fields".
# 9.2 After the fix the output is:
#       TimestampMixin: set updated_at
#       ValidateMixin: validate fields
#       Model.save: INSERT/UPDATE
#       AuditMixin: write audit entry
#     "write audit entry" appears after INSERT because AuditMixin.save()
#     calls super().save() FIRST (which reaches Model and prints INSERT) and
#     only then prints the audit line - the audit entry is written after the
#     row is actually saved.
# 9.3 ValidateMixin must RAISE an exception (ValueError), not return
#     silently. A silent return looks like success to the caller: the
#     invoice is not saved, yet no error surfaces anywhere - exactly the
#     "201 Created but nothing in the DB" bug. An exception stops the whole
#     chain and forces the caller to notice.
# 9.4 class Invoice(TimestampMixin, AuditMixin, Model, ValidateMixin):
#     MRO = TimestampMixin, AuditMixin, Model, ValidateMixin.
#     Output: set updated_at, Model.save: INSERT/UPDATE, AuditMixin:
#     write audit entry. ValidateMixin NEVER runs - validation is silently
#     skipped. Rule: Model must stay LAST in the bases. Everything after the
#     class that does not call super() (or after Model) is dead code.
import pytest


class Model:
    def save(self):
        print("Model.save: INSERT/UPDATE")


class TimestampMixin:
    def save(self):
        print("TimestampMixin: set updated_at")
        super().save()


class ValidateMixin:
    def validate(self) -> bool:
        return getattr(self, "amount", 0) > 0

    def save(self):
        print("ValidateMixin: validate fields")
        if not self.validate():
            raise ValueError("invalid invoice - not saved")
        super().save()


class AuditMixin:
    def save(self):
        super().save()
        print("AuditMixin: write audit entry")


class Invoice(TimestampMixin, ValidateMixin, AuditMixin, Model):
    def __init__(self, amount: int = 100_000):
        self.amount = amount


def test_valid_invoice_prints_all_four_lines(capsys):
    Invoice(amount=100_000).save()
    out = capsys.readouterr().out.splitlines()
    assert out == [
        "TimestampMixin: set updated_at",
        "ValidateMixin: validate fields",
        "Model.save: INSERT/UPDATE",
        "AuditMixin: write audit entry",
    ]


def test_reordered_bases_skip_validation(capsys):
    class ReorderedInvoice(TimestampMixin, AuditMixin, Model, ValidateMixin):
        amount = 0

    assert [c.__name__ for c in ReorderedInvoice.__mro__ if c is not object] == [
        "ReorderedInvoice",
        "TimestampMixin",
        "AuditMixin",
        "Model",
        "ValidateMixin",
    ]
    ReorderedInvoice().save()
    out = capsys.readouterr().out.splitlines()
    assert out == [
        "TimestampMixin: set updated_at",
        "Model.save: INSERT/UPDATE",
        "AuditMixin: write audit entry",
    ]


def test_invalid_invoice_raises_and_stops(capsys):
    with pytest.raises(ValueError):
        Invoice(amount=0).save()
    out = capsys.readouterr().out.splitlines()
    assert out == ["TimestampMixin: set updated_at", "ValidateMixin: validate fields"]
    assert "Model.save: INSERT/UPDATE" not in out
    assert "AuditMixin: write audit entry" not in out
