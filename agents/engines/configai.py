"""
OneLastAI Platform - ConfigAI Agent Engine
AI configuration and optimization specialist for AI systems and parameters
"""
from .base import BaseAgentEngine
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConfigAIEngine(BaseAgentEngine):
    """
    ConfigAI - AI Configuration Engine
    Specializes in AI system configuration, parameter optimization, and setup
    """
    
    def __init__(self):
        super().__init__('configai')
        self.ai_config_templates = self.load_ai_config_templates()
    
    def load_ai_config_templates(self) -> Dict[str, Any]:
        """Load AI configuration templates for different use cases."""
        return {
            'creative': {
                'temperature': 0.9,
                'top_p': 0.95,
                'frequency_penalty': 0.1,
                'presence_penalty': 0.1
            },
            'analytical': {
                'temperature': 0.3,
                'top_p': 0.8,
                'frequency_penalty': 0.5,
                'presence_penalty': 0.3
            },
            'balanced': {
                'temperature': 0.7,
                'top_p': 0.9,
                'frequency_penalty': 0.3,
                'presence_penalty': 0.2
            },
            'precise': {
                'temperature': 0.1,
                'top_p': 0.7,
                'frequency_penalty': 0.8,
                'presence_penalty': 0.5
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with AI configuration focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'ai_configuration'
            context['user_message'] = message
            
            # Analyze configuration intent
            config_intent = self.analyze_config_intent(message)
            context['config_intent'] = config_intent
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build configuration-focused system prompt
            config_prompt = self.build_config_prompt(config_intent)
            enhanced_prompt = self.system_prompt + config_prompt
            
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
            logger.error(f"Error in ConfigAI engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_config_intent(self, message: str) -> Dict[str, Any]:
        """Analyze AI configuration related intent."""
        message_lower = message.lower()
        
        intents = {
            'parameter_tuning': any(word in message_lower for word in 
                                    ['parameter', 'tuning', 'temperature', 'top_p']),
            'model_selection': any(word in message_lower for word in 
                                   ['model', 'gpt', 'claude', 'choose']),
            'prompt_engineering': any(word in message_lower for word in 
                                      ['prompt', 'system', 'engineering']),
            'optimization': any(word in message_lower for word in 
                                ['optimize', 'improve', 'enhance', 'better']),
            'troubleshooting': any(word in message_lower for word in 
                                   ['error', 'problem', 'issue', 'fix']),
            'setup': any(word in message_lower for word in 
                         ['setup', 'configure', 'install', 'initialize'])
        }
        
        # Detect configuration type
        config_types = []
        if any(word in message_lower for word in ['creative', 'art', 'story']):
            config_types.append('creative')
        elif any(word in message_lower for word in ['analysis', 'data', 'precise']):
            config_types.append('analytical')
        elif any(word in message_lower for word in ['accurate', 'exact', 'precise']):
            config_types.append('precise')
        else:
            config_types.append('balanced')
        
        return {
            'primary_intent': max(intents.items(), key=lambda x: x[1])[0] 
                             if any(intents.values()) else 'general',
            'config_type': config_types[0],
            'all_intents': {k: v for k, v in intents.items() if v}
        }
    
    def build_config_prompt(self, config_intent: Dict[str, Any]) -> str:
        """Build AI configuration focused prompt."""
        intent = config_intent['primary_intent']
        config_type = config_intent['config_type']
        
        intent_prompts = {
            'parameter_tuning': f"\n\nFocus on AI parameter optimization for {config_type} use cases. Provide specific parameter recommendations.",
            'model_selection': "\n\nFocus on AI model selection. Compare different models and their strengths for specific use cases.",
            'prompt_engineering': "\n\nFocus on prompt engineering best practices. Help create effective system prompts and user interactions.",
            'optimization': "\n\nFocus on AI system optimization. Identify bottlenecks and provide improvement strategies.",
            'troubleshooting': "\n\nFocus on AI troubleshooting. Diagnose issues and provide step-by-step solutions.",
            'setup': "\n\nFocus on AI system setup and configuration. Provide clear implementation guidance."
        }
        
        base_prompt = intent_prompts.get(intent, '')
        
        if config_type in self.ai_config_templates:
            template = self.ai_config_templates[config_type]
            base_prompt += f"\n\nRecommended {config_type} configuration: {template}"
        
        return base_prompt