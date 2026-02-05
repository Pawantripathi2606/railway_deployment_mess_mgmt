"""
Activity logging helper functions for the mess management system
"""
from django.contrib.auth.models import User
from .models import ActivityLog


def log_activity(user, action_type, description, related_id=None):
    """
    Log a user activity to the database
    
    Args:
        user: User object
        action_type: Type of action ('login', 'payment', 'message', 'profile', 'other')
        description: Human-readable description of the activity
        related_id: Optional ID of related object (payment ID, message ID, etc.)
    
    Returns:
        ActivityLog object
    """
    activity = ActivityLog.objects.create(
        user=user,
        action_type=action_type,
        description=description,
        related_object_id=related_id
    )
    return activity


def get_recent_activities(user, limit=10):
    """
    Get recent activities for a user
    
    Args:
        user: User object
        limit: Number of activities to retrieve (default: 10)
    
    Returns:
        QuerySet of ActivityLog objects
    """
    return ActivityLog.objects.filter(user=user).order_by('-timestamp')[:limit]


def get_all_recent_activities(limit=20):
    """
    Get recent activities across all users (for admin view)
    
    Args:
        limit: Number of activities to retrieve (default: 20)
    
    Returns:
        QuerySet of ActivityLog objects
    """
    return ActivityLog.objects.all().order_by('-timestamp')[:limit]
