"""
WebSocket URL routing for OneLastAI Platform.
"""

from django.urls import path
from channels.routing import URLRouter

# Import WebSocket consumers
from agents.consumers import AgentChatConsumer
from voice.consumers import VoiceAgentConsumer
from dashboard.consumers import DashboardConsumer
from community.consumers import CommunityConsumer

websocket_urlpatterns = [
    # Agent Chat WebSockets
    path('ws/agents/<str:agent_id>/chat/', AgentChatConsumer.as_asgi()),
    path('ws/agents/<str:agent_id>/voice/', VoiceAgentConsumer.as_asgi()),
    
    # Dashboard WebSockets
    path('ws/dashboard/', DashboardConsumer.as_asgi()),
    path('ws/dashboard/analytics/', DashboardConsumer.as_asgi()),
    
    # Community Features
    path('ws/community/chat/', CommunityConsumer.as_asgi()),
    path('ws/community/notifications/', CommunityConsumer.as_asgi()),
]