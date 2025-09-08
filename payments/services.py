"""
OneLastAI Platform - Payment Services
Advanced payment processing services supporting multiple gateways
"""
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
import stripe
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .models import (
    PaymentGateway, SubscriptionPlan, UserSubscription, Payment, 
    Invoice, PaymentMethod, DiscountCoupon, CouponUsage, WebhookEvent
)
from accounts.models import User

logger = logging.getLogger(__name__)


class PaymentGatewayService:
    """Base service for payment gateway operations"""
    
    def __init__(self, gateway_name: str):
        self.gateway = PaymentGateway.objects.get(name=gateway_name, is_active=True)
        self.setup_gateway()
    
    def setup_gateway(self):
        """Setup gateway-specific configuration"""
        raise NotImplementedError
    
    def create_customer(self, user: User) -> str:
        """Create customer in payment gateway"""
        raise NotImplementedError
    
    def create_payment_method(self, user: User, payment_data: Dict) -> str:
        """Create payment method"""
        raise NotImplementedError
    
    def create_subscription(self, user: User, plan: SubscriptionPlan, payment_method_id: str) -> Dict:
        """Create subscription"""
        raise NotImplementedError
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel subscription"""
        raise NotImplementedError
    
    def process_payment(self, amount: Decimal, currency: str, payment_method_id: str, 
                       description: str = None) -> Dict:
        """Process one-time payment"""
        raise NotImplementedError


class StripePaymentService(PaymentGatewayService):
    """Stripe payment gateway service"""
    
    def setup_gateway(self):
        """Setup Stripe configuration"""
        stripe.api_key = self.gateway.secret_key
    
    def create_customer(self, user: User) -> str:
        """Create Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name(),
                metadata={
                    'user_id': user.id,
                    'subscription_tier': user.subscription_tier
                }
            )
            
            logger.info(f"Stripe customer created: {customer.id} for user {user.email}")
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation failed: {str(e)}")
            raise ValidationError(f"Failed to create customer: {str(e)}")
    
    def create_payment_method(self, user: User, payment_data: Dict) -> str:
        """Create Stripe payment method"""
        try:
            payment_method = stripe.PaymentMethod.create(
                type='card',
                card={
                    'token': payment_data.get('token')
                }
            )
            
            # Attach to customer if exists
            if 'customer_id' in payment_data:
                payment_method.attach(customer=payment_data['customer_id'])
            
            return payment_method.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment method creation failed: {str(e)}")
            raise ValidationError(f"Failed to create payment method: {str(e)}")
    
    def create_subscription(self, user: User, plan: SubscriptionPlan, 
                           payment_method_id: str, customer_id: str = None) -> Dict:
        """Create Stripe subscription"""
        try:
            # Create customer if not provided
            if not customer_id:
                customer_id = self.create_customer(user)
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    'price': plan.stripe_price_id,
                }],
                default_payment_method=payment_method_id,
                expand=['latest_invoice.payment_intent'],
                metadata={
                    'user_id': user.id,
                    'plan_id': str(plan.id)
                }
            )
            
            return {
                'subscription_id': subscription.id,
                'customer_id': customer_id,
                'status': subscription.status,
                'current_period_start': datetime.fromtimestamp(subscription.current_period_start),
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end),
                'latest_invoice': subscription.latest_invoice
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe subscription creation failed: {str(e)}")
            raise ValidationError(f"Failed to create subscription: {str(e)}")
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel Stripe subscription"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            logger.info(f"Stripe subscription canceled: {subscription_id}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe subscription cancellation failed: {str(e)}")
            return False
    
    def process_payment(self, amount: Decimal, currency: str, payment_method_id: str,
                       description: str = None, customer_id: str = None) -> Dict:
        """Process Stripe payment"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                payment_method=payment_method_id,
                customer=customer_id,
                description=description,
                confirm=True,
                return_url=f"{settings.FRONTEND_URL}/payments/success/"
            )
            
            return {
                'payment_intent_id': intent.id,
                'status': intent.status,
                'client_secret': intent.client_secret,
                'requires_action': intent.status == 'requires_action'
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment failed: {str(e)}")
            raise ValidationError(f"Payment failed: {str(e)}")
    
    def retrieve_subscription(self, subscription_id: str) -> Dict:
        """Retrieve Stripe subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': datetime.fromtimestamp(subscription.current_period_start),
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end),
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'canceled_at': datetime.fromtimestamp(subscription.canceled_at) if subscription.canceled_at else None
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe subscription retrieval failed: {str(e)}")
            return {}


class PayPalPaymentService(PaymentGatewayService):
    """PayPal payment gateway service (placeholder)"""
    
    def setup_gateway(self):
        """Setup PayPal configuration"""
        # PayPal SDK setup would go here
        pass
    
    def create_customer(self, user: User) -> str:
        """Create PayPal customer (billing agreement)"""
        # PayPal implementation
        return f"paypal_customer_{user.id}"
    
    def create_payment_method(self, user: User, payment_data: Dict) -> str:
        """Create PayPal payment method"""
        # PayPal implementation
        return f"paypal_pm_{user.id}"
    
    def create_subscription(self, user: User, plan: SubscriptionPlan, payment_method_id: str) -> Dict:
        """Create PayPal subscription"""
        # PayPal subscription implementation
        return {
            'subscription_id': f"paypal_sub_{user.id}",
            'status': 'active'
        }
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel PayPal subscription"""
        # PayPal cancellation implementation
        return True
    
    def process_payment(self, amount: Decimal, currency: str, payment_method_id: str,
                       description: str = None) -> Dict:
        """Process PayPal payment"""
        # PayPal payment implementation
        return {
            'payment_id': f"paypal_payment_{timezone.now().timestamp()}",
            'status': 'completed'
        }


class SubscriptionService:
    """Service for managing user subscriptions"""
    
    @staticmethod
    def create_subscription(user: User, plan: SubscriptionPlan, payment_method_id: str,
                          gateway_name: str = 'stripe', coupon_code: str = None) -> UserSubscription:
        """Create new subscription for user"""
        
        try:
            with transaction.atomic():
                # Get payment gateway service
                if gateway_name == 'stripe':
                    gateway_service = StripePaymentService(gateway_name)
                elif gateway_name == 'paypal':
                    gateway_service = PayPalPaymentService(gateway_name)
                else:
                    raise ValidationError(f"Unsupported gateway: {gateway_name}")
                
                # Apply coupon if provided
                discount_amount = Decimal('0')
                if coupon_code:
                    coupon = DiscountCoupon.objects.get(code=coupon_code, is_active=True)
                    is_valid, message = coupon.is_valid(user=user, plan=plan)
                    if not is_valid:
                        raise ValidationError(message)
                    
                    discount_amount = coupon.calculate_discount(plan.price)
                
                # Calculate final amount
                final_amount = plan.price - discount_amount
                
                # Create subscription in gateway
                gateway_data = gateway_service.create_subscription(
                    user=user,
                    plan=plan,
                    payment_method_id=payment_method_id
                )
                
                # Create local subscription record
                subscription = UserSubscription.objects.create(
                    user=user,
                    plan=plan,
                    gateway=gateway_service.gateway,
                    gateway_subscription_id=gateway_data['subscription_id'],
                    gateway_customer_id=gateway_data.get('customer_id', ''),
                    status='active',
                    current_period_start=gateway_data['current_period_start'],
                    current_period_end=gateway_data['current_period_end'],
                    amount=final_amount,
                    currency=plan.currency,
                    next_billing_date=gateway_data['current_period_end']
                )
                
                # Update user subscription tier
                user.subscription_tier = plan.plan_type
                user.api_limit_reset_date = gateway_data['current_period_end']
                user.save(update_fields=['subscription_tier', 'api_limit_reset_date'])
                
                # Record coupon usage if applicable
                if coupon_code and discount_amount > 0:
                    coupon.current_uses += 1
                    coupon.save()
                    
                    CouponUsage.objects.create(
                        coupon=coupon,
                        user=user,
                        discount_amount=discount_amount
                    )
                
                # Create payment record
                Payment.objects.create(
                    user=user,
                    subscription=subscription,
                    payment_type='subscription',
                    status='succeeded',
                    amount=final_amount,
                    currency=plan.currency,
                    gateway=gateway_service.gateway,
                    gateway_payment_id=gateway_data.get('payment_id', ''),
                    succeeded_at=timezone.now(),
                    description=f"Subscription to {plan.name}"
                )
                
                logger.info(f"Subscription created: {subscription.id} for user {user.email}")
                return subscription
                
        except Exception as e:
            logger.error(f"Subscription creation failed: {str(e)}")
            raise ValidationError(f"Failed to create subscription: {str(e)}")
    
    @staticmethod
    def cancel_subscription(subscription: UserSubscription, reason: str = '') -> bool:
        """Cancel user subscription"""
        
        try:
            # Get gateway service
            if subscription.gateway.name == 'stripe':
                gateway_service = StripePaymentService(subscription.gateway.name)
            elif subscription.gateway.name == 'paypal':
                gateway_service = PayPalPaymentService(subscription.gateway.name)
            else:
                raise ValidationError(f"Unsupported gateway: {subscription.gateway.name}")
            
            # Cancel in gateway
            success = gateway_service.cancel_subscription(subscription.gateway_subscription_id)
            
            if success:
                # Update local record
                subscription.status = 'canceled'
                subscription.canceled_at = timezone.now()
                subscription.metadata.update({
                    'cancellation_reason': reason,
                    'canceled_by': 'user'
                })
                subscription.save()
                
                logger.info(f"Subscription canceled: {subscription.id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Subscription cancellation failed: {str(e)}")
            return False
    
    @staticmethod
    def upgrade_subscription(subscription: UserSubscription, new_plan: SubscriptionPlan) -> bool:
        """Upgrade user subscription to new plan"""
        
        try:
            with transaction.atomic():
                # Calculate prorated amount
                days_remaining = subscription.days_remaining()
                old_daily_rate = subscription.plan.monthly_price / 30
                new_daily_rate = new_plan.monthly_price / 30
                
                proration_credit = old_daily_rate * days_remaining
                proration_charge = new_daily_rate * days_remaining
                upgrade_amount = proration_charge - proration_credit
                
                # Process upgrade payment if needed
                if upgrade_amount > 0:
                    # Create upgrade payment
                    Payment.objects.create(
                        user=subscription.user,
                        subscription=subscription,
                        payment_type='upgrade',
                        status='succeeded',
                        amount=upgrade_amount,
                        currency=new_plan.currency,
                        gateway=subscription.gateway,
                        succeeded_at=timezone.now(),
                        description=f"Upgrade to {new_plan.name}"
                    )
                
                # Update subscription
                subscription.plan = new_plan
                subscription.amount = new_plan.price
                subscription.save()
                
                # Update user tier
                subscription.user.subscription_tier = new_plan.plan_type
                subscription.user.save(update_fields=['subscription_tier'])
                
                logger.info(f"Subscription upgraded: {subscription.id} to {new_plan.name}")
                return True
                
        except Exception as e:
            logger.error(f"Subscription upgrade failed: {str(e)}")
            return False
    
    @staticmethod
    def sync_subscription_status(subscription: UserSubscription) -> None:
        """Sync subscription status with gateway"""
        
        try:
            if subscription.gateway.name == 'stripe':
                gateway_service = StripePaymentService(subscription.gateway.name)
                gateway_data = gateway_service.retrieve_subscription(
                    subscription.gateway_subscription_id
                )
                
                if gateway_data:
                    # Update status if changed
                    if gateway_data['status'] != subscription.status:
                        subscription.status = gateway_data['status']
                        subscription.current_period_start = gateway_data['current_period_start']
                        subscription.current_period_end = gateway_data['current_period_end']
                        
                        if gateway_data.get('canceled_at'):
                            subscription.canceled_at = gateway_data['canceled_at']
                        
                        subscription.save()
                        
                        logger.info(f"Subscription status synced: {subscription.id}")
                
        except Exception as e:
            logger.error(f"Subscription sync failed: {str(e)}")


class PaymentService:
    """Service for payment processing"""
    
    @staticmethod
    def process_one_time_payment(user: User, amount: Decimal, description: str,
                                payment_method_id: str, gateway_name: str = 'stripe') -> Payment:
        """Process one-time payment"""
        
        try:
            # Get gateway service
            if gateway_name == 'stripe':
                gateway_service = StripePaymentService(gateway_name)
            elif gateway_name == 'paypal':
                gateway_service = PayPalPaymentService(gateway_name)
            else:
                raise ValidationError(f"Unsupported gateway: {gateway_name}")
            
            # Process payment
            gateway_data = gateway_service.process_payment(
                amount=amount,
                currency='USD',
                payment_method_id=payment_method_id,
                description=description
            )
            
            # Create payment record
            payment = Payment.objects.create(
                user=user,
                payment_type='one_time',
                status='processing' if gateway_data.get('requires_action') else 'succeeded',
                amount=amount,
                currency='USD',
                gateway=gateway_service.gateway,
                gateway_payment_id=gateway_data.get('payment_intent_id', ''),
                attempted_at=timezone.now(),
                description=description
            )
            
            if payment.status == 'succeeded':
                payment.succeeded_at = timezone.now()
                payment.save()
            
            logger.info(f"Payment processed: {payment.id} for user {user.email}")
            return payment
            
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            raise ValidationError(f"Payment failed: {str(e)}")
    
    @staticmethod
    def refund_payment(payment: Payment, amount: Decimal = None, reason: str = '') -> bool:
        """Refund payment"""
        
        try:
            if not payment.can_refund():
                return False
            
            refund_amount = amount or payment.refundable_amount()
            
            # Process refund in gateway
            if payment.gateway.name == 'stripe':
                stripe.Refund.create(
                    payment_intent=payment.gateway_payment_id,
                    amount=int(refund_amount * 100),  # Convert to cents
                    reason='requested_by_customer'
                )
            
            # Update payment record
            payment.refunded_amount += refund_amount
            payment.refund_reason = reason
            
            if payment.refunded_amount >= payment.amount:
                payment.status = 'refunded'
            else:
                payment.status = 'partially_refunded'
            
            payment.save()
            
            logger.info(f"Payment refunded: {payment.id} amount: ${refund_amount}")
            return True
            
        except Exception as e:
            logger.error(f"Refund failed: {str(e)}")
            return False


class InvoiceService:
    """Service for invoice management"""
    
    @staticmethod
    def generate_invoice(subscription: UserSubscription, payment: Payment = None) -> Invoice:
        """Generate invoice for subscription"""
        
        try:
            # Calculate dates
            issue_date = timezone.now().date()
            due_date = issue_date + timedelta(days=30)
            
            # Create invoice
            invoice = Invoice.objects.create(
                user=subscription.user,
                subscription=subscription,
                payment=payment,
                status='open' if not payment else 'paid',
                subtotal=subscription.amount,
                total=subscription.amount,
                currency=subscription.currency,
                issue_date=issue_date,
                due_date=due_date,
                paid_date=payment.succeeded_at.date() if payment and payment.succeeded_at else None
            )
            
            # Add invoice items
            from .models import InvoiceItem
            InvoiceItem.objects.create(
                invoice=invoice,
                description=f"{subscription.plan.name} - {subscription.plan.get_billing_cycle_display()}",
                quantity=1,
                unit_price=subscription.amount,
                total_price=subscription.amount
            )
            
            logger.info(f"Invoice generated: {invoice.invoice_number}")
            return invoice
            
        except Exception as e:
            logger.error(f"Invoice generation failed: {str(e)}")
            raise ValidationError(f"Failed to generate invoice: {str(e)}")


class WebhookService:
    """Service for handling payment gateway webhooks"""
    
    @staticmethod
    def process_stripe_webhook(event_data: Dict) -> bool:
        """Process Stripe webhook event"""
        
        try:
            event_type = event_data.get('type')
            event_id = event_data.get('id')
            
            # Create webhook event record
            gateway = PaymentGateway.objects.get(name='stripe')
            webhook_event, created = WebhookEvent.objects.get_or_create(
                gateway=gateway,
                event_id=event_id,
                defaults={
                    'event_type': event_type,
                    'data': event_data
                }
            )
            
            if not created and webhook_event.processed:
                return True  # Already processed
            
            # Process different event types
            if event_type == 'invoice.payment_succeeded':
                WebhookService._handle_invoice_payment_succeeded(event_data['data']['object'])
            
            elif event_type == 'invoice.payment_failed':
                WebhookService._handle_invoice_payment_failed(event_data['data']['object'])
            
            elif event_type == 'customer.subscription.updated':
                WebhookService._handle_subscription_updated(event_data['data']['object'])
            
            elif event_type == 'customer.subscription.deleted':
                WebhookService._handle_subscription_deleted(event_data['data']['object'])
            
            # Mark as processed
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            logger.info(f"Webhook processed: {event_type} - {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            
            # Update webhook event with error
            if 'webhook_event' in locals():
                webhook_event.error_message = str(e)
                webhook_event.retry_count += 1
                webhook_event.save()
            
            return False
    
    @staticmethod
    def _handle_invoice_payment_succeeded(invoice_data: Dict):
        """Handle successful invoice payment"""
        subscription_id = invoice_data.get('subscription')
        
        try:
            subscription = UserSubscription.objects.get(
                gateway_subscription_id=subscription_id
            )
            
            # Update subscription status
            subscription.status = 'active'
            subscription.current_period_start = datetime.fromtimestamp(
                invoice_data['period_start']
            )
            subscription.current_period_end = datetime.fromtimestamp(
                invoice_data['period_end']
            )
            subscription.save()
            
            # Reset usage counters
            subscription.reset_usage()
            
        except UserSubscription.DoesNotExist:
            logger.warning(f"Subscription not found: {subscription_id}")
    
    @staticmethod
    def _handle_invoice_payment_failed(invoice_data: Dict):
        """Handle failed invoice payment"""
        subscription_id = invoice_data.get('subscription')
        
        try:
            subscription = UserSubscription.objects.get(
                gateway_subscription_id=subscription_id
            )
            
            subscription.status = 'past_due'
            subscription.save()
            
        except UserSubscription.DoesNotExist:
            logger.warning(f"Subscription not found: {subscription_id}")
    
    @staticmethod
    def _handle_subscription_updated(subscription_data: Dict):
        """Handle subscription update"""
        subscription_id = subscription_data.get('id')
        
        try:
            subscription = UserSubscription.objects.get(
                gateway_subscription_id=subscription_id
            )
            
            # Sync subscription status
            SubscriptionService.sync_subscription_status(subscription)
            
        except UserSubscription.DoesNotExist:
            logger.warning(f"Subscription not found: {subscription_id}")
    
    @staticmethod
    def _handle_subscription_deleted(subscription_data: Dict):
        """Handle subscription deletion"""
        subscription_id = subscription_data.get('id')
        
        try:
            subscription = UserSubscription.objects.get(
                gateway_subscription_id=subscription_id
            )
            
            subscription.status = 'canceled'
            subscription.ended_at = timezone.now()
            subscription.save()
            
            # Downgrade user to free tier
            subscription.user.subscription_tier = 'free'
            subscription.user.save(update_fields=['subscription_tier'])
            
        except UserSubscription.DoesNotExist:
            logger.warning(f"Subscription not found: {subscription_id}")
