"""
Email template utilities for sending beautiful HTML emails
"""


def get_email_base_template(title, content):
    """
    Base HTML email template with professional styling
    """
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Arial', 'Helvetica', sans-serif; background-color: #f4f7fa;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px 10px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold; text-align: center;">
                                🍽️ Mess Management System
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            {content}
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f9fa; border-radius: 0 0 10px 10px;">
                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding-bottom: 15px;">
                                        <p style="margin: 0; color: #6c757d; font-size: 14px; text-align: center;">
                                            <strong>Need Help?</strong>
                                        </p>
                                        <p style="margin: 5px 0 0; color: #6c757d; font-size: 14px; text-align: center;">
                                            📧 Email: <a href="mailto:pawantripathi802@gmail.com" style="color: #667eea; text-decoration: none;">pawantripathi802@gmail.com</a>
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="border-top: 1px solid #dee2e6; padding-top: 15px;">
                                        <p style="margin: 0; color: #adb5bd; font-size: 12px; text-align: center;">
                                            © 2026 Mess Management System. All rights reserved.
                                        </p>
                                        <p style="margin: 5px 0 0; color: #adb5bd; font-size: 12px; text-align: center;">
                                            This is an automated message. Please do not reply to this email.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """


def get_welcome_email_html(user_name, email, username):
    """
    Generate beautiful HTML welcome email
    """
    content = f"""
    <h2 style="color: #2d3748; margin: 0 0 20px; font-size: 24px;">
        Welcome, {user_name}! 🎉
    </h2>
    
    <p style="color: #4a5568; font-size: 16px; line-height: 1.6; margin: 0 0 20px;">
        Congratulations! Your account has been successfully created. We're excited to have you as part of our mess management community.
    </p>
    
    <div style="background-color: #f7fafc; border-left: 4px solid #667eea; padding: 20px; margin: 25px 0; border-radius: 4px;">
        <h3 style="margin: 0 0 15px; color: #2d3748; font-size: 18px;">📋 Your Account Details</h3>
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #4a5568; font-size: 15px;">
                    <strong>Name:</strong>
                </td>
                <td style="padding: 8px 0; color: #2d3748; font-size: 15px;">
                    {user_name}
                </td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #4a5568; font-size: 15px;">
                    <strong>Username:</strong>
                </td>
                <td style="padding: 8px 0; color: #2d3748; font-size: 15px;">
                    {username}
                </td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #4a5568; font-size: 15px;">
                    <strong>Email:</strong>
                </td>
                <td style="padding: 8px 0; color: #2d3748; font-size: 15px;">
                    {email}
                </td>
            </tr>
        </table>
    </div>
    
    <div style="background-color: #f0fff4; border: 1px solid #9ae6b4; padding: 20px; margin: 25px 0; border-radius: 6px;">
        <h3 style="margin: 0 0 15px; color: #22543d; font-size: 18px;">✅ What You Can Do Now</h3>
        <ul style="margin: 0; padding-left: 20px; color: #2f855a; font-size: 15px; line-height: 1.8;">
            <li>View your monthly payment status</li>
            <li>Check detailed mess expenses and grocery lists</li>
            <li>Browse the weekly meal calendar</li>
            <li>Send messages to the admin team</li>
            <li>Access transparent financial data</li>
            <li>Download payment receipts</li>
        </ul>
    </div>
    
    <div style="text-align: center; margin: 30px 0 20px;">
        <a href="http://127.0.0.1:8000/accounts/login/" 
           style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 14px 40px; border-radius: 6px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 6px rgba(102, 126, 234, 0.4);">
            🚀 Login to Your Account
        </a>
    </div>
    
    <p style="color: #718096; font-size: 14px; line-height: 1.6; margin: 25px 0 0; text-align: center;">
        Thank you for joining us! If you have any questions, feel free to reach out.
    </p>
    """
    
    return get_email_base_template("Welcome to Mess Management", content)


def get_password_reset_email_html(user_name, reset_link):
    """
    Generate beautiful HTML password reset email
    """
    content = f"""
    <h2 style="color: #2d3748; margin: 0 0 20px; font-size: 24px;">
        🔐 Password Reset Request
    </h2>
    
    <p style="color: #4a5568; font-size: 16px; line-height: 1.6; margin: 0 0 20px;">
        Hi {user_name},
    </p>
    
    <p style="color: #4a5568; font-size: 16px; line-height: 1.6; margin: 0 0 25px;">
        We received a request to reset your password for your Mess Management account. Click the button below to create a new password:
    </p>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{reset_link}" 
           style="display: inline-block; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); color: #ffffff; text-decoration: none; padding: 14px 40px; border-radius: 6px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 6px rgba(255, 107, 107, 0.4);">
            Reset My Password
        </a>
    </div>
    
    <div style="background-color: #fff5f5; border-left: 4px solid #fc8181; padding: 20px; margin: 25px 0; border-radius: 4px;">
        <p style="margin: 0; color: #742a2a; font-size: 14px; line-height: 1.6;">
            <strong>⚠️ Security Notice:</strong><br>
            This link will expire in <strong>1 hour</strong> for your security. If you didn't request this password reset, you can safely ignore this email.
        </p>
    </div>
    
    <p style="color: #718096; font-size: 14px; line-height: 1.6; margin: 25px 0 10px;">
        If the button doesn't work, copy and paste this link into your browser:
    </p>
    <p style="color: #667eea; font-size: 13px; word-break: break-all; margin: 0; padding: 10px; background-color: #f7fafc; border-radius: 4px;">
        {reset_link}
    </p>
    """
    
    return get_email_base_template("Password Reset Request", content)


def get_payment_reminder_email_html(user_name, month_year, amount, status, upi_id):
    """
    Generate beautiful HTML payment reminder email
    """
    content = f"""
    <h2 style="color: #2d3748; margin: 0 0 20px; font-size: 24px;">
        💰 Payment Reminder - {month_year}
    </h2>
    
    <p style="color: #4a5568; font-size: 16px; line-height: 1.6; margin: 0 0 20px;">
        Dear {user_name},
    </p>
    
    <p style="color: #4a5568; font-size: 16px; line-height: 1.6; margin: 0 0 25px;">
        This is a friendly reminder about your mess payment for <strong>{month_year}</strong>.
    </p>
    
    <div style="background-color: #fffaf0; border-left: 4px solid #f6ad55; padding: 20px; margin: 25px 0; border-radius: 4px;">
        <h3 style="margin: 0 0 15px; color: #744210; font-size: 18px;">📊 Payment Details</h3>
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #744210; font-size: 15px;">
                    <strong>Amount Due:</strong>
                </td>
                <td style="padding: 8px 0; color: #2d3748; font-size: 18px; font-weight: bold;">
                    ₹{amount}
                </td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #744210; font-size: 15px;">
                    <strong>Status:</strong>
                </td>
                <td style="padding: 8px 0;">
                    <span style="background-color: #fed7d7; color: #c53030; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: bold;">
                        {status.upper()}
                    </span>
                </td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #744210; font-size: 15px;">
                    <strong>Month:</strong>
                </td>
                <td style="padding: 8px 0; color: #2d3748; font-size: 15px;">
                    {month_year}
                </td>
            </tr>
        </table>
    </div>
    
    <div style="background-color: #f0fff4; border: 1px solid #9ae6b4; padding: 20px; margin: 25px 0; border-radius: 6px;">
        <h3 style="margin: 0 0 15px; color: #22543d; font-size: 18px;">💳 Payment Information</h3>
        <p style="margin: 0 0 10px; color: #2f855a; font-size: 15px;">
            <strong>UPI ID:</strong> <span style="background-color: #c6f6d5; padding: 4px 10px; border-radius: 4px; font-family: monospace;">{upi_id}</span>
        </p>
        <p style="margin: 15px 0 0; color: #2f855a; font-size: 14px;">
            Please make your payment at your earliest convenience to avoid any inconvenience.
        </p>
    </div>
    
    <div style="text-align: center; margin: 30px 0 20px;">
        <a href="http://127.0.0.1:8000/user/payment/" 
           style="display: inline-block; background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); color: #ffffff; text-decoration: none; padding: 14px 40px; border-radius: 6px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 6px rgba(72, 187, 120, 0.4);">
            View Payment Details
        </a>
    </div>
    
    <p style="color: #718096; font-size: 14px; line-height: 1.6; margin: 25px 0 0; text-align: center;">
        Thank you for your cooperation!
    </p>
    """
    
    return get_email_base_template("Payment Reminder", content)


def get_password_reset_success_email_html(user_name):
    """
    Generate beautiful HTML password reset success confirmation email
    """
    content = f"""
    <h2 style="color: #2d3748; margin: 0 0 20px; font-size: 24px;">
        ✅ Password Reset Successful
    </h2>
    
    <p style="color: #4a5568; font-size: 16px; line-height: 1.6; margin: 0 0 20px;">
        Hi {user_name},
    </p>
    
    <p style="color: #4a5568; font-size: 16px; line-height: 1.6; margin: 0 0 25px;">
        Your password has been <strong>successfully reset</strong>. You can now login to your Mess Management account using your new password.
    </p>
    
    <div style="background-color: #f0fff4; border-left: 4px solid #48bb78; padding: 20px; margin: 25px 0; border-radius: 4px;">
        <h3 style="margin: 0 0 10px; color: #22543d; font-size: 18px;">✓ Next Steps</h3>
        <p style="margin: 0; color: #2f855a; font-size: 15px; line-height: 1.6;">
            You can now login to your account using your new password. Your account remains secure and all your data is safe.
        </p>
    </div>
    
    <div style="text-align: center; margin: 30px 0 20px;">
        <a href="http://127.0.0.1:8000/accounts/login/" 
           style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 14px 40px; border-radius: 6px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 6px rgba(102, 126, 234, 0.4);">
            🚀 Login to Your Account
        </a>
    </div>
    
    <div style="background-color: #fff5f5; border-left: 4px solid #fc8181; padding: 20px; margin: 25px 0; border-radius: 4px;">
        <p style="margin: 0; color: #742a2a; font-size: 14px; line-height: 1.6;">
            <strong>⚠️ Security Notice:</strong><br>
            If you did not perform this password reset, please contact our support team immediately at <a href="mailto:pawantripathi802@gmail.com" style="color: #742a2a; text-decoration: underline;">pawantripathi802@gmail.com</a>
        </p>
    </div>
    
    <p style="color: #718096; font-size: 14px; line-height: 1.6; margin: 25px 0 0; text-align: center;">
        Your account security is our priority. Thank you for using Mess Management System!
    </p>
    """
    
    return get_email_base_template("Password Reset Successful", content)
