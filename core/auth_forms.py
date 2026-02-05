"""
Custom form to show helpful error messages for role-based login
"""
from allauth.account.forms import LoginForm as AllauthLoginForm
from django.contrib import messages
from django.contrib.auth.models import User


class UserLoginForm(AllauthLoginForm):
    """
    Custom login form that provides helpful messages for admin users
    """
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check if user exists and is admin
        login_value = cleaned_data.get('login', '')
        
        if login_value:
            try:
                # Try to find user by username or email
                user = User.objects.filter(username=login_value).first()
                if not user:
                    user = User.objects.filter(email=login_value).first()
                
                if user and hasattr(user, 'profile') and user.profile.role == 'admin':
                    # Add a helpful error message
                    self.add_error(None, 
                        '⚠️ Admin Access Detected! You are trying to login as an administrator. '
                        'Please use the Admin Login Portal at /manage/login/ instead.'
                    )
            except (User.DoesNotExist, AttributeError):
                pass
        
        return cleaned_data
