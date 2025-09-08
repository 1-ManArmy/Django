"""
Custom User Model for OneLastAI Platform.
Extends Django's AbstractUser with additional fields and functionality.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid


class User(AbstractUser):
    """Custom User model with additional fields for OneLastAI platform."""
    
    SUBSCRIPTION_TIERS = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('pro', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=_('Enter a valid username. This value may contain only letters, '
                         'numbers, and @/./+/-/_ characters.')
            ),
        ],
    )
    
    # Profile Information
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Subscription & Billing
    subscription_tier = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_TIERS, 
        default='free'
    )
    subscription_active = models.BooleanField(default=True)
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    
    # Usage Tracking
    total_conversations = models.IntegerField(default=0)
    total_tokens_used = models.BigIntegerField(default=0)
    monthly_tokens_used = models.IntegerField(default=0)
    last_token_reset = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    preferred_ai_model = models.CharField(max_length=50, default='gpt-4')
    preferred_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Feature Flags
    beta_features_enabled = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=True)
    usage_analytics = models.BooleanField(default=True)
    
    # Authentication & Security
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    
    # Social Authentication
    google_id = models.CharField(max_length=100, blank=True, unique=True, null=True)
    github_id = models.CharField(max_length=100, blank=True, unique=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['subscription_tier']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def display_name_or_email(self):
        """Return display name or email if no display name set."""
        return self.display_name or self.email
    
    def get_tokens_remaining(self):
        """Calculate remaining tokens for current billing period."""
        if self.subscription_tier == 'free':
            return max(0, 10000 - self.monthly_tokens_used)
        elif self.subscription_tier == 'basic':
            return max(0, 100000 - self.monthly_tokens_used)
        elif self.subscription_tier == 'pro':
            return max(0, 1000000 - self.monthly_tokens_used)
        else:  # enterprise
            return float('inf')  # Unlimited
    
    def can_use_premium_features(self):
        """Check if user has access to premium features."""
        return self.subscription_tier in ['pro', 'enterprise']
    
    def can_use_agent(self, agent_name):
        """Check if user can access a specific agent."""
        # Free tier has access to basic agents only
        if self.subscription_tier == 'free':
            basic_agents = [
                'neochat', 'infoseek', 'contentcrafter', 'taskmaster'
            ]
            return agent_name in basic_agents
        
        # All other tiers have full access
        return True
    
    def reset_monthly_usage(self):
        """Reset monthly token usage (called by scheduled task)."""
        from django.utils import timezone
        self.monthly_tokens_used = 0
        self.last_token_reset = timezone.now()
        self.save(update_fields=['monthly_tokens_used', 'last_token_reset'])


class UserProfile(models.Model):
    """Extended user profile information."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Professional Information
    company = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=50, blank=True)
    
    # Location
    country = models.CharField(max_length=2, blank=True)  # ISO country code
    city = models.CharField(max_length=100, blank=True)
    
    # Interests and Usage
    primary_use_case = models.CharField(max_length=100, blank=True)
    interests = models.JSONField(default=list, blank=True)
    favorite_agents = models.JSONField(default=list, blank=True)
    
    # Onboarding
    onboarding_completed = models.BooleanField(default=False)
    onboarding_step = models.IntegerField(default=0)
    
    # Privacy Settings
    profile_public = models.BooleanField(default=False)
    show_usage_stats = models.BooleanField(default=True)
    allow_data_collection = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"{self.user.email} Profile"


class UserApiKey(models.Model):
    """API keys for users to access the platform programmatically."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=100)  # User-defined name for the key
    key = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    
    # Permissions
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    
    # Usage tracking
    last_used = models.DateTimeField(null=True, blank=True)
    total_requests = models.IntegerField(default=0)
    
    # Rate limiting
    rate_limit_per_hour = models.IntegerField(default=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('User API Key')
        verbose_name_plural = _('User API Keys')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"
    
    def is_expired(self):
        """Check if API key is expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at


class UserActivity(models.Model):
    """Track user activities for analytics and security."""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('conversation_start', 'Conversation Started'),
        ('agent_interaction', 'Agent Interaction'),
        ('subscription_change', 'Subscription Changed'),
        ('profile_update', 'Profile Updated'),
        ('api_usage', 'API Usage'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=200, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.timestamp}"
