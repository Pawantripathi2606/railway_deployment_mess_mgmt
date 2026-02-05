"""
Custom Allauth adapter to send welcome emails and show success messages
"""
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to handle signup success messages and welcome emails
    """
    
    def save_user(self, request, user, form, commit=True):
        """
        Save user and send welcome email
        """
        user = super().save_user(request, user, form, commit=False)
        
        if commit:
            user.save()
            
            # Send beautiful HTML welcome email
            from django.core.mail import EmailMultiAlternatives
            from core.email_templates import get_welcome_email_html
            
            try:
                subject = '🎉 Welcome to Mess Management System!'
                text_content = f'''
Dear {user.first_name or user.username},

Congratulations! Your account has been successfully created.

Your Account Details:
- Username: {user.username}
- Email: {user.email}

Login here: http://127.0.0.1:8000/accounts/login/

For assistance, contact: pawantripathi802@gmail.com

Best regards,
Mess Management Team
                '''
                
                html_content = get_welcome_email_html(
                    user_name=user.first_name or user.username,
                    email=user.email,
                    username=user.username
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
                print(f"Failed to send welcome email: {e}")
        
        return user
    
    def respond_user_inactive(self, request, user):
        """
        Custom response for inactive users
        """
        messages.error(
            request,
            'Your account is inactive. Please contact the administrator.'
        )
        return super().respond_user_inactive(request, user)
    
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        """
        Override to add custom HTML message for signup success
        """
        # Let allauth add its normal messages
        super().add_message(request, level, message_template, message_context, extra_tags)
