from django.urls import path
from django.http import HttpResponse

app_name = 'monitoring'

def health_check(request):
    return HttpResponse("Health check OK")

urlpatterns = [
    path('health/', health_check, name='health'),
]
