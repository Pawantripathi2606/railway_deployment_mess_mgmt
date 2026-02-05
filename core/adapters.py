"""
Custom Allauth adapter to enforce role-based login
Prevents admin users from logging in through the user login page
"""
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class RoleBasedAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to enforce role-based login separation:
    - Admin users can only login from /manage/login/
    - Regular users can only login from /accounts/login/ (allauth)
    """
    
    def login(self, request, user):
        """
        Override login to check user role before allowing access
        """
        # Check if user has a profile
        if hasattr(user, 'profile'):
            # If user is admin, reject login from allauth (user side)
            if user.profile.role == 'admin':
                messages.warning(
                    request,
                    '⚠️ Admin Access Detected! You are trying to login as an administrator. '
                    'Please use the Admin Login Portal instead. '
                    '<a href="/manage/login/" class="alert-link">Click here to go to Admin Login</a>',
                    extra_tags='safe'
                )
                # Don't proceed with login
                return redirect('admin_login')
        
        # For regular users, proceed with normal login
        return super().login(request, user)
    
    def authentication_failed(self, request, **credentials):
        """
        Called when authentication fails
        """
        # Get the username that was attempted
        username = credentials.get('username', '')
        
        # Check if this username belongs to an admin
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=username)
            if hasattr(user, 'profile') and user.profile.role == 'admin':
                messages.error(
                    request,
                    'Admin users must login from the admin portal at /manage/login/'
                )
                return
        except User.DoesNotExist:
            pass
        
        # Default behavior for failed authentication
        super().authentication_failed(request, **credentials)
