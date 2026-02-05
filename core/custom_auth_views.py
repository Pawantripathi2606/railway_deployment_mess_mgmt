from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string


class CustomPasswordResetView(PasswordResetView):
    """
    Custom password reset view that sends different emails based on user existence
    - If user exists: Send password reset link (as HTML email)
    - If user doesn't exist: Send registration instructions
    """
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        
        # Check if user with this email exists
        user_exists = User.objects.filter(email=email).exists()
        
        if user_exists:
            # User exists - send normal password reset email
            return super().form_valid(form)
        else:
            # User doesn't exist - send registration instructions email
            self.send_registration_email(email)
            # Still redirect to done page (don't reveal user doesn't exist in the UI)
            return redirect('password_reset_done')
    
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Override send_mail to send HTML emails properly.
        This ensures the password reset email is rendered as HTML in email clients.
        CRITICAL FIX: Always use EmailMultiAlternatives to prevent raw HTML display.
        """
        subject = render_to_string(subject_template_name, context)
        # Remove newlines from subject
        subject = ''.join(subject.splitlines())
        
        # Render the HTML email template
        html_email = render_to_string(email_template_name, context)
        
        # Create plain text version (strip HTML tags)
        from django.utils.html import strip_tags
        text_email = strip_tags(html_email)
        
        # CRITICAL: Create email with both HTML and plain text versions
        # This ensures email clients display HTML, not raw code
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_email,  # Plain text fallback
            from_email=from_email,
            to=[to_email]
        )
        # Attach HTML as alternative with proper MIME type
        email_message.attach_alternative(html_email, "text/html")
        
        # Send the email
        email_message.send(fail_silently=False)
    
    def send_registration_email(self, email):
        """Send beautifully designed email to unregistered users with registration instructions"""
        subject = '🔒 Account Not Found - Mess Manager'
        
        # Plain text version
        message = f"""
Hello,

We received a password reset request for this email address ({email}).

However, we couldn't find an account associated with this email in our Mess Management System.

📝 To use our system, please:

1. Contact the mess admin to register your account
2. Or ask the admin to add your email to the system
3. Once registered, you can use the password reset feature

If you believe this is an error or need assistance, please contact the mess administrator.

Best regards,
Mess Manager Team
        """
        
        # Beautiful HTML version with modern design
        html_message = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Not Found - Mess Manager</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
    
    <!-- Main Container -->
    <table width="100%" cellpadding="0" cellspacing="0" style="padding: 40px 20px;">
        <tr>
            <td align="center">
                
                <!-- Email Card -->
                <table width="600" cellpadding="0" cellspacing="0" style="background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; max-width: 100%;">
                    
                    <!-- Header with Icon -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 50px 40px; text-align: center;">
                            <!-- Icon Circle -->
                            <div style="background: rgba(255,255,255,0.2); width: 120px; height: 120px; border-radius: 60px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px); border: 3px solid rgba(255,255,255,0.3);">
                                <div style="font-size: 60px; line-height: 1;">🔒</div>
                            </div>
                            <h1 style="margin: 0; color: white; font-size: 32px; font-weight: 700; text-shadow: 0 2px 10px rgba(0,0,0,0.2);">Account Not Found</h1>
                            <p style="margin: 10px 0 0; color: rgba(255,255,255,0.95); font-size: 16px;">Mess Management System</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            
                            <!-- Alert Box -->
                            <div style="background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%); border-left: 5px solid #f56565; border-radius: 10px; padding: 20px; margin-bottom: 30px;">
                                <p style="margin: 0; color: #742a2a; font-size: 16px; line-height: 1.6;">
                                    <strong style="font-size: 18px;">⚠️ Email Not Registered</strong><br><br>
                                    We received a password reset request for:<br>
                                    <strong style="background: white; padding: 5px 10px; border-radius: 5px; display: inline-block; margin-top: 5px;">{email}</strong>
                                </p>
                                <p style="margin: 15px 0 0; color: #742a2a; font-size: 14px;">
                                    However, this email is not registered in our system.
                                </p>
                            </div>
                            
                            <!-- Steps Card -->
                            <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e1effe 100%); border-radius: 15px; padding: 30px; margin-bottom: 25px; border: 2px solid #90cdf4;">
                                <h2 style="margin: 0 0 20px; color: #2c5282; font-size: 22px; display: flex; align-items: center;">
                                    <span style="font-size: 28px; margin-right: 10px;">📝</span>
                                    How to Get Access
                                </h2>
                                
                                <!-- Step 1 -->
                                <div style="background: white; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                                    <div style="display: flex; align-items: start;">
                                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px; flex-shrink: 0;">1</div>
                                        <div>
                                            <strong style="color: #2d3748; font-size: 16px; display: block; margin-bottom: 5px;">Contact Mess Admin</strong>
                                            <p style="margin: 0; color: #718096; font-size: 14px; line-height: 1.5;">Ask the admin to create an account for you in the system</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Step 2 -->
                                <div style="background: white; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                                    <div style="display: flex; align-items: start;">
                                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px; flex-shrink: 0;">2</div>
                                        <div>
                                            <strong style="color: #2d3748; font-size: 16px; display: block; margin-bottom: 5px;">Provide Your Details</strong>
                                            <p style="margin: 0; color: #718096; font-size: 14px; line-height: 1.5;">Share your name and this email address ({email})</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Step 3 -->
                                <div style="background: white; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                                    <div style="display: flex; align-items: start;">
                                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px; flex-shrink: 0;">3</div>
                                        <div>
                                            <strong style="color: #2d3748; font-size: 16px; display: block; margin-bottom: 5px;">Wait for Registration</strong>
                                            <p style="margin: 0; color: #718096; font-size: 14px; line-height: 1.5;">Admin will add you to the system within 24-48 hours</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Step 4 -->
                                <div style="background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                                    <div style="display: flex; align-items: start;">
                                        <div style="background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px; flex-shrink: 0;">✓</div>
                                        <div>
                                            <strong style="color: #2d3748; font-size: 16px; display: block; margin-bottom: 5px;">Login & Use System</strong>
                                            <p style="margin: 0; color: #718096; font-size: 14px; line-height: 1.5;">Once registered, you'll receive your login credentials via email</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Info Box -->
                            <div style="background: linear-gradient(135deg, #fef5e7 0%, #fce38a 100%); border-left: 5px solid #f6ad55; border-radius: 10px; padding: 20px; margin-bottom: 25px;">
                                <p style="margin: 0; color: #744210; font-size: 15px; line-height: 1.6;">
                                    <strong style="font-size: 18px;">💡 Already Registered?</strong><br><br>
                                    If you believe you're already registered, you might have used a different email address. Please check which email you used during registration or contact the admin for verification.
                                </p>
                            </div>
                            
                            <!-- Help Section -->
                            <div style="background: #f7fafc; border-radius: 10px; padding: 20px; text-align: center;">
                                <p style="margin: 0 0 15px; color: #4a5568; font-size: 14px;">Need immediate assistance?</p>
                                <a href="mailto:pawantripathi802@gmail.com" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 12px 30px; border-radius: 25px; font-weight: 600; font-size: 14px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                                    📧 Contact Admin
                                </a>
                            </div>
                            
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0 0 10px; color: #718096; font-size: 14px;">
                                <strong style="color: #2d3748;">🍽️ Mess Manager</strong><br>
                                Your Complete Mess Management Solution
                            </p>
                            <p style="margin: 0; color: #a0aec0; font-size: 12px;">
                                This is an automated message. Please do not reply to this email.<br>
                                © 2026 Mess Manager. All rights reserved.
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
            </td>
        </tr>
    </table>
    
</body>
</html>
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending registration email: {e}")
