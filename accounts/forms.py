"""
OneLastAI Platform - Authentication Forms
Modern, secure forms with validation and user experience enhancements
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from allauth.account.forms import SignupForm, LoginForm
import re

from .models import User, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form with additional fields"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'autocomplete': 'given-name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
            'autocomplete': 'family-name'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username'
        })
    )
    
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password'
        })
    )
    
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
    )
    
    terms_agreed = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_("I agree to the Terms of Service and Privacy Policy")
    )
    
    newsletter_signup = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_("Subscribe to OneLastAI newsletter for updates and tips")
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        """Validate email uniqueness and format"""
        email = self.cleaned_data.get('email')
        
        if email:
            email = email.lower().strip()
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                raise ValidationError(_("An account with this email already exists."))
            
            # Additional email validation
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError(_("Please enter a valid email address."))
                
        return email

    def clean_username(self):
        """Validate username format and uniqueness"""
        username = self.cleaned_data.get('username')
        
        if username:
            username = username.lower().strip()
            
            # Check format (alphanumeric, underscore, dash allowed)
            if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                raise ValidationError(
                    _("Username can only contain letters, numbers, underscores, and dashes.")
                )
            
            # Check length
            if len(username) < 3:
                raise ValidationError(_("Username must be at least 3 characters long."))
            
            # Check reserved usernames
            reserved_names = ['admin', 'api', 'www', 'mail', 'support', 'help', 'info']
            if username.lower() in reserved_names:
                raise ValidationError(_("This username is reserved. Please choose another."))
                
        return username

    def clean_password1(self):
        """Enhanced password validation"""
        password = self.cleaned_data.get('password1')
        
        if password:
            # Django's built-in validation
            validate_password(password)
            
            # Additional custom validation
            if len(password) < 8:
                raise ValidationError(_("Password must be at least 8 characters long."))
                
            if not re.search(r'[A-Z]', password):
                raise ValidationError(_("Password must contain at least one uppercase letter."))
                
            if not re.search(r'[a-z]', password):
                raise ValidationError(_("Password must contain at least one lowercase letter."))
                
            if not re.search(r'\d', password):
                raise ValidationError(_("Password must contain at least one number."))
                
        return password

    def save(self, commit=True):
        """Save user with additional fields"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower().strip()
        
        if commit:
            user.save()
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                newsletter_subscribed=self.cleaned_data.get('newsletter_signup', False)
            )
            
        return user


class CustomUserChangeForm(UserChangeForm):
    """Enhanced user update form"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': True  # Email changes require special verification
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password field from change form
        if 'password' in self.fields:
            del self.fields['password']


class UserProfileForm(forms.ModelForm):
    """User profile editing form"""
    
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell us about yourself...',
            'maxlength': 500
        })
    )
    
    location = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, Country'
        })
    )
    
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://your-website.com'
        })
    )
    
    twitter_handle = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '@username'
        })
    )
    
    linkedin_profile = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://linkedin.com/in/username'
        })
    )
    
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    newsletter_subscribed = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    email_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    push_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = UserProfile
        fields = [
            'bio', 'location', 'website', 'twitter_handle', 'linkedin_profile',
            'avatar', 'newsletter_subscribed', 'email_notifications', 'push_notifications'
        ]

    def clean_twitter_handle(self):
        """Validate Twitter handle format"""
        handle = self.cleaned_data.get('twitter_handle')
        
        if handle:
            handle = handle.strip()
            if not handle.startswith('@'):
                handle = '@' + handle
            
            if not re.match(r'^@[A-Za-z0-9_]{1,15}$', handle):
                raise ValidationError(_("Please enter a valid Twitter handle."))
                
        return handle

    def clean_avatar(self):
        """Validate avatar image"""
        avatar = self.cleaned_data.get('avatar')
        
        if avatar:
            # Check file size (max 5MB)
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError(_("Avatar image must be less than 5MB."))
            
            # Check image format
            if not avatar.content_type.startswith('image/'):
                raise ValidationError(_("Please upload a valid image file."))
                
        return avatar


class PasswordChangeForm(forms.Form):
    """Enhanced password change form"""
    
    current_password = forms.CharField(
        label=_("Current Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password'
        })
    )
    
    new_password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    
    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        """Validate current password"""
        password = self.cleaned_data.get('current_password')
        
        if not self.user.check_password(password):
            raise ValidationError(_("Your current password is incorrect."))
            
        return password

    def clean_new_password1(self):
        """Validate new password"""
        password = self.cleaned_data.get('new_password1')
        
        if password:
            validate_password(password, self.user)
            
        return password

    def clean_new_password2(self):
        """Validate password confirmation"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("The two password fields didn't match."))
            
        return password2

    def save(self):
        """Save new password"""
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


class AccountDeactivationForm(forms.Form):
    """Account deactivation form with confirmation"""
    
    password = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password to confirm'
        })
    )
    
    reason = forms.ChoiceField(
        label=_("Reason for Deactivation"),
        choices=[
            ('', 'Select a reason...'),
            ('not_using', 'Not using the service anymore'),
            ('too_expensive', 'Too expensive'),
            ('missing_features', 'Missing features I need'),
            ('found_alternative', 'Found a better alternative'),
            ('privacy_concerns', 'Privacy concerns'),
            ('technical_issues', 'Technical issues'),
            ('other', 'Other')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    feedback = forms.CharField(
        label=_("Additional Feedback (Optional)"),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Help us improve by sharing your feedback...'
        })
    )
    
    confirm_deactivation = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_("I understand that deactivating my account will disable access to all services")
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        """Validate password"""
        password = self.cleaned_data.get('password')
        
        if not self.user.check_password(password):
            raise ValidationError(_("Incorrect password."))
            
        return password


class CustomLoginForm(LoginForm):
    """Enhanced login form with additional features"""
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_("Remember me for 30 days")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Update widget attributes
        self.fields['login'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email or Username',
            'autocomplete': 'username'
        })
        
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })


class CustomSignupForm(SignupForm):
    """Enhanced signup form for allauth"""
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    terms_agreed = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def save(self, request):
        """Save user with additional fields"""
        user = super().save(request)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.save()
        
        # Create profile
        UserProfile.objects.create(user=user)
        
        return user


class APIKeyForm(forms.Form):
    """Form for generating API keys"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'API Key Name (e.g., "Mobile App", "Website")'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Optional description of how this key will be used'
        })
    )

    def clean_name(self):
        """Validate API key name"""
        name = self.cleaned_data.get('name')
        
        if name:
            name = name.strip()
            
            # Check for reasonable length
            if len(name) < 3:
                raise ValidationError(_("API key name must be at least 3 characters long."))
                
        return name
