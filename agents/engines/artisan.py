"""
OneLastAI Platform - Artisan Agent Engine
Creative arts and crafts specialist for artistic creation and design
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ArtisanEngine(BaseAgentEngine):
    """
    Artisan - Creative Arts Engine
    Specializes in artistic creation, crafts, design, and creative techniques
    """
    
    def __init__(self):
        super().__init__('artisan')
        self.art_mediums = self.initialize_art_mediums()
    
    def initialize_art_mediums(self) -> Dict[str, Any]:
        """Initialize artistic mediums and their characteristics."""
        return {
            'digital_art': {
                'tools': ['photoshop', 'illustrator', 'procreate', 'blender'],
                'techniques': ['layering', 'blending', 'masking', 'lighting'],
                'styles': ['realistic', 'abstract', 'minimalist', 'surreal']
            },
            'traditional_painting': {
                'tools': ['oils', 'acrylics', 'watercolors', 'pastels'],
                'techniques': ['blending', 'glazing', 'impasto', 'wet_on_wet'],
                'styles': ['realism', 'impressionism', 'abstract', 'expressionism']
            },
            'drawing': {
                'tools': ['pencil', 'charcoal', 'ink', 'markers'],
                'techniques': ['shading', 'cross_hatching', 'stippling', 'blending'],
                'styles': ['realistic', 'cartoon', 'sketch', 'technical']
            },
            'sculpture': {
                'tools': ['clay', 'stone', 'metal', 'wood'],
                'techniques': ['carving', 'modeling', 'casting', 'welding'],
                'styles': ['abstract', 'figurative', 'modern', 'classical']
            },
            'crafts': {
                'tools': ['fabric', 'yarn', 'beads', 'paper'],
                'techniques': ['sewing', 'knitting', 'weaving', 'origami'],
                'styles': ['traditional', 'modern', 'bohemian', 'minimalist']
            },
            'graphic_design': {
                'tools': ['design_software', 'typography', 'color_theory'],
                'techniques': ['composition', 'hierarchy', 'contrast', 'alignment'],
                'styles': ['modern', 'vintage', 'minimal', 'bold']
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with artistic creation focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'artistic_creation'
            context['user_message'] = message
            
            # Analyze artistic intent
            artistic_analysis = self.analyze_artistic_intent(message)
            context['artistic_analysis'] = artistic_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build artistic-focused system prompt
            artistic_prompt = self.build_artistic_prompt(artistic_analysis)
            enhanced_prompt = self.system_prompt + artistic_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-6:])
            
            messages.append({'role': 'user', 'content': message})
            
            # Use high creativity parameters for artistic work
            params = self.get_ai_parameters()
            params['temperature'] = 0.85  # High creativity
            
            response = ai_service.chat_completion(
                messages=messages,
                **params
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in Artisan engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_artistic_intent(self, message: str) -> Dict[str, Any]:
        """Analyze artistic creation intent and medium preferences."""
        message_lower = message.lower()
        
        # Detect art medium
        medium_scores = {}
        for medium, config in self.art_mediums.items():
            score = 0
            medium_name = medium.replace('_', ' ')
            if medium_name in message_lower or medium in message_lower:
                score += 3
            
            # Check for medium-specific tools and techniques
            for tool in config['tools']:
                if tool.replace('_', ' ') in message_lower:
                    score += 2
            
            for technique in config['techniques']:
                if technique.replace('_', ' ') in message_lower:
                    score += 1
            
            if score > 0:
                medium_scores[medium] = score
        
        # Detect artistic goals
        goals = {
            'learning': any(word in message_lower for word in 
                            ['learn', 'tutorial', 'how_to', 'beginner']),
            'creation': any(word in message_lower for word in 
                            ['create', 'make', 'design', 'build']),
            'improvement': any(word in message_lower for word in 
                               ['improve', 'better', 'enhance', 'refine']),
            'inspiration': any(word in message_lower for word in 
                               ['inspire', 'ideas', 'creative', 'concept'])
        }
        
        # Detect skill level
        skill_levels = {
            'beginner': any(word in message_lower for word in 
                            ['beginner', 'new', 'start', 'basic']),
            'intermediate': any(word in message_lower for word in 
                                ['intermediate', 'some_experience', 'moderate']),
            'advanced': any(word in message_lower for word in 
                            ['advanced', 'expert', 'professional', 'master'])
        }
        
        # Detect project scope
        scopes = {
            'quick_project': any(word in message_lower for word in 
                                 ['quick', 'simple', 'easy', 'short']),
            'detailed_project': any(word in message_lower for word in 
                                    ['detailed', 'complex', 'elaborate', 'comprehensive']),
            'series': any(word in message_lower for word in 
                          ['series', 'collection', 'multiple', 'set'])
        }
        
        primary_medium = max(medium_scores.items(), key=lambda x: x[1])[0] \
                        if medium_scores else 'digital_art'
        
        primary_goal = max(goals.items(), key=lambda x: x[1])[0] \
                      if any(goals.values()) else 'creation'
        
        skill_level = max(skill_levels.items(), key=lambda x: x[1])[0] \
                     if any(skill_levels.values()) else 'intermediate'
        
        project_scope = max(scopes.items(), key=lambda x: x[1])[0] \
                       if any(scopes.values()) else 'detailed_project'
        
        return {
            'medium': primary_medium,
            'goal': primary_goal,
            'skill_level': skill_level,
            'project_scope': project_scope,
            'artistic_elements': self.extract_artistic_elements(message)
        }
    
    def extract_artistic_elements(self, message: str) -> List[str]:
        """Extract artistic elements and concepts mentioned."""
        elements = [
            'color', 'composition', 'perspective', 'lighting', 'texture',
            'form', 'balance', 'contrast', 'harmony', 'rhythm', 'proportion',
            'style', 'mood', 'theme', 'concept', 'technique', 'medium'
        ]
        
        message_lower = message.lower()
        detected = [element for element in elements if element in message_lower]
        
        return detected[:8]  # Return up to 8 artistic elements
    
    def build_artistic_prompt(self, artistic_analysis: Dict[str, Any]) -> str:
        """Build artistic creation focused prompt."""
        medium = artistic_analysis['medium']
        goal = artistic_analysis['goal']
        skill_level = artistic_analysis['skill_level']
        scope = artistic_analysis['project_scope']
        elements = artistic_analysis.get('artistic_elements', [])
        
        prompt = f"\n\nArtistic Focus: {medium.replace('_', ' ').title()}"
        prompt += f"\n- Goal: {goal.title()}"
        prompt += f"\n- Skill Level: {skill_level.replace('_', ' ').title()}"
        prompt += f"\n- Project Scope: {scope.replace('_', ' ').title()}"
        
        if elements:
            prompt += f"\n- Artistic Elements: {', '.join(elements)}"
        
        # Add medium-specific guidance
        if medium in self.art_mediums:
            medium_config = self.art_mediums[medium]
            prompt += f"\n- Recommended Tools: {', '.join(medium_config['tools'][:3])}"
            prompt += f"\n- Key Techniques: {', '.join([t.replace('_', ' ') for t in medium_config['techniques'][:3]])}"
            prompt += f"\n- Style Options: {', '.join(medium_config['styles'][:3])}"
        
        goal_guidance = {
            'learning': "Focus on educational content, step-by-step instructions, and skill development.",
            'creation': "Focus on practical guidance, creative techniques, and project execution.",
            'improvement': "Focus on advanced techniques, critique, and skill enhancement strategies.",
            'inspiration': "Focus on creative ideas, artistic concepts, and imaginative possibilities."
        }
        
        skill_guidance = {
            'beginner': "Provide clear, detailed instructions with foundational concepts and basic techniques.",
            'intermediate': "Balance technique explanation with creative exploration and skill building.",
            'advanced': "Focus on sophisticated techniques, artistic theory, and professional-level guidance."
        }
        
        scope_guidance = {
            'quick_project': "Focus on simple, achievable projects that can be completed in a short time.",
            'detailed_project': "Provide comprehensive guidance for complex, multi-step artistic endeavors.",
            'series': "Consider project continuity, thematic consistency, and progressive skill development."
        }
        
        prompt += f"\n\nGoal Guidance: {goal_guidance.get(goal, 'Provide comprehensive artistic guidance.')}"
        prompt += f"\nSkill Guidance: {skill_guidance.get(skill_level, 'Match guidance to skill level.')}"
        prompt += f"\nScope Guidance: {scope_guidance.get(scope, 'Align guidance with project scope.')}"
        
        return prompt