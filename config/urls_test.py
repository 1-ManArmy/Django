"""
Minimal URL configuration for OneLastAI testing.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Main URL patterns
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Test homepage
    path('', TemplateView.as_view(template_name='core/home.html'), name='home'),
    
    # Core apps
    path('accounts/', include('accounts.urls_test')),
    path('agents/', include('agents.urls_test')),
    path('ai/', include('ai_services.urls_test')),
    path('core/', include('core.urls_test')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                         document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                         document_root=settings.MEDIA_ROOT)

# Admin customization
admin.site.site_header = "OneLastAI Test Administration"
admin.site.site_title = "OneLastAI Test Admin Portal"
admin.site.index_title = "Welcome to OneLastAI Test Administration"