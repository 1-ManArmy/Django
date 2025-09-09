"""
OneLastAI Platform - InfoSeek Agent Engine
Advanced information research and discovery specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class InfoSeekEngine(BaseAgentEngine):
    """
    InfoSeek - Information Research Engine
    Specializes in research methodology, information discovery, and data analysis
    """
    
    def __init__(self):
        super().__init__('infoseek')
        self.research_methods = self.initialize_research_methods()
    
    def initialize_research_methods(self) -> Dict[str, Any]:
        """Initialize different research methodologies."""
        return {
            'academic': {
                'sources': ['scholarly_articles', 'peer_reviewed', 'journals'],
                'approach': 'systematic_review',
                'validation': 'citation_analysis'
            },
            'market': {
                'sources': ['industry_reports', 'surveys', 'statistics'],
                'approach': 'competitive_analysis',
                'validation': 'cross_reference'
            },
            'technical': {
                'sources': ['documentation', 'specifications', 'forums'],
                'approach': 'hands_on_testing',
                'validation': 'expert_verification'
            },
            'news': {
                'sources': ['news_outlets', 'press_releases', 'social_media'],
                'approach': 'real_time_monitoring',
                'validation': 'source_credibility'
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with research methodology focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'information_research'
            context['user_message'] = message
            
            # Analyze research intent and methodology
            research_plan = self.analyze_research_intent(message)
            context['research_plan'] = research_plan
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build research-focused system prompt
            research_prompt = self.build_research_prompt(research_plan)
            enhanced_prompt = self.system_prompt + research_prompt
            
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
            logger.error(f"Error in InfoSeek engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_research_intent(self, message: str) -> Dict[str, Any]:
        """Analyze research intent and determine optimal methodology."""
        message_lower = message.lower()
        
        # Determine research type
        research_types = {
            'academic': any(word in message_lower for word in 
                            ['research', 'study', 'paper', 'academic', 'scholarly']),
            'market': any(word in message_lower for word in 
                          ['market', 'industry', 'business', 'competitor']),
            'technical': any(word in message_lower for word in 
                             ['technical', 'specification', 'how-to', 'implement']),
            'news': any(word in message_lower for word in 
                        ['news', 'current', 'recent', 'latest', 'trending'])
        }
        
        # Determine research depth
        depth_indicators = {
            'deep': any(word in message_lower for word in 
                        ['comprehensive', 'detailed', 'thorough', 'complete']),
            'quick': any(word in message_lower for word in 
                         ['quick', 'brief', 'summary', 'overview']),
            'focused': any(word in message_lower for word in 
                           ['specific', 'particular', 'focused', 'targeted'])
        }
        
        primary_type = max(research_types.items(), key=lambda x: x[1])[0] \
                      if any(research_types.values()) else 'academic'
        
        depth = max(depth_indicators.items(), key=lambda x: x[1])[0] \
               if any(depth_indicators.values()) else 'focused'
        
        return {
            'research_type': primary_type,
            'depth': depth,
            'methodology': self.research_methods.get(primary_type, {}),
            'keywords': self.extract_research_keywords(message)
        }
    
    def extract_research_keywords(self, message: str) -> List[str]:
        """Extract key research terms from the message."""
        import re
        
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Filter out common words and focus on research-relevant terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'what', 'how', 'when', 'where', 
            'why', 'find', 'search', 'look', 'get', 'need', 'want'
        }
        
        keywords = [word for word in words 
                   if len(word) > 3 and word not in stop_words]
        
        return keywords[:8]  # Return top 8 keywords
    
    def build_research_prompt(self, research_plan: Dict[str, Any]) -> str:
        """Build research methodology focused prompt."""
        research_type = research_plan['research_type']
        depth = research_plan['depth']
        methodology = research_plan['methodology']
        
        prompt = f"\n\nResearch Focus: {research_type.title()} Research"
        prompt += f"\n- Depth: {depth} investigation"
        
        if methodology:
            prompt += f"\n- Preferred sources: {', '.join(methodology.get('sources', []))}"
            prompt += f"\n- Approach: {methodology.get('approach', 'systematic')}"
            prompt += f"\n- Validation method: {methodology.get('validation', 'cross_reference')}"
        
        if research_plan.get('keywords'):
            prompt += f"\n- Key terms: {', '.join(research_plan['keywords'])}"
        
        type_guidance = {
            'academic': "Focus on peer-reviewed sources, systematic methodology, and scholarly rigor.",
            'market': "Focus on industry data, competitive analysis, and business intelligence.",
            'technical': "Focus on documentation, specifications, and practical implementation.",
            'news': "Focus on current events, trending topics, and real-time information."
        }
        
        prompt += f"\n\nGuidance: {type_guidance.get(research_type, 'Provide comprehensive research analysis.')}"
        
        return prompt