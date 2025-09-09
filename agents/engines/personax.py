"""
OneLastAI Platform - PersonaX Agent Engine
Personality-driven chat specialist with adaptive personality modeling
"""
from .base import BaseAgentEngine
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class PersonaXEngine(BaseAgentEngine):
    """
    PersonaX - Personality-driven Chat Engine
    Specializes in adaptive personality modeling and character-based interactions
    """
    
    def __init__(self):
        super().__init__('personax')
        self.personality_profiles = self.load_personality_profiles()
    
    def load_personality_profiles(self) -> Dict[str, Any]:
        """Load different personality profiles for adaptation."""
        return {
            'enthusiastic': {'energy': 90, 'optimism': 85, 'expressiveness': 80},
            'analytical': {'logic': 90, 'precision': 85, 'methodical': 80},
            'creative': {'imagination': 90, 'artistic': 85, 'unconventional': 80},
            'supportive': {'empathy': 90, 'nurturing': 85, 'patience': 80},
            'professional': {'formal': 85, 'efficient': 80, 'structured': 75}
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with adaptive personality modeling."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'personality_driven'
            context['user_message'] = message
            
            # Detect optimal personality for this interaction
            optimal_persona = self.detect_optimal_personality(message, context)
            context['active_personality'] = optimal_persona
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build personality-adapted system prompt
            persona_prompt = self.build_personality_prompt(optimal_persona)
            enhanced_prompt = self.system_prompt + persona_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-6:])
            
            messages.append({'role': 'user', 'content': message})
            
            response = ai_service.chat_completion(
                messages=messages,
                **self.get_ai_parameters()
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in PersonaX engine: {e}")
            return self.handle_error(e, context)
    
    def detect_optimal_personality(self, message: str, context: Dict[str, Any]) -> str:
        """Detect the optimal personality profile for the current interaction."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['analyze', 'data', 'logic', 'think']):
            return 'analytical'
        elif any(word in message_lower for word in ['creative', 'art', 'imagine', 'design']):
            return 'creative'
        elif any(word in message_lower for word in ['help', 'support', 'advice', 'comfort']):
            return 'supportive'
        elif any(word in message_lower for word in ['business', 'work', 'professional', 'formal']):
            return 'professional'
        else:
            return 'enthusiastic'  # Default to enthusiastic
    
    def build_personality_prompt(self, persona: str) -> str:
        """Build personality-specific prompt addition."""
        profile = self.personality_profiles.get(persona, {})
        
        persona_descriptions = {
            'enthusiastic': "\n\nYou're energetic, optimistic, and expressive. Show excitement and positive energy in your responses.",
            'analytical': "\n\nYou're logical, precise, and methodical. Approach topics with structured thinking and clear analysis.",
            'creative': "\n\nYou're imaginative, artistic, and unconventional. Bring creativity and fresh perspectives to conversations.",
            'supportive': "\n\nYou're empathetic, nurturing, and patient. Focus on providing comfort and understanding support.",
            'professional': "\n\nYou're formal, efficient, and structured. Maintain a business-appropriate tone and organized responses."
        }
        
        return persona_descriptions.get(persona, '')