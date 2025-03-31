"""URL configuration for the expenses app."""

from django.urls import path
from expenses import views
from django.contrib.auth import views as auth_views
# pylint: disable=invalid-name
app_name = 'expenses'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Authentication
    path("sign-up/", views.sign_up, name="sign_up"),
    path("login/sign-up/", views.sign_up, name="sign_up"),
    path('logout/', views.logout_view, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # Expense Management
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/update/<int:expense_id>/', views.update_expense, name='update_expense'),
    path('expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('expenses/export_pdf/', views.export_expenses_pdf, name='export_expenses_pdf'),
    # Reports
    path('expenses/generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('expenses/send_report/', views.send_email_report, name='send_email_report'),
]
