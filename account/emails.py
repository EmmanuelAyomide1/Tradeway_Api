from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging


logger = logging.getLogger(__name__)

def send_email(subject, recipient, context, template_name):
    """
    Utility to send an email with HTML and plain text content.

    Args:
        subject: Email subject
        recipient: Recipient email address
        context: Context for the email template
        template_name: Path to the email template
    """
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
  
        with get_connection() as connection:
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[recipient],
                connection=connection,
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
    except Exception as e:
        logger.error(f"Error sending email to {recipient}: {e}")
        raise e


def send_verification_email(name: str, email: str, otp: str) -> None:
    """
    Sends am welcome email containing a verification OTP to new users

    Args:
        name: User's first name
        email: User's email address
        otp: Verification OTP
    """
    try:
        context = {
            'name': name,
            'email': email,
            'otp': otp
        }
        send_email(
            subject='Welcome to Tradeway',
            recipient=email,
            context=context,
            template_name='otp_verification.html',
        )
        logger.info(f"Verification email successfully sent to {email}")
    except Exception as e:
        logger.warning(f"Could not send verification email to {email} due to: {e}")
        raise e


def send_password_reset_email(email: str, code: str) -> None:
    """
    Sends a password reset email to the user

    Args:
        email: User's email address
        token: Password reset token
    """
    try:
        context = {
            'email': email,
            'code': code
        }
        send_email(
            subject='Tradeway Password Reset',
            recipient=email,
            context=context,
            template_name='password_reset.html',
        )
        logger.info(f"Password reset email successfully sent to {email}")
    except Exception as e:
        logger.warning(f"Could not send password reset email to {email} due to: {e}")
        raise e