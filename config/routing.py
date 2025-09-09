"""
OneLastAI Platform - WebSocket Routing Configuration
Defines URL routing for WebSocket consumers with real-time features
"""
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path

# Import WebSocket consumers
from agents.consumers import (
    AgentChatConsumer,
    VoiceAgentConsumer,
    DashboardConsumer,
    CommunityConsumer
)

websocket_urlpatterns = [
    # Agent Chat WebSockets - Real-time messaging with AI agents
    path('ws/agents/<int:agent_id>/chat/', AgentChatConsumer.as_asgi()),
    path('ws/agents/<int:agent_id>/voice/', VoiceAgentConsumer.as_asgi()),
    
    # Dashboard WebSockets - Real-time analytics and notifications
    path('ws/dashboard/', DashboardConsumer.as_asgi()),
    
    # Community Features - Global chat and notifications
    path('ws/community/', CommunityConsumer.as_asgi()),
]

# Complete ASGI application configuration
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})