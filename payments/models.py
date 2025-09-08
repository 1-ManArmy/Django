"""
OneLastAI Platform - Payment Models
Advanced payment processing models supporting multiple gateways and subscription management
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from datetime import timedelta

User = get_user_model()


class PaymentGateway(models.Model):
    """Payment gateway configuration"""
    
    GATEWAY_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('razorpay', 'Razorpay'),
        ('square', 'Square'),
        ('braintree', 'Braintree'),
    ]
    
    name = models.CharField(max_length=50, choices=GATEWAY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_test_mode = models.BooleanField(default=True)
    
    # Configuration (stored as JSON in production, use separate fields for simplicity)
    api_key = models.CharField(max_length=255, blank=True)
    secret_key = models.CharField(max_length=255, blank=True)
    webhook_secret = models.CharField(max_length=255, blank=True)
    
    # Settings
    supports_subscriptions = models.BooleanField(default=True)
    supports_one_time = models.BooleanField(default=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_gateways'
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateways'
    
    def __str__(self):
        return f"{self.display_name} ({'Test' if self.is_test_mode else 'Live'})"


class SubscriptionPlan(models.Model):
    """Subscription plans available to users"""
    
    BILLING_CYCLES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
        ('lifetime', 'Lifetime'),
    ]
    
    PLAN_TYPES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    
    # Features & Limits
    api_requests_limit = models.IntegerField(default=100)
    agents_access = models.JSONField(default=list)  # List of agent IDs/types
    max_conversations = models.IntegerField(default=10)
    max_api_keys = models.IntegerField(default=1)
    
    # Features flags
    voice_agents_enabled = models.BooleanField(default=False)
    image_generation_enabled = models.BooleanField(default=False)
    video_generation_enabled = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    custom_branding = models.BooleanField(default=False)
    analytics_access = models.BooleanField(default=False)
    
    # Gateway Integration
    stripe_price_id = models.CharField(max_length=255, blank=True)
    paypal_plan_id = models.CharField(max_length=255, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    # Metadata
    description = models.TextField(blank=True)
    features_list = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['sort_order', 'price']
        unique_together = ['plan_type', 'billing_cycle']
    
    def __str__(self):
        return f"{self.name} ({self.get_billing_cycle_display()})"
    
    @property
    def monthly_price(self):
        """Calculate monthly equivalent price"""
        if self.billing_cycle == 'monthly':
            return self.price
        elif self.billing_cycle == 'quarterly':
            return self.price / 3
        elif self.billing_cycle == 'annually':
            return self.price / 12
        else:
            return 0  # Lifetime


class UserSubscription(models.Model):
    """User subscription instances"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
        ('past_due', 'Past Due'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    
    # Subscription Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    canceled_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Gateway Integration
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    gateway_subscription_id = models.CharField(max_length=255, blank=True)
    gateway_customer_id = models.CharField(max_length=255, blank=True)
    
    # Usage Tracking
    api_requests_used = models.IntegerField(default=0)
    last_usage_reset = models.DateTimeField(auto_now_add=True)
    
    # Billing
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    next_billing_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_subscriptions'
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"
    
    def is_active(self):
        """Check if subscription is currently active"""
        return (
            self.status == 'active' and 
            timezone.now() <= self.current_period_end
        )
    
    def days_remaining(self):
        """Get days remaining in current period"""
        if self.current_period_end:
            delta = self.current_period_end - timezone.now()
            return max(0, delta.days)
        return 0
    
    def usage_percentage(self):
        """Get API usage percentage for current period"""
        if self.plan.api_requests_limit > 0:
            return min(100, (self.api_requests_used / self.plan.api_requests_limit) * 100)
        return 0
    
    def can_use_api(self):
        """Check if user can make API requests"""
        return (
            self.is_active() and 
            self.api_requests_used < self.plan.api_requests_limit
        )
    
    def reset_usage(self):
        """Reset usage counters for new billing period"""
        self.api_requests_used = 0
        self.last_usage_reset = timezone.now()
        self.save(update_fields=['api_requests_used', 'last_usage_reset'])


class Payment(models.Model):
    """Individual payment records"""
    
    PAYMENT_TYPES = [
        ('subscription', 'Subscription'),
        ('one_time', 'One-time'),
        ('upgrade', 'Upgrade'),
        ('addon', 'Add-on'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, null=True, blank=True)
    
    # Payment Details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Gateway Details
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    gateway_payment_id = models.CharField(max_length=255, blank=True)
    gateway_transaction_id = models.CharField(max_length=255, blank=True)
    
    # Payment Method
    payment_method_type = models.CharField(max_length=50, blank=True)  # card, bank, wallet
    last_four = models.CharField(max_length=4, blank=True)  # Last 4 digits of card
    brand = models.CharField(max_length=50, blank=True)  # visa, mastercard, etc.
    
    # Timestamps
    attempted_at = models.DateTimeField(null=True, blank=True)
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_code = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    
    # Refunds
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.CharField(max_length=255, blank=True)
    
    # Metadata
    description = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['gateway_payment_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.email} - ${self.amount}"
    
    def is_successful(self):
        return self.status == 'succeeded'
    
    def can_refund(self):
        return self.status == 'succeeded' and self.refunded_amount < self.amount
    
    def refundable_amount(self):
        return self.amount - self.refunded_amount


class Invoice(models.Model):
    """Invoice generation and tracking"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('uncollectible', 'Uncollectible'),
        ('void', 'Void'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, null=True, blank=True)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, null=True, blank=True)
    
    # Invoice Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Dates
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    
    # Gateway Integration
    gateway_invoice_id = models.CharField(max_length=255, blank=True)
    
    # PDF Storage
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.user.email}"
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        if not self.invoice_number:
            prefix = f"OLA-{timezone.now().strftime('%Y%m')}"
            count = Invoice.objects.filter(
                invoice_number__startswith=prefix
            ).count() + 1
            self.invoice_number = f"{prefix}-{count:04d}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.generate_invoice_number()
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """Individual items on an invoice"""
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'invoice_items'
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'
    
    def __str__(self):
        return f"{self.description} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class PaymentMethod(models.Model):
    """Stored payment methods for users"""
    
    METHOD_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('bank_account', 'Bank Account'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    
    # Method Details
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    is_default = models.BooleanField(default=False)
    
    # Gateway Integration
    gateway_method_id = models.CharField(max_length=255)
    
    # Card Details (for display)
    brand = models.CharField(max_length=50, blank=True)
    last_four = models.CharField(max_length=4, blank=True)
    exp_month = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)])
    exp_year = models.IntegerField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_methods'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.method_type == 'card':
            return f"**** **** **** {self.last_four} ({self.brand})"
        return f"{self.get_method_type_display()}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default payment method per user
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class DiscountCoupon(models.Model):
    """Discount coupons and promotional codes"""
    
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
    ]
    
    APPLIES_TO = [
        ('all', 'All Plans'),
        ('specific_plans', 'Specific Plans'),
        ('first_payment', 'First Payment Only'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Discount Details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    applies_to = models.CharField(max_length=20, choices=APPLIES_TO, default='all')
    applicable_plans = models.ManyToManyField(SubscriptionPlan, blank=True)
    
    # Usage Limits
    max_uses = models.IntegerField(null=True, blank=True)
    max_uses_per_user = models.IntegerField(default=1)
    current_uses = models.IntegerField(default=0)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'discount_coupons'
        verbose_name = 'Discount Coupon'
        verbose_name_plural = 'Discount Coupons'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def is_valid(self, user=None, plan=None):
        """Check if coupon is valid for use"""
        now = timezone.now()
        
        # Basic validity checks
        if not self.is_active:
            return False, "Coupon is not active"
        
        if now < self.valid_from:
            return False, "Coupon is not yet valid"
        
        if self.valid_until and now > self.valid_until:
            return False, "Coupon has expired"
        
        if self.max_uses and self.current_uses >= self.max_uses:
            return False, "Coupon usage limit reached"
        
        # User-specific checks
        if user:
            user_uses = CouponUsage.objects.filter(
                coupon=self, 
                user=user
            ).count()
            
            if user_uses >= self.max_uses_per_user:
                return False, "You have already used this coupon"
        
        # Plan-specific checks
        if plan and self.applies_to == 'specific_plans':
            if not self.applicable_plans.filter(id=plan.id).exists():
                return False, "Coupon not applicable to this plan"
        
        return True, "Coupon is valid"
    
    def calculate_discount(self, amount):
        """Calculate discount amount"""
        if self.discount_type == 'percentage':
            return min(amount, amount * (self.discount_value / 100))
        else:  # fixed_amount
            return min(amount, self.discount_value)


class CouponUsage(models.Model):
    """Track coupon usage by users"""
    
    coupon = models.ForeignKey(DiscountCoupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'coupon_usages'
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'
        unique_together = ['coupon', 'user', 'payment']
    
    def __str__(self):
        return f"{self.user.email} used {self.coupon.code}"


class WebhookEvent(models.Model):
    """Webhook events from payment gateways"""
    
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    event_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=100)
    
    # Processing status
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Event data
    data = models.JSONField()
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'webhook_events'
        verbose_name = 'Webhook Event'
        verbose_name_plural = 'Webhook Events'
        ordering = ['-created_at']
        unique_together = ['gateway', 'event_id']
    
    def __str__(self):
        return f"{self.gateway.name} - {self.event_type} ({self.event_id})"
