"""
OneLastAI Platform - Authentication URLs
URL patterns for all authentication-related views and endpoints
"""
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = 'accounts'

# API Router for ViewSets (if needed in the future)
router = DefaultRouter()
# router.register(r'profile', UserProfileViewSet)

urlpatterns = [
    # API Authentication Endpoints
    path('api/auth/login/', views.CustomTokenObtainPairView.as_view(), name='api_login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('api/auth/logout/', views.logout_view, name='api_logout'),
    path('api/auth/register/', views.UserRegistrationView.as_view(), name='api_register'),
    
    # User Management API
    path('api/user/profile/', views.UserProfileView.as_view(), name='api_user_profile'),
    path('api/user/dashboard/', views.user_dashboard_data, name='api_dashboard'),
    path('api/user/subscription/', views.SubscriptionManagementView.as_view(), name='api_subscription'),
    path('api/user/deactivate/', views.account_deactivation_view, name='api_deactivate'),
    
    # API Key Management
    path('api/keys/', views.generate_api_key_view, name='api_key_generate'),
    path('api/keys/<int:key_id>/revoke/', views.revoke_api_key_view, name='api_key_revoke'),
    
    # Social Authentication
    path('api/auth/google/', views.GoogleLogin.as_view(), name='google_login'),
    path('api/auth/github/', views.GitHubLogin.as_view(), name='github_login'),
    
    # Web Views (Traditional Django)
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True,
        extra_context={
            'page_title': 'Sign In to OneLastAI',
            'show_social_login': True
        }
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='accounts:login'
    ), name='logout'),
    
    # Profile Management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('settings/', views.account_settings_view, name='settings'),
    path('subscription/', views.SubscriptionManagementView.as_view(), name='subscription'),
    
    # Password Management
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/accounts/password/change/done/',
        extra_context={'page_title': 'Change Password'}
    ), name='password_change'),
    
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html',
        extra_context={'page_title': 'Password Changed'}
    ), name='password_change_done'),
    
    path('password/reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='emails/password_reset_email.html',
        html_email_template_name='emails/password_reset_email.html',
        success_url='/accounts/password/reset/done/',
        extra_context={'page_title': 'Reset Password'}
    ), name='password_reset'),
    
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
        extra_context={'page_title': 'Password Reset Sent'}
    ), name='password_reset_done'),
    
    path('password/reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/password/reset/complete/',
        extra_context={'page_title': 'Confirm Password Reset'}
    ), name='password_reset_confirm'),
    
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
        extra_context={'page_title': 'Password Reset Complete'}
    ), name='password_reset_complete'),
    
    # Email Management
    path('email/verify/<str:token>/', views.UserLoginView.as_view(), name='verify_email'),  # Placeholder
    path('email/change/<str:token>/', views.UserLoginView.as_view(), name='verify_email_change'),  # Placeholder
    
    # Registration Flow
    path('registration/success/', views.registration_success_view, name='registration_success'),
    
    # Account Management
    path('deactivate/', views.account_deactivation_view, name='deactivate'),
    
    # Include allauth URLs for social authentication
    path('social/', include('allauth.urls')),
    
    # Include router URLs
    path('api/', include(router.urls)),
]

# Additional patterns for development/testing
if hasattr(settings, 'DEBUG') and settings.DEBUG:
    urlpatterns += [
        # Debug/testing endpoints
        path('debug/user-info/', views.user_dashboard_data, name='debug_user_info'),
    ]
