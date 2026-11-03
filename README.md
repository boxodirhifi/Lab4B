# Lab 4B — Inheritance, Polymorphism and Composition

Turin Polytechnic University in Tashkent · Design of Software System

Tasks 1–10 (bonus tasks E1–E5 skipped on purpose). One file per task,
answers are comments at the top of each file, tests are in the same file.

## Run

```bash
pip install pytest mypy pyflakes
cd Lab4B_Inheritance_Polymorphism
pytest .
mypy task06.py
```

## Files

| File | Topic |
|------|-------|
| task01.py | PaymentMethod ABC, Checkout without if/elif, BankTransfer |
| task02.py | Abstract Notifier, Telegram/SMS, per-channel text limit |
| task03.py | Subscription with net() hook, VAT in one place |
| task04.py | AuditLog with composition (append-only) |
| task05.py | Employee with pluggable role + role history |
| task06.py | Duck typing + typing.Protocol (Writable) for export |
| task07.py | Money value object (frozen dataclass) |
| task08.py | One search() instead of fake "overloading" |
| task09.py | Mixin save() chain, MRO, validation that stops the save |
| task10.py | String → class registry at the HTTP edge |
