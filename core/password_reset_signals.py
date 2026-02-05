"""
Custom signal handlers for password reset to send confirmation emails
"""
from django.dispatch import receiver
from allauth.account.signals import password_reset
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from core.email_templates import get_password_reset_success_email_html


@receiver(password_reset)
def send_password_reset_confirmation(sender, request, user, **kwargs):
    """
    Send confirmation email after successful password reset
    """
    try:
        subject = '✅ Password Reset Successful - Mess Management'
        text_content = f'''
Hi {user.first_name or user.username},

Your password has been successfully reset.

You can now login to your account using your new password.

If you did not perform this password reset, please contact us immediately.

Login here: http://127.0.0.1:8000/accounts/login/

For assistance, contact: pawantripathi802@gmail.com

Best regards,
Mess Management Team
        '''
        
        html_content = get_password_reset_success_email_html(
            user_name=user.first_name or user.username
        )
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        
        print(f"✅ Password reset confirmation email sent to {user.email}")
        
    except Exception as e:
        # Log the error but don't fail the password reset
        print(f"Failed to send password reset confirmation email: {e}")
