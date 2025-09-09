"""
OneLastAI Platform - DocuMind Agent Engine
Advanced documentation and knowledge management specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DocuMindEngine(BaseAgentEngine):
    """
    DocuMind - Documentation Management Engine
    Specializes in creating, organizing, and maintaining documentation systems
    """
    
    def __init__(self):
        super().__init__('documind')
        self.document_types = self.initialize_document_types()
    
    def initialize_document_types(self) -> Dict[str, Any]:
        """Initialize different documentation types and their characteristics."""
        return {
            'technical': {
                'structure': ['overview', 'requirements', 'implementation', 'examples'],
                'style': 'precise_and_detailed',
                'audience': 'developers_and_technical_users'
            },
            'user_guide': {
                'structure': ['introduction', 'getting_started', 'features', 'troubleshooting'],
                'style': 'clear_and_accessible',
                'audience': 'end_users'
            },
            'api': {
                'structure': ['endpoints', 'parameters', 'responses', 'examples'],
                'style': 'structured_and_comprehensive',
                'audience': 'developers'
            },
            'process': {
                'structure': ['purpose', 'steps', 'roles', 'outcomes'],
                'style': 'step_by_step',
                'audience': 'team_members'
            },
            'policy': {
                'structure': ['scope', 'requirements', 'procedures', 'compliance'],
                'style': 'formal_and_authoritative',
                'audience': 'organization_members'
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with documentation focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'documentation_management'
            context['user_message'] = message
            
            # Analyze documentation intent
            doc_plan = self.analyze_documentation_intent(message)
            context['documentation_plan'] = doc_plan
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build documentation-focused system prompt
            doc_prompt = self.build_documentation_prompt(doc_plan)
            enhanced_prompt = self.system_prompt + doc_prompt
            
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
            logger.error(f"Error in DocuMind engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_documentation_intent(self, message: str) -> Dict[str, Any]:
        """Analyze documentation intent and requirements."""
        message_lower = message.lower()
        
        # Determine document type
        doc_type_indicators = {
            'technical': any(word in message_lower for word in 
                             ['technical', 'implementation', 'architecture', 'design']),
            'user_guide': any(word in message_lower for word in 
                              ['user', 'guide', 'tutorial', 'how-to', 'manual']),
            'api': any(word in message_lower for word in 
                       ['api', 'endpoint', 'reference', 'integration']),
            'process': any(word in message_lower for word in 
                           ['process', 'procedure', 'workflow', 'steps']),
            'policy': any(word in message_lower for word in 
                          ['policy', 'standard', 'guideline', 'compliance'])
        }
        
        # Determine documentation action
        actions = {
            'create': any(word in message_lower for word in 
                          ['create', 'write', 'draft', 'new']),
            'update': any(word in message_lower for word in 
                          ['update', 'revise', 'modify', 'change']),
            'organize': any(word in message_lower for word in 
                            ['organize', 'structure', 'arrange', 'format']),
            'review': any(word in message_lower for word in 
                          ['review', 'check', 'validate', 'audit'])
        }
        
        doc_type = max(doc_type_indicators.items(), key=lambda x: x[1])[0] \
                  if any(doc_type_indicators.values()) else 'technical'
        
        action = max(actions.items(), key=lambda x: x[1])[0] \
                if any(actions.values()) else 'create'
        
        return {
            'document_type': doc_type,
            'action': action,
            'structure': self.document_types[doc_type]['structure'],
            'style': self.document_types[doc_type]['style'],
            'audience': self.document_types[doc_type]['audience'],
            'content_areas': self.identify_content_areas(message)
        }
    
    def identify_content_areas(self, message: str) -> List[str]:
        """Identify specific content areas mentioned in the message."""
        import re
        
        # Extract potential content areas
        content_indicators = [
            'introduction', 'overview', 'setup', 'installation', 'configuration',
            'features', 'functionality', 'examples', 'troubleshooting', 'faq',
            'security', 'performance', 'best_practices', 'limitations'
        ]
        
        message_lower = message.lower()
        identified_areas = []
        
        for indicator in content_indicators:
            if indicator in message_lower or indicator.replace('_', ' ') in message_lower:
                identified_areas.append(indicator)
        
        return identified_areas[:6]  # Return up to 6 content areas
    
    def build_documentation_prompt(self, doc_plan: Dict[str, Any]) -> str:
        """Build documentation-focused system prompt."""
        doc_type = doc_plan['document_type']
        action = doc_plan['action']
        structure = doc_plan['structure']
        audience = doc_plan['audience']
        
        prompt = f"\n\nDocumentation Focus: {doc_type.replace('_', ' ').title()} Documentation"
        prompt += f"\n- Action: {action.title()} documentation"
        prompt += f"\n- Target audience: {audience.replace('_', ' ')}"
        prompt += f"\n- Recommended structure: {' → '.join(structure)}"
        
        if doc_plan.get('content_areas'):
            prompt += f"\n- Content areas: {', '.join(doc_plan['content_areas'])}"
        
        action_guidance = {
            'create': "Focus on comprehensive documentation creation with clear structure and examples.",
            'update': "Focus on improving existing documentation while maintaining consistency.",
            'organize': "Focus on logical structure, navigation, and information architecture.",
            'review': "Focus on accuracy, completeness, and adherence to documentation standards."
        }
        
        style_guidance = {
            'precise_and_detailed': "Use precise technical language with detailed explanations.",
            'clear_and_accessible': "Use clear, jargon-free language accessible to all users.",
            'structured_and_comprehensive': "Provide complete, well-organized reference material.",
            'step_by_step': "Break down information into clear, sequential steps.",
            'formal_and_authoritative': "Use formal language with authoritative tone."
        }
        
        prompt += f"\n\nGuidance: {action_guidance.get(action, 'Provide comprehensive documentation support.')}"
        prompt += f"\nStyle: {style_guidance.get(doc_plan['style'], 'Use appropriate documentation style.')}"
        
        return prompt