"""
OneLastAI Platform - Payment URLs
URL routing for payment system
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'payments'

# API Router
router = DefaultRouter()
router.register(r'subscription-plans', views.SubscriptionPlansViewSet, basename='subscription-plans')
router.register(r'user-subscription', views.UserSubscriptionViewSet, basename='user-subscription')
router.register(r'payment-methods', views.PaymentMethodsViewSet, basename='payment-methods')
router.register(r'payments', views.PaymentsViewSet, basename='payments')
router.register(r'invoices', views.InvoicesViewSet, basename='invoices')
router.register(r'coupons', views.CouponsViewSet, basename='coupons')

# URL Patterns
urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # API Endpoints
    path('api/subscription/create/', views.CreateSubscriptionView.as_view(), name='create-subscription'),
    path('api/subscription/upgrade/', views.UpgradeSubscriptionView.as_view(), name='upgrade-subscription'),
    path('api/subscription/cancel/', views.CancelSubscriptionView.as_view(), name='cancel-subscription'),
    path('api/subscription/reactivate/', views.ReactivateSubscriptionView.as_view(), name='reactivate-subscription'),
    
    path('api/payment/create/', views.CreatePaymentView.as_view(), name='create-payment'),
    path('api/payment/refund/<uuid:payment_id>/', views.RefundPaymentView.as_view(), name='refund-payment'),
    
    path('api/coupon/validate/', views.ValidateCouponView.as_view(), name='validate-coupon'),
    path('api/billing/summary/', views.BillingSummaryView.as_view(), name='billing-summary'),
    
    # Webhook endpoints
    path('webhooks/stripe/', views.stripe_webhook, name='stripe-webhook'),
    path('webhooks/paypal/', views.paypal_webhook, name='paypal-webhook'),
    
    # Web Interface URLs
    path('', views.billing_dashboard, name='dashboard'),
    path('plans/', views.subscription_plans_page, name='plans'),
    path('signup/<uuid:plan_id>/', views.subscription_signup, name='signup'),
    path('payment-methods/', views.payment_methods_page, name='payment-methods'),
    path('payment-methods/add/', views.add_payment_method, name='add-payment-method'),
    path('payment-methods/<uuid:method_id>/delete/', views.delete_payment_method, name='delete-payment-method'),
    path('payment-methods/<uuid:method_id>/default/', views.set_default_payment_method, name='set-default-payment-method'),
    
    path('subscription/', views.subscription_management, name='subscription'),
    path('subscription/upgrade/', views.upgrade_subscription_page, name='upgrade'),
    path('subscription/cancel/', views.cancel_subscription_page, name='cancel'),
    
    path('invoices/', views.invoices_page, name='invoices'),
    path('invoices/<uuid:invoice_id>/', views.invoice_detail, name='invoice-detail'),
    path('invoices/<uuid:invoice_id>/download/', views.download_invoice, name='download-invoice'),
    
    path('payments/', views.payments_history, name='payments'),
    path('payments/new/', views.make_payment, name='make-payment'),
    
    # Admin URLs (staff only)
    path('admin/coupons/', views.admin_coupons, name='admin-coupons'),
    path('admin/coupons/create/', views.admin_create_coupon, name='admin-create-coupon'),
    path('admin/coupons/<uuid:coupon_id>/edit/', views.admin_edit_coupon, name='admin-edit-coupon'),
    path('admin/plans/', views.admin_plans, name='admin-plans'),
    path('admin/plans/create/', views.admin_create_plan, name='admin-create-plan'),
    path('admin/plans/<uuid:plan_id>/edit/', views.admin_edit_plan, name='admin-edit-plan'),
    path('admin/subscriptions/', views.admin_subscriptions, name='admin-subscriptions'),
    path('admin/payments/', views.admin_payments, name='admin-payments'),
]
