"""
Custom authentication backend to enforce role-based login
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class RoleBasedAuthBackend(ModelBackend):
    """
    Custom authentication backend that checks user roles
    This runs during authentication, before login
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user and check role-based access
        Only applies role checking during LOGIN, not signup
        """
        # First, use default authentication
        user = super().authenticate(request, username=username, password=password, **kwargs)
        
        if user is None:
            return None
        
        # ONLY apply role checking during LOGIN pages, NOT signup
        # Check if this is a login request (not signup)
        if request and request.path in ['/accounts/login/', '/manage/login/']:
            # User login page - reject admin users
            if request.path == '/accounts/login/':
                if hasattr(user, 'profile') and user.profile.role == 'admin':
                    # Return None to indicate authentication failure
                    return None
            
            # Admin login page - reject regular users  
            if request.path == '/manage/login/':
                if hasattr(user, 'profile') and user.profile.role != 'admin':
                    # Return None to indicate authentication failure
                    return None
        
        # For signup and other authentication requests, allow through
        # Authentication successful
        return user
