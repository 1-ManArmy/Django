"""
OneLastAI Platform - Payment Views
Advanced payment processing views for subscriptions, billing, and payment management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.generic import ListView, DetailView, CreateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.db import transaction
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal
import json
import logging
import stripe

from .models import (
    SubscriptionPlan, UserSubscription, Payment, Invoice, 
    PaymentMethod, DiscountCoupon, PaymentGateway
)
from .services import (
    StripePaymentService, PaymentService, SubscriptionService,
    InvoiceService, WebhookService
)
from .serializers import (
    SubscriptionPlanSerializer, UserSubscriptionSerializer,
    PaymentSerializer, InvoiceSerializer, PaymentMethodSerializer
)
from .forms import (
    SubscriptionPlanForm, SubscriptionSignupForm, PaymentMethodForm, 
    OneTimePaymentForm, DiscountCouponForm, CouponValidationForm,
    InvoiceSearchForm
)

logger = logging.getLogger(__name__)


class SubscriptionPlansView(APIView):
    """Get available subscription plans"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get all active subscription plans"""
        try:
            plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'price')
            
            # Add current user's plan info if authenticated
            current_plan_id = None
            if request.user.is_authenticated:
                current_subscription = UserSubscription.objects.filter(
                    user=request.user,
                    status='active'
                ).first()
                
                if current_subscription:
                    current_plan_id = current_subscription.plan.id
            
            plans_data = []
            for plan in plans:
                plan_data = SubscriptionPlanSerializer(plan).data
                plan_data['is_current'] = (plan.id == current_plan_id)
                plan_data['can_upgrade'] = (
                    request.user.is_authenticated and 
                    (not current_plan_id or plan.id != current_plan_id)
                )
                plans_data.append(plan_data)
            
            return Response({
                'plans': plans_data,
                'currency': 'USD',
                'billing_cycles': dict(SubscriptionPlan.BILLING_CYCLES)
            })
            
        except Exception as e:
            logger.error(f"Error fetching subscription plans: {str(e)}")
            return Response(
                {'error': 'Failed to fetch subscription plans'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSubscriptionView(LoginRequiredMixin, APIView):
    """Manage user subscription"""
    
    def get(self, request):
        """Get current user subscription details"""
        try:
            subscription = UserSubscription.objects.filter(
                user=request.user,
                status__in=['active', 'past_due', 'canceled']
            ).select_related('plan', 'gateway').first()
            
            if not subscription:
                return Response({
                    'subscription': None,
                    'plan': None,
                    'status': 'no_subscription'
                })
            
            # Get usage statistics
            usage_stats = {
                'api_requests_used': subscription.api_requests_used,
                'api_requests_limit': subscription.plan.api_requests_limit,
                'usage_percentage': subscription.usage_percentage(),
                'days_remaining': subscription.days_remaining(),
                'can_use_api': subscription.can_use_api()
            }
            
            # Get recent payments
            recent_payments = Payment.objects.filter(
                user=request.user,
                subscription=subscription
            ).order_by('-created_at')[:5]
            
            return Response({
                'subscription': UserSubscriptionSerializer(subscription).data,
                'plan': SubscriptionPlanSerializer(subscription.plan).data,
                'usage_stats': usage_stats,
                'recent_payments': PaymentSerializer(recent_payments, many=True).data,
                'can_cancel': subscription.status == 'active',
                'can_upgrade': subscription.status == 'active'
            })
            
        except Exception as e:
            logger.error(f"Error fetching user subscription: {str(e)}")
            return Response(
                {'error': 'Failed to fetch subscription details'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create new subscription"""
        try:
            plan_id = request.data.get('plan_id')
            payment_method_token = request.data.get('payment_method_token')
            coupon_code = request.data.get('coupon_code')
            gateway = request.data.get('gateway', 'stripe')
            
            if not plan_id or not payment_method_token:
                return Response(
                    {'error': 'Plan ID and payment method are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user already has active subscription
            existing_subscription = UserSubscription.objects.filter(
                user=request.user,
                status='active'
            ).first()
            
            if existing_subscription:
                return Response(
                    {'error': 'User already has an active subscription'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get subscription plan
            plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
            
            # Create subscription
            subscription = SubscriptionService.create_subscription(
                user=request.user,
                plan=plan,
                payment_method_id=payment_method_token,
                gateway_name=gateway,
                coupon_code=coupon_code
            )
            
            return Response({
                'subscription': UserSubscriptionSerializer(subscription).data,
                'message': f'Successfully subscribed to {plan.name}!',
                'redirect_url': '/dashboard/subscription/'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Subscription creation failed: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request):
        """Cancel subscription"""
        try:
            subscription = UserSubscription.objects.filter(
                user=request.user,
                status='active'
            ).first()
            
            if not subscription:
                return Response(
                    {'error': 'No active subscription found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            reason = request.data.get('reason', 'User requested cancellation')
            
            success = SubscriptionService.cancel_subscription(subscription, reason)
            
            if success:
                return Response({
                    'message': 'Subscription canceled successfully',
                    'ends_at': subscription.current_period_end
                })
            else:
                return Response(
                    {'error': 'Failed to cancel subscription'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Subscription cancellation failed: {str(e)}")
            return Response(
                {'error': 'Failed to cancel subscription'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubscriptionUpgradeView(LoginRequiredMixin, APIView):
    """Handle subscription upgrades"""
    
    def post(self, request):
        """Upgrade subscription to new plan"""
        try:
            new_plan_id = request.data.get('plan_id')
            
            if not new_plan_id:
                return Response(
                    {'error': 'New plan ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get current subscription
            current_subscription = UserSubscription.objects.filter(
                user=request.user,
                status='active'
            ).first()
            
            if not current_subscription:
                return Response(
                    {'error': 'No active subscription found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get new plan
            new_plan = get_object_or_404(SubscriptionPlan, id=new_plan_id, is_active=True)
            
            # Check if it's actually an upgrade
            if new_plan.price <= current_subscription.plan.price:
                return Response(
                    {'error': 'New plan must be higher tier than current plan'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Perform upgrade
            success = SubscriptionService.upgrade_subscription(current_subscription, new_plan)
            
            if success:
                return Response({
                    'subscription': UserSubscriptionSerializer(current_subscription).data,
                    'message': f'Successfully upgraded to {new_plan.name}!'
                })
            else:
                return Response(
                    {'error': 'Failed to upgrade subscription'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Subscription upgrade failed: {str(e)}")
            return Response(
                {'error': 'Failed to upgrade subscription'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentMethodsView(LoginRequiredMixin, APIView):
    """Manage user payment methods"""
    
    def get(self, request):
        """Get user's payment methods"""
        try:
            payment_methods = PaymentMethod.objects.filter(
                user=request.user,
                is_active=True
            ).order_by('-is_default', '-created_at')
            
            return Response({
                'payment_methods': PaymentMethodSerializer(payment_methods, many=True).data
            })
            
        except Exception as e:
            logger.error(f"Error fetching payment methods: {str(e)}")
            return Response(
                {'error': 'Failed to fetch payment methods'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Add new payment method"""
        try:
            payment_token = request.data.get('payment_token')
            gateway_name = request.data.get('gateway', 'stripe')
            
            if not payment_token:
                return Response(
                    {'error': 'Payment token is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create payment method through gateway
            if gateway_name == 'stripe':
                gateway_service = StripePaymentService(gateway_name)
                
                # Create customer if doesn't exist
                customer_id = request.user.stripe_customer_id if hasattr(request.user, 'stripe_customer_id') else None
                if not customer_id:
                    customer_id = gateway_service.create_customer(request.user)
                
                # Create payment method
                payment_method_id = gateway_service.create_payment_method(
                    request.user, 
                    {'token': payment_token, 'customer_id': customer_id}
                )
                
                # Store locally
                payment_method = PaymentMethod.objects.create(
                    user=request.user,
                    gateway=gateway_service.gateway,
                    method_type='card',
                    gateway_method_id=payment_method_id,
                    is_default=not PaymentMethod.objects.filter(user=request.user).exists()
                )
                
                return Response({
                    'payment_method': PaymentMethodSerializer(payment_method).data,
                    'message': 'Payment method added successfully'
                }, status=status.HTTP_201_CREATED)
            
            else:
                return Response(
                    {'error': f'Unsupported gateway: {gateway_name}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Payment method creation failed: {str(e)}")
            return Response(
                {'error': 'Failed to add payment method'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, method_id):
        """Delete payment method"""
        try:
            payment_method = get_object_or_404(
                PaymentMethod, 
                id=method_id, 
                user=request.user, 
                is_active=True
            )
            
            payment_method.is_active = False
            payment_method.save()
            
            return Response({'message': 'Payment method removed successfully'})
            
        except Exception as e:
            logger.error(f"Payment method deletion failed: {str(e)}")
            return Response(
                {'error': 'Failed to remove payment method'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentHistoryView(LoginRequiredMixin, ListView):
    """Display user's payment history"""
    model = Payment
    template_name = 'payments/payment_history.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        return Payment.objects.filter(
            user=self.request.user
        ).select_related('gateway', 'subscription').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get payment statistics
        payments = self.get_queryset()
        context.update({
            'total_payments': payments.count(),
            'successful_payments': payments.filter(status='succeeded').count(),
            'total_amount': sum(p.amount for p in payments.filter(status='succeeded')),
            'page_title': 'Payment History'
        })
        
        return context


class InvoicesView(LoginRequiredMixin, ListView):
    """Display user's invoices"""
    model = Invoice
    template_name = 'payments/invoices.html'
    context_object_name = 'invoices'
    paginate_by = 20
    
    def get_queryset(self):
        return Invoice.objects.filter(
            user=self.request.user
        ).select_related('subscription', 'payment').order_by('-created_at')


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    """Display invoice details"""
    model = Invoice
    template_name = 'payments/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice_items'] = self.object.items.all()
        return context


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_coupon(request):
    """Validate coupon code"""
    try:
        coupon_code = request.data.get('coupon_code')
        plan_id = request.data.get('plan_id')
        
        if not coupon_code:
            return Response(
                {'error': 'Coupon code is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coupon = DiscountCoupon.objects.get(code=coupon_code, is_active=True)
        except DiscountCoupon.DoesNotExist:
            return Response(
                {'valid': False, 'message': 'Invalid coupon code'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get plan if provided
        plan = None
        if plan_id:
            try:
                plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            except SubscriptionPlan.DoesNotExist:
                return Response(
                    {'error': 'Invalid plan'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate coupon
        is_valid, message = coupon.is_valid(user=request.user, plan=plan)
        
        if is_valid and plan:
            discount_amount = coupon.calculate_discount(plan.price)
            final_amount = plan.price - discount_amount
            
            return Response({
                'valid': True,
                'message': message,
                'coupon': {
                    'code': coupon.code,
                    'name': coupon.name,
                    'discount_type': coupon.discount_type,
                    'discount_value': coupon.discount_value,
                    'discount_amount': discount_amount,
                    'final_amount': final_amount
                }
            })
        else:
            return Response({
                'valid': is_valid,
                'message': message
            })
            
    except Exception as e:
        logger.error(f"Coupon validation failed: {str(e)}")
        return Response(
            {'error': 'Failed to validate coupon'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    try:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, 
                sig_header, 
                settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return HttpResponseBadRequest('Invalid payload')
        except stripe.error.SignatureVerificationError:
            return HttpResponseBadRequest('Invalid signature')
        
        # Process webhook event
        success = WebhookService.process_stripe_webhook(event)
        
        if success:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)
            
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        return HttpResponse(status=500)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_payment(request):
    """Process one-time payment"""
    try:
        amount = Decimal(str(request.data.get('amount', 0)))
        description = request.data.get('description', 'OneLastAI Payment')
        payment_method_id = request.data.get('payment_method_id')
        gateway = request.data.get('gateway', 'stripe')
        
        if amount <= 0:
            return Response(
                {'error': 'Invalid amount'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not payment_method_id:
            return Response(
                {'error': 'Payment method is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process payment
        payment = PaymentService.process_one_time_payment(
            user=request.user,
            amount=amount,
            description=description,
            payment_method_id=payment_method_id,
            gateway_name=gateway
        )
        
        return Response({
            'payment': PaymentSerializer(payment).data,
            'message': 'Payment processed successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Payment processing failed: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@login_required
def billing_dashboard(request):
    """Main billing dashboard view"""
    try:
        # Get current subscription
        subscription = UserSubscription.objects.filter(
            user=request.user,
            status__in=['active', 'past_due', 'canceled']
        ).select_related('plan').first()
        
        # Get recent payments
        recent_payments = Payment.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        # Get recent invoices
        recent_invoices = Invoice.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        # Get payment methods
        payment_methods = PaymentMethod.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-is_default')
        
        # Calculate statistics
        total_spent = sum(
            p.amount for p in Payment.objects.filter(
                user=request.user, 
                status='succeeded'
            )
        )
        
        context = {
            'subscription': subscription,
            'recent_payments': recent_payments,
            'recent_invoices': recent_invoices,
            'payment_methods': payment_methods,
            'total_spent': total_spent,
            'page_title': 'Billing Dashboard'
        }
        
        return render(request, 'payments/billing_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Billing dashboard error: {str(e)}")
        messages.error(request, 'Failed to load billing dashboard')
        return redirect('dashboard:home')


@login_required
def subscription_plans_page(request):
    """Subscription plans selection page"""
    try:
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'price')
        
        # Get current subscription
        current_subscription = UserSubscription.objects.filter(
            user=request.user,
            status='active'
        ).first()
        
        context = {
            'plans': plans,
            'current_subscription': current_subscription,
            'page_title': 'Choose Your Plan',
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
        }
        
        return render(request, 'payments/subscription_plans.html', context)
        
    except Exception as e:
        logger.error(f"Subscription plans page error: {str(e)}")
        messages.error(request, 'Failed to load subscription plans')
        return redirect('dashboard:home')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def billing_summary(request):
    """Get billing summary for dashboard"""
    try:
        # Get subscription info
        subscription = UserSubscription.objects.filter(
            user=request.user,
            status__in=['active', 'past_due']
        ).select_related('plan').first()
        
        # Calculate totals
        total_payments = Payment.objects.filter(user=request.user).count()
        successful_payments = Payment.objects.filter(
            user=request.user, 
            status='succeeded'
        ).count()
        
        total_spent = sum(
            p.amount for p in Payment.objects.filter(
                user=request.user, 
                status='succeeded'
            )
        )
        
        # Next billing date
        next_billing = None
        if subscription and subscription.next_billing_date:
            next_billing = subscription.next_billing_date.isoformat()
        
        return Response({
            'subscription': {
                'active': subscription.is_active() if subscription else False,
                'plan_name': subscription.plan.name if subscription else None,
                'amount': subscription.amount if subscription else 0,
                'next_billing_date': next_billing,
                'days_remaining': subscription.days_remaining() if subscription else 0,
                'usage_percentage': subscription.usage_percentage() if subscription else 0
            },
            'payment_stats': {
                'total_payments': total_payments,
                'successful_payments': successful_payments,
                'success_rate': (successful_payments / total_payments * 100) if total_payments > 0 else 0,
                'total_spent': total_spent
            }
        })
        
    except Exception as e:
        logger.error(f"Billing summary error: {str(e)}")
        return Response(
            {'error': 'Failed to get billing summary'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
