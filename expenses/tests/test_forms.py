import pytest
from django.contrib.auth.models import User
from expenses.forms import RegisterForm, ExpenseForm
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_register_form_valid():
    form_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'password1': 'StrongPass123!',
        'password2': 'StrongPass123!',
    }
    form = RegisterForm(data=form_data)
    assert form.is_valid(), f"Errors: {form.errors}"


@pytest.mark.django_db
def test_register_form_password_mismatch():
    form_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'password1': 'StrongPass123!',
        'password2': 'WrongPassword!',
    }
    form = RegisterForm(data=form_data)
    assert not form.is_valid()
    assert 'password2' in form.errors


@pytest.mark.django_db
def test_expense_form_valid():
    file_data = SimpleUploadedFile("receipt.jpg", b"dummy-content", content_type="image/jpeg")
    form_data = {
        'title': 'Lunch',
        'description': 'Team lunch',
        'amount': 200.00,
        'category': 'Food',
        'payment_method': 'Cash',
        'date': date.today(),
        'is_recurring': False,
    }
    form = ExpenseForm(data=form_data, files={'receipt': file_data})
    assert form.is_valid(), f"Errors: {form.errors}"
