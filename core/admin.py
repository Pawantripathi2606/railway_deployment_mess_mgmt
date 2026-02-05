from django.contrib import admin
from .models import UserProfile, Payment, Grocery, FixedExpense, Message, MealPlan, ActivityLog, UserSettings, MessSettings


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'room_no', 'dark_mode', 'is_active')
    list_filter = ('role', 'is_active', 'dark_mode')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone', 'room_no')
    ordering = ('-created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'month_year', 'amount', 'status', 'paid_date', 'transaction_id')
    list_filter = ('status', 'month_year', 'paid_date')
    search_fields = ('user__username', 'user__first_name', 'transaction_id')
    ordering = ('-created_at',)


@admin.register(Grocery)
class GroceryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'category', 'quantity', 'price', 'purchase_date', 'month_year')
    list_filter = ('category', 'month_year', 'purchase_date')
    search_fields = ('item_name',)
    ordering = ('-created_at',)


@admin.register(FixedExpense)
class FixedExpenseAdmin(admin.ModelAdmin):
    list_display = ('month_year', 'kitchen_rent', 'maid_salary', 'gas_cylinder', 'other_expenses', 'total_fixed_expense')
    list_filter = ('month_year',)
    ordering = ('-month_year',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'status', 'created_at', 'resolved_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'subject', 'message')
    ordering = ('-created_at',)


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_payment_reminders', 'dashboard_default_view', 'payment_reminder_days', 'updated_at')
    list_filter = ('email_payment_reminders', 'dashboard_default_view')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Preferences', {
            'fields': ('email_payment_reminders', 'email_grocery_updates', 'email_monthly_reports', 'email_admin_messages')
        }),
        ('Privacy Settings', {
            'fields': ('show_phone_to_members', 'show_payment_status')
        }),
        ('Display Preferences', {
            'fields': ('dashboard_default_view', 'payment_history_months')
        }),
        ('Payment Preferences', {
            'fields': ('preferred_upi_app', 'payment_reminder_days', 'auto_download_receipt')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(MessSettings)
class MessSettingsAdmin(admin.ModelAdmin):
    list_display = ('mess_name', 'default_monthly_fee', 'billing_day', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('General Information', {
            'fields': ('mess_name', 'address', 'contact_email', 'contact_phone', 'operating_hours')
        }),
        ('Payment Configuration', {
            'fields': ('default_monthly_fee', 'billing_day', 'late_payment_penalty', 'late_payment_penalty_type',
                      'allow_partial_payments', 'grace_period_days')
        }),
        ('UPI Configuration', {
            'fields': ('admin_upi_id', 'upi_qr_code')
        }),
        ('User Management', {
            'fields': ('allow_self_registration', 'require_admin_approval', 'max_users_allowed', 'inactive_user_cleanup_days')
        }),
        ('Payment Reminders', {
            'fields': ('first_reminder_days', 'second_reminder_days', 'final_reminder_days', 'send_overdue_reminders')
        }),
        ('Reports', {
            'fields': ('auto_generate_monthly_report', 'report_generation_day', 'auto_email_reports',
                      'include_payment_details', 'include_grocery_details')
        }),
        ('Security', {
            'fields': ('require_strong_passwords', 'min_password_length', 'session_timeout_minutes',
                      'max_login_attempts', 'lockout_duration_minutes')
        }),
        ('Display & UI', {
            'fields': ('default_theme', 'currency_symbol', 'date_format', 'time_zone')
        }),
        ('System Configuration', {
            'fields': ('data_retention_months', 'auto_backup_enabled', 'backup_frequency_days',
                      'enable_activity_logging', 'log_retention_days')
        }),
        ('Email', {
            'fields': ('email_signature', 'smtp_configured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Only one instance allowed (singleton)
        return not MessSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Cannot delete settings
        return False


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('date', 'breakfast', 'lunch', 'dinner')
    list_filter = ('date',)
    search_fields = ('breakfast', 'lunch', 'dinner', 'notes')
    ordering = ('-date',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'description', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('user__username', 'user__first_name', 'description')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
