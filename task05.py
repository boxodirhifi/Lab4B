# Lab 4B - Task 5: A promotion that broke the payroll history
#
# Answers:
# 5.1 "A lecturer is an employee" is true only while the object lives, but on
#     promotion the old object was deleted and a new one created. What really
#     changes on promotion is the *role*, not the person. So role must not be
#     the class.
# 5.2 Employee now has a role (LecturerRole / HeadRole). monthly_pay() asks
#     the role - no if on the kind of role.
# 5.3 employee.change_role(new_role) swaps the role; emp_id and the object
#     itself stay the same, so payroll/timesheet/access references still work.
# 5.4 Employee keeps a role history: a list of (role, start_date). Employee
#     has-a history - composition (the history belongs to the employee and
#     dies with it). role_at(date) picks the latest entry with start_date <=
#     date, so payroll for a past month uses the role that was active then.
from datetime import date
import pytest


class LecturerRole:
    def __init__(self, hours: int):
        self.hours = hours

    def monthly_pay(self) -> int:
        return self.hours * 120_000


class HeadRole:
    def __init__(self, salary: int):
        self.salary = salary

    def monthly_pay(self) -> int:
        return self.salary + 3_000_000


class Employee:
    def __init__(self, emp_id: int, name: str, role, today: date | None = None):
        self.emp_id = emp_id
        self.name = name
        self.role = role
        self.role_history = [(role, today or date.today())]

    def monthly_pay(self) -> int:
        return self.role.monthly_pay()

    def role_at(self, when: date):
        active_role = None
        active_start = None
        for role, start in self.role_history:
            if start <= when and (active_start is None or start >= active_start):
                active_role, active_start = role, start
        if active_role is None:
            raise ValueError(f"no role recorded on {when.isoformat()}")
        return active_role

    def monthly_pay_for(self, when: date) -> int:
        return self.role_at(when).monthly_pay()

    def change_role(self, new_role, when: date | None = None) -> None:
        self.role = new_role
        self.role_history.append((new_role, when or date.today()))


def test_lecturer_pay():
    e = Employee(1, "Aziza", LecturerRole(hours=40))
    assert e.monthly_pay() == 4_800_000


def test_promotion_keeps_same_object_and_id():
    e = Employee(1, "Aziza", LecturerRole(hours=40), today=date(2026, 1, 1))
    staff = [e]
    e.change_role(HeadRole(salary=14_000_000), when=date(2026, 11, 1))
    assert staff[0] is e
    assert e.emp_id == 1
    assert e.monthly_pay() == 17_000_000


def test_role_history():
    e = Employee(1, "Aziza", LecturerRole(hours=40), today=date(2026, 1, 1))
    e.change_role(HeadRole(salary=14_000_000), when=date(2026, 11, 1))
    assert len(e.role_history) == 2
    assert isinstance(e.role_history[0][0], LecturerRole)
    assert isinstance(e.role_history[1][0], HeadRole)
    assert e.role_history[0][1] == date(2026, 1, 1)
    assert e.role_history[1][1] == date(2026, 11, 1)


def test_payroll_for_historical_date_uses_role_active_then():
    e = Employee(1, "Aziza", LecturerRole(hours=40), today=date(2026, 1, 1))
    e.change_role(HeadRole(salary=14_000_000), when=date(2026, 11, 1))
    e.change_role(LecturerRole(hours=80), when=date(2026, 12, 1))
    assert e.monthly_pay_for(date(2026, 6, 30)) == 4_800_000
    assert e.monthly_pay_for(date(2026, 11, 15)) == 17_000_000
    assert e.monthly_pay_for(date(2026, 12, 15)) == 9_600_000


def test_payroll_before_first_role_raises():
    e = Employee(1, "Aziza", LecturerRole(hours=40), today=date(2026, 1, 1))
    with pytest.raises(ValueError):
        e.monthly_pay_for(date(2025, 12, 31))
