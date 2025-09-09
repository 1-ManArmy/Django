"""
OneLastAI Platform - Girlfriend Agent Engine
Emotional companion with deep empathy and relationship intelligence
"""
from .base import BaseAgentEngine
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class GirlfriendEngine(BaseAgentEngine):
    """
    Girlfriend - Emotional Companion Engine
    Specializes in emotional support, companionship, and relationship dynamics
    """
    
    def __init__(self):
        super().__init__('girlfriend')
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with emotional companion approach."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'emotional_companion'
            context['user_message'] = message
            
            # Analyze emotional needs
            emotional_state = self.analyze_emotional_needs(message)
            context['emotional_state'] = emotional_state
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build emotionally intelligent system prompt
            emotional_prompt = self.build_emotional_response_prompt(emotional_state)
            enhanced_prompt = self.system_prompt + emotional_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-8:])
            
            messages.append({'role': 'user', 'content': message})
            
            # Use parameters optimized for emotional connection
            params = self.get_ai_parameters()
            params['temperature'] = 0.85  # Higher warmth
            
            response = ai_service.chat_completion(
                messages=messages,
                **params
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in Girlfriend engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_emotional_needs(self, message: str) -> Dict[str, Any]:
        """Analyze the user's emotional needs from their message."""
        message_lower = message.lower()
        
        needs = {
            'support': any(word in message_lower for word in ['sad', 'down', 'upset', 'hurt', 'difficult']),
            'celebration': any(word in message_lower for word in ['happy', 'excited', 'achieved', 'success']),
            'comfort': any(word in message_lower for word in ['lonely', 'scared', 'anxious', 'worried']),
            'validation': any(word in message_lower for word in ['doubt', 'unsure', 'confused', 'lost']),
            'connection': any(word in message_lower for word in ['miss', 'love', 'care', 'together'])
        }
        
        return needs
    
    def build_emotional_response_prompt(self, emotional_state: Dict[str, Any]) -> str:
        """Build emotionally appropriate response prompt."""
        prompt_additions = []
        
        if emotional_state.get('support'):
            prompt_additions.append("\n\nThe user needs emotional support. Be compassionate, understanding, and offer comfort.")
        
        if emotional_state.get('celebration'):
            prompt_additions.append("\n\nThe user is celebrating something positive. Share their joy and excitement.")
        
        if emotional_state.get('comfort'):
            prompt_additions.append("\n\nThe user needs comfort and reassurance. Be gentle, soothing, and protective.")
        
        if emotional_state.get('validation'):
            prompt_additions.append("\n\nThe user needs validation and confidence. Affirm their worth and capabilities.")
        
        if emotional_state.get('connection'):
            prompt_additions.append("\n\nThe user is seeking emotional connection. Be warm, intimate, and emotionally present.")
        
        return ''.join(prompt_additions)