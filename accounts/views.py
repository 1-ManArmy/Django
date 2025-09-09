"""
OneLastAI Platform - Advanced Authentication Views
Comprehensive authentication system with social logins, JWT, and enterprise features
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.db import transaction
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
import json
import logging
from datetime import datetime, timedelta

from .models import User, UserProfile, UserApiKey
from .forms import (
    CustomUserCreationForm, 
    CustomUserChangeForm, 
    UserProfileForm,
    PasswordChangeForm,
    AccountDeactivationForm
)
from .serializers import (
    UserSerializer, 
    UserProfileSerializer,
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer
)
from .services import (
    UserRegistrationService,
    AuthenticationService,
    UserAnalyticsService,
    SubscriptionService
)
from .utils import generate_api_key, send_welcome_email, track_user_activity

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view with enhanced user data"""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Track successful login
                username = request.data.get('username')
                user = User.objects.filter(username=username).first()
                if user:
                    track_user_activity(user, 'login', request)
                    UserAnalyticsService.track_login(user, request)
                    
                    # Update last login
                    user.last_login = timezone.now()
                    user.save(update_fields=['last_login'])
                    
            return response
            
        except Exception as e:
            logger.error(f"Token obtain error: {str(e)}")
            return Response(
                {'error': 'Authentication failed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserRegistrationView(CreateView):
    """Enhanced user registration with email verification and analytics"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:registration_success')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Create user through service
                user = UserRegistrationService.create_user(
                    email=form.cleaned_data['email'],
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password1'],
                    first_name=form.cleaned_data.get('first_name', ''),
                    last_name=form.cleaned_data.get('last_name', ''),
                    request=self.request
                )
                
                # Generate API key
                api_key = generate_api_key(user)
                
                # Send welcome email
                send_welcome_email(user)
                
                # Track registration
                UserAnalyticsService.track_registration(user, self.request)
                
                messages.success(
                    self.request, 
                    'Registration successful! Please check your email to verify your account.'
                )
                
                return redirect(self.success_url)
                
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            messages.error(self.request, 'Registration failed. Please try again.')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Join OneLastAI',
            'show_social_login': True,
            'features': [
                'Access to 24 AI Agents',
                'Real-time Chat Interface',
                'API Access',
                'Community Features'
            ]
        })
        return context


class UserLoginView(APIView):
    """Enhanced login view with multiple authentication methods"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            remember_me = request.data.get('remember_me', False)
            
            if not username or not password:
                return Response(
                    {'error': 'Username and password are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Authenticate user
            user = AuthenticationService.authenticate_user(username, password)
            
            if not user:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if not user.is_active:
                return Response(
                    {'error': 'Account is deactivated'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Set token expiry based on remember_me
            if remember_me:
                access_token.set_exp(lifetime=timedelta(days=30))
            
            # Update user login info
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Track login
            track_user_activity(user, 'login', request)
            UserAnalyticsService.track_login(user, request)
            
            response_data = {
                'access': str(access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
                'subscription_tier': user.subscription_tier,
                'api_usage': {
                    'requests_used': user.api_requests_count,
                    'requests_limit': user.get_api_limit(),
                    'reset_date': user.api_limit_reset_date
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': 'Login failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(LoginRequiredMixin, UpdateView):
    """User profile management view"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        track_user_activity(self.request.user, 'profile_update', self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user statistics
        stats = UserAnalyticsService.get_user_stats(user)
        
        # Get API keys
        api_keys = UserApiKey.objects.filter(user=user, is_active=True)
        
        context.update({
            'user_stats': stats,
            'api_keys': api_keys,
            'subscription_info': {
                'tier': user.subscription_tier,
                'api_limit': user.get_api_limit(),
                'requests_used': user.api_requests_count,
                'can_upgrade': user.subscription_tier != 'enterprise'
            },
            'social_accounts': SocialAccount.objects.filter(user=user),
            'recent_activity': UserAnalyticsService.get_recent_activity(user)
        })
        return context


class SubscriptionManagementView(LoginRequiredMixin, DetailView):
    """Subscription and billing management"""
    model = User
    template_name = 'accounts/subscription.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context.update({
            'subscription_plans': [
                {
                    'name': 'Free',
                    'price': 0,
                    'api_limit': 100,
                    'features': ['Basic AI Access', 'Community Support'],
                    'current': user.subscription_tier == 'free'
                },
                {
                    'name': 'Basic',
                    'price': 29,
                    'api_limit': 1000,
                    'features': ['All AI Agents', 'Email Support', 'API Access'],
                    'current': user.subscription_tier == 'basic'
                },
                {
                    'name': 'Pro',
                    'price': 99,
                    'api_limit': 10000,
                    'features': ['Priority Support', 'Advanced Features', 'Analytics'],
                    'current': user.subscription_tier == 'pro'
                },
                {
                    'name': 'Enterprise',
                    'price': 299,
                    'api_limit': 100000,
                    'features': ['Custom Solutions', '24/7 Support', 'White-label'],
                    'current': user.subscription_tier == 'enterprise'
                }
            ],
            'billing_history': SubscriptionService.get_billing_history(user),
            'next_billing_date': user.subscription_end_date,
            'usage_stats': UserAnalyticsService.get_usage_stats(user)
        })
        return context


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_api_key_view(request):
    """Generate new API key for user"""
    try:
        name = request.data.get('name', f'API Key {timezone.now().strftime("%Y-%m-%d")}')
        
        # Check if user can create more API keys
        existing_keys = UserApiKey.objects.filter(user=request.user, is_active=True).count()
        max_keys = 5 if request.user.subscription_tier == 'enterprise' else 3
        
        if existing_keys >= max_keys:
            return Response(
                {'error': f'Maximum {max_keys} API keys allowed for your plan'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        api_key = generate_api_key(request.user, name)
        
        return Response({
            'api_key': api_key.key,
            'name': api_key.name,
            'created_at': api_key.created_at,
            'message': 'API key generated successfully. Please save it securely.'
        })
        
    except Exception as e:
        logger.error(f"API key generation error: {str(e)}")
        return Response(
            {'error': 'Failed to generate API key'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def revoke_api_key_view(request, key_id):
    """Revoke API key"""
    try:
        api_key = get_object_or_404(
            UserApiKey, 
            id=key_id, 
            user=request.user, 
            is_active=True
        )
        
        api_key.is_active = False
        api_key.revoked_at = timezone.now()
        api_key.save()
        
        return Response({'message': 'API key revoked successfully'})
        
    except Exception as e:
        logger.error(f"API key revocation error: {str(e)}")
        return Response(
            {'error': 'Failed to revoke API key'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class GoogleLogin(SocialLoginView):
    """Google OAuth2 login"""
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH2_CALLBACK_URL
    client_class = OAuth2Client


class GitHubLogin(SocialLoginView):
    """GitHub OAuth2 login"""
    adapter_class = GitHubOAuth2Adapter
    callback_url = settings.GITHUB_CALLBACK_URL
    client_class = OAuth2Client


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def account_deactivation_view(request):
    """Account deactivation with confirmation"""
    try:
        password = request.data.get('password')
        reason = request.data.get('reason', '')
        
        if not password:
            return Response(
                {'error': 'Password confirmation required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        if not user.check_password(password):
            return Response(
                {'error': 'Invalid password'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Deactivate account
        user.is_active = False
        user.deactivated_at = timezone.now()
        user.deactivation_reason = reason
        user.save()
        
        # Revoke all API keys
        UserApiKey.objects.filter(user=user, is_active=True).update(
            is_active=False,
            revoked_at=timezone.now()
        )
        
        # Track deactivation
        UserAnalyticsService.track_deactivation(user, reason)
        
        return Response({'message': 'Account deactivated successfully'})
        
    except Exception as e:
        logger.error(f"Account deactivation error: {str(e)}")
        return Response(
            {'error': 'Failed to deactivate account'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_data(request):
    """Get dashboard data for authenticated user"""
    try:
        user = request.user
        
        # Get user statistics
        stats = UserAnalyticsService.get_dashboard_stats(user)
        
        # Get recent conversations
        from agents.models import AgentConversation
        recent_conversations = AgentConversation.objects.filter(
            user=user
        ).select_related('agent').order_by('-created_at')[:10]
        
        dashboard_data = {
            'user': UserSerializer(user).data,
            'stats': stats,
            'recent_conversations': [
                {
                    'id': conv.id,
                    'agent_name': conv.agent.name,
                    'title': conv.title[:50],
                    'created_at': conv.created_at,
                    'message_count': conv.messages.count()
                }
                for conv in recent_conversations
            ],
            'subscription': {
                'tier': user.subscription_tier,
                'api_limit': user.get_api_limit(),
                'requests_used': user.api_requests_count,
                'reset_date': user.api_limit_reset_date
            },
            'quick_actions': [
                {'name': 'Start Chat', 'url': '/chat/', 'icon': 'chat'},
                {'name': 'View Agents', 'url': '/agents/', 'icon': 'robot'},
                {'name': 'API Keys', 'url': '/accounts/api-keys/', 'icon': 'key'},
                {'name': 'Subscription', 'url': '/accounts/subscription/', 'icon': 'credit-card'}
            ]
        }
        
        return Response(dashboard_data)
        
    except Exception as e:
        logger.error(f"Dashboard data error: {str(e)}")
        return Response(
            {'error': 'Failed to load dashboard data'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@require_http_methods(["GET"])
def registration_success_view(request):
    """Registration success page"""
    return render(request, 'accounts/registration_success.html', {
        'page_title': 'Welcome to OneLastAI!',
        'next_steps': [
            'Check your email for verification link',
            'Complete your profile setup',
            'Explore our AI agents',
            'Join the community'
        ]
    })


@login_required
def account_settings_view(request):
    """Account settings page"""
    user = request.user
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account settings updated successfully!')
            return redirect('accounts:settings')
    else:
        form = CustomUserChangeForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'page_title': 'Account Settings',
        'security_settings': {
            'two_factor_enabled': False,  # Will implement 2FA later
            'last_password_change': user.password_changed_at,
            'login_attempts': UserAnalyticsService.get_login_attempts(user)
        }
    }
    
    return render(request, 'accounts/settings.html', context)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Enhanced logout with token blacklisting"""
    try:
        refresh_token = request.data.get('refresh_token')
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                logger.warning(f"Token blacklist error: {str(e)}")
        
        # Track logout
        track_user_activity(request.user, 'logout', request)
        
        return Response({'message': 'Logged out successfully'})
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response(
            {'error': 'Logout failed'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
