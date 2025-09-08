"""
Base Agent Engine for OneLastAI Platform.
Provides the foundation for all AI agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator
from django.conf import settings
from ai_services.services import ai_service_manager
from ai_services.models import Conversation, Message
from agents.models import Agent, AgentConversation
import logging
import json
import time

logger = logging.getLogger(__name__)


class AgentEngine(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.agent = self._load_agent_config()
        self.conversation_history = []
        self.context_data = {}
    
    def _load_agent_config(self) -> Agent:
        """Load agent configuration from database."""
        try:
            return Agent.objects.get(agent_id=self.agent_id, is_active=True)
        except Agent.DoesNotExist:
            raise ValueError(f"Agent '{self.agent_id}' not found or inactive")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    def get_personality_prompt(self) -> str:
        """Get the personality prompt for this agent."""
        return self.agent.personality_prompt
    
    def get_full_system_prompt(self) -> str:
        """Combine system and personality prompts."""
        system = self.get_system_prompt()
        personality = self.get_personality_prompt()
        
        return f"""SYSTEM INSTRUCTIONS:
{system}

PERSONALITY AND BEHAVIOR:
{personality}

IMPORTANT: Always stay in character and follow both the system instructions and personality guidelines."""
    
    async def process_message(self, user_message: str, conversation_id: str = None, 
                            user=None, **kwargs) -> Dict[str, Any]:
        """Process a user message and generate response."""
        try:
            # Load or create conversation
            conversation = await self._get_or_create_conversation(
                conversation_id, user, user_message
            )
            
            # Prepare messages for AI service
            messages = await self._prepare_messages(conversation, user_message)
            
            # Generate AI response
            ai_config = self._get_ai_config()
            response = await ai_service_manager.generate_response(
                provider=ai_config['provider'],
                model=ai_config['model'],
                messages=messages,
                **ai_config['parameters']
            )
            
            # Save message to conversation
            await self._save_message(conversation, user_message, response)
            
            # Update conversation metadata
            await self._update_conversation_stats(conversation, response)
            
            return {
                'response': response['content'],
                'conversation_id': str(conversation.id),
                'agent_id': self.agent_id,
                'agent_name': self.agent.name,
                'tokens_used': response.get('tokens_used', 0),
                'response_time_ms': response.get('response_time_ms', 0),
            }
            
        except Exception as e:
            logger.error(f"Error processing message for agent {self.agent_id}: {e}")
            return {
                'error': 'Failed to process message',
                'message': str(e),
                'agent_id': self.agent_id,
            }
    
    async def process_message_stream(self, user_message: str, conversation_id: str = None,
                                   user=None, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Process message with streaming response."""
        try:
            # Load or create conversation
            conversation = await self._get_or_create_conversation(
                conversation_id, user, user_message
            )
            
            # Prepare messages for AI service
            messages = await self._prepare_messages(conversation, user_message)
            
            # Get AI service for streaming
            ai_config = self._get_ai_config()
            service = ai_service_manager.get_service(
                ai_config['provider'], ai_config['model'], **ai_config['parameters']
            )
            
            # Stream response
            full_response = ""
            start_time = time.time()
            
            async for chunk in service.generate_chat_stream(messages, **ai_config['parameters']):
                full_response += chunk
                yield {
                    'chunk': chunk,
                    'conversation_id': str(conversation.id),
                    'agent_id': self.agent_id,
                }
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Create response dict for saving
            response = {
                'content': full_response,
                'role': 'assistant',
                'response_time_ms': response_time_ms,
            }
            
            # Save message to conversation
            await self._save_message(conversation, user_message, response)
            
            # Send completion signal
            yield {
                'completed': True,
                'conversation_id': str(conversation.id),
                'agent_id': self.agent_id,
                'response_time_ms': response_time_ms,
            }
            
        except Exception as e:
            logger.error(f"Error streaming for agent {self.agent_id}: {e}")
            yield {
                'error': 'Failed to process streaming message',
                'message': str(e),
                'agent_id': self.agent_id,
            }
    
    async def _get_or_create_conversation(self, conversation_id: str, user, 
                                        first_message: str) -> Conversation:
        """Get existing conversation or create new one."""
        from django.db import sync_to_async
        
        if conversation_id:
            try:
                conversation = await sync_to_async(Conversation.objects.get)(
                    id=conversation_id, user=user
                )
                return conversation
            except Conversation.DoesNotExist:
                pass
        
        # Create new conversation
        title = self._generate_conversation_title(first_message)
        conversation = await sync_to_async(Conversation.objects.create)(
            user=user,
            agent_name=self.agent_id,
            title=title,
            ai_config=self.agent.default_ai_config,
        )
        
        # Create agent-specific conversation
        await sync_to_async(AgentConversation.objects.create)(
            conversation=conversation,
            agent=self.agent,
        )
        
        return conversation
    
    async def _prepare_messages(self, conversation: Conversation, 
                              user_message: str) -> List[Dict[str, Any]]:
        """Prepare message history for AI service."""
        from django.db import sync_to_async
        
        messages = []
        
        # Add system message
        messages.append({
            'role': 'system',
            'content': self.get_full_system_prompt()
        })
        
        # Add conversation history (last N messages)
        if self.agent.memory_enabled:
            recent_messages = await sync_to_async(list)(
                conversation.messages.order_by('-created_at')[:10]
            )
            
            for msg in reversed(recent_messages):
                messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
        
        # Add current user message
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        return messages
    
    async def _save_message(self, conversation: Conversation, user_message: str, 
                          ai_response: Dict[str, Any]):
        """Save messages to conversation."""
        from django.db import sync_to_async
        
        # Save user message
        await sync_to_async(Message.objects.create)(
            conversation=conversation,
            role='user',
            content=user_message,
        )
        
        # Save AI response
        await sync_to_async(Message.objects.create)(
            conversation=conversation,
            role='assistant',
            content=ai_response['content'],
            tokens_used=ai_response.get('tokens_used', 0),
            response_time_ms=ai_response.get('response_time_ms', 0),
            model_used=ai_response.get('model', ''),
        )
    
    async def _update_conversation_stats(self, conversation: Conversation, 
                                       response: Dict[str, Any]):
        """Update conversation statistics."""
        from django.db import sync_to_async
        from django.db.models import F
        
        tokens_used = response.get('tokens_used', 0)
        
        # Update conversation totals
        await sync_to_async(Conversation.objects.filter(id=conversation.id).update)(
            total_tokens_used=F('total_tokens_used') + tokens_used,
            updated_at=sync_to_async(lambda: timezone.now())(),
        )
        
        # Update agent totals
        await sync_to_async(Agent.objects.filter(id=self.agent.id).update)(
            total_conversations=F('total_conversations') + 1
        )
    
    def _generate_conversation_title(self, first_message: str) -> str:
        """Generate a title for the conversation."""
        # Simple title generation - take first 50 chars
        title = first_message[:50].strip()
        if len(first_message) > 50:
            title += "..."
        return title or f"Chat with {self.agent.name}"
    
    def _get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration for this agent."""
        config = self.agent.default_ai_config
        
        if config:
            return {
                'provider': config.provider.name,
                'model': config.model.model_id,
                'parameters': {
                    'temperature': self.agent.temperature,
                    'max_tokens': self.agent.max_tokens,
                    'top_p': config.top_p,
                    'frequency_penalty': config.frequency_penalty,
                    'presence_penalty': config.presence_penalty,
                }
            }
        else:
            # Default configuration
            return {
                'provider': 'openai',
                'model': 'gpt-4',
                'parameters': {
                    'temperature': self.agent.temperature,
                    'max_tokens': self.agent.max_tokens,
                    'top_p': 1.0,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0,
                }
            }


class ConversationalAgent(AgentEngine):
    """Base class for conversational agents."""
    
    def get_system_prompt(self) -> str:
        return """You are an advanced conversational AI designed to engage in natural, 
helpful, and meaningful dialogue with users. You should be friendly, knowledgeable, 
and adapt your communication style to match the user's needs and preferences."""


class TechnicalAgent(AgentEngine):
    """Base class for technical agents."""
    
    def get_system_prompt(self) -> str:
        return """You are a technical AI assistant with deep expertise in technology, 
programming, systems architecture, and problem-solving. Provide accurate, detailed, 
and actionable technical guidance. Use examples and best practices in your responses."""


class CreativeAgent(AgentEngine):
    """Base class for creative agents."""
    
    def get_system_prompt(self) -> str:
        return """You are a creative AI assistant designed to help with creative tasks, 
content generation, artistic endeavors, and innovative thinking. Approach problems 
with creativity and imagination while maintaining quality and usefulness."""


class BusinessAgent(AgentEngine):
    """Base class for business agents."""
    
    def get_system_prompt(self) -> str:
        return """You are a business-focused AI assistant with expertise in strategy, 
analytics, operations, and decision-making. Provide professional, data-driven insights 
and actionable business recommendations."""