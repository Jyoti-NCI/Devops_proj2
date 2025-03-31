from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from .models import Expense
from .forms import ExpenseForm, RegisterForm
from reportlab.pdfgen import canvas
from io import BytesIO
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime
from django.contrib.auth.models import Group
from .aws_utils.s3_utils import upload_to_s3
from .aws_utils.sns_utils import send_sns_alert
from .aws_utils.cloudwatch_utils import log_to_cloudwatch
from django.conf import settings
from django.contrib import messages

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('/login')
    else:
        form = RegisterForm()
    return render(request, 'registration/sign_up.html', {"form": form})
    
def logout_view(request):
    logout(request)
    return redirect('expenses:login')

# Dashboard view with statistics
@login_required
def dashboard(request):
    if request.user.is_superuser:
        expenses = Expense.objects.all()
    else:
        expenses = Expense.objects.filter(user=request.user, is_active=True)
    total_expense = sum(exp.amount for exp in expenses) if expenses else 0
    category_expenses = {cat: sum(exp.amount for exp in expenses if exp.category == cat) for cat, _ in Expense.CATEGORY_CHOICES}
    return render(request, 'expenses/dashboard.html', {
        'expenses': expenses,
        'total_expense': total_expense,
        'category_expenses': category_expenses
    })

# List all expenses with filtering
@login_required
def expense_list(request):
    if request.user.is_superuser:
        expenses = Expense.objects.all()  # Admin sees all
    else:
        expenses = Expense.objects.filter(user=request.user, is_active=True)  # Users see only theirs
    # Filtering the expenses
    category_filter = request.GET.get('category', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    if category_filter:
        expenses = expenses.filter(category=category_filter)
    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])
    return render(request, 'expenses/expense_list.html', {'expenses': expenses, 'expense': Expense, 'selected_category': category_filter,
        'start_date': start_date,
        'end_date': end_date})

# Add new expense
@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            # Assigning logged in user
            expense.user = request.user
            # Handle receipt upload to S3
            if request.FILES.get('receipt'):
                file_obj = request.FILES['receipt']
                uploaded_url = upload_to_s3(file_obj, settings.AWS_S3_BUCKET_NAME)
                expense.receipt_url = uploaded_url

            expense.save()

            # Send SNS Alert if expense amount is high
            if expense.amount >= 10000:
                send_sns_alert(
                    message=f"⚠️ High Expense Alert!\n\nUser: {request.user.username}\nAmount: ₹{expense.amount}\nCategory: {expense.category}\nTitle: {expense.title}",
                    subject="High Expense Alert"
                )

            log_to_cloudwatch(f"[EXPENSE CREATED] ₹{expense.amount} - {expense.category} by {request.user.username}")
            messages.success(request, 'Expense added successfully!')
            return redirect('expenses:expense_list')
        else:
            print("Form is not valid:", form.errors)
    else:
        form = ExpenseForm()

    return render(request, 'expenses/expense_form.html', {'form': form, 'expense': None})

# Update expense
@login_required
def update_expense(request, expense_id):
    try:
        if request.user.is_superuser:
            expense = Expense.objects.get(id=expense_id)
        else:
            expense = Expense.objects.get(id=expense_id, user=request.user, is_active=True)
    except Expense.DoesNotExist:
        raise Http404("Expense not found")
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            updated_expense = form.save(commit=False)
             # Upload new receipt to S3 if provided
            if request.FILES.get('receipt'):
                file_obj = request.FILES['receipt']
                uploaded_url = upload_to_s3(file_obj, settings.AWS_S3_BUCKET_NAME)
                updated_expense.receipt_url = uploaded_url

            updated_expense.save()

            # SNS alert if updated amount is large
            if updated_expense.amount >= 300:
                send_sns_alert(
                    message=f"⚠️ High Expense Updated!\n\nUser: {request.user.username}\nAmount: ₹{updated_expense.amount}\nCategory: {updated_expense.category}\nTitle: {updated_expense.title}",
                    subject="Updated Expense Alert"
                )

            log_to_cloudwatch(f"[EXPENSE UPDATED] ₹{updated_expense.amount} - {updated_expense.category} by {request.user.username}")
            messages.success(request, "Expense updated successfully!")
            return redirect('expenses:expense_list')
        else:
            print("Update form is invalid:", form.errors)
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expenses/expense_form.html', {'form': form, 'expense': expense})

# Delete expense
@login_required
def delete_expense(request, expense_id):
    try:
        if request.user.is_superuser:
            expense = Expense.objects.get(id=expense_id)
        else:
            expense = Expense.objects.get(id=expense_id, user=request.user, is_active=True)
    except Expense.DoesNotExist:
        raise Http404("Expense not found")
    if request.method == 'POST':
        title = expense.title
        amount = expense.amount
        #expense.is_active = False  # Soft delete
        expense.delete()

        log_to_cloudwatch(f"[EXPENSE DELETED] ₹{amount} - {title} by {request.user.username}")
        messages.success(request, "Expense deleted successfully.")
        return redirect('expenses:expense_list')

    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})
@login_required
def export_expenses_pdf(request):
    category_filter = request.GET.get('category', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()
    print("Exporting with filters:")
    print("Category:", category_filter)
    print("Start:", start_date)
    print("End:", end_date)

    #superuser sees all, others see their own
    if request.user.is_superuser:
        expenses = Expense.objects.all()
    else:
        expenses = Expense.objects.filter(user=request.user, is_active=True)

    if category_filter:
        expenses = expenses.filter(category=category_filter)

    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])

    if not expenses.exists():
        return HttpResponse("No expenses found for the selected filters.", content_type="text/plain")

    return generate_pdf(request, expenses)  
    
@login_required
def generate_pdf(request, expenses):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 14)
    p.drawString(100, 800, "Filtered Expense Report")

    y = 780
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Date")
    p.drawString(150, y, "Title")
    p.drawString(300, y, "Amount")
    p.drawString(400, y, "Category")
    y -= 20
    p.setFont("Helvetica", 12)

    for expense in expenses:
        p.drawString(50, y, str(expense.date))
        p.drawString(150, y, expense.title[:20])  
        p.drawString(300, y, f"${expense.amount}")
        p.drawString(400, y, expense.category)
        y -= 20
        if y < 50:  
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 780

    p.save()
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Filtered_Expense_Report.pdf"'
    return response

@login_required
def send_email_report(request):
    # Base queryset
    if request.user.is_superuser:
        expenses = Expense.objects.all()
    else:
        expenses = Expense.objects.filter(user=request.user, is_active=True)

    # Optional filters (if you later want to filter by GET params like category/date)
    category_filter = request.GET.get('category', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    if category_filter:
        expenses = expenses.filter(category=category_filter)
    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])

    # No data case
    if not expenses.exists():
        return HttpResponse("No expenses to report", content_type="text/plain")

    # Generate the PDF file
    pdf_response = generate_pdf(request, expenses)
    pdf_data = pdf_response.content

    subject = "Your Expense Report"
    html_message = render_to_string('expenses/email_report.html', {
        'user': request.user,
        'expenses': expenses
    })
    plain_message = strip_tags(html_message)

    email = EmailMessage(
        subject,
        plain_message,
        'jyotijakhar2401@gmail.com',  # Sender's email
        [request.user.email]          # Recipient
    )
    email.attach('Expense_Report.pdf', pdf_data, 'application/pdf')
    email.send()

    return HttpResponse("Expense report emailed successfully", content_type="text/plain")