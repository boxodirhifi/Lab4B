# Lab 4B - Task 3: Students charged without VAT
#
# Answers:
# 3.1 FamilySubscription.__init__ forgot super().__init__(user, months), so
#     user, months and base_monthly are never set. The error appears only when
#     price() is called because __init__ itself does nothing with those
#     attributes - Python happily creates the object, and only later access
#     to self.base_monthly raises AttributeError.
# 3.2 Children now override only net(). VAT is applied once, in
#     Subscription.price().
# 3.3 See the tests below:
#     standard 3 months = 168 000, student 3 months = 84 000,
#     family 4 members 3 months = 369 600.
# 3.4 Changing VAT to 15 % touches only Subscription (one line, VAT_PERCENT).
#     No child class needs to be opened.
class Subscription:
    VAT_PERCENT = 12

    def __init__(self, user, months):
        self.user = user
        self.months = months
        self.base_monthly = 50_000

    def net(self) -> int:
        return self.base_monthly * self.months

    def price(self) -> int:
        return self.net() * (100 + self.VAT_PERCENT) // 100


class StudentSubscription(Subscription):
    def net(self) -> int:
        return super().net() // 2


class FamilySubscription(Subscription):
    def __init__(self, user, months, members):
        super().__init__(user, months)
        self.members = members

    def net(self) -> int:
        extra = 20_000 * (len(self.members) - 1) * self.months
        return super().net() + extra


def test_standard_3_months():
    assert Subscription("ali", 3).price() == 168_000


def test_student_3_months():
    assert StudentSubscription("vali", 3).price() == 84_000


def test_family_4_members_3_months():
    assert FamilySubscription("guli", 3, ["a", "b", "c", "d"]).price() == 369_600
