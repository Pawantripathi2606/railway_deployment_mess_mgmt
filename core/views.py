from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO

from .models import (UserProfile, Payment, Grocery, FixedExpense, Message,
                     MealPlan, ActivityLog, UserSettings, MessSettings)
from .forms import (UserRegistrationForm, UserEditForm, PaymentForm, UserPaymentForm,
                    GroceryForm, FixedExpenseForm, MessageForm, AdminReplyForm)
from .meal_forms import MealPlanForm
from .decorators import admin_required, user_required, role_required


# ==================== Authentication Views ====================

def landing_page(request):
    """Landing page - Under Construction"""
    return render(request, 'landing.html')


def role_selection(request):
    """Landing page for role selection"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'auth/role_selection.html')


def user_login(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'profile') and user.profile.is_active:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Your account is inactive. Please contact admin.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')


def user_logout(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('role_selection')


def admin_login(request):
    """Admin-only login view - NO Google OAuth"""
    # Disable CSRF for this view if needed, or ensure template has token
    if request.user.is_authenticated:
        # If already logged in, check if admin
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return redirect('admin_dashboard')
        else:
            messages.warning(request, 'You need admin privileges to access this page.')
            return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'admin/admin_login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is admin
            if hasattr(user, 'profile') and user.profile.role == 'admin':
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('admin_dashboard')
            else:
                messages.warning(request, '⚠️ User Access Detected! This is the Admin Portal. Regular users should login from the User Portal instead.')
                return redirect('account_login')
        else:
            messages.error(request, 'Invalid admin credentials.')
    
    return render(request, 'admin/admin_login.html')


@login_required
def dashboard(request):
    """Main dashboard - routes to admin or user dashboard based on role"""
    if hasattr(request.user, 'profile'):
        if request.user.profile.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('user_dashboard')
    else:
        messages.error(request, 'Profile not found. Please contact admin.')
        return redirect('logout')


# ==================== Admin Views ====================

@admin_required
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    current_month = datetime.now().strftime('%Y-%m')
    
    # Statistics
    total_users = UserProfile.objects.filter(role='user', is_active=True).count()
    total_payments = Payment.objects.filter(month_year=current_month, status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_payments = Payment.objects.filter(month_year=current_month, status='pending').count()
    total_groceries = Grocery.objects.filter(month_year=current_month).aggregate(Sum('price'))['price__sum'] or 0
    
    # Fixed expenses for current month
    try:
        fixed_expense = FixedExpense.objects.get(month_year=current_month)
        total_fixed = fixed_expense.total_fixed_expense
    except FixedExpense.DoesNotExist:
        total_fixed = 0
    
    # Pending messages
    pending_messages = Message.objects.filter(status='pending').count()
    
    # Recent payments
    recent_payments = Payment.objects.select_related('user').order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_payments': total_payments,
        'pending_payments': pending_payments,
        'total_groceries': total_groceries,
        'total_fixed': total_fixed,
        'total_expenses': total_groceries + total_fixed,
        'pending_messages': pending_messages,
        'recent_payments': recent_payments,
        'current_month': current_month,
    }
    
    return render(request, 'admin/dashboard.html', context)


# ==================== User Management Views ====================

@admin_required
def user_list(request):
    """List all users"""
    users = UserProfile.objects.select_related('user').filter(role='user').order_by('-created_at')
    context = {'users': users}
    return render(request, 'admin/user_list.html', context)


@admin_required
def user_create(request):
    """Create new user"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('user_list')
    else:
        form = UserRegistrationForm()
    
    context = {'form': form}
    return render(request, 'admin/user_create.html', context)


@admin_required
def user_edit(request, user_id):
    """Edit existing user"""
    profile = get_object_or_404(UserProfile, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=profile)
    
    context = {'form': form, 'profile': profile}
    return render(request, 'admin/user_edit.html', context)


@admin_required
def user_delete(request, user_id):
    """Delete user"""
    profile = get_object_or_404(UserProfile, id=user_id)
    
    if request.method == 'POST':
        username = profile.user.username
        profile.user.delete()  # This will cascade delete the profile
        messages.success(request, f'User {username} deleted successfully.')
        return redirect('user_list')
    
    context = {'profile': profile}
    return render(request, 'admin/user_delete.html', context)


# ==================== Payment Management Views ====================

@admin_required
def payment_list(request):
    """List all payments"""
    month_filter = request.GET.get('month', datetime.now().strftime('%Y-%m'))
    payments = Payment.objects.select_related('user').filter(month_year=month_filter).order_by('-created_at')
    
    # Get distinct months for filter
    months = Payment.objects.values_list('month_year', flat=True).distinct().order_by('-month_year')
    
    context = {
        'payments': payments,
        'months': months,
        'selected_month': month_filter,
    }
    return render(request, 'admin/payment_list.html', context)


@admin_required
def payment_create(request):
    """Create new payment"""
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment record created successfully.')
            return redirect('payment_list')
    else:
        form = PaymentForm()
    
    context = {'form': form}
    return render(request, 'admin/payment_create.html', context)


@admin_required
def payment_edit(request, payment_id):
    """Edit existing payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment updated successfully.')
            return redirect('payment_list')
    else:
        form = PaymentForm(instance=payment)
    
    context = {'form': form, 'payment': payment}
    return render(request, 'admin/payment_edit.html', context)


@admin_required
def payment_delete(request, payment_id):
    """Delete payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully.')
        return redirect('payment_list')
    
    context = {'payment': payment}
    return render(request, 'admin/payment_delete.html', context)


# ==================== Grocery Management Views ====================

@admin_required
def grocery_list(request):
    """List all grocery items"""
    month_filter = request.GET.get('month', datetime.now().strftime('%Y-%m'))
    groceries = Grocery.objects.filter(month_year=month_filter).order_by('-created_at')
    
    # Get distinct months
    months = Grocery.objects.values_list('month_year', flat=True).distinct().order_by('-month_year')
    
    # Calculate total
    total = groceries.aggregate(Sum('price'))['price__sum'] or 0
    
    context = {
        'groceries': groceries,
        'months': months,
        'selected_month': month_filter,
        'total': total,
    }
    return render(request, 'admin/grocery_list.html', context)


@admin_required
def grocery_create(request):
    """Create new grocery item"""
    if request.method == 'POST':
        form = GroceryForm(request.POST)
        if form.is_valid():
            grocery = form.save(commit=False)
            grocery.created_by = request.user
            grocery.save()
            messages.success(request, 'Grocery item added successfully.')
            return redirect('grocery_list')
    else:
        form = GroceryForm(initial={'month_year': datetime.now().strftime('%Y-%m')})
    
    context = {'form': form}
    return render(request, 'admin/grocery_create.html', context)


@admin_required
def grocery_edit(request, grocery_id):
    """Edit existing grocery item"""
    grocery = get_object_or_404(Grocery, id=grocery_id)
    
    if request.method == 'POST':
        form = GroceryForm(request.POST, instance=grocery)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grocery item updated successfully.')
            return redirect('grocery_list')
    else:
        form = GroceryForm(instance=grocery)
    
    context = {'form': form, 'grocery': grocery}
    return render(request, 'admin/grocery_edit.html', context)


@admin_required
def grocery_delete(request, grocery_id):
    """Delete grocery item"""
    grocery = get_object_or_404(Grocery, id=grocery_id)
    
    if request.method == 'POST':
        grocery.delete()
        messages.success(request, 'Grocery item deleted successfully.')
        return redirect('grocery_list')
    
    context = {'grocery': grocery}
    return render(request, 'admin/grocery_delete.html', context)


# ==================== Fixed Expense Management Views ====================

@admin_required
def expense_list(request):
    """List all fixed expenses"""
    expenses = FixedExpense.objects.all().order_by('-month_year')
    context = {'expenses': expenses}
    return render(request, 'admin/expense_list.html', context)


@admin_required
def expense_create(request):
    """Create new fixed expense"""
    if request.method == 'POST':
        form = FixedExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fixed expense created successfully.')
            return redirect('expense_list')
    else:
        form = FixedExpenseForm(initial={'month_year': datetime.now().strftime('%Y-%m')})
    
    context = {'form': form}
    return render(request, 'admin/expense_create.html', context)


@admin_required
def expense_edit(request, expense_id):
    """Edit existing fixed expense"""
    expense = get_object_or_404(FixedExpense, id=expense_id)
    
    if request.method == 'POST':
        form = FixedExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fixed expense updated successfully.')
            return redirect('expense_list')
    else:
        form = FixedExpenseForm(instance=expense)
    
    context = {'form': form, 'expense': expense}
    return render(request, 'admin/expense_edit.html', context)


@admin_required
def expense_delete(request, expense_id):
    """Delete fixed expense"""
    expense = get_object_or_404(FixedExpense, id=expense_id)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Fixed expense deleted successfully.')
        return redirect('expense_list')
    
    context = {'expense': expense}
    return render(request, 'admin/expense_delete.html', context)


# ==================== Message Management Views ====================

@admin_required
def admin_messages(request):
    """View all messages from users"""
    status_filter = request.GET.get('status', 'all')
    
    # Only show user-initiated messages, not system reminders
    if status_filter == 'all':
        message_list = Message.objects.select_related('user').filter(message_type='user').order_by('-created_at')
    else:
        message_list = Message.objects.select_related('user').filter(message_type='user', status=status_filter).order_by('-created_at')
    
    context = {
        'messages': message_list,
        'status_filter': status_filter,
    }
    return render(request, 'admin/messages.html', context)


@admin_required
def message_resolve(request, message_id):
    """Mark message as resolved"""
    message = get_object_or_404(Message, id=message_id)
    message.status = 'resolved'
    message.resolved_at = timezone.now()
    message.save()
    messages.success(request, 'Message marked as resolved.')
    return redirect('admin_messages')


@admin_required
def message_reply(request, message_id):
    """Admin reply to user message"""
    message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        form = AdminReplyForm(request.POST, instance=message)
        if form.is_valid():
            message = form.save(commit=False)
            message.replied_at = timezone.now()
            message.save()
            messages.success(request, f'Reply sent to {message.user.get_full_name()}')
            return redirect('admin_messages')
    else:
        form = AdminReplyForm(instance=message)
    
    context = {
        'form': form,
        'message': message,
    }
    return render(request, 'admin/message_reply.html', context)


@admin_required
def send_payment_reminder(request, payment_id):
    """Send payment reminder to user"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Get UPI settings
    try:
        mess_settings = MessSettings.objects.first()
        upi_id = mess_settings.admin_upi_id if mess_settings and mess_settings.admin_upi_id else "Not configured"
    except MessSettings.DoesNotExist:
        upi_id = "Not configured"
    
    # Create default reminder message
    default_message = f"""Dear {payment.user.first_name},

This is a friendly reminder that your mess payment for {payment.month_year} is currently {payment.get_status_display().lower()}.

Payment Amount: ₹{payment.amount}
Status: {payment.get_status_display()}

Please pay your bill on time to avoid any inconvenience.

Payment Details:
UPI ID: {upi_id}

Thank you for your cooperation!

- Mess Management"""
    
    # Create message
    Message.objects.create(
        user=payment.user,
        subject=f"Payment Reminder - {payment.month_year}",
        message=default_message,
        message_type='system',  # Mark as system message so it doesn't show in admin section
        status='pending'
    )
    
    messages.success(request, f'Payment reminder sent to {payment.user.get_full_name()}')
    return redirect('payment_list')


# ==================== Meal Calendar ====================

@admin_required
def meal_calendar(request):
    """Admin view meal calendar"""
    from datetime import datetime, timedelta
    import calendar
    
    # Get current month/year or from query params
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    # Get all meal plans for this month
    meal_plans = MealPlan.objects.filter(
        date__year=year,
        date__month=month
    )
    
    # Create a dictionary for easy lookup
    meal_dict = {mp.date.day: mp for mp in meal_plans}
    
    # Get calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Calculate prev/next month
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    
    context = {
        'calendar': cal,
        'meal_dict': meal_dict,
        'year': year,
        'month': month,
        'month_name': month_name,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': datetime.now().date(),
    }
    return render(request, 'admin/meal_calendar.html', context)


@admin_required
def meal_plan_create(request):
    """Create meal plan"""
    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meal plan created successfully.')
            return redirect('meal_calendar')
    else:
        # Pre-fill date if provided
        initial_date = request.GET.get('date')
        form = MealPlanForm(initial={'date': initial_date} if initial_date else {})
    
    context = {'form': form}
    return render(request, 'admin/meal_plan_form.html', context)


@admin_required
def meal_plan_edit(request, plan_id):
    """Edit meal plan"""
    meal_plan = get_object_or_404(MealPlan, id=plan_id)
    
    if request.method == 'POST':
        form = MealPlanForm(request.POST, instance=meal_plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meal plan updated successfully.')
            return redirect('meal_calendar')
    else:
        form = MealPlanForm(instance=meal_plan)
    
    context = {'form': form, 'meal_plan': meal_plan}
    return render(request, 'admin/meal_plan_form.html', context)


@admin_required
def meal_plan_delete(request, plan_id):
    """Delete meal plan"""
    meal_plan = get_object_or_404(MealPlan, id=plan_id)
    meal_plan.delete()
    messages.success(request, 'Meal plan deleted successfully.')
    return redirect('meal_calendar')


@user_required
def user_meal_calendar(request):
    """User view meal calendar"""
    from datetime import datetime
    import calendar
    
    # Get current month/year or from query params
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    # Get all meal plans for this month
    meal_plans = MealPlan.objects.filter(
        date__year=year,
        date__month=month
    )
    
    # Create a dictionary for easy lookup
    meal_dict = {mp.date.day: mp for mp in meal_plans}
    
    # Get calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Calculate prev/next month
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    
    context = {
        'calendar': cal,
        'meal_dict': meal_dict,
        'year': year,
        'month': month,
        'month_name': month_name,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': datetime.now().date(),
    }
    return render(request, 'user/meal_calendar.html', context)




# ==================== Report Generation ====================

@admin_required
def monthly_report(request):
    """Generate monthly PDF report"""
    month_year = request.GET.get('month', datetime.now().strftime('%Y-%m'))
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f'Mess Management Report - {month_year}', title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Payments Summary
    payments = Payment.objects.filter(month_year=month_year)
    total_collected = payments.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_count = payments.filter(status='pending').count()
    
    elements.append(Paragraph('Payment Summary', styles['Heading2']))
    payment_data = [
        ['Total Collected', f'₹{total_collected:.2f}'],
        ['Pending Payments', str(pending_count)],
        ['Total Users', str(payments.count())],
    ]
    payment_table = Table(payment_data, colWidths=[3*inch, 2*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Grocery Expenses
    groceries = Grocery.objects.filter(month_year=month_year)
    total_grocery = groceries.aggregate(Sum('price'))['price__sum'] or 0
    
    elements.append(Paragraph('Grocery Expenses', styles['Heading2']))
    grocery_data = [['Item', 'Category', 'Quantity', 'Price']]
    for item in groceries:
        grocery_data.append([item.item_name, item.category, item.quantity, f'₹{item.price:.2f}'])
    grocery_data.append(['', '', 'Total', f'₹{total_grocery:.2f}'])
    
    grocery_table = Table(grocery_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    grocery_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#ecf0f1')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(grocery_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Fixed Expenses
    try:
        fixed_exp = FixedExpense.objects.get(month_year=month_year)
        elements.append(Paragraph('Fixed Expenses', styles['Heading2']))
        fixed_data = [
            ['Kitchen Rent', f'₹{fixed_exp.kitchen_rent:.2f}'],
            ['Maid Salary', f'₹{fixed_exp.maid_salary:.2f}'],
            ['Gas Cylinder', f'₹{fixed_exp.gas_cylinder:.2f}'],
            ['Other Expenses', f'₹{fixed_exp.other_expenses:.2f}'],
            ['Total Fixed', f'₹{fixed_exp.total_fixed_expense:.2f}'],
        ]
        fixed_table = Table(fixed_data, colWidths=[3*inch, 2*inch])
        fixed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -2), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(fixed_table)
    except FixedExpense.DoesNotExist:
        elements.append(Paragraph('No fixed expenses recorded for this month.', styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="mess_report_{month_year}.pdf"'
    return response


# ==================== User Views ====================

@user_required
def user_dashboard(request):
    """User dashboard"""
    current_month = datetime.now().strftime('%Y-%m')
    
    # Get user's payment for current month
    try:
        payment = Payment.objects.get(user=request.user, month_year=current_month)
    except Payment.DoesNotExist:
        payment = None
    
    # Get total expenses for current month
    total_grocery = Grocery.objects.filter(month_year=current_month).aggregate(Sum('price'))['price__sum'] or 0
    
    try:
        fixed_expense = FixedExpense.objects.get(month_year=current_month)
        total_fixed = fixed_expense.total_fixed_expense
    except FixedExpense.DoesNotExist:
        total_fixed = 0
    
    total_expenses = total_grocery + total_fixed
    
    # Recent messages
    recent_messages = Message.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'payment': payment,
        'total_expenses': total_expenses,
        'current_month': current_month,
        'recent_messages': recent_messages,
    }
    
    return render(request, 'user/dashboard.html', context)


@user_required
def user_payment(request):
    """User payment submission"""
    current_month = datetime.now().strftime('%Y-%m')
    
    # Get or create payment record for current month
    payment, created = Payment.objects.get_or_create(
        user=request.user,
        month_year=current_month,
        defaults={'amount': 0, 'status': 'pending'}
    )
    
    if request.method == 'POST':
        form = UserPaymentForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.status = 'pending'  # Admin will verify
            payment.paid_date = timezone.now()
            payment.save()
            messages.success(request, 'Payment submitted successfully. Waiting for admin verification.')
            return redirect('user_dashboard')
    else:
        form = UserPaymentForm(instance=payment)
    
    # Get UPI details if available
    try:
        mess_settings = MessSettings.objects.first()
    except MessSettings.DoesNotExist:
        mess_settings = None
    
    context = {
        'form': form,
        'payment': payment,
        'mess_settings': mess_settings,
    }
    return render(request, 'user/payment.html', context)


@user_required
def user_send_message(request):
    """Send message to admin"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.save()
            messages.success(request, 'Message sent to admin successfully.')
            return redirect('user_dashboard')
    else:
        form = MessageForm()
    
    # Get user's previous messages
    user_messages = Message.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'form': form,
        'user_messages': user_messages,
    }
    return render(request, 'user/send_message.html', context)


@user_required
def user_messages_list(request):
    """User view all their messages"""
    user_messages = Message.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'user_messages': user_messages,
    }
    return render(request, 'user/messages_list.html', context)


@user_required
def user_message_reply(request, message_id):
    """User reply to admin's response"""
    message = get_object_or_404(Message, id=message_id, user=request.user)
    
    if request.method == 'POST':
        user_reply = request.POST.get('user_reply', '').strip()
        if user_reply:
            message.user_reply = user_reply
            message.user_replied_at = timezone.now()
            message.save()
            messages.success(request, 'Your reply has been sent to admin.')
            return redirect('user_messages_list')
        else:
            messages.error(request, 'Reply cannot be empty.')
    
    context = {
        'message': message,
    }
    return render(request, 'user/message_reply.html', context)


@user_required
def user_receipt(request):
    """Generate personal receipt PDF"""
    month_year = request.GET.get('month', datetime.now().strftime('%Y-%m'))
    
    try:
        payment = Payment.objects.get(user=request.user, month_year=month_year)
    except Payment.DoesNotExist:
        messages.error(request, 'No payment record found for the selected month.')
        return redirect('user_dashboard')
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    elements.append(Paragraph('Payment Receipt', title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # User Details
    user_data = [
        ['Name', request.user.get_full_name()],
        ['Username', request.user.username],
        ['Month', month_year],
    ]
    user_table = Table(user_data, colWidths=[2*inch, 4*inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(user_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Payment Details
    payment_data = [
        ['Amount', f'₹{payment.amount:.2f}'],
        ['Status', payment.get_status_display()],
        ['Transaction ID', payment.transaction_id or 'N/A'],
        ['Payment Date', payment.paid_date.strftime('%d-%m-%Y %H:%M') if payment.paid_date else 'N/A'],
    ]
    payment_table = Table(payment_data, colWidths=[2*inch, 4*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(payment_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{request.user.username}_{month_year}.pdf"'
    return response


@login_required
def transparent_data(request):
    """View all transparent mess data"""
    month_filter = request.GET.get('month', datetime.now().strftime('%Y-%m'))
    
    # Get all data for the month
    groceries = Grocery.objects.filter(month_year=month_filter).order_by('-purchase_date')
    total_grocery = groceries.aggregate(Sum('price'))['price__sum'] or 0
    
    try:
        fixed_expense = FixedExpense.objects.get(month_year=month_filter)
    except FixedExpense.DoesNotExist:
        fixed_expense = None
    
    payments = Payment.objects.filter(month_year=month_filter).select_related('user')
    total_collected = payments.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get distinct months
    months = Grocery.objects.values_list('month_year', flat=True).distinct().order_by('-month_year')
    
    context = {
        'groceries': groceries,
        'total_grocery': total_grocery,
        'fixed_expense': fixed_expense,
        'payments': payments,
        'total_collected': total_collected,
        'selected_month': month_filter,
        'months': months,
    }
    
    return render(request, 'user/transparent_data.html', context)


# ==================== Theme Preference ====================

@login_required
def save_theme_preference(request):
    """Save user's dark mode preference via AJAX"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            dark_mode = data.get('dark_mode', False)
            
            # Update user profile
            profile = request.user.profile
            profile.dark_mode = dark_mode
            profile.save()
            
            return JsonResponse({'success': True, 'message': 'Theme preference saved'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


# ==================== Profile Settings ====================

@login_required
def profile_settings(request):
    """User profile settings and picture upload"""
    from .forms import ProfileSettingsForm
    
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update profile
            profile = form.save()
            
            # Update user fields
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_settings')
    else:
        form = ProfileSettingsForm(instance=profile)
    
    context = {'form': form, 'profile': profile}
    return render(request, 'user/profile_settings.html', context)


# ==================== Excel Export Views ====================

@admin_required
def export_payments_excel(request):
    """Export payments to Excel"""
    from .excel_export import export_payments_to_excel
    
    month_filter = request.GET.get('month', datetime.now().strftime('%Y-%m'))
    payments = Payment.objects.select_related('user').filter(month_year=month_filter).order_by('-created_at')
    
    return export_payments_to_excel(payments, month_filter)


@admin_required
def export_groceries_excel(request):
    """Export groceries to Excel"""
    from .excel_export import export_groceries_to_excel
    
    month_filter = request.GET.get('month', datetime.now().strftime('%Y-%m'))
    groceries = Grocery.objects.filter(month_year=month_filter).order_by('-purchase_date')
    
    return export_groceries_to_excel(groceries, month_filter)


@admin_required
def export_monthly_report_excel(request):
    """Export comprehensive monthly report to Excel"""
    from .excel_export import export_monthly_report_to_excel
    
    month_year = request.GET.get('month', datetime.now().strftime('%Y-%m'))
    
    payments = Payment.objects.filter(month_year=month_year).select_related('user')
    groceries = Grocery.objects.filter(month_year=month_year)
    
    try:
        fixed_expense = FixedExpense.objects.get(month_year=month_year)
    except FixedExpense.DoesNotExist:
        fixed_expense = None
    
    return export_monthly_report_to_excel(month_year, payments, groceries, fixed_expense)


# ==================== Settings Views ====================

@login_required
def user_settings(request):
    """User settings page with all preference forms"""
    from .forms import (UserNotificationSettingsForm, UserPrivacySettingsForm,
                        UserDisplaySettingsForm, UserPaymentSettingsForm)
    
    # Get or create user settings
    user_settings_obj, created = UserSettings.objects.get_or_create(user=request.user)
    
    # Get mess settings for displaying admin UPI details
    mess_settings = MessSettings.get_settings()
    
    if request.method == 'POST':
        section = request.POST.get('section')
        
        if section == 'notifications':
            form = UserNotificationSettingsForm(request.POST, instance=user_settings_obj)
        elif section == 'privacy':
            form = UserPrivacySettingsForm(request.POST, instance=user_settings_obj)
        elif section == 'display':
            form = UserDisplaySettingsForm(request.POST, instance=user_settings_obj)
        elif section == 'payment':
            form = UserPaymentSettingsForm(request.POST, instance=user_settings_obj)
        else:
            messages.error(request, 'Invalid section')
            return redirect('user_settings')
        
        if form.is_valid():
            form.save()
            messages.success(request, f'{section.capitalize()} settings saved successfully!')
            return redirect('user_settings')
        else:
            messages.error(request, 'Please fix the errors below')
    
    context = {
        'user_settings': user_settings_obj,
        'mess_settings': mess_settings,
        'notification_form': UserNotificationSettingsForm(instance=user_settings_obj),
        'privacy_form': UserPrivacySettingsForm(instance=user_settings_obj),
        'display_form': UserDisplaySettingsForm(instance=user_settings_obj),
        'payment_form': UserPaymentSettingsForm(instance=user_settings_obj),
    }
    return render(request, 'user/settings.html', context)


@admin_required
def admin_settings(request):
    """Admin settings page with all configuration forms"""
    from .forms import (MessGeneralSettingsForm, PaymentConfigurationForm,
                        UserManagementSettingsForm, ReminderSettingsForm,
                        ReportSettingsForm, SecuritySettingsForm,
                        DisplaySettingsForm, SystemSettingsForm)
    
    # Get or create mess settings (singleton)
    mess_settings = MessSettings.get_settings()
    
    if request.method == 'POST':
        section = request.POST.get('section')
        
        forms_map = {
            'general': MessGeneralSettingsForm,
            'payment': PaymentConfigurationForm,
            'users': UserManagementSettingsForm,
            'reminders': ReminderSettingsForm,
            'reports': ReportSettingsForm,
            'security': SecuritySettingsForm,
            'display': DisplaySettingsForm,
            'system': SystemSettingsForm,
        }
        
        form_class = forms_map.get(section)
        if form_class:
            form = form_class(request.POST, request.FILES, instance=mess_settings)
            if form.is_valid():
                form.save()
                messages.success(request, f'{section.capitalize()} settings saved successfully!')
                return redirect('admin_settings')
            else:
                messages.error(request, 'Please fix the errors below')
        else:
            messages.error(request, 'Invalid section')
            return redirect('admin_settings')
    
    context = {
        'mess_settings': mess_settings,
        'general_form': MessGeneralSettingsForm(instance=mess_settings),
        'payment_form': PaymentConfigurationForm(instance=mess_settings),
        'users_form': UserManagementSettingsForm(instance=mess_settings),
        'reminders_form': ReminderSettingsForm(instance=mess_settings),
        'reports_form': ReportSettingsForm(instance=mess_settings),
        'security_form': SecuritySettingsForm(instance=mess_settings),
        'display_form': DisplaySettingsForm(instance=mess_settings),
        'system_form': SystemSettingsForm(instance=mess_settings),
    }
    return render(request, 'admin/settings.html', context)


# ==================== Custom Password Reset ====================

def custom_password_reset(request):
    """
    Custom password reset view that sends different emails based on user existence
    - If user exists: Send password reset link
    - If user doesn't exist: Send registration instructions
    """
    from .custom_auth_views import CustomPasswordResetView
    
    view = CustomPasswordResetView.as_view(template_name='registration/password_reset_form.html')
    return view(request)
