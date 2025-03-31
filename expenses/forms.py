"""Forms for user registration and expense management."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Expense

class RegisterForm(UserCreationForm):
    """Form for registering new users with additional fields."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "password1", "password2"]
class ExpenseForm(forms.ModelForm):
    """Form for creating and updating expenses."""
    receipt = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Expense
        fields = ['title', 
        'description', 
        'amount', 
        'category', 
        'payment_method', 
        'date', 
        'receipt', 
        'is_recurring']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    