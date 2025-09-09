"""
OneLastAI Platform - Authentication Serializers
Advanced serializers for API authentication and user management
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from allauth.socialaccount.models import SocialAccount
import logging

from .models import User, UserProfile, UserApiKey

logger = logging.getLogger(__name__)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data"""
    
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'location', 'website', 'twitter_handle', 'linkedin_profile',
            'avatar', 'avatar_url', 'newsletter_subscribed', 'email_notifications',
            'push_notifications', 'timezone', 'language', 'theme_preference'
        ]
        read_only_fields = ['avatar_url']

    def get_avatar_url(self, obj):
        """Get avatar URL with fallback"""
        if obj.avatar:
            return obj.avatar.url
        return f"https://ui-avatars.com/api/?name={obj.user.get_full_name() or obj.user.username}&background=6366f1&color=fff&size=200"


class UserSerializer(serializers.ModelSerializer):
    """Main user serializer with profile and statistics"""
    
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    subscription_info = serializers.SerializerMethodField()
    api_usage = serializers.SerializerMethodField()
    social_accounts = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'date_joined', 'last_login', 'subscription_tier',
            'api_requests_count', 'profile', 'subscription_info', 'api_usage',
            'social_accounts', 'is_email_verified'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'api_requests_count',
            'subscription_tier', 'is_email_verified'
        ]

    def get_full_name(self, obj):
        """Get user's full name"""
        return obj.get_full_name() or obj.username

    def get_subscription_info(self, obj):
        """Get subscription information"""
        return {
            'tier': obj.subscription_tier,
            'tier_display': obj.get_subscription_tier_display(),
            'api_limit': obj.get_api_limit(),
            'requests_remaining': max(0, obj.get_api_limit() - obj.api_requests_count),
            'reset_date': obj.api_limit_reset_date,
            'is_premium': obj.subscription_tier != 'free'
        }

    def get_api_usage(self, obj):
        """Get API usage statistics"""
        return {
            'requests_made': obj.api_requests_count,
            'requests_limit': obj.get_api_limit(),
            'usage_percentage': min(100, (obj.api_requests_count / obj.get_api_limit()) * 100) if obj.get_api_limit() > 0 else 0,
            'reset_date': obj.api_limit_reset_date
        }

    def get_social_accounts(self, obj):
        """Get connected social accounts"""
        social_accounts = SocialAccount.objects.filter(user=obj)
        return [
            {
                'provider': account.provider,
                'uid': account.uid,
                'connected_at': account.date_joined
            }
            for account in social_accounts
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration via API"""
    
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Password must be at least 8 characters with uppercase, lowercase, and number'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    terms_agreed = serializers.BooleanField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'terms_agreed'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_username(self, value):
        """Validate username"""
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        
        if User.objects.filter(username=value.lower()).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        
        return value.lower()

    def validate_password(self, value):
        """Validate password strength"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_terms_agreed(self, value):
        """Ensure terms are accepted"""
        if not value:
            raise serializers.ValidationError("You must agree to the terms of service.")
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Password confirmation doesn't match."
            })
        return attrs

    def create(self, validated_data):
        """Create user with validated data"""
        # Remove non-user fields
        validated_data.pop('password_confirm')
        validated_data.pop('terms_agreed')
        
        # Create user
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        
        # Create profile
        UserProfile.objects.create(user=user)
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Enhanced JWT token serializer with user data"""
    
    def validate(self, attrs):
        """Validate credentials and return enhanced token data"""
        try:
            data = super().validate(attrs)
            
            # Add user information to response
            user = self.user
            data.update({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.get_full_name(),
                    'subscription_tier': user.subscription_tier,
                    'is_email_verified': user.is_email_verified
                },
                'subscription': {
                    'tier': user.subscription_tier,
                    'api_limit': user.get_api_limit(),
                    'requests_used': user.api_requests_count
                },
                'permissions': {
                    'can_use_premium_features': user.subscription_tier != 'free',
                    'can_access_api': True,
                    'max_api_keys': 5 if user.subscription_tier == 'enterprise' else 3
                }
            })
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return data
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            raise serializers.ValidationError('Authentication failed')

    @classmethod
    def get_token(cls, user):
        """Get token with custom claims"""
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['subscription_tier'] = user.subscription_tier
        token['is_email_verified'] = user.is_email_verified
        
        return token


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

    def validate_username(self, value):
        """Validate username uniqueness (excluding current user)"""
        user = self.instance
        if User.objects.filter(username=value.lower()).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value.lower()


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password changes"""
    
    current_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_current_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        """Validate new password"""
        try:
            validate_password(value, self.context['request'].user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Password confirmation doesn't match."
            })
        
        if attrs['current_password'] == attrs['new_password']:
            raise serializers.ValidationError({
                'new_password': "New password must be different from current password."
            })
        
        return attrs

    def save(self):
        """Update user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.password_changed_at = timezone.now()
        user.save()
        return user


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API key management"""
    
    key = serializers.CharField(read_only=True)
    
    class Meta:
        model = UserApiKey
        fields = [
            'id', 'name', 'description', 'key', 'created_at',
            'last_used_at', 'is_active', 'usage_count'
        ]
        read_only_fields = ['key', 'created_at', 'last_used_at', 'usage_count']

    def create(self, validated_data):
        """Create new API key"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    
    total_conversations = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    favorite_agents = serializers.ListField(child=serializers.CharField())
    api_requests_today = serializers.IntegerField()
    api_requests_this_month = serializers.IntegerField()
    account_age_days = serializers.IntegerField()
    last_activity = serializers.DateTimeField()


class UserActivitySerializer(serializers.Serializer):
    """Serializer for user activity logs"""
    
    activity_type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    description = serializers.CharField()
    ip_address = serializers.IPAddressField()
    user_agent = serializers.CharField()


class SocialAccountSerializer(serializers.ModelSerializer):
    """Serializer for social account connections"""
    
    class Meta:
        model = SocialAccount
        fields = ['provider', 'uid', 'date_joined']
        read_only_fields = ['provider', 'uid', 'date_joined']


class UserDashboardSerializer(serializers.Serializer):
    """Comprehensive dashboard data serializer"""
    
    user = UserSerializer()
    stats = UserStatsSerializer()
    recent_activity = UserActivitySerializer(many=True)
    api_keys = APIKeySerializer(many=True)
    subscription_usage = serializers.DictField()
    quick_actions = serializers.ListField(child=serializers.DictField())


class AccountDeactivationSerializer(serializers.Serializer):
    """Serializer for account deactivation"""
    
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    reason = serializers.ChoiceField(
        choices=[
            ('not_using', 'Not using the service anymore'),
            ('too_expensive', 'Too expensive'),
            ('missing_features', 'Missing features I need'),
            ('found_alternative', 'Found a better alternative'),
            ('privacy_concerns', 'Privacy concerns'),
            ('technical_issues', 'Technical issues'),
            ('other', 'Other')
        ]
    )
    feedback = serializers.CharField(required=False, allow_blank=True)

    def validate_password(self, value):
        """Validate password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect password.")
        return value


class UserLoginSerializer(serializers.Serializer):
    """Enhanced login serializer"""
    
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    remember_me = serializers.BooleanField(default=False)

    def validate(self, attrs):
        """Validate login credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Try to authenticate with username or email
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                # Try email authentication
                try:
                    user_obj = User.objects.get(email=username.lower())
                    user = authenticate(
                        request=self.context.get('request'),
                        username=user_obj.username,
                        password=password
                    )
                except User.DoesNotExist:
                    pass
            
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('Account is deactivated.')
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password.')
        
        return attrs
