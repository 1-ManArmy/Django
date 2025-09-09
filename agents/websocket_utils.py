"""
OneLastAI Platform - WebSocket Utilities
Helper functions and decorators for WebSocket operations
"""
import json
import asyncio
from functools import wraps
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.core.cache import cache


def websocket_auth_required(func):
    """Decorator to ensure WebSocket user is authenticated"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.scope['user'].is_authenticated:
            await self.close(code=4001)  # Custom close code for unauthorized
            return
        return await func(self, *args, **kwargs)
    return wrapper


def rate_limit_websocket(rate='10/min'):
    """Rate limiting decorator for WebSocket messages"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if hasattr(self, 'scope') and 'user' in self.scope:
                user = self.scope['user']
                if user.is_authenticated:
                    cache_key = f"ws_rate_limit_{user.id}_{func.__name__}"
                    current_count = cache.get(cache_key, 0)
                    
                    # Simple rate limiting (can be enhanced)
                    limit = int(rate.split('/')[0])
                    if current_count >= limit:
                        await self.send_error('Rate limit exceeded')
                        return
                    
                    cache.set(cache_key, current_count + 1, 60)  # 1 minute window
            
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator


class WebSocketMessageHandler:
    """Base class for handling WebSocket messages with validation"""
    
    @staticmethod
    def validate_message_format(data):
        """Validate message format and required fields"""
        if not isinstance(data, dict):
            raise ValueError("Message must be a JSON object")
        
        if 'type' not in data:
            raise ValueError("Message must include 'type' field")
        
        return True
    
    @staticmethod
    def sanitize_message_content(content):
        """Sanitize message content for security"""
        if not isinstance(content, str):
            return str(content)
        
        # Basic HTML escaping and length limiting
        import html
        content = html.escape(content.strip())
        
        # Limit message length
        max_length = 10000
        if len(content) > max_length:
            content = content[:max_length] + "... (truncated)"
        
        return content
    
    @staticmethod
    async def broadcast_to_group(channel_layer, group_name, message):
        """Helper to broadcast message to a group"""
        await channel_layer.group_send(group_name, message)


class WebSocketConnectionManager:
    """Manage WebSocket connections and user sessions"""
    
    def __init__(self):
        self.active_connections = {}
        self.user_sessions = {}
    
    def add_connection(self, user_id, channel_name, connection_type='chat'):
        """Add a new WebSocket connection"""
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        
        self.active_connections[user_id][channel_name] = {
            'type': connection_type,
            'connected_at': asyncio.get_event_loop().time(),
            'last_activity': asyncio.get_event_loop().time()
        }
    
    def remove_connection(self, user_id, channel_name):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].pop(channel_name, None)
            
            # Clean up empty user entries
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    def update_activity(self, user_id, channel_name):
        """Update last activity for a connection"""
        if (user_id in self.active_connections and 
            channel_name in self.active_connections[user_id]):
            self.active_connections[user_id][channel_name]['last_activity'] = (
                asyncio.get_event_loop().time()
            )
    
    def get_user_connections(self, user_id):
        """Get all connections for a user"""
        return self.active_connections.get(user_id, {})
    
    def is_user_online(self, user_id):
        """Check if user has any active connections"""
        return user_id in self.active_connections and bool(
            self.active_connections[user_id]
        )


# Global connection manager instance
connection_manager = WebSocketConnectionManager()


class AIResponseCache:
    """Cache for AI responses to reduce redundant API calls"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def _get_cache_key(self, agent_id, message, context_hash=None):
        """Generate cache key for AI response"""
        import hashlib
        
        # Create a hash of the input for caching
        content = f"{agent_id}:{message}"
        if context_hash:
            content += f":{context_hash}"
        
        return f"ai_response:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def get_cached_response(self, agent_id, message, context=None):
        """Get cached AI response if available"""
        cache_key = self._get_cache_key(agent_id, message)
        return cache.get(cache_key)
    
    async def cache_response(self, agent_id, message, response, context=None):
        """Cache AI response"""
        cache_key = self._get_cache_key(agent_id, message)
        cache.set(cache_key, response, self.cache_timeout)


# Global AI response cache instance
ai_response_cache = AIResponseCache()


async def notify_user_status_change(user_id, status, channel_layer):
    """Notify other users about user status change (online/offline)"""
    await channel_layer.group_send(
        'community_global',
        {
            'type': 'user_status_update',
            'user_id': user_id,
            'status': status
        }
    )


@database_sync_to_async
def get_user_subscription_info(user):
    """Get user subscription information async"""
    subscription = getattr(user, 'subscription', None)
    if not subscription:
        return {
            'plan': 'free',
            'api_limit': 0,
            'api_used': 0,
            'features': []
        }
    
    return {
        'plan': subscription.plan.name,
        'api_limit': subscription.plan.api_requests_limit,
        'api_used': subscription.api_requests_used,
        'features': {
            'voice_agents': subscription.plan.voice_agents_enabled,
            'priority_support': subscription.plan.priority_support,
            'custom_agents': subscription.plan.custom_agents_allowed,
        }
    }


async def validate_websocket_permissions(user, action, resource_id=None):
    """Validate if user has permission for WebSocket action"""
    if not user.is_authenticated:
        return False, "Authentication required"
    
    subscription_info = await get_user_subscription_info(user)
    
    # Check specific action permissions
    if action == 'voice_chat':
        if not subscription_info['features']['voice_agents']:
            return False, "Voice chat requires premium subscription"
    
    elif action == 'api_request':
        if subscription_info['api_used'] >= subscription_info['api_limit']:
            return False, "API limit exceeded"
    
    return True, "Allowed"


def format_websocket_error(error_code, message, details=None):
    """Format WebSocket error messages consistently"""
    error_data = {
        'type': 'error',
        'code': error_code,
        'message': message
    }
    
    if details:
        error_data['details'] = details
    
    return json.dumps(error_data)


def format_websocket_success(message_type, data, metadata=None):
    """Format WebSocket success messages consistently"""
    success_data = {
        'type': message_type,
        'data': data
    }
    
    if metadata:
        success_data['metadata'] = metadata
    
    return json.dumps(success_data)