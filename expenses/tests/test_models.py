from mixer.backend.django import mixer
import pytest
@pytest.mark.django_db
class TestModels:
    def test_expense_is_post_production_completed(self):
        expense = mixer.blend('expenses.Expense', amount=120.0)
        assert expense.is_post_production_completed == True
    def test_expense_is_not_post_production_completed(self):
        expense = mixer.blend('expenses.Expense', amount=0.0)
        assert expense.is_post_production_completed == False