from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from functools import wraps


def admin_required(function=None):
    """
    Decorator for views that checks user is admin
    """
    def check_admin(user):
        return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'
    
    actual_decorator = user_passes_test(check_admin, login_url='login')
    
    if function:
        return actual_decorator(function)
    return actual_decorator


def user_required(function=None):
    """
    Decorator for views that checks user is a regular user
    """
    def check_user(user):
        return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'user'
    
    actual_decorator = user_passes_test(check_user, login_url='login')
    
    if function:
        return actual_decorator(function)
    return actual_decorator


def role_required(*roles):
    """
    Decorator that checks if user has one of the specified roles
    Usage: @role_required('admin', 'user')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not hasattr(request.user, 'profile'):
                return redirect('login')
            
            if request.user.profile.role not in roles:
                return redirect('login')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
