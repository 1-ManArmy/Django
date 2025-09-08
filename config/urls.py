"""
Main URL configuration for OneLastAI Platform.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Main URL patterns
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Core Application
    path('', include('core.urls')),
    
    # Authentication
    path('auth/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    
    # API
    path('api/v1/', include('api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'),
         name='redoc'),
    
    # AI Services & Agents
    path('agents/', include('agents.urls')),
    path('ai/', include('ai_services.urls')),
    path('voice/', include('voice.urls')),
    
    # Business Features
    path('payments/', include('payments.urls')),
    path('community/', include('community.urls')),
    path('dashboard/', include('dashboard.urls')),
    
    # Infrastructure
    path('webhooks/', include('webhooks.urls')),
    path('health/', include('monitoring.urls')),
    
    # Legacy support
    path('hello/', TemplateView.as_view(template_name='hello_world/index.html'),
         name='hello_world'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                         document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                         document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Custom error pages
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
handler403 = 'core.views.handler403'
handler400 = 'core.views.handler400'

# Admin customization
admin.site.site_header = "OneLastAI Administration"
admin.site.site_title = "OneLastAI Admin Portal"
admin.site.index_title = "Welcome to OneLastAI Administration"
