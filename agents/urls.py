"""
OneLastAI Platform - Agents URL Configuration
Web and API routes for agent interactions and conversation management
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

# API Router for REST endpoints
router = DefaultRouter()
router.register(r'conversations', api_views.ConversationViewSet, basename='conversation')
router.register(r'messages', api_views.MessageViewSet, basename='message')

app_name = 'agents'

urlpatterns = [
    # Web Interface URLs
    path('', views.agent_list, name='list'),
    path('<int:agent_id>/', views.agent_detail, name='detail'),
    
    # Chat Interface
    path('chat/', views.chat_interface, name='chat'),
    path('<int:agent_id>/chat/', views.agent_chat, name='agent_chat'),
    
    # Conversation Management
    path('conversations/', views.conversation_list, name='conversations'),
    path('conversations/history/', views.conversation_history, name='history'),
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    
    # Voice Features (Premium)
    path('<int:agent_id>/voice/', views.voice_chat, name='voice_chat'),
    
    # API Endpoints
    path('api/', include(router.urls)),
]
