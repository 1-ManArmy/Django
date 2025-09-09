"""
OneLastAI Platform - IdeaForge Agent Engine
Innovation and ideation specialist for creative problem-solving
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class IdeaForgeEngine(BaseAgentEngine):
    """
    IdeaForge - Innovation & Ideation Engine
    Specializes in creative thinking, innovation, and idea development
    """
    
    def __init__(self):
        super().__init__('ideaforge')
        self.thinking_methods = self.initialize_thinking_methods()
    
    def initialize_thinking_methods(self) -> Dict[str, Any]:
        """Initialize creative thinking and ideation methods."""
        return {
            'brainstorming': {
                'techniques': ['mind_mapping', 'word_association', 'free_writing'],
                'focus': 'quantity_over_quality',
                'approach': 'divergent_thinking'
            },
            'design_thinking': {
                'techniques': ['empathy_mapping', 'problem_definition', 'ideation', 'prototyping'],
                'focus': 'user_centered_solutions',
                'approach': 'human_centered_design'
            },
            'scamper': {
                'techniques': ['substitute', 'combine', 'adapt', 'modify', 'put_to_use', 'eliminate', 'reverse'],
                'focus': 'systematic_innovation',
                'approach': 'structured_creativity'
            },
            'lateral_thinking': {
                'techniques': ['random_stimulation', 'provocation', 'alternatives'],
                'focus': 'unconventional_solutions',
                'approach': 'pattern_breaking'
            },
            'six_hats': {
                'techniques': ['facts', 'emotions', 'caution', 'optimism', 'creativity', 'process'],
                'focus': 'comprehensive_analysis',
                'approach': 'multi_perspective_thinking'
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with innovation and ideation focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'innovation_ideation'
            context['user_message'] = message
            
            # Analyze ideation intent
            ideation_analysis = self.analyze_ideation_intent(message)
            context['ideation_analysis'] = ideation_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build ideation-focused system prompt
            ideation_prompt = self.build_ideation_prompt(ideation_analysis)
            enhanced_prompt = self.system_prompt + ideation_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-6:])
            
            messages.append({'role': 'user', 'content': message})
            
            # Use high creativity parameters for ideation
            params = self.get_ai_parameters()
            params['temperature'] = 0.9  # High creativity
            params['top_p'] = 0.95  # High diversity
            
            response = ai_service.chat_completion(
                messages=messages,
                **params
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in IdeaForge engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_ideation_intent(self, message: str) -> Dict[str, Any]:
        """Analyze ideation and innovation intent."""
        message_lower = message.lower()
        
        # Detect thinking method preferences
        method_indicators = {}
        for method, config in self.thinking_methods.items():
            score = 0
            if method.replace('_', ' ') in message_lower:
                score += 3
            for technique in config['techniques']:
                if technique.replace('_', ' ') in message_lower:
                    score += 1
            if score > 0:
                method_indicators[method] = score
        
        # Detect innovation domains
        domains = {
            'business': any(word in message_lower for word in 
                            ['business', 'startup', 'company', 'revenue']),
            'technology': any(word in message_lower for word in 
                              ['technology', 'software', 'app', 'digital']),
            'product': any(word in message_lower for word in 
                           ['product', 'service', 'solution', 'offering']),
            'process': any(word in message_lower for word in 
                           ['process', 'workflow', 'system', 'method']),
            'creative': any(word in message_lower for word in 
                            ['art', 'design', 'creative', 'aesthetic'])
        }
        
        # Detect ideation goals
        goals = {
            'problem_solving': any(word in message_lower for word in 
                                   ['problem', 'challenge', 'issue', 'solve']),
            'innovation': any(word in message_lower for word in 
                              ['innovate', 'new', 'novel', 'breakthrough']),
            'improvement': any(word in message_lower for word in 
                               ['improve', 'enhance', 'optimize', 'better']),
            'exploration': any(word in message_lower for word in 
                               ['explore', 'discover', 'investigate', 'research'])
        }
        
        best_method = max(method_indicators.items(), key=lambda x: x[1])[0] \
                     if method_indicators else 'brainstorming'
        
        primary_domain = max(domains.items(), key=lambda x: x[1])[0] \
                        if any(domains.values()) else 'general'
        
        primary_goal = max(goals.items(), key=lambda x: x[1])[0] \
                      if any(goals.values()) else 'innovation'
        
        return {
            'method': best_method,
            'domain': primary_domain,
            'goal': primary_goal,
            'context_keywords': self.extract_context_keywords(message)
        }
    
    def extract_context_keywords(self, message: str) -> List[str]:
        """Extract contextual keywords for ideation focus."""
        import re
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Filter for innovation-relevant terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'idea', 'think', 'create', 'make'
        }
        
        keywords = [word for word in words 
                   if len(word) > 3 and word not in stop_words]
        
        return keywords[:8]  # Return top 8 context keywords
    
    def build_ideation_prompt(self, ideation_analysis: Dict[str, Any]) -> str:
        """Build innovation and ideation focused prompt."""
        method = ideation_analysis['method']
        domain = ideation_analysis['domain']
        goal = ideation_analysis['goal']
        keywords = ideation_analysis.get('context_keywords', [])
        
        prompt = f"\n\nIdeation Focus: {method.replace('_', ' ').title()} Method"
        prompt += f"\n- Domain: {domain.title()}"
        prompt += f"\n- Goal: {goal.replace('_', ' ').title()}"
        
        if keywords:
            prompt += f"\n- Context: {', '.join(keywords[:5])}"
        
        # Add method-specific guidance
        if method in self.thinking_methods:
            method_config = self.thinking_methods[method]
            prompt += f"\n- Techniques: {', '.join([t.replace('_', ' ') for t in method_config['techniques']])}"
            prompt += f"\n- Approach: {method_config['approach'].replace('_', ' ')}"
        
        goal_guidance = {
            'problem_solving': "Focus on identifying root causes and generating multiple solution paths.",
            'innovation': "Focus on breakthrough thinking, novel combinations, and disruptive possibilities.",
            'improvement': "Focus on optimization opportunities, incremental enhancements, and efficiency gains.",
            'exploration': "Focus on discovery, new possibilities, and expanding the solution space."
        }
        
        domain_guidance = {
            'business': "Consider market dynamics, user needs, business models, and value creation.",
            'technology': "Consider technical feasibility, scalability, user experience, and innovation potential.",
            'product': "Consider user needs, functionality, design, and market fit.",
            'process': "Consider efficiency, automation, user experience, and optimization opportunities.",
            'creative': "Consider aesthetic appeal, emotional impact, artistic expression, and cultural relevance."
        }
        
        prompt += f"\n\nGoal Guidance: {goal_guidance.get(goal, 'Generate innovative and creative ideas.')}"
        prompt += f"\nDomain Guidance: {domain_guidance.get(domain, 'Apply creative thinking to the specific context.')}"
        
        return prompt