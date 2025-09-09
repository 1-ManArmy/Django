"""
OneLastAI Platform - Memora Agent Engine
Advanced memory management and knowledge organization specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoraEngine(BaseAgentEngine):
    """
    Memora - Memory Management Engine
    Specializes in information storage, retrieval, and knowledge organization
    """
    
    def __init__(self):
        super().__init__('memora')
        self.memory_types = self.initialize_memory_types()
    
    def initialize_memory_types(self) -> Dict[str, Any]:
        """Initialize different types of memory management."""
        return {
            'episodic': 'Personal experiences and events',
            'semantic': 'Facts, concepts, and general knowledge',
            'procedural': 'Skills, processes, and how-to information',
            'working': 'Temporary information for current tasks',
            'autobiographical': 'Personal history and significant memories'
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with memory-focused approach."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'memory_management'
            context['user_message'] = message
            
            # Analyze memory intent
            memory_intent = self.analyze_memory_intent(message)
            context['memory_intent'] = memory_intent
            
            # Process memory-related operations
            memory_context = self.build_memory_context(message, context)
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build memory-enhanced system prompt
            memory_prompt = self.build_memory_prompt(memory_intent, memory_context)
            enhanced_prompt = self.system_prompt + memory_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-8:])
            
            messages.append({'role': 'user', 'content': message})
            
            response = ai_service.chat_completion(
                messages=messages,
                **self.get_ai_parameters()
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in Memora engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_memory_intent(self, message: str) -> Dict[str, Any]:
        """Analyze what type of memory operation is needed."""
        message_lower = message.lower()
        
        intents = {
            'store': any(word in message_lower for word in ['remember', 'save', 'store', 'note']),
            'recall': any(word in message_lower for word in ['recall', 'remember', 'what was', 'remind']),
            'organize': any(word in message_lower for word in ['organize', 'categorize', 'group', 'structure']),
            'search': any(word in message_lower for word in ['find', 'search', 'look for', 'locate']),
            'update': any(word in message_lower for word in ['update', 'change', 'modify', 'edit']),
            'delete': any(word in message_lower for word in ['delete', 'remove', 'forget', 'clear'])
        }
        
        primary_intent = max(intents.items(), key=lambda x: x[1])
        
        return {
            'primary': primary_intent[0] if primary_intent[1] else 'recall',
            'all_intents': {k: v for k, v in intents.items() if v}
        }
    
    def build_memory_context(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build memory-specific context for processing."""
        return {
            'timestamp': datetime.now().isoformat(),
            'conversation_id': context.get('conversation_id'),
            'user_id': context.get('user_id'),
            'memory_keywords': self.extract_memory_keywords(message),
            'context_importance': self.assess_importance(message)
        }
    
    def extract_memory_keywords(self, message: str) -> List[str]:
        """Extract important keywords for memory indexing."""
        # Simple keyword extraction - could be enhanced with NLP
        import re
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        return keywords[:10]  # Return top 10 keywords
    
    def assess_importance(self, message: str) -> str:
        """Assess the importance level of the information."""
        importance_indicators = {
            'high': ['important', 'critical', 'urgent', 'must', 'essential'],
            'medium': ['should', 'need', 'want', 'prefer'],
            'low': ['maybe', 'perhaps', 'might', 'could']
        }
        
        message_lower = message.lower()
        
        for level, indicators in importance_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                return level
        
        return 'medium'  # Default importance
    
    def build_memory_prompt(self, memory_intent: Dict[str, Any], memory_context: Dict[str, Any]) -> str:
        """Build memory-focused system prompt."""
        intent = memory_intent['primary']
        
        intent_prompts = {
            'store': "\n\nFocus on information storage: Help organize and structure information for future retrieval. Create clear categories and relationships.",
            'recall': "\n\nFocus on information retrieval: Help access and present stored information clearly and contextually.",
            'organize': "\n\nFocus on information organization: Structure data logically with clear hierarchies and relationships.",
            'search': "\n\nFocus on information discovery: Help locate relevant information using various search strategies.",
            'update': "\n\nFocus on information modification: Help update existing information while maintaining context and relationships.",
            'delete': "\n\nFocus on information removal: Help safely remove information while considering dependencies and relationships."
        }
        
        base_prompt = intent_prompts.get(intent, '')
        
        if memory_context.get('context_importance') == 'high':
            base_prompt += "\n\nThis information appears to be highly important - treat with special attention."
        
        return base_prompt