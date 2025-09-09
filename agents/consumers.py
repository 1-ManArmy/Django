"""
OneLastAI Platform - WebSocket Consumers
Real-time communication handlers for agents, dashboard, and community features
"""
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

from agents.models import Agent, AgentConversation, Message
from ai_services.services import AIServiceFactory

User = get_user_model()


class AgentChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time agent chat"""
    
    async def connect(self):
        self.agent_id = self.scope['url_route']['kwargs']['agent_id']
        self.user = self.scope['user']
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join agent chat room
        self.room_name = f'agent_chat_{self.agent_id}_{self.user.id}'
        self.room_group_name = f'chat_{self.room_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to agent chat'
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle received WebSocket messages"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'user_message':
                await self.handle_user_message(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing_indicator(text_data_json)
            elif message_type == 'voice_message':
                await self.handle_voice_message(text_data_json)
                
        except json.JSONDecodeError:
            await self.send_error('Invalid message format')
        except Exception as e:
            await self.send_error(f'Error processing message: {str(e)}')
    
    async def handle_user_message(self, data):
        """Process user message and generate AI response"""
        message_content = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not message_content:
            await self.send_error('Message cannot be empty')
            return
        
        try:
            # Get or create agent
            agent = await self.get_agent(self.agent_id)
            if not agent:
                await self.send_error('Agent not found')
                return
            
            # Check user's API usage limits
            can_use = await self.check_api_limits(self.user)
            if not can_use:
                await self.send_error('API usage limit exceeded. Please upgrade your plan.')
                return
            
            # Get or create conversation
            conversation = await self.get_or_create_conversation(agent, conversation_id)
            
            # Save user message
            user_message = await self.save_message(
                conversation, 
                message_content, 
                'user'
            )
            
            # Send typing indicator
            await self.send(text_data=json.dumps({
                'type': 'agent_typing',
                'agent_id': self.agent_id
            }))
            
            # Generate AI response
            ai_response = await self.generate_ai_response(agent, message_content, conversation)
            
            # Save AI message
            ai_message = await self.save_message(
                conversation,
                ai_response,
                'agent'
            )
            
            # Update user's API usage
            await self.increment_api_usage(self.user)
            
            # Send AI response
            await self.send(text_data=json.dumps({
                'type': 'agent_message',
                'message': ai_response,
                'message_id': ai_message.id,
                'conversation_id': conversation.id,
                'timestamp': ai_message.created_at.isoformat()
            }))
            
        except Exception as e:
            await self.send_error(f'Failed to process message: {str(e)}')
    
    async def handle_typing_indicator(self, data):
        """Handle typing indicator from user"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'user_id': self.user.id,
                'is_typing': data.get('is_typing', False)
            }
        )
    
    async def handle_voice_message(self, data):
        """Handle voice message processing"""
        # TODO: Implement voice message handling
        await self.send_error('Voice messages not yet implemented')
    
    @database_sync_to_async
    def get_agent(self, agent_id):
        """Get agent by ID"""
        try:
            return Agent.objects.get(id=agent_id, is_active=True)
        except Agent.DoesNotExist:
            return None
    
    @database_sync_to_async
    def check_api_limits(self, user):
        """Check if user can make API requests"""
        subscription = getattr(user, 'subscription', None)
        if not subscription:
            return False
        return subscription.can_use_api()
    
    @database_sync_to_async
    def get_or_create_conversation(self, agent, conversation_id=None):
        """Get existing or create new conversation"""
        if conversation_id:
            try:
                return AgentConversation.objects.get(
                    id=conversation_id,
                    user=self.user,
                    agent=agent
                )
            except AgentConversation.DoesNotExist:
                pass
        
        # Create new conversation
        conversation = AgentConversation.objects.create(
            user=self.user,
            agent=agent,
            title=f"Chat with {agent.get_display_name()}"
        )
        return conversation
    
    @database_sync_to_async
    def save_message(self, conversation, content, sender):
        """Save message to database"""
        return Message.objects.create(
            conversation=conversation,
            content=content,
            sender=sender,
            metadata={'timestamp': timezone.now().isoformat()}
        )
    
    async def generate_ai_response(self, agent, message, conversation):
        """Generate AI response using the appropriate service"""
        try:
            # Get conversation history
            history = await self.get_conversation_history(conversation)
            
            # Get AI service
            ai_service = AIServiceFactory.get_service(agent.ai_provider)
            
            # Generate response
            response = await asyncio.to_thread(
                ai_service.generate_response,
                message,
                context={
                    'agent': agent,
                    'conversation_history': history,
                    'user': self.user
                }
            )
            
            return response
            
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"
    
    @database_sync_to_async
    def get_conversation_history(self, conversation, limit=10):
        """Get recent conversation history"""
        messages = Message.objects.filter(
            conversation=conversation
        ).order_by('-created_at')[:limit]
        
        history = []
        for message in reversed(messages):
            history.append({
                'role': 'user' if message.sender == 'user' else 'assistant',
                'content': message.content
            })
        
        return history
    
    @database_sync_to_async
    def increment_api_usage(self, user):
        """Increment user's API usage counter"""
        subscription = getattr(user, 'subscription', None)
        if subscription:
            subscription.api_requests_used += 1
            subscription.save(update_fields=['api_requests_used'])
    
    async def send_error(self, error_message):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message
        }))
    
    # Group message handlers
    async def user_typing(self, event):
        """Send typing indicator to client"""
        if event['user_id'] != self.user.id:  # Don't send back to sender
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'is_typing': event['is_typing']
            }))


class VoiceAgentConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for voice chat with agents"""
    
    async def connect(self):
        self.agent_id = self.scope['url_route']['kwargs']['agent_id']
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user has voice features enabled
        subscription = getattr(self.user, 'subscription', None)
        if not subscription or not subscription.plan.voice_agents_enabled:
            await self.close()
            return
        
        self.room_name = f'voice_chat_{self.agent_id}_{self.user.id}'
        self.room_group_name = f'voice_{self.room_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle voice data"""
        # TODO: Implement voice processing
        data = json.loads(text_data)
        
        if data.get('type') == 'voice_data':
            # Process voice data
            await self.process_voice_data(data.get('audio_data'))
    
    async def process_voice_data(self, audio_data):
        """Process voice input and generate voice response"""
        # TODO: Implement speech-to-text, AI processing, and text-to-speech
        pass


class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time dashboard updates"""
    
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_name = f'dashboard_{self.user.id}'
        self.room_group_name = f'dashboard_{self.room_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial dashboard data
        await self.send_dashboard_data()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle dashboard requests"""
        data = json.loads(text_data)
        
        if data.get('type') == 'request_update':
            await self.send_dashboard_data()
    
    async def send_dashboard_data(self):
        """Send current dashboard data to client"""
        dashboard_data = await self.get_dashboard_data()
        
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': dashboard_data
        }))
    
    @database_sync_to_async
    def get_dashboard_data(self):
        """Get current dashboard statistics"""
        subscription = getattr(self.user, 'subscription', None)
        
        # Get conversation count
        conversation_count = AgentConversation.objects.filter(user=self.user).count()
        
        # Get recent activity
        recent_messages = Message.objects.filter(
            conversation__user=self.user
        ).order_by('-created_at')[:5]
        
        return {
            'api_usage': subscription.api_requests_used if subscription else 0,
            'api_limit': subscription.plan.api_requests_limit if subscription else 0,
            'conversation_count': conversation_count,
            'subscription_status': subscription.status if subscription else 'inactive',
            'recent_activity': [
                {
                    'id': msg.id,
                    'content': msg.content[:100],
                    'timestamp': msg.created_at.isoformat()
                }
                for msg in recent_messages
            ]
        }
    
    # Group message handlers
    async def dashboard_notification(self, event):
        """Send notification to dashboard"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'level': event.get('level', 'info')
        }))


class CommunityConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for community features"""
    
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_group_name = 'community_global'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle community messages"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'community_message':
            await self.handle_community_message(data)
    
    async def handle_community_message(self, data):
        """Handle community chat message"""
        message = data.get('message', '').strip()
        
        if not message:
            return
        
        # Broadcast to community
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'community_message_broadcast',
                'message': message,
                'user_id': self.user.id,
                'username': self.user.username,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    async def community_message_broadcast(self, event):
        """Send community message to all clients"""
        await self.send(text_data=json.dumps({
            'type': 'community_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))
    
    async def system_notification(self, event):
        """Send system notification to community"""
        await self.send(text_data=json.dumps({
            'type': 'system_notification',
            'message': event['message'],
            'level': event.get('level', 'info')
        }))