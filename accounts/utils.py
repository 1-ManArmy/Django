"""
OneLastAI Platform - Authentication Utils
Utility functions for user management, security, and helper operations
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from django.utils import timezone
import secrets
import hashlib
import re
import logging
from typing import Optional, List, Dict, Any
from user_agents import parse
import requests

from .models import User, APIKey

logger = logging.getLogger(__name__)


def generate_api_key(user: User, name: str = None) -> APIKey:
    """
    Generate a secure API key for the user
    """
    if not name:
        name = f"API Key {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Generate secure key
    key = f"ola_{secrets.token_urlsafe(32)}"
    
    api_key = APIKey.objects.create(
        user=user,
        name=name,
        key=key
    )
    
    logger.info(f"API key generated for user {user.email}: {name}")
    return api_key


def send_welcome_email(user: User) -> bool:
    """
    Send welcome email to new user
    """
    try:
        context = {
            'user': user,
            'site_name': 'OneLastAI',
            'login_url': f"{settings.FRONTEND_URL}/login/",
            'dashboard_url': f"{settings.FRONTEND_URL}/dashboard/",
            'agents_url': f"{settings.FRONTEND_URL}/agents/",
            'support_email': settings.DEFAULT_FROM_EMAIL,
            'year': timezone.now().year
        }
        
        # Render email content
        html_content = render_to_string('emails/welcome.html', context)
        text_content = strip_tags(html_content)
        
        # Create and send email
        email = EmailMultiAlternatives(
            subject='Welcome to OneLastAI - Your AI Agent Network Awaits!',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Welcome email sent to: {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False


def send_password_reset_email(user: User) -> bool:
    """
    Send password reset email
    """
    try:
        # Generate reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        context = {
            'user': user,
            'reset_url': f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/",
            'site_name': 'OneLastAI',
            'support_email': settings.DEFAULT_FROM_EMAIL,
            'expiry_hours': 24
        }
        
        html_content = render_to_string('emails/password_reset.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject='OneLastAI - Password Reset Request',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Password reset email sent to: {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False


def send_email_change_verification(user: User, new_email: str) -> bool:
    """
    Send email change verification
    """
    try:
        # Generate verification token
        token = hashlib.sha256(
            f"{user.pk}{new_email}{timezone.now().date()}{settings.SECRET_KEY}".encode()
        ).hexdigest()
        
        context = {
            'user': user,
            'new_email': new_email,
            'verification_url': f"{settings.FRONTEND_URL}/verify-email-change/{token}/",
            'site_name': 'OneLastAI',
            'support_email': settings.DEFAULT_FROM_EMAIL
        }
        
        html_content = render_to_string('emails/email_change_verification.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject='OneLastAI - Verify Your New Email Address',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[new_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Email change verification sent to: {new_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email change verification: {str(e)}")
        return False


def generate_username_suggestions(base_username: str, email: str = None) -> List[str]:
    """
    Generate username suggestions when the desired one is taken
    """
    suggestions = []
    
    # Clean base username
    base = re.sub(r'[^a-zA-Z0-9_]', '', base_username.lower())
    
    # Add number variations
    for i in range(1, 10):
        suggestion = f"{base}{i}"
        if not User.objects.filter(username=suggestion).exists():
            suggestions.append(suggestion)
    
    # Add email-based suggestions if available
    if email:
        email_base = email.split('@')[0].lower()
        email_base = re.sub(r'[^a-zA-Z0-9_]', '', email_base)
        
        if email_base != base and not User.objects.filter(username=email_base).exists():
            suggestions.append(email_base)
        
        for i in range(1, 5):
            suggestion = f"{email_base}{i}"
            if not User.objects.filter(username=suggestion).exists():
                suggestions.append(suggestion)
    
    # Add random variations
    import random
    suffixes = ['ai', 'user', 'dev', 'pro', 'plus']
    for suffix in suffixes:
        suggestion = f"{base}_{suffix}"
        if not User.objects.filter(username=suggestion).exists():
            suggestions.append(suggestion)
    
    return suggestions[:10]  # Return up to 10 suggestions


def validate_username_format(username: str) -> Dict[str, Any]:
    """
    Validate username format and return detailed feedback
    """
    result = {
        'is_valid': True,
        'errors': [],
        'suggestions': []
    }
    
    # Length check
    if len(username) < 3:
        result['errors'].append('Username must be at least 3 characters long')
        result['is_valid'] = False
    elif len(username) > 30:
        result['errors'].append('Username must be less than 30 characters')
        result['is_valid'] = False
    
    # Character check
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        result['errors'].append('Username can only contain letters, numbers, and underscores')
        result['is_valid'] = False
    
    # Must start with letter or number
    if not re.match(r'^[a-zA-Z0-9]', username):
        result['errors'].append('Username must start with a letter or number')
        result['is_valid'] = False
    
    # Reserved names check
    reserved_names = [
        'admin', 'administrator', 'root', 'api', 'www', 'mail', 'email',
        'support', 'help', 'info', 'news', 'blog', 'dev', 'test', 'demo',
        'onelastai', 'system', 'null', 'undefined'
    ]
    
    if username.lower() in reserved_names:
        result['errors'].append('This username is reserved')
        result['is_valid'] = False
        result['suggestions'] = generate_username_suggestions(username)
    
    return result


def get_client_ip(request) -> Optional[str]:
    """
    Get client IP address from request
    """
    if not request:
        return None
    
    # Check for forwarded IPs (load balancers, proxies)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    # Check for real IP (some proxies use this)
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip.strip()
    
    # Fall back to REMOTE_ADDR
    return request.META.get('REMOTE_ADDR')


def get_user_agent(request) -> Optional[str]:
    """
    Get user agent from request
    """
    if not request:
        return None
    
    return request.META.get('HTTP_USER_AGENT', '')


def parse_user_agent(user_agent_string: str) -> Dict[str, str]:
    """
    Parse user agent string into components
    """
    try:
        user_agent = parse(user_agent_string)
        
        return {
            'browser': user_agent.browser.family,
            'browser_version': user_agent.browser.version_string,
            'os': user_agent.os.family,
            'os_version': user_agent.os.version_string,
            'device': user_agent.device.family,
            'is_mobile': user_agent.is_mobile,
            'is_tablet': user_agent.is_tablet,
            'is_pc': user_agent.is_pc,
            'is_bot': user_agent.is_bot
        }
    except Exception as e:
        logger.error(f"Error parsing user agent: {str(e)}")
        return {
            'browser': 'Unknown',
            'browser_version': '',
            'os': 'Unknown',
            'os_version': '',
            'device': 'Unknown',
            'is_mobile': False,
            'is_tablet': False,
            'is_pc': False,
            'is_bot': False
        }


def track_user_activity(user: User, activity_type: str, request=None, 
                       description: str = None, metadata: Dict = None) -> None:
    """
    Track user activity (simplified version - would use dedicated model in production)
    """
    try:
        activity_data = {
            'user_id': user.id,
            'activity_type': activity_type,
            'timestamp': timezone.now(),
            'ip_address': get_client_ip(request),
            'user_agent': get_user_agent(request),
            'description': description or f"User {activity_type}",
            'metadata': metadata or {}
        }
        
        # In production, this would save to an ActivityLog model
        logger.info(f"Activity tracked: {user.email} - {activity_type}")
        
    except Exception as e:
        logger.error(f"Activity tracking error: {str(e)}")


def validate_password_complexity(password: str) -> Dict[str, Any]:
    """
    Validate password complexity with detailed feedback
    """
    result = {
        'is_valid': True,
        'score': 0,
        'max_score': 6,
        'feedback': {
            'length': False,
            'uppercase': False,
            'lowercase': False,
            'numbers': False,
            'special_chars': False,
            'no_common_patterns': False
        },
        'suggestions': []
    }
    
    # Length check (minimum 8 characters)
    if len(password) >= 8:
        result['feedback']['length'] = True
        result['score'] += 1
    else:
        result['suggestions'].append('Use at least 8 characters')
    
    # Uppercase letters
    if re.search(r'[A-Z]', password):
        result['feedback']['uppercase'] = True
        result['score'] += 1
    else:
        result['suggestions'].append('Add uppercase letters')
    
    # Lowercase letters
    if re.search(r'[a-z]', password):
        result['feedback']['lowercase'] = True
        result['score'] += 1
    else:
        result['suggestions'].append('Add lowercase letters')
    
    # Numbers
    if re.search(r'\d', password):
        result['feedback']['numbers'] = True
        result['score'] += 1
    else:
        result['suggestions'].append('Add numbers')
    
    # Special characters
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result['feedback']['special_chars'] = True
        result['score'] += 1
    else:
        result['suggestions'].append('Add special characters (!@#$%^&*)')
    
    # Common patterns check
    common_patterns = [
        'password', '123456', 'qwerty', 'admin', 'login',
        '111111', 'abc123', 'password123'
    ]
    
    if not any(pattern in password.lower() for pattern in common_patterns):
        result['feedback']['no_common_patterns'] = True
        result['score'] += 1
    else:
        result['suggestions'].append('Avoid common patterns and dictionary words')
    
    # Overall validation
    result['is_valid'] = result['score'] >= 4  # Require at least 4/6 criteria
    
    return result


def sanitize_email(email: str) -> str:
    """
    Sanitize and normalize email address
    """
    if not email:
        return ''
    
    # Convert to lowercase and strip whitespace
    email = email.lower().strip()
    
    # Remove any potential dangerous characters
    email = re.sub(r'[^\w\.-@]', '', email)
    
    return email


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure token
    """
    return secrets.token_urlsafe(length)


def hash_api_key(api_key: str) -> str:
    """
    Hash API key for secure storage
    """
    return hashlib.sha256(f"{api_key}{settings.SECRET_KEY}".encode()).hexdigest()


def verify_recaptcha(recaptcha_response: str, request=None) -> bool:
    """
    Verify reCAPTCHA response
    """
    if not settings.RECAPTCHA_SECRET_KEY:
        return True  # Skip verification if not configured
    
    try:
        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
            'remoteip': get_client_ip(request)
        }
        
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data,
            timeout=10
        )
        
        result = response.json()
        return result.get('success', False)
        
    except Exception as e:
        logger.error(f"reCAPTCHA verification error: {str(e)}")
        return False


def check_password_breach(password: str) -> bool:
    """
    Check if password appears in known breaches using HaveIBeenPwned API
    """
    try:
        # Hash the password
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]
        
        # Query HaveIBeenPwned API
        response = requests.get(
            f'https://api.pwnedpasswords.com/range/{prefix}',
            timeout=5
        )
        
        if response.status_code == 200:
            # Check if our suffix appears in the results
            hashes = response.text.split('\n')
            for hash_line in hashes:
                if hash_line.startswith(suffix):
                    count = int(hash_line.split(':')[1])
                    logger.warning(f"Password found in {count} breaches")
                    return True
        
        return False
        
    except Exception as e:
        logger.error(f"Password breach check error: {str(e)}")
        return False  # Don't block user if service is unavailable


def format_user_activity_description(activity_type: str, metadata: Dict = None) -> str:
    """
    Format user activity description based on type and metadata
    """
    descriptions = {
        'login': 'Logged in to OneLastAI',
        'logout': 'Logged out of OneLastAI',
        'register': 'Registered new account',
        'profile_update': 'Updated profile information',
        'password_change': 'Changed password',
        'api_key_generate': 'Generated new API key',
        'api_key_revoke': 'Revoked API key',
        'subscription_upgrade': 'Upgraded subscription',
        'conversation_start': 'Started new conversation',
        'message_send': 'Sent message to AI agent'
    }
    
    base_description = descriptions.get(activity_type, f'Performed {activity_type}')
    
    # Add metadata details if available
    if metadata:
        if activity_type == 'conversation_start' and 'agent_name' in metadata:
            base_description = f"Started conversation with {metadata['agent_name']}"
        elif activity_type == 'api_key_generate' and 'key_name' in metadata:
            base_description = f"Generated API key: {metadata['key_name']}"
    
    return base_description


def get_timezone_choices() -> List[tuple]:
    """
    Get list of timezone choices for user profile
    """
    import pytz
    
    common_timezones = [
        'US/Eastern', 'US/Central', 'US/Mountain', 'US/Pacific',
        'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Rome',
        'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Kolkata', 'Asia/Dubai',
        'Australia/Sydney', 'Australia/Melbourne',
        'America/New_York', 'America/Los_Angeles', 'America/Chicago',
        'UTC'
    ]
    
    choices = []
    for tz in common_timezones:
        try:
            timezone_obj = pytz.timezone(tz)
            choices.append((tz, tz.replace('_', ' ')))
        except:
            continue
    
    return sorted(choices, key=lambda x: x[1])


def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """
    Mask sensitive data like API keys, showing only first/last few characters
    """
    if not data or len(data) <= visible_chars * 2:
        return mask_char * len(data) if data else ''
    
    visible_start = data[:visible_chars]
    visible_end = data[-visible_chars:]
    masked_middle = mask_char * (len(data) - visible_chars * 2)
    
    return f"{visible_start}{masked_middle}{visible_end}"
