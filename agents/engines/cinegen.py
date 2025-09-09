"""
OneLastAI Platform - CineGen Agent Engine
Cinematic and video content generation specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CineGenEngine(BaseAgentEngine):
    """
    CineGen - Cinematic Generation Engine
    Specializes in video content creation, storytelling, and cinematic production
    """
    
    def __init__(self):
        super().__init__('cinegen')
        self.content_formats = self.initialize_content_formats()
    
    def initialize_content_formats(self) -> Dict[str, Any]:
        """Initialize video content formats and their characteristics."""
        return {
            'short_form': {
                'duration': '15-60 seconds',
                'platforms': ['tiktok', 'instagram_reels', 'youtube_shorts'],
                'style': 'fast_paced_engaging',
                'elements': ['hook', 'quick_story', 'call_to_action']
            },
            'medium_form': {
                'duration': '1-10 minutes',
                'platforms': ['youtube', 'instagram', 'twitter'],
                'style': 'informative_entertaining',
                'elements': ['intro', 'main_content', 'conclusion']
            },
            'long_form': {
                'duration': '10+ minutes',
                'platforms': ['youtube', 'vimeo', 'streaming'],
                'style': 'comprehensive_narrative',
                'elements': ['introduction', 'development', 'climax', 'resolution']
            },
            'commercial': {
                'duration': '15-60 seconds',
                'platforms': ['tv', 'streaming', 'social_media'],
                'style': 'persuasive_memorable',
                'elements': ['attention', 'interest', 'desire', 'action']
            },
            'documentary': {
                'duration': '20+ minutes',
                'platforms': ['streaming', 'tv', 'film_festivals'],
                'style': 'informative_compelling',
                'elements': ['premise', 'investigation', 'evidence', 'conclusion']
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with cinematic content generation focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'cinematic_generation'
            context['user_message'] = message
            
            # Analyze cinematic intent
            cinematic_analysis = self.analyze_cinematic_intent(message)
            context['cinematic_analysis'] = cinematic_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build cinematic-focused system prompt
            cinematic_prompt = self.build_cinematic_prompt(cinematic_analysis)
            enhanced_prompt = self.system_prompt + cinematic_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-6:])
            
            messages.append({'role': 'user', 'content': message})
            
            # Use creative parameters for cinematic content
            params = self.get_ai_parameters()
            params['temperature'] = 0.85  # Higher creativity for content generation
            
            response = ai_service.chat_completion(
                messages=messages,
                **params
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in CineGen engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_cinematic_intent(self, message: str) -> Dict[str, Any]:
        """Analyze cinematic content creation intent."""
        message_lower = message.lower()
        
        # Detect content format
        format_indicators = {}
        for format_type, config in self.content_formats.items():
            score = 0
            if any(platform in message_lower for platform in config.get('platforms', [])):
                score += 2
            if any(element in message_lower for element in config.get('elements', [])):
                score += 1
            if score > 0:
                format_indicators[format_type] = score
        
        # Detect production phases
        phases = {
            'concept': any(word in message_lower for word in 
                           ['concept', 'idea', 'brainstorm', 'theme']),
            'script': any(word in message_lower for word in 
                          ['script', 'screenplay', 'dialogue', 'story']),
            'production': any(word in message_lower for word in 
                              ['shoot', 'film', 'record', 'production']),
            'post_production': any(word in message_lower for word in 
                                   ['edit', 'post', 'effects', 'color', 'sound'])
        }
        
        # Detect genres and styles
        genres = {
            'drama': any(word in message_lower for word in 
                         ['drama', 'emotional', 'character']),
            'comedy': any(word in message_lower for word in 
                          ['comedy', 'funny', 'humor']),
            'action': any(word in message_lower for word in 
                          ['action', 'adventure', 'thriller']),
            'documentary': any(word in message_lower for word in 
                               ['documentary', 'factual', 'real']),
            'commercial': any(word in message_lower for word in 
                              ['commercial', 'ad', 'marketing'])
        }
        
        primary_format = max(format_indicators.items(), key=lambda x: x[1])[0] \
                        if format_indicators else 'medium_form'
        
        primary_phase = max(phases.items(), key=lambda x: x[1])[0] \
                       if any(phases.values()) else 'concept'
        
        detected_genres = [genre for genre, detected in genres.items() if detected]
        
        return {
            'format': primary_format,
            'phase': primary_phase,
            'genres': detected_genres if detected_genres else ['general'],
            'visual_elements': self.extract_visual_elements(message)
        }
    
    def extract_visual_elements(self, message: str) -> List[str]:
        """Extract visual and cinematic elements mentioned."""
        elements = [
            'cinematography', 'lighting', 'composition', 'color_grading',
            'camera_movement', 'framing', 'editing', 'transitions',
            'visual_effects', 'animation', 'graphics', 'typography',
            'music', 'sound_design', 'voiceover', 'dialogue'
        ]
        
        message_lower = message.lower()
        detected = [element for element in elements 
                   if element.replace('_', ' ') in message_lower or element in message_lower]
        
        return detected[:8]  # Return up to 8 visual elements
    
    def build_cinematic_prompt(self, cinematic_analysis: Dict[str, Any]) -> str:
        """Build cinematic content generation focused prompt."""
        format_type = cinematic_analysis['format']
        phase = cinematic_analysis['phase']
        genres = cinematic_analysis['genres']
        visual_elements = cinematic_analysis.get('visual_elements', [])
        
        prompt = f"\n\nCinematic Focus: {format_type.replace('_', ' ').title()} Content"
        prompt += f"\n- Production Phase: {phase.replace('_', ' ').title()}"
        prompt += f"\n- Genres: {', '.join([g.title() for g in genres])}"
        
        if visual_elements:
            prompt += f"\n- Visual Elements: {', '.join([e.replace('_', ' ') for e in visual_elements])}"
        
        # Add format-specific guidance
        if format_type in self.content_formats:
            format_config = self.content_formats[format_type]
            prompt += f"\n- Duration: {format_config['duration']}"
            prompt += f"\n- Style: {format_config['style'].replace('_', ' ')}"
            prompt += f"\n- Key Elements: {', '.join(format_config['elements'])}"
        
        phase_guidance = {
            'concept': "Focus on creative ideation, theme development, and conceptual framework.",
            'script': "Focus on narrative structure, dialogue, character development, and storytelling.",
            'production': "Focus on filming techniques, direction, cinematography, and production logistics.",
            'post_production': "Focus on editing, effects, color grading, sound design, and final polish."
        }
        
        prompt += f"\n\nPhase Guidance: {phase_guidance.get(phase, 'Provide comprehensive cinematic guidance.')}"
        
        return prompt