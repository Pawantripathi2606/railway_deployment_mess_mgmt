"""
Signal handlers for the core app
Automatically creates UserProfile when new users are created
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create UserProfile automatically when a new User is created
    This handles both regular signup and admin-created users
    """
    if created:
        # Check if profile already exists (using database query for reliability)
        if not UserProfile.objects.filter(user=instance).exists():
            # Check for temporary profile data from forms
            role = getattr(instance, '_profile_role', 'user')
            phone = getattr(instance, '_profile_phone', '')
            room_no = getattr(instance, '_profile_room_no', '')
            
            UserProfile.objects.create(
                user=instance,
                role=role,
                phone=phone,
                room_no=room_no,
                dark_mode=False
            )


@receiver(user_signed_up)
def create_profile_for_social_user(sender, request, user, **kwargs):
    """
    Ensure UserProfile is created for social authentication users
    This is a fallback for allauth social signups
    """
    # Check if profile exists (using database query for reliability)
    if not UserProfile.objects.filter(user=user).exists():
        UserProfile.objects.create(
            user=user,
            role='user',  # Default role for social auth users
            dark_mode=False
        )
        
    # Set first name and last name from social account if available
    sociallogin = kwargs.get('sociallogin')
    if sociallogin:
        # Get extra data from social account
        extra_data = sociallogin.account.extra_data
        
        # Update user's name from Google data
        if not user.first_name and 'given_name' in extra_data:
            user.first_name = extra_data.get('given_name', '')
        
        if not user.last_name and 'family_name' in extra_data:
            user.last_name = extra_data.get('family_name', '')
        
        if user.first_name or user.last_name:
            user.save()
    
    # Send welcome email for Google OAuth signups
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings
    from core.email_templates import get_welcome_email_html
    
    try:
        subject = '🎉 Welcome to Mess Management System!'
        text_content = f'''
Dear {user.first_name or user.username},

Congratulations! Your account has been successfully created using Google Sign-In.

Your Account Details:
- Name: {user.get_full_name() or user.username}
- Email: {user.email}

Login here: http://127.0.0.1:8000/accounts/login/

For assistance, contact: pawantripathi802@gmail.com

Best regards,
Mess Management Team
        '''
        
        html_content = get_welcome_email_html(
            user_name=user.first_name or user.username,
            email=user.email,
            username=user.username or user.email.split('@')[0]
        )
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        
    except Exception as e:
        # Log the error but don't fail signup
        print(f"Failed to send welcome email for social signup: {e}")
