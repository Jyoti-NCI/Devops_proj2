from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    """ class for expense""
    CATEGORY_CHOICES = [
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Shopping', 'Shopping'),
        ('Bills', 'Bills'),
        ('Entertainment', 'Entertainment'),
        ('Others', 'Others'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Credit Card', 'Credit Card'),
        ('Bank Transfer', 'Bank Transfer'),
    ]
    # Linking to User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Title of the expense
    title = models.CharField(max_length=200)
    # Optional description
    description = models.TextField(blank=True, null=True)
    #Amount spent 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Expense category
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    # Type of payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='Cash')
    # Date of expense
    date = models.DateField()
    # When the expense was created
    created_at = models.DateTimeField(auto_now_add=True)
    # If it is recurring expense
    is_recurring = models.BooleanField(default=False)
    # Track modifications - last modified 
    updated_at = models.DateTimeField(auto_now=True)
    # Soft delete feature i.e., inactive means deleted
    is_active = models.BooleanField(default=True)  
    receipt_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - ${self.amount} ({self.category})"
        
    @property
    def is_post_production_completed(self):
        return self.amount > 0.0
