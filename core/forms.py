from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Payment, Grocery, FixedExpense, Message, UserSettings, MessSettings


class UserRegistrationForm(UserCreationForm):
    """Form for creating new users by admin"""
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    room_no = forms.CharField(max_length=20, required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, initial='user')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        # Store profile data as temporary attributes for the signal handler
        user._profile_role = self.cleaned_data['role']
        user._profile_phone = self.cleaned_data['phone']
        user._profile_room_no = self.cleaned_data['room_no']
        
        if commit:
            user.save()
            # Signal handler will create the UserProfile automatically
        return user


class UserEditForm(forms.ModelForm):
    """Form for editing existing users"""
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    room_no = forms.CharField(max_length=20, required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            profile = self.instance.userprofile
            self.fields['phone'].initial = profile.phone
            self.fields['room_no'].initial = profile.room_no
            self.fields['role'].initial = profile.role


class PaymentForm(forms.ModelForm):
    """Form for payment management"""
    class Meta:
        model = Payment
        fields = ['user', 'month_year', 'amount', 'status', 'transaction_id', 'proof_image']
        widgets = {
            'month_year': forms.TextInput(attrs={'type': 'month'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }


class UserPaymentForm(forms.ModelForm):
    """Form for user payment submission"""
    class Meta:
        model = Payment
        fields = ['transaction_id', 'proof_image']
        widgets = {
            'transaction_id': forms.TextInput(attrs={'placeholder': 'Enter UPI/Bank transaction ID'}),
        }


class GroceryForm(forms.ModelForm):
    """Form for grocery management"""
    class Meta:
        model = Grocery
        fields = ['item_name', 'category', 'quantity', 'price', 'purchase_date', 'month_year']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'month_year': forms.TextInput(attrs={'type': 'month'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }


class FixedExpenseForm(forms.ModelForm):
    """Form for fixed expense management"""
    class Meta:
        model = FixedExpense
        fields = ['month_year', 'kitchen_rent', 'maid_salary', 'gas_cylinder', 'other_expenses']
        widgets = {
            'month_year': forms.TextInput(attrs={'type': 'month'}),
            'kitchen_rent': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'maid_salary': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'gas_cylinder': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'other_expenses': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }


class MessageForm(forms.ModelForm):
    """Form for users to send messages"""
    class Meta:
        model = Message
        fields = ('subject', 'message')
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Enter subject'}),
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter your message'}),
        }


class AdminReplyForm(forms.ModelForm):
    """Form for admin reply to user messages"""
    class Meta:
        model = Message
        fields = ['admin_reply']
        widgets = {
            'admin_reply': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Type your reply here...'}),
        }
        labels = {
            'admin_reply': 'Reply to User'
        }


class ProfileSettingsForm(forms.ModelForm):
    """Form for user profile settings"""
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'room_no', 'profile_picture']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': 'Phone number'}),
            'room_no': forms.TextInput(attrs={'placeholder': 'Room number'}),
        }
        labels = {
            'profile_picture': 'Profile Picture (Optional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email


# ============ USER SETTINGS FORMS ============

class UserNotificationSettingsForm(forms.ModelForm):
    """Form for user notification preferences"""
    class Meta:
        model = UserSettings
        fields = ['email_payment_reminders', 'email_grocery_updates', 
                  'email_monthly_reports', 'email_admin_messages']
        widgets = {
            'email_payment_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_grocery_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_monthly_reports': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_admin_messages': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserPrivacySettingsForm(forms.ModelForm):
    """Form for user privacy settings"""
    class Meta:
        model = UserSettings
        fields = ['show_phone_to_members', 'show_payment_status']
        widgets = {
            'show_phone_to_members': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_payment_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserDisplaySettingsForm(forms.ModelForm):
    """Form for user display preferences"""
    class Meta:
        model = UserSettings
        fields = ['dashboard_default_view', 'payment_history_months']
        widgets = {
            'dashboard_default_view': forms.Select(attrs={'class': 'form-control'}),
            'payment_history_months': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '24'}),
        }


class UserPaymentSettingsForm(forms.ModelForm):
    """Form for user payment preferences"""
    class Meta:
        model = UserSettings
        fields = ['preferred_upi_app', 'payment_reminder_days', 'auto_download_receipt']
        widgets = {
            'preferred_upi_app': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., GPay, PhonePe, Paytm'}),
            'payment_reminder_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '30'}),
            'auto_download_receipt': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ============ ADMIN SETTINGS FORMS ============

class MessGeneralSettingsForm(forms.ModelForm):
    """Form for mess general information"""
    class Meta:
        model = MessSettings
        fields = ['mess_name', 'address', 'contact_email', 'contact_phone', 'operating_hours']
        widgets = {
            'mess_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'operating_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 7 AM - 10 PM'}),
        }


class PaymentConfigurationForm(forms.ModelForm):
    """Form for payment configuration"""
    class Meta:
        model = MessSettings
        fields = ['default_monthly_fee', 'billing_day', 'late_payment_penalty', 
                  'late_payment_penalty_type', 'allow_partial_payments', 'grace_period_days',
                  'admin_upi_id', 'upi_qr_code']
        widgets = {
            'default_monthly_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'billing_day': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '31'}),
            'late_payment_penalty': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'late_payment_penalty_type': forms.Select(attrs={'class': 'form-control'}),
            'allow_partial_payments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'grace_period_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'admin_upi_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'yourname@upi'}),
        }


class UserManagementSettingsForm(forms.ModelForm):
    """Form for user management settings"""
    class Meta:
        model = MessSettings
        fields = ['allow_self_registration', 'require_admin_approval', 
                  'max_users_allowed', 'inactive_user_cleanup_days']
        widgets = {
            'allow_self_registration': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'require_admin_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_users_allowed': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'inactive_user_cleanup_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class ReminderSettingsForm(forms.ModelForm):
    """Form for payment reminder settings"""
    class Meta:
        model = MessSettings
        fields = ['first_reminder_days', 'second_reminder_days', 
                  'final_reminder_days', 'send_overdue_reminders']
        widgets = {
            'first_reminder_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'second_reminder_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'final_reminder_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'send_overdue_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ReportSettingsForm(forms.ModelForm):
    """Form for report configuration"""
    class Meta:
        model = MessSettings
        fields = ['auto_generate_monthly_report', 'report_generation_day', 
                  'auto_email_reports', 'include_payment_details', 'include_grocery_details']
        widgets = {
            'auto_generate_monthly_report': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'report_generation_day': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '31'}),
            'auto_email_reports': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_payment_details': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_grocery_details': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SecuritySettingsForm(forms.ModelForm):
    """Form for security settings"""
    class Meta:
        model = MessSettings
        fields = ['require_strong_passwords', 'min_password_length', 'session_timeout_minutes',
                  'max_login_attempts', 'lockout_duration_minutes']
        widgets = {
            'require_strong_passwords': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'min_password_length': forms.NumberInput(attrs={'class': 'form-control', 'min': '4', 'max': '20'}),
            'session_timeout_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '5'}),
            'max_login_attempts': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'lockout_duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class DisplaySettingsForm(forms.ModelForm):
    """Form for display and UI settings"""
    class Meta:
        model = MessSettings
        fields = ['default_theme', 'currency_symbol', 'date_format', 'time_zone']
        widgets = {
            'default_theme': forms.Select(attrs={'class': 'form-control'}),
            'currency_symbol': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '5'}),
            'date_format': forms.Select(attrs={'class': 'form-control'}),
            'time_zone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SystemSettingsForm(forms.ModelForm):
    """Form for system configuration"""
    class Meta:
        model = MessSettings
        fields = ['data_retention_months', 'auto_backup_enabled', 'backup_frequency_days',
                  'enable_activity_logging', 'log_retention_days']
        widgets = {
            'data_retention_months': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'auto_backup_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'backup_frequency_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'enable_activity_logging': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'log_retention_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
