"""
OneLastAI Platform - Payment Forms
Django forms for payment system UI
"""
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from .models import (
    SubscriptionPlan, UserSubscription, PaymentMethod, 
    DiscountCoupon, Invoice, Payment
)
from .services import SubscriptionService, PaymentService

User = get_user_model()


class CreditCardWidget(forms.TextInput):
    """Custom widget for credit card input"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control cc-input',
            'autocomplete': 'cc-number',
            'data-mask': '0000 0000 0000 0000',
            'maxlength': '19',
            'placeholder': '1234 5678 9012 3456'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class ExpiryWidget(forms.TextInput):
    """Custom widget for expiry date input"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control expiry-input',
            'data-mask': '00/00',
            'maxlength': '5',
            'placeholder': 'MM/YY'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class CVCWidget(forms.TextInput):
    """Custom widget for CVC input"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control cvc-input',
            'autocomplete': 'cc-csc',
            'maxlength': '4',
            'placeholder': '123'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class SubscriptionPlanForm(forms.ModelForm):
    """Form for creating/editing subscription plans"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'name', 'plan_type', 'billing_cycle', 'price', 'currency',
            'api_requests_limit', 'max_conversations', 'max_api_keys',
            'voice_agents_enabled', 'image_generation_enabled', 
            'video_generation_enabled', 'priority_support', 
            'custom_branding', 'analytics_access', 'description',
            'features_list', 'is_featured', 'is_active'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_type': forms.Select(attrs={'class': 'form-control'}),
            'billing_cycle': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 3}),
            'api_requests_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_conversations': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_api_keys': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'features_list': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 6,
                'placeholder': 'Enter features separated by new lines'
            }),
            'voice_agents_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image_generation_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'video_generation_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'priority_support': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'custom_branding': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'analytics_access': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_price(self):
        """Validate price"""
        price = self.cleaned_data.get('price')
        if price is not None:
            if price < 0:
                raise ValidationError("Price cannot be negative")
            if price > 10000:
                raise ValidationError("Price cannot exceed $10,000")
        return price
    
    def clean_currency(self):
        """Validate currency"""
        currency = self.cleaned_data.get('currency', '').upper()
        supported_currencies = ['USD', 'EUR', 'GBP']
        if currency and currency not in supported_currencies:
            raise ValidationError(f"Currency must be one of: {', '.join(supported_currencies)}")
        return currency


class SubscriptionSignupForm(forms.Form):
    """Form for subscription signup"""
    
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        widget=forms.RadioSelect(attrs={'class': 'plan-selector'}),
        empty_label=None
    )
    
    # Payment information
    card_number = forms.CharField(
        max_length=19,
        widget=CreditCardWidget(),
        label='Card Number'
    )
    
    expiry_date = forms.CharField(
        max_length=5,
        widget=ExpiryWidget(),
        label='Expiry Date'
    )
    
    cvc = forms.CharField(
        max_length=4,
        widget=CVCWidget(),
        label='CVC'
    )
    
    # Billing information
    billing_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Cardholder Name'
    )
    
    billing_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Billing Email'
    )
    
    billing_address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Address'
    )
    
    billing_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='City'
    )
    
    billing_state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='State/Province'
    )
    
    billing_postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Postal Code'
    )
    
    billing_country = forms.CharField(
        max_length=2,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2}),
        label='Country Code (e.g., US, CA, GB)'
    )
    
    # Optional coupon
    coupon_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code (optional)'
        }),
        label='Coupon Code'
    )
    
    # Terms acceptance
    accept_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I accept the Terms of Service and Privacy Policy'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill email if user is provided
        if self.user and self.user.is_authenticated:
            self.fields['billing_email'].initial = self.user.email
            self.fields['billing_name'].initial = self.user.get_full_name()
    
    def clean_card_number(self):
        """Clean and validate card number"""
        card_number = self.cleaned_data.get('card_number', '').replace(' ', '')
        
        if not card_number.isdigit():
            raise ValidationError("Card number must contain only digits")
        
        if len(card_number) < 13 or len(card_number) > 19:
            raise ValidationError("Invalid card number length")
        
        # Simple Luhn algorithm check
        def luhn_check(card_num):
            digits = [int(d) for d in card_num]
            for i in range(len(digits) - 2, -1, -2):
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            return sum(digits) % 10 == 0
        
        if not luhn_check(card_number):
            raise ValidationError("Invalid card number")
        
        return card_number
    
    def clean_expiry_date(self):
        """Clean and validate expiry date"""
        expiry = self.cleaned_data.get('expiry_date', '')
        
        if '/' not in expiry or len(expiry) != 5:
            raise ValidationError("Expiry date must be in MM/YY format")
        
        month_str, year_str = expiry.split('/')
        
        try:
            month = int(month_str)
            year = int(year_str) + 2000  # Convert YY to YYYY
        except ValueError:
            raise ValidationError("Invalid expiry date")
        
        if month < 1 or month > 12:
            raise ValidationError("Invalid month")
        
        # Check if card is expired
        now = timezone.now()
        if year < now.year or (year == now.year and month < now.month):
            raise ValidationError("Card has expired")
        
        return expiry
    
    def clean_cvc(self):
        """Clean and validate CVC"""
        cvc = self.cleaned_data.get('cvc', '')
        
        if not cvc.isdigit():
            raise ValidationError("CVC must contain only digits")
        
        if len(cvc) < 3 or len(cvc) > 4:
            raise ValidationError("CVC must be 3 or 4 digits")
        
        return cvc
    
    def clean_coupon_code(self):
        """Validate coupon code if provided"""
        coupon_code = self.cleaned_data.get('coupon_code', '').strip()
        
        if coupon_code:
            try:
                coupon = DiscountCoupon.objects.get(code=coupon_code, is_active=True)
                is_valid, message = coupon.is_valid(user=self.user)
                if not is_valid:
                    raise ValidationError(message)
            except DiscountCoupon.DoesNotExist:
                raise ValidationError("Invalid coupon code")
        
        return coupon_code
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        
        # Check if user already has active subscription
        if self.user and hasattr(self.user, 'subscriptions'):
            active_subscription = self.user.subscriptions.filter(status='active').first()
            if active_subscription:
                raise ValidationError("You already have an active subscription")
        
        return cleaned_data


class PaymentMethodForm(forms.Form):
    """Form for adding payment methods"""
    
    card_number = forms.CharField(
        max_length=19,
        widget=CreditCardWidget(),
        label='Card Number'
    )
    
    expiry_date = forms.CharField(
        max_length=5,
        widget=ExpiryWidget(),
        label='Expiry Date'
    )
    
    cvc = forms.CharField(
        max_length=4,
        widget=CVCWidget(),
        label='CVC'
    )
    
    cardholder_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Cardholder Name'
    )
    
    is_default = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Make this my default payment method'
    )
    
    def clean_card_number(self):
        """Clean and validate card number - reuse from SubscriptionSignupForm"""
        card_number = self.cleaned_data.get('card_number', '').replace(' ', '')
        
        if not card_number.isdigit():
            raise ValidationError("Card number must contain only digits")
        
        if len(card_number) < 13 or len(card_number) > 19:
            raise ValidationError("Invalid card number length")
        
        return card_number
    
    def clean_expiry_date(self):
        """Clean and validate expiry date - reuse from SubscriptionSignupForm"""
        expiry = self.cleaned_data.get('expiry_date', '')
        
        if '/' not in expiry or len(expiry) != 5:
            raise ValidationError("Expiry date must be in MM/YY format")
        
        month_str, year_str = expiry.split('/')
        
        try:
            month = int(month_str)
            year = int(year_str) + 2000
        except ValueError:
            raise ValidationError("Invalid expiry date")
        
        if month < 1 or month > 12:
            raise ValidationError("Invalid month")
        
        now = timezone.now()
        if year < now.year or (year == now.year and month < now.month):
            raise ValidationError("Card has expired")
        
        return expiry


class OneTimePaymentForm(forms.Form):
    """Form for one-time payments"""
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        }),
        label='Amount'
    )
    
    currency = forms.ChoiceField(
        choices=[('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='USD',
        label='Currency'
    )
    
    description = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Payment description (optional)'
        }),
        label='Description'
    )
    
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.none(),  # Will be set in __init__
        widget=forms.RadioSelect(attrs={'class': 'payment-method-selector'}),
        label='Payment Method'
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set payment methods for the user
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(
            user=user,
            is_active=True
        )
    
    def clean_amount(self):
        """Validate payment amount"""
        amount = self.cleaned_data.get('amount')
        
        if amount and amount > Decimal('10000.00'):
            raise ValidationError("Payment amount cannot exceed $10,000")
        
        return amount


class DiscountCouponForm(forms.ModelForm):
    """Form for creating/editing discount coupons"""
    
    class Meta:
        model = DiscountCoupon
        fields = [
            'code', 'name', 'description', 'discount_type', 'discount_value',
            'applies_to', 'max_uses', 'max_uses_per_user', 'valid_from',
            'valid_until', 'is_active'
        ]
        
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'discount_type': forms.Select(attrs={'class': 'form-control'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'applies_to': forms.Select(attrs={'class': 'form-control'}),
            'max_uses': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_uses_per_user': forms.NumberInput(attrs={'class': 'form-control'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_code(self):
        """Validate coupon code"""
        code = self.cleaned_data.get('code', '').upper()
        
        if len(code) < 3:
            raise ValidationError("Coupon code must be at least 3 characters long")
        
        # Check for existing coupon (excluding current instance)
        existing = DiscountCoupon.objects.filter(code=code)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise ValidationError("A coupon with this code already exists")
        
        return code
    
    def clean_discount_value(self):
        """Validate discount value based on type"""
        discount_type = self.cleaned_data.get('discount_type')
        discount_value = self.cleaned_data.get('discount_value')
        
        if discount_value is not None:
            if discount_value <= 0:
                raise ValidationError("Discount value must be positive")
            
            if discount_type == 'percentage' and discount_value > 100:
                raise ValidationError("Percentage discount cannot exceed 100%")
            
            if discount_type == 'fixed_amount' and discount_value > 1000:
                raise ValidationError("Fixed discount cannot exceed $1,000")
        
        return discount_value
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        
        valid_from = cleaned_data.get('valid_from')
        valid_until = cleaned_data.get('valid_until')
        
        if valid_from and valid_until:
            if valid_from >= valid_until:
                raise ValidationError("Valid until date must be after valid from date")
        
        return cleaned_data


class CouponValidationForm(forms.Form):
    """Simple form for coupon code validation"""
    
    coupon_code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code'
        }),
        label='Coupon Code'
    )
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_coupon_code(self):
        """Validate coupon code"""
        code = self.cleaned_data.get('coupon_code', '').strip().upper()
        
        try:
            coupon = DiscountCoupon.objects.get(code=code, is_active=True)
            is_valid, message = coupon.is_valid(user=self.user)
            if not is_valid:
                raise ValidationError(message)
            
            # Store the coupon object for later use
            self.coupon = coupon
            
        except DiscountCoupon.DoesNotExist:
            raise ValidationError("Invalid coupon code")
        
        return code


class InvoiceSearchForm(forms.Form):
    """Form for searching invoices"""
    
    STATUS_CHOICES = [('', 'All')] + Invoice.STATUS_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Status'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='From Date'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='To Date'
    )
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search invoices...'
        }),
        label='Search'
    )
    
    def clean(self):
        """Validate date range"""
        cleaned_data = super().clean()
        
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to:
            if date_from > date_to:
                raise ValidationError("From date cannot be after to date")
        
        return cleaned_data
