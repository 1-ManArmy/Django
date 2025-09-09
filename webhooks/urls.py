from django.urls import path
from django.http import HttpResponse

app_name = 'webhooks'

def placeholder_webhook(request):
    return HttpResponse("Webhook endpoint placeholder")

urlpatterns = [
    # Placeholder webhook endpoints
    path('stripe/', placeholder_webhook, name='stripe'),
    path('paypal/', placeholder_webhook, name='paypal'),
]
