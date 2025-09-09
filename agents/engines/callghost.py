"""
OneLastAI Platform - CallGhost Agent Engine
Advanced communication assistant for calls, meetings, and voice interactions
"""
from .base import BaseAgentEngine
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class CallGhostEngine(BaseAgentEngine):
    """
    CallGhost - Communication Assistant Engine
    Specializes in call preparation, meeting facilitation, and voice communication
    """
    
    def __init__(self):
        super().__init__('callghost')
        self.communication_modes = self.load_communication_modes()
    
    def load_communication_modes(self) -> Dict[str, Any]:
        """Load different communication scenarios and approaches."""
        return {
            'meeting_prep': {
                'focus': 'agenda_creation',
                'tone': 'professional',
                'structure': 'organized'
            },
            'call_script': {
                'focus': 'conversation_flow',
                'tone': 'natural',
                'structure': 'flexible'
            },
            'presentation': {
                'focus': 'clear_delivery',
                'tone': 'confident',
                'structure': 'logical'
            },
            'negotiation': {
                'focus': 'strategic_planning',
                'tone': 'diplomatic',
                'structure': 'tactical'
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with communication assistance focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'communication_assistance'
            context['user_message'] = message
            
            # Identify communication scenario
            comm_scenario = self.identify_communication_scenario(message)
            context['communication_scenario'] = comm_scenario
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build scenario-specific system prompt
            scenario_prompt = self.build_scenario_prompt(comm_scenario)
            enhanced_prompt = self.system_prompt + scenario_prompt
            
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
            logger.error(f"Error in CallGhost engine: {e}")
            return self.handle_error(e, context)
    
    def identify_communication_scenario(self, message: str) -> str:
        """Identify the type of communication scenario."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['meeting', 'agenda', 'discussion']):
            return 'meeting_prep'
        elif any(word in message_lower for word in ['call', 'phone', 'conversation']):
            return 'call_script'
        elif any(word in message_lower for word in ['present', 'pitch', 'demo']):
            return 'presentation'
        elif any(word in message_lower for word in ['negotiate', 'deal', 'contract']):
            return 'negotiation'
        else:
            return 'call_script'  # Default
    
    def build_scenario_prompt(self, scenario: str) -> str:
        """Build scenario-specific communication prompt."""
        mode = self.communication_modes.get(scenario, {})
        
        scenario_prompts = {
            'meeting_prep': "\n\nFocus on meeting preparation: Create clear agendas, define objectives, and structure productive discussions.",
            'call_script': "\n\nFocus on natural conversation flow: Help create engaging, authentic dialogue that feels natural and effective.",
            'presentation': "\n\nFocus on clear delivery: Structure information for maximum impact, clarity, and audience engagement.",
            'negotiation': "\n\nFocus on strategic communication: Balance assertiveness with diplomacy, prepare for various scenarios."
        }
        
        return scenario_prompts.get(scenario, '')