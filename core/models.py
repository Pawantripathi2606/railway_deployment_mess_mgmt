from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class UserProfile(models.Model):
    """Extended user model with role and additional information"""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=15, blank=True, null=True)
    room_no = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, help_text="User profile picture")
    dark_mode = models.BooleanField(default=False, help_text="Enable dark mode theme")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class Payment(models.Model):
    """Payment records for users"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    month_year = models.CharField(max_length=7, help_text="Format: YYYY-MM")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    proof_image = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    paid_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.month_year} - {self.status}"
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        unique_together = ('user', 'month_year')
        ordering = ['-month_year', 'user__first_name']


class Grocery(models.Model):
    """Grocery item purchases"""
    CATEGORY_CHOICES = (
        ('vegetables', 'Vegetables'),
        ('grains', 'Grains'),
        ('dairy', 'Dairy'),
        ('spices', 'Spices'),
        ('other', 'Other'),
    )
    
    item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    quantity = models.CharField(max_length=50, help_text="e.g., 5 kg, 2 liters")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    month_year = models.CharField(max_length=7, help_text="Format: YYYY-MM")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.item_name} - {self.month_year}"
    
    class Meta:
        verbose_name = 'Grocery'
        verbose_name_plural = 'Groceries'
        ordering = ['-purchase_date']


class FixedExpense(models.Model):
    """Fixed monthly expenses"""
    month_year = models.CharField(max_length=7, unique=True, help_text="Format: YYYY-MM")
    kitchen_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maid_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gas_cylinder = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    @property
    def total_fixed_expense(self):
        return self.kitchen_rent + self.maid_salary + self.gas_cylinder + self.other_expenses
    
    def __str__(self):
        return f"Fixed Expenses - {self.month_year}"
    
    class Meta:
        verbose_name = 'Fixed Expense'
        verbose_name_plural = 'Fixed Expenses'
        ordering = ['-month_year']


class Message(models.Model):
    """Messages from users to admin"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    )
    
    MESSAGE_TYPE_CHOICES = (
        ('user', 'User Message'),
        ('system', 'System/Reminder'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='user', help_text="Type of message")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    admin_reply = models.TextField(blank=True, null=True, help_text="Admin's response to this message")
    replied_at = models.DateTimeField(blank=True, null=True)
    user_reply = models.TextField(blank=True, null=True, help_text="User's response to admin reply")
    user_replied_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.subject}"
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-created_at']



class MealPlan(models.Model):
    """Daily meal plan"""
    date = models.DateField(unique=True, help_text="Date for this meal plan")
    breakfast = models.TextField(blank=True, null=True, help_text="Breakfast menu")
    lunch = models.TextField(blank=True, null=True, help_text="Lunch menu")
    dinner = models.TextField(blank=True, null=True, help_text="Dinner menu")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Meal Plan - {self.date}"
    
    class Meta:
        verbose_name = 'Meal Plan'
        verbose_name_plural = 'Meal Plans'
        ordering = ['-date']


class ActivityLog(models.Model):
    """Track user activities for activity feed"""
    ACTION_TYPE_CHOICES = (
        ('login', 'Login'),
        ('payment', 'Payment'),
        ('message', 'Message'),
        ('profile', 'Profile Update'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES, default='other')
    description = models.TextField(help_text="Description of the activity")
    timestamp = models.DateTimeField(auto_now_add=True)
    related_object_id = models.IntegerField(null=True, blank=True, help_text="ID of related object (payment, message, etc.)")
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.action_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']


class UserSettings(models.Model):
    """User-specific settings and preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    
    # Notification Preferences
    email_payment_reminders = models.BooleanField(default=True, help_text="Receive payment reminder emails")
    email_grocery_updates = models.BooleanField(default=True, help_text="Receive grocery update emails")
    email_monthly_reports = models.BooleanField(default=True, help_text="Receive monthly report emails")
    email_admin_messages = models.BooleanField(default=True, help_text="Receive admin message notifications")
    
    # Privacy Settings
    show_phone_to_members = models.BooleanField(default=True, help_text="Show phone number to other members")
    show_payment_status = models.BooleanField(default=True, help_text="Show payment status to other members")
    
    # Display Preferences
    dashboard_default_view = models.CharField(
        max_length=20, 
        choices=[('current', 'Current Month'), ('all', 'All Time')], 
        default='current',
        help_text="Default dashboard time range"
    )
    payment_history_months = models.IntegerField(default=6, help_text="Number of months to show in payment history")
    
    # Payment Preferences
    preferred_upi_app = models.CharField(max_length=20, blank=True, help_text="Preferred UPI app (GPay, PhonePe, Paytm)")
    saved_upi_ids = models.JSONField(default=list, blank=True, help_text="List of saved UPI IDs")
    payment_reminder_days = models.IntegerField(default=3, help_text="Days before due date to receive reminder")
    auto_download_receipt = models.BooleanField(default=True, help_text="Auto-download receipt on payment")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.user.get_full_name()}"
    
    class Meta:
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'


class MessSettings(models.Model):
    """System-wide mess configuration settings (Singleton)"""
    
    # General Information
    mess_name = models.CharField(max_length=200, default="Mess Management System")
    address = models.TextField(blank=True, help_text="Mess address")
    contact_email = models.EmailField(blank=True, help_text="Contact email for inquiries")
    contact_phone = models.CharField(max_length=15, blank=True, help_text="Contact phone number")
    operating_hours = models.CharField(max_length=100, blank=True, help_text="Operating hours (e.g., 7 AM - 10 PM)")
    
    # Payment Configuration
    default_monthly_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Default monthly fee amount"
    )
    billing_day = models.IntegerField(
        default=1, 
        help_text="Day of month for billing (1-31)"
    )
    late_payment_penalty = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Late payment penalty (₹ or %)"
    )
    late_payment_penalty_type = models.CharField(
        max_length=10,
        choices=[('fixed', 'Fixed Amount'), ('percent', 'Percentage')],
        default='fixed'
    )
    allow_partial_payments = models.BooleanField(default=False, help_text="Allow users to make partial payments")
    grace_period_days = models.IntegerField(default=3, help_text="Grace period after due date")
    
    # UPI Configuration
    admin_upi_id = models.CharField(max_length=100, blank=True, help_text="Admin UPI ID for payments")
    upi_qr_code = models.ImageField(upload_to='upi_qr/', blank=True, null=True, help_text="UPI QR code image")
    
    # User Management
    allow_self_registration = models.BooleanField(default=False, help_text="Allow users to register themselves")
    require_admin_approval = models.BooleanField(default=True, help_text="Require admin approval for new users")
    max_users_allowed = models.IntegerField(default=50, help_text="Maximum number of users allowed")
    inactive_user_cleanup_days = models.IntegerField(default=90, help_text="Days before inactive users are flagged")
    
    # Payment Reminder Configuration
    first_reminder_days = models.IntegerField(default=7, help_text="Days before due date for first reminder")
    second_reminder_days = models.IntegerField(default=3, help_text="Days before due date for second reminder")
    final_reminder_days = models.IntegerField(default=1, help_text="Days before due date for final reminder")
    send_overdue_reminders = models.BooleanField(default=True, help_text="Send reminders for overdue payments")
    
    # Report Configuration
    auto_generate_monthly_report = models.BooleanField(default=True, help_text="Auto-generate monthly reports")
    report_generation_day = models.IntegerField(default=1, help_text="Day of month to generate reports")
    auto_email_reports = models.BooleanField(default=True, help_text="Auto-email reports to all users")
    include_payment_details = models.BooleanField(default=True, help_text="Include payment details in reports")
    include_grocery_details = models.BooleanField(default=True, help_text="Include grocery details in reports")
    
    # Security Settings
    require_strong_passwords = models.BooleanField(default=True, help_text="Require strong passwords")
    min_password_length = models.IntegerField(default=8, help_text="Minimum password length")
    session_timeout_minutes = models.IntegerField(default=60, help_text="Session timeout in minutes")
    max_login_attempts = models.IntegerField(default=5, help_text="Maximum login attempts before lockout")
    lockout_duration_minutes = models.IntegerField(default=30, help_text="Account lockout duration")
    
    # Display & UI Settings
    default_theme = models.CharField(
        max_length=10, 
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='auto',
        help_text="Default theme for new users"
    )
    currency_symbol = models.CharField(max_length=5, default='₹', help_text="Currency symbol")
    date_format = models.CharField(
        max_length=20, 
        choices=[
            ('DD/MM/YYYY', 'DD/MM/YYYY'),
            ('MM/DD/YYYY', 'MM/DD/YYYY'),
            ('YYYY-MM-DD', 'YYYY-MM-DD')
        ],
        default='DD/MM/YYYY',
        help_text="Date display format"
    )
    time_zone = models.CharField(max_length=50, default='Asia/Kolkata', help_text="System timezone")
    
    # System Configuration
    data_retention_months = models.IntegerField(default=24, help_text="Months to retain old data")
    auto_backup_enabled = models.BooleanField(default=True, help_text="Enable automatic backups")
    backup_frequency_days = models.IntegerField(default=7, help_text="Backup frequency in days")
    enable_activity_logging = models.BooleanField(default=True, help_text="Enable activity logging")
    log_retention_days = models.IntegerField(default=90, help_text="Days to retain activity logs")
    
    # Email Configuration
    email_signature = models.TextField(blank=True, help_text="Email signature for automated emails")
    smtp_configured = models.BooleanField(default=False, help_text="SMTP email is configured")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Mess Settings'
        verbose_name_plural = 'Mess Settings'
    
    def save(self, *args, **kwargs):
        # Singleton pattern - only one instance allowed
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion
        pass
    
    @classmethod
    def get_settings(cls):
        """Get or create the single settings instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return f"Mess Settings: {self.mess_name}"
