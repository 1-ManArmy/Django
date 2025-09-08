"""
OneLastAI Platform - Payment Serializers
API serializers for payment system models
"""
from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone

from .models import (
    SubscriptionPlan, UserSubscription, Payment, Invoice, 
    InvoiceItem, PaymentMethod, DiscountCoupon, PaymentGateway
)


class PaymentGatewaySerializer(serializers.ModelSerializer):
    """Serializer for payment gateways"""
    
    class Meta:
        model = PaymentGateway
        fields = [
            'name', 'display_name', 'is_active', 'supports_subscriptions',
            'supports_one_time', 'currency'
        ]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""
    
    billing_cycle_display = serializers.CharField(source='get_billing_cycle_display', read_only=True)
    plan_type_display = serializers.CharField(source='get_plan_type_display', read_only=True)
    monthly_price = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'plan_type_display', 'billing_cycle', 
            'billing_cycle_display', 'price', 'monthly_price', 'currency',
            'api_requests_limit', 'max_conversations', 'max_api_keys',
            'voice_agents_enabled', 'image_generation_enabled', 
            'video_generation_enabled', 'priority_support', 'custom_branding',
            'analytics_access', 'description', 'features_list', 'is_featured'
        ]
    
    def get_monthly_price(self, obj):
        """Get monthly equivalent price"""
        return float(obj.monthly_price)


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions"""
    
    plan = SubscriptionPlanSerializer(read_only=True)
    gateway = PaymentGatewaySerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    usage_percentage = serializers.SerializerMethodField()
    can_use_api = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'plan', 'gateway', 'status', 'status_display', 'started_at',
            'current_period_start', 'current_period_end', 'canceled_at', 'ended_at',
            'amount', 'currency', 'next_billing_date', 'api_requests_used',
            'last_usage_reset', 'is_active', 'days_remaining', 'usage_percentage',
            'can_use_api', 'gateway_subscription_id'
        ]
        read_only_fields = [
            'id', 'started_at', 'gateway_subscription_id', 'gateway_customer_id'
        ]
    
    def get_is_active(self, obj):
        return obj.is_active()
    
    def get_days_remaining(self, obj):
        return obj.days_remaining()
    
    def get_usage_percentage(self, obj):
        return obj.usage_percentage()
    
    def get_can_use_api(self, obj):
        return obj.can_use_api()


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""
    
    gateway = PaymentGatewaySerializer(read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_successful = serializers.SerializerMethodField()
    can_refund = serializers.SerializerMethodField()
    refundable_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_type', 'payment_type_display', 'status', 'status_display',
            'amount', 'currency', 'gateway', 'payment_method_type', 'last_four',
            'brand', 'attempted_at', 'succeeded_at', 'failed_at', 'error_code',
            'error_message', 'refunded_amount', 'refund_reason', 'description',
            'created_at', 'is_successful', 'can_refund', 'refundable_amount'
        ]
        read_only_fields = [
            'id', 'gateway_payment_id', 'gateway_transaction_id', 'created_at',
            'updated_at'
        ]
    
    def get_is_successful(self, obj):
        return obj.is_successful()
    
    def get_can_refund(self, obj):
        return obj.can_refund()
    
    def get_refundable_amount(self, obj):
        return float(obj.refundable_amount())


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice items"""
    
    class Meta:
        model = InvoiceItem
        fields = [
            'description', 'quantity', 'unit_price', 'total_price', 'metadata'
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices"""
    
    items = InvoiceItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'status', 'status_display', 'subtotal',
            'tax_amount', 'discount_amount', 'total', 'currency', 'issue_date',
            'due_date', 'paid_date', 'items', 'payment', 'notes', 'created_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'gateway_invoice_id', 'created_at', 'updated_at'
        ]


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods"""
    
    gateway = PaymentGatewaySerializer(read_only=True)
    method_type_display = serializers.CharField(source='get_method_type_display', read_only=True)
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'gateway', 'method_type', 'method_type_display', 'is_default',
            'brand', 'last_four', 'exp_month', 'exp_year', 'is_active',
            'verified', 'created_at', 'display_name'
        ]
        read_only_fields = [
            'id', 'gateway_method_id', 'created_at', 'updated_at'
        ]
    
    def get_display_name(self, obj):
        return str(obj)


class DiscountCouponSerializer(serializers.ModelSerializer):
    """Serializer for discount coupons"""
    
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)
    applies_to_display = serializers.CharField(source='get_applies_to_display', read_only=True)
    is_valid_now = serializers.SerializerMethodField()
    usage_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = DiscountCoupon
        fields = [
            'id', 'code', 'name', 'description', 'discount_type', 'discount_type_display',
            'discount_value', 'applies_to', 'applies_to_display', 'max_uses',
            'max_uses_per_user', 'current_uses', 'valid_from', 'valid_until',
            'is_active', 'is_valid_now', 'usage_stats', 'created_at'
        ]
        read_only_fields = ['id', 'current_uses', 'created_at', 'updated_at']
    
    def get_is_valid_now(self, obj):
        is_valid, _ = obj.is_valid()
        return is_valid
    
    def get_usage_stats(self, obj):
        return {
            'total_uses': obj.current_uses,
            'remaining_uses': (obj.max_uses - obj.current_uses) if obj.max_uses else None,
            'usage_percentage': (obj.current_uses / obj.max_uses * 100) if obj.max_uses else 0
        }


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating payments"""
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    currency = serializers.CharField(max_length=3, default='USD')
    description = serializers.CharField(max_length=255, required=False)
    payment_method_id = serializers.CharField(max_length=255)
    gateway = serializers.CharField(max_length=50, default='stripe')
    
    def validate_amount(self, value):
        """Validate payment amount"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        
        if value > 10000:  # $10,000 limit
            raise serializers.ValidationError("Amount exceeds maximum limit")
        
        return value
    
    def validate_currency(self, value):
        """Validate currency code"""
        supported_currencies = ['USD', 'EUR', 'GBP']
        if value.upper() not in supported_currencies:
            raise serializers.ValidationError(f"Currency not supported. Supported: {supported_currencies}")
        
        return value.upper()


class SubscriptionCreateSerializer(serializers.Serializer):
    """Serializer for creating subscriptions"""
    
    plan_id = serializers.UUIDField()
    payment_method_token = serializers.CharField(max_length=255)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    gateway = serializers.CharField(max_length=50, default='stripe')
    
    def validate_plan_id(self, value):
        """Validate plan exists and is active"""
        try:
            plan = SubscriptionPlan.objects.get(id=value, is_active=True)
            return value
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive subscription plan")
    
    def validate_coupon_code(self, value):
        """Validate coupon code if provided"""
        if value:
            try:
                coupon = DiscountCoupon.objects.get(code=value, is_active=True)
                is_valid, message = coupon.is_valid()
                if not is_valid:
                    raise serializers.ValidationError(message)
            except DiscountCoupon.DoesNotExist:
                raise serializers.ValidationError("Invalid coupon code")
        
        return value


class CouponValidationSerializer(serializers.Serializer):
    """Serializer for validating coupon codes"""
    
    coupon_code = serializers.CharField(max_length=50)
    plan_id = serializers.UUIDField(required=False)
    
    def validate_coupon_code(self, value):
        """Check if coupon exists"""
        try:
            DiscountCoupon.objects.get(code=value, is_active=True)
            return value
        except DiscountCoupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code")


class PaymentMethodCreateSerializer(serializers.Serializer):
    """Serializer for creating payment methods"""
    
    payment_token = serializers.CharField(max_length=255)
    gateway = serializers.CharField(max_length=50, default='stripe')
    is_default = serializers.BooleanField(default=False)
    
    def validate_gateway(self, value):
        """Validate gateway is supported"""
        supported_gateways = ['stripe', 'paypal']
        if value not in supported_gateways:
            raise serializers.ValidationError(f"Unsupported gateway. Supported: {supported_gateways}")
        
        return value


class SubscriptionUpgradeSerializer(serializers.Serializer):
    """Serializer for subscription upgrades"""
    
    new_plan_id = serializers.UUIDField()
    
    def validate_new_plan_id(self, value):
        """Validate new plan exists and is active"""
        try:
            SubscriptionPlan.objects.get(id=value, is_active=True)
            return value
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid subscription plan")
    
    def validate(self, attrs):
        """Validate upgrade is valid"""
        user = self.context['request'].user
        
        # Check current subscription
        current_subscription = UserSubscription.objects.filter(
            user=user,
            status='active'
        ).first()
        
        if not current_subscription:
            raise serializers.ValidationError("No active subscription found")
        
        # Check if new plan is higher tier
        new_plan = SubscriptionPlan.objects.get(id=attrs['new_plan_id'])
        if new_plan.price <= current_subscription.plan.price:
            raise serializers.ValidationError("New plan must be higher tier than current plan")
        
        return attrs


class BillingSummarySerializer(serializers.Serializer):
    """Serializer for billing summary data"""
    
    subscription = serializers.DictField()
    payment_stats = serializers.DictField()
    recent_payments = PaymentSerializer(many=True)
    upcoming_invoices = InvoiceSerializer(many=True)


class WebhookEventSerializer(serializers.Serializer):
    """Serializer for webhook event data"""
    
    event_type = serializers.CharField(max_length=100)
    event_id = serializers.CharField(max_length=255)
    gateway = serializers.CharField(max_length=50)
    data = serializers.JSONField()
    
    def validate_gateway(self, value):
        """Validate gateway exists"""
        if not PaymentGateway.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive gateway")
        
        return value
