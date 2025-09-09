"""
OneLastAI Platform - Base Agent Engine
Base class for all specialized AI agent engines with advanced tuning capabilities
"""
import yaml
import os
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class BaseAgentEngine(ABC):
    """
    Base class for all AI agent engines.
    Each agent has its own engine for specialized behavior and processing.
    """
    
    def __init__(self, agent_id: str, config_path: Optional[str] = None):
        """
        Initialize the agent engine with configuration.
        
        Args:
            agent_id: Unique identifier for the agent
            config_path: Path to the YAML configuration file
        """
        self.agent_id = agent_id
        self.config = self.load_config(config_path)
        self.personality = self.config.get('personality', {})
        self.capabilities = self.config.get('capabilities', [])
        self.system_prompt = self.build_system_prompt()
        self.conversation_memory = {}
        
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load agent configuration from YAML file."""
        if not config_path:
            config_path = os.path.join(
                settings.BASE_DIR, 
                'agents', 
                'configs', 
                f'{self.agent_id}.yml'
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"Loaded config for agent {self.agent_id}")
                return config
        except FileNotFoundError:
            logger.warning(f"Config file not found for agent {self.agent_id}: {config_path}")
            return self.get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config for agent {self.agent_id}: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if YAML file is not available."""
        return {
            'name': f'Agent {self.agent_id}',
            'version': '1.0',
            'personality': {
                'traits': ['helpful', 'professional'],
                'communication_style': 'balanced',
                'formality_level': 'professional'
            },
            'capabilities': ['chat', 'analysis'],
            'parameters': {
                'temperature': 0.7,
                'max_tokens': 2000,
                'top_p': 0.9
            }
        }
    
    def build_system_prompt(self) -> str:
        """Build the system prompt based on configuration."""
        base_prompt = self.config.get('system_prompt', {})
        
        # Combine role, personality, and capabilities into system prompt
        role = base_prompt.get('role', f'You are {self.config.get("name", self.agent_id)}')
        personality_desc = self.build_personality_description()
        capabilities_desc = self.build_capabilities_description()
        
        prompt_parts = [
            role,
            personality_desc,
            capabilities_desc,
            base_prompt.get('instructions', ''),
            base_prompt.get('constraints', '')
        ]
        
        return '\n\n'.join(filter(None, prompt_parts))
    
    def build_personality_description(self) -> str:
        """Build personality description from config."""
        traits = self.personality.get('traits', [])
        style = self.personality.get('communication_style', 'balanced')
        formality = self.personality.get('formality_level', 'professional')
        
        if not traits:
            return ""
        
        return (f"Your personality traits include: {', '.join(traits)}. "
                f"You communicate in a {style} manner with {formality} formality.")
    
    def build_capabilities_description(self) -> str:
        """Build capabilities description from config."""
        capabilities = self.config.get('capabilities', [])
        if not capabilities:
            return ""
        
        return f"Your capabilities include: {', '.join(capabilities)}."
    
    @abstractmethod
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """
        Process incoming message and generate response.
        
        Args:
            message: User input message
            context: Conversation context and metadata
            
        Returns:
            Generated response string
        """
        pass
    
    def preprocess_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess the incoming message before AI processing.
        
        Args:
            message: Raw user message
            context: Current conversation context
            
        Returns:
            Processed context with enhanced information
        """
        # Add personality context
        context['personality'] = self.personality
        
        # Add conversation history if available
        conversation_id = context.get('conversation_id')
        if conversation_id and conversation_id in self.conversation_memory:
            context['recent_history'] = self.conversation_memory[conversation_id][-10:]
        
        # Add agent-specific context
        context['agent_capabilities'] = self.capabilities
        context['agent_config'] = self.config
        
        return context
    
    def postprocess_response(self, response: str, context: Dict[str, Any]) -> str:
        """
        Postprocess the AI response before returning to user.
        
        Args:
            response: Raw AI response
            context: Conversation context
            
        Returns:
            Processed response string
        """
        # Apply personality filters
        response = self.apply_personality_filters(response)
        
        # Apply formatting based on agent preferences
        response = self.apply_formatting(response)
        
        # Store in conversation memory
        self.update_conversation_memory(context, response)
        
        return response
    
    def apply_personality_filters(self, response: str) -> str:
        """Apply personality-based filters to the response."""
        # Implement personality-specific modifications
        formality = self.personality.get('formality_level', 'professional')
        
        if formality == 'casual':
            # Make response more casual
            response = response.replace('I would recommend', "I'd suggest")
            response = response.replace('Please note that', "Just so you know")
        elif formality == 'formal':
            # Make response more formal
            response = response.replace("can't", "cannot")
            response = response.replace("don't", "do not")
        
        return response
    
    def apply_formatting(self, response: str) -> str:
        """Apply agent-specific formatting to response."""
        formatting = self.config.get('formatting', {})
        
        # Apply bullet points if preferred
        if formatting.get('use_bullet_points', False):
            # Convert numbered lists to bullet points
            import re
            response = re.sub(r'^\d+\.\s+', '• ', response, flags=re.MULTILINE)
        
        # Apply emphasis if preferred
        if formatting.get('use_emphasis', False):
            # Add emphasis to key points
            response = re.sub(r'\b(important|key|critical|essential)\b', 
                            r'**\1**', response, flags=re.IGNORECASE)
        
        return response
    
    def update_conversation_memory(self, context: Dict[str, Any], response: str):
        """Update conversation memory with recent exchange."""
        conversation_id = context.get('conversation_id')
        if not conversation_id:
            return
        
        if conversation_id not in self.conversation_memory:
            self.conversation_memory[conversation_id] = []
        
        # Add user message and agent response to memory
        user_message = context.get('user_message', '')
        self.conversation_memory[conversation_id].extend([
            {'role': 'user', 'content': user_message},
            {'role': 'assistant', 'content': response}
        ])
        
        # Keep only last 50 exchanges
        if len(self.conversation_memory[conversation_id]) > 100:
            self.conversation_memory[conversation_id] = \
                self.conversation_memory[conversation_id][-100:]
    
    def get_ai_parameters(self) -> Dict[str, Any]:
        """Get AI model parameters from configuration."""
        return self.config.get('parameters', {
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 0.9,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0
        })
    
    def validate_input(self, message: str) -> bool:
        """Validate user input message."""
        if not message or not message.strip():
            return False
        
        # Check message length limits
        max_length = self.config.get('limits', {}).get('max_input_length', 10000)
        if len(message) > max_length:
            return False
        
        return True
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> str:
        """Handle errors gracefully with agent-appropriate responses."""
        error_responses = self.config.get('error_responses', {
            'default': "I apologize, but I'm experiencing technical difficulties. Please try again.",
            'timeout': "I'm taking longer than usual to respond. Please be patient or try again.",
            'invalid_input': "I couldn't understand your request. Could you please rephrase it?"
        })
        
        error_type = type(error).__name__.lower()
        return error_responses.get(error_type, error_responses['default'])

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