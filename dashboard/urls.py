from django.urls import path
from django.http import HttpResponse

app_name = 'dashboard'

def dashboard_placeholder(request):
    return HttpResponse("Dashboard placeholder")

urlpatterns = [
    path('', dashboard_placeholder, name='index'),
]
