"""
OneLastAI Platform - NeoChat Agent Engine
Advanced conversational AI with sophisticated dialogue capabilities
"""
from .base import BaseAgentEngine
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class NeoChatEngine(BaseAgentEngine):
    """
    NeoChat - Advanced Conversational AI Engine
    Specializes in natural, engaging conversations with emotional intelligence
    """
    
    def __init__(self):
        super().__init__('neochat')
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process conversational message with advanced dialogue techniques."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            # Enhance context for advanced conversation
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'advanced_dialogue'
            context['emotional_awareness'] = True
            context['user_message'] = message
            
            # Analyze conversation sentiment and adjust response style
            sentiment = self.analyze_sentiment(message)
            context['sentiment'] = sentiment
            
            # Use AI service for generation
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build enhanced system prompt for NeoChat
            enhanced_prompt = self.system_prompt + f"""
            
            Current conversation context:
            - Sentiment: {sentiment}
            - User seems: {self.interpret_user_state(message)}
            
            Respond with:
            - Natural, flowing conversation
            - Emotional intelligence and empathy
            - Engaging follow-up questions when appropriate
            - Personal but respectful tone
            """
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            # Add conversation history
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-8:])
            
            messages.append({'role': 'user', 'content': message})
            
            # Generate response with optimized parameters for conversation
            params = self.get_ai_parameters()
            params['temperature'] = 0.8  # Higher creativity for natural conversation
            
            response = ai_service.chat_completion(
                messages=messages,
                **params
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in NeoChat engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_sentiment(self, message: str) -> str:
        """Analyze the sentiment of the user's message."""
        # Simple keyword-based sentiment analysis
        positive_keywords = ['happy', 'great', 'awesome', 'love', 'excited', 'wonderful']
        negative_keywords = ['sad', 'angry', 'frustrated', 'hate', 'terrible', 'awful']
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in message_lower)
        negative_count = sum(1 for word in negative_keywords if word in message_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def interpret_user_state(self, message: str) -> str:
        """Interpret the user's emotional/mental state from their message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['help', 'confused', 'stuck']):
            return 'seeking help'
        elif any(word in message_lower for word in ['excited', 'amazing', 'wow']):
            return 'enthusiastic'
        elif any(word in message_lower for word in ['tired', 'exhausted', 'stressed']):
            return 'fatigued'
        elif '?' in message:
            return 'curious'
        else:
            return 'conversational'