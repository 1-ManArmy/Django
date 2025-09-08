"""
OneLastAI Platform - Authentication Services
Business logic and helper services for user management and authentication
"""
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
import logging
import hashlib
import secrets
from typing import Optional, Dict, Any, List

from .models import User, UserProfile, APIKey
from .utils import generate_username_suggestions, get_client_ip, get_user_agent

logger = logging.getLogger(__name__)


class UserRegistrationService:
    """Service for handling user registration logic"""
    
    @staticmethod
    def create_user(email: str, username: str, password: str, 
                   first_name: str = '', last_name: str = '', 
                   request=None) -> User:
        """
        Create a new user with validation and setup
        """
        try:
            with transaction.atomic():
                # Normalize data
                email = email.lower().strip()
                username = username.lower().strip()
                
                # Check for existing users
                if User.objects.filter(email=email).exists():
                    raise ValidationError("Email already registered")
                
                if User.objects.filter(username=username).exists():
                    raise ValidationError("Username already taken")
                
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create user profile
                profile = UserProfile.objects.create(
                    user=user,
                    registration_ip=get_client_ip(request) if request else None,
                    registration_user_agent=get_user_agent(request) if request else None
                )
                
                # Generate initial API key
                api_key = APIKey.objects.create(
                    user=user,
                    name="Default API Key",
                    key=UserRegistrationService._generate_api_key()
                )
                
                logger.info(f"User registered successfully: {user.email}")
                return user
                
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            raise

    @staticmethod
    def _generate_api_key() -> str:
        """Generate a secure API key"""
        return f"ola_{secrets.token_urlsafe(32)}"

    @staticmethod
    def send_verification_email(user: User) -> bool:
        """Send email verification"""
        try:
            # Generate verification token
            token = hashlib.sha256(
                f"{user.email}{user.date_joined}{settings.SECRET_KEY}".encode()
            ).hexdigest()
            
            # Prepare email context
            context = {
                'user': user,
                'verification_url': f"{settings.FRONTEND_URL}/verify-email/{token}/",
                'site_name': 'OneLastAI',
                'support_email': settings.DEFAULT_FROM_EMAIL
            }
            
            # Render email templates
            html_message = render_to_string('emails/verification.html', context)
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject='Welcome to OneLastAI - Verify Your Email',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Verification email sent to: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False


class AuthenticationService:
    """Service for handling authentication logic"""
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Authenticate user by username or email
        """
        try:
            # First try username
            user = authenticate(username=username, password=password)
            
            if not user:
                # Try email authentication
                try:
                    user_obj = User.objects.get(email=username.lower())
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None

    @staticmethod
    def generate_tokens(user: User, remember_me: bool = False) -> Dict[str, str]:
        """Generate JWT tokens for user"""
        try:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Extend token lifetime if remember_me is True
            if remember_me:
                access_token.set_exp(lifetime=timedelta(days=30))
                refresh.set_exp(lifetime=timedelta(days=60))
            
            return {
                'access': str(access_token),
                'refresh': str(refresh)
            }
            
        except Exception as e:
            logger.error(f"Token generation error: {str(e)}")
            raise

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength and return feedback"""
        feedback = {
            'is_valid': True,
            'score': 0,
            'errors': [],
            'suggestions': []
        }
        
        # Length check
        if len(password) < 8:
            feedback['errors'].append("Password must be at least 8 characters long")
            feedback['is_valid'] = False
        else:
            feedback['score'] += 1
        
        # Character variety checks
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if has_upper:
            feedback['score'] += 1
        else:
            feedback['errors'].append("Include at least one uppercase letter")
            feedback['is_valid'] = False
        
        if has_lower:
            feedback['score'] += 1
        else:
            feedback['errors'].append("Include at least one lowercase letter")
        
        if has_digit:
            feedback['score'] += 1
        else:
            feedback['errors'].append("Include at least one number")
        
        if has_special:
            feedback['score'] += 1
        else:
            feedback['suggestions'].append("Consider adding special characters")
        
        # Common password check (simplified)
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() in common_passwords:
            feedback['errors'].append("This password is too common")
            feedback['is_valid'] = False
        
        return feedback


class UserAnalyticsService:
    """Service for user analytics and tracking"""
    
    @staticmethod
    def track_login(user: User, request=None) -> None:
        """Track user login"""
        try:
            # Update user login stats
            user.login_count = (user.login_count or 0) + 1
            user.last_login_ip = get_client_ip(request) if request else None
            user.last_login_user_agent = get_user_agent(request) if request else None
            user.save(update_fields=['login_count', 'last_login_ip', 'last_login_user_agent'])
            
            logger.info(f"Login tracked for user: {user.email}")
            
        except Exception as e:
            logger.error(f"Login tracking error: {str(e)}")

    @staticmethod
    def track_registration(user: User, request=None) -> None:
        """Track user registration"""
        try:
            # Track registration source, referrer, etc.
            # This can be expanded with more detailed analytics
            logger.info(f"Registration tracked for user: {user.email}")
            
        except Exception as e:
            logger.error(f"Registration tracking error: {str(e)}")

    @staticmethod
    def track_deactivation(user: User, reason: str) -> None:
        """Track user deactivation"""
        try:
            user.deactivation_reason = reason
            user.deactivated_at = timezone.now()
            user.save(update_fields=['deactivation_reason', 'deactivated_at'])
            
            logger.info(f"Deactivation tracked for user: {user.email}")
            
        except Exception as e:
            logger.error(f"Deactivation tracking error: {str(e)}")

    @staticmethod
    def get_user_stats(user: User) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        try:
            # Import here to avoid circular imports
            from agents.models import AgentConversation
            
            conversations = AgentConversation.objects.filter(user=user)
            
            stats = {
                'total_conversations': conversations.count(),
                'total_messages': sum(conv.messages.count() for conv in conversations),
                'api_requests_made': user.api_requests_count,
                'api_requests_remaining': max(0, user.get_api_limit() - user.api_requests_count),
                'account_age_days': (timezone.now() - user.date_joined).days,
                'login_count': user.login_count or 0,
                'subscription_tier': user.subscription_tier,
                'last_login': user.last_login,
                'is_email_verified': user.is_email_verified
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Stats generation error: {str(e)}")
            return {}

    @staticmethod
    def get_dashboard_stats(user: User) -> Dict[str, Any]:
        """Get dashboard-specific statistics"""
        try:
            from agents.models import AgentConversation
            
            # Get recent activity
            recent_conversations = AgentConversation.objects.filter(
                user=user
            ).order_by('-created_at')[:5]
            
            # Calculate usage metrics
            api_usage_percentage = 0
            if user.get_api_limit() > 0:
                api_usage_percentage = (user.api_requests_count / user.get_api_limit()) * 100
            
            stats = {
                'conversations_today': AgentConversation.objects.filter(
                    user=user,
                    created_at__date=timezone.now().date()
                ).count(),
                'conversations_total': AgentConversation.objects.filter(user=user).count(),
                'api_usage_percentage': min(100, api_usage_percentage),
                'favorite_agents': UserAnalyticsService._get_favorite_agents(user),
                'recent_conversations': [
                    {
                        'id': conv.id,
                        'title': conv.title,
                        'agent': conv.agent.name,
                        'created_at': conv.created_at
                    }
                    for conv in recent_conversations
                ]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Dashboard stats error: {str(e)}")
            return {}

    @staticmethod
    def _get_favorite_agents(user: User) -> List[str]:
        """Get user's most used agents"""
        try:
            from agents.models import AgentConversation
            from django.db.models import Count
            
            favorite_agents = AgentConversation.objects.filter(
                user=user
            ).values('agent__name').annotate(
                usage_count=Count('id')
            ).order_by('-usage_count')[:3]
            
            return [agent['agent__name'] for agent in favorite_agents]
            
        except Exception as e:
            logger.error(f"Favorite agents error: {str(e)}")
            return []

    @staticmethod
    def get_usage_stats(user: User) -> Dict[str, Any]:
        """Get detailed usage statistics"""
        try:
            now = timezone.now()
            
            # API usage statistics
            api_stats = {
                'requests_today': 0,  # Would need activity logging
                'requests_this_week': 0,
                'requests_this_month': user.api_requests_count,  # Simplified
                'requests_limit': user.get_api_limit()
            }
            
            # Conversation statistics
            from agents.models import AgentConversation
            conversations = AgentConversation.objects.filter(user=user)
            
            conversation_stats = {
                'total_conversations': conversations.count(),
                'conversations_this_month': conversations.filter(
                    created_at__month=now.month,
                    created_at__year=now.year
                ).count(),
                'average_messages_per_conversation': 0
            }
            
            # Calculate average messages
            total_messages = sum(conv.messages.count() for conv in conversations)
            if conversations.exists():
                conversation_stats['average_messages_per_conversation'] = total_messages / conversations.count()
            
            return {
                'api': api_stats,
                'conversations': conversation_stats,
                'account': {
                    'age_days': (now - user.date_joined).days,
                    'login_count': user.login_count or 0
                }
            }
            
        except Exception as e:
            logger.error(f"Usage stats error: {str(e)}")
            return {}

    @staticmethod
    def get_recent_activity(user: User) -> List[Dict[str, Any]]:
        """Get recent user activity"""
        try:
            # This would typically come from an activity log table
            # For now, return basic activities based on existing data
            activities = []
            
            if user.last_login:
                activities.append({
                    'type': 'login',
                    'description': 'Logged in to OneLastAI',
                    'timestamp': user.last_login,
                    'icon': 'login'
                })
            
            # Add more activity types as needed
            from agents.models import AgentConversation
            recent_conversations = AgentConversation.objects.filter(
                user=user
            ).order_by('-created_at')[:3]
            
            for conv in recent_conversations:
                activities.append({
                    'type': 'conversation',
                    'description': f'Started conversation with {conv.agent.name}',
                    'timestamp': conv.created_at,
                    'icon': 'chat'
                })
            
            return sorted(activities, key=lambda x: x['timestamp'], reverse=True)[:10]
            
        except Exception as e:
            logger.error(f"Recent activity error: {str(e)}")
            return []

    @staticmethod
    def get_login_attempts(user: User) -> List[Dict[str, Any]]:
        """Get recent login attempts (simplified)"""
        # This would typically come from a security log
        return [
            {
                'timestamp': user.last_login,
                'ip_address': user.last_login_ip or 'Unknown',
                'success': True,
                'user_agent': user.last_login_user_agent or 'Unknown'
            }
        ] if user.last_login else []


class SubscriptionService:
    """Service for handling subscriptions and billing"""
    
    @staticmethod
    def get_subscription_info(user: User) -> Dict[str, Any]:
        """Get user subscription information"""
        return {
            'tier': user.subscription_tier,
            'tier_display': user.get_subscription_tier_display(),
            'api_limit': user.get_api_limit(),
            'requests_used': user.api_requests_count,
            'requests_remaining': max(0, user.get_api_limit() - user.api_requests_count),
            'reset_date': user.api_limit_reset_date,
            'can_upgrade': user.subscription_tier != 'enterprise'
        }

    @staticmethod
    def get_billing_history(user: User) -> List[Dict[str, Any]]:
        """Get user billing history (placeholder)"""
        # This would integrate with payment processor
        return [
            {
                'date': timezone.now() - timedelta(days=30),
                'amount': 29.00,
                'plan': 'Basic Plan',
                'status': 'paid',
                'invoice_url': '#'
            }
        ] if user.subscription_tier != 'free' else []

    @staticmethod
    def can_upgrade_subscription(user: User, target_tier: str) -> bool:
        """Check if user can upgrade to target tier"""
        tier_hierarchy = ['free', 'basic', 'pro', 'enterprise']
        
        current_index = tier_hierarchy.index(user.subscription_tier)
        target_index = tier_hierarchy.index(target_tier)
        
        return target_index > current_index


class APIKeyService:
    """Service for API key management"""
    
    @staticmethod
    def generate_api_key(user: User, name: str, description: str = '') -> APIKey:
        """Generate new API key for user"""
        try:
            # Check limits
            existing_keys = APIKey.objects.filter(user=user, is_active=True).count()
            max_keys = 5 if user.subscription_tier == 'enterprise' else 3
            
            if existing_keys >= max_keys:
                raise ValidationError(f"Maximum {max_keys} API keys allowed")
            
            # Generate key
            api_key = APIKey.objects.create(
                user=user,
                name=name,
                description=description,
                key=f"ola_{secrets.token_urlsafe(32)}"
            )
            
            logger.info(f"API key generated for user: {user.email}")
            return api_key
            
        except Exception as e:
            logger.error(f"API key generation error: {str(e)}")
            raise

    @staticmethod
    def revoke_api_key(user: User, key_id: int) -> bool:
        """Revoke API key"""
        try:
            api_key = APIKey.objects.get(id=key_id, user=user, is_active=True)
            api_key.is_active = False
            api_key.revoked_at = timezone.now()
            api_key.save()
            
            logger.info(f"API key revoked: {api_key.name}")
            return True
            
        except APIKey.DoesNotExist:
            logger.error(f"API key not found: {key_id}")
            return False
        except Exception as e:
            logger.error(f"API key revocation error: {str(e)}")
            return False

    @staticmethod
    def validate_api_key(key: str) -> Optional[User]:
        """Validate API key and return associated user"""
        try:
            api_key = APIKey.objects.select_related('user').get(
                key=key,
                is_active=True
            )
            
            # Update usage stats
            api_key.usage_count += 1
            api_key.last_used_at = timezone.now()
            api_key.save(update_fields=['usage_count', 'last_used_at'])
            
            return api_key.user
            
        except APIKey.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"API key validation error: {str(e)}")
            return None
