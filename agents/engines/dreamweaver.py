"""
OneLastAI Platform - DreamWeaver Agent Engine
Creative storytelling and imagination specialist for narrative content
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DreamWeaverEngine(BaseAgentEngine):
    """
    DreamWeaver - Creative Storytelling Engine
    Specializes in narrative creation, world-building, and imaginative content
    """
    
    def __init__(self):
        super().__init__('dreamweaver')
        self.story_elements = self.initialize_story_elements()
    
    def initialize_story_elements(self) -> Dict[str, Any]:
        """Initialize storytelling elements and narrative structures."""
        return {
            'narrative_structures': {
                'three_act': ['setup', 'confrontation', 'resolution'],
                'heros_journey': ['call_to_adventure', 'trials', 'transformation', 'return'],
                'five_act': ['exposition', 'rising_action', 'climax', 'falling_action', 'denouement'],
                'episodic': ['introduction', 'conflict', 'resolution', 'cliffhanger']
            },
            'genres': {
                'fantasy': {
                    'elements': ['magic', 'mythical_creatures', 'otherworldly_settings'],
                    'themes': ['good_vs_evil', 'coming_of_age', 'quest']
                },
                'sci_fi': {
                    'elements': ['technology', 'space', 'future_society'],
                    'themes': ['humanity_vs_technology', 'exploration', 'ethics']
                },
                'mystery': {
                    'elements': ['clues', 'investigation', 'revelation'],
                    'themes': ['truth', 'justice', 'hidden_secrets']
                },
                'romance': {
                    'elements': ['relationships', 'emotional_connection', 'obstacles'],
                    'themes': ['love', 'sacrifice', 'personal_growth']
                },
                'thriller': {
                    'elements': ['suspense', 'danger', 'pacing'],
                    'themes': ['survival', 'pursuit', 'revelation']
                }
            },
            'character_archetypes': {
                'hero': 'Protagonist who drives the story forward',
                'mentor': 'Wise guide who provides wisdom and guidance',
                'shadow': 'Antagonist representing opposition or inner conflict',
                'ally': 'Supportive companion who aids the hero',
                'trickster': 'Character who brings humor and unpredictability'
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with creative storytelling focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'creative_storytelling'
            context['user_message'] = message
            
            # Analyze storytelling intent
            story_analysis = self.analyze_storytelling_intent(message)
            context['story_analysis'] = story_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build storytelling-focused system prompt
            story_prompt = self.build_storytelling_prompt(story_analysis)
            enhanced_prompt = self.system_prompt + story_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-8:])
            
            messages.append({'role': 'user', 'content': message})
            
            # Use high creativity parameters for storytelling
            params = self.get_ai_parameters()
            params['temperature'] = 0.9  # Maximum creativity
            params['top_p'] = 0.95  # High diversity
            
            response = ai_service.chat_completion(
                messages=messages,
                **params
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in DreamWeaver engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_storytelling_intent(self, message: str) -> Dict[str, Any]:
        """Analyze storytelling intent and creative requirements."""
        message_lower = message.lower()
        
        # Detect story formats
        formats = {
            'short_story': any(word in message_lower for word in 
                               ['short story', 'flash fiction', 'brief tale']),
            'novel': any(word in message_lower for word in 
                         ['novel', 'book', 'long story', 'full length']),
            'screenplay': any(word in message_lower for word in 
                              ['screenplay', 'script', 'movie', 'film']),
            'poem': any(word in message_lower for word in 
                        ['poem', 'poetry', 'verse', 'lyrical']),
            'dialogue': any(word in message_lower for word in 
                            ['dialogue', 'conversation', 'exchange', 'talk'])
        }
        
        # Detect genres
        detected_genres = []
        for genre, config in self.story_elements['genres'].items():
            if genre.replace('_', ' ') in message_lower or genre in message_lower:
                detected_genres.append(genre)
            elif any(element.replace('_', ' ') in message_lower 
                    for element in config['elements']):
                detected_genres.append(genre)
        
        # Detect story development phase
        phases = {
            'ideation': any(word in message_lower for word in 
                            ['idea', 'concept', 'brainstorm', 'inspiration']),
            'planning': any(word in message_lower for word in 
                            ['outline', 'structure', 'plot', 'plan']),
            'writing': any(word in message_lower for word in 
                           ['write', 'draft', 'create', 'compose']),
            'revision': any(word in message_lower for word in 
                            ['revise', 'edit', 'improve', 'refine'])
        }
        
        primary_format = max(formats.items(), key=lambda x: x[1])[0] \
                        if any(formats.values()) else 'short_story'
        
        primary_phase = max(phases.items(), key=lambda x: x[1])[0] \
                       if any(phases.values()) else 'ideation'
        
        return {
            'format': primary_format,
            'genres': detected_genres if detected_genres else ['general'],
            'phase': primary_phase,
            'creative_elements': self.extract_creative_elements(message),
            'themes': self.identify_themes(message)
        }
    
    def extract_creative_elements(self, message: str) -> List[str]:
        """Extract creative and narrative elements mentioned."""
        elements = [
            'character', 'plot', 'setting', 'conflict', 'theme', 'dialogue',
            'symbolism', 'metaphor', 'imagery', 'tension', 'twist', 'climax',
            'world_building', 'atmosphere', 'voice', 'perspective'
        ]
        
        message_lower = message.lower()
        detected = [element for element in elements 
                   if element.replace('_', ' ') in message_lower]
        
        return detected[:8]  # Return up to 8 creative elements
    
    def identify_themes(self, message: str) -> List[str]:
        """Identify thematic elements in the message."""
        universal_themes = [
            'love', 'betrayal', 'redemption', 'coming_of_age', 'sacrifice',
            'power', 'freedom', 'identity', 'family', 'friendship', 'justice',
            'survival', 'transformation', 'good_vs_evil', 'hope', 'loss'
        ]
        
        message_lower = message.lower()
        identified_themes = [theme for theme in universal_themes 
                           if theme.replace('_', ' ') in message_lower]
        
        return identified_themes[:4]  # Return up to 4 themes
    
    def build_storytelling_prompt(self, story_analysis: Dict[str, Any]) -> str:
        """Build creative storytelling focused prompt."""
        format_type = story_analysis['format']
        genres = story_analysis['genres']
        phase = story_analysis['phase']
        elements = story_analysis.get('creative_elements', [])
        themes = story_analysis.get('themes', [])
        
        prompt = f"\n\nStorytelling Focus: {format_type.replace('_', ' ').title()}"
        prompt += f"\n- Development Phase: {phase.title()}"
        prompt += f"\n- Genres: {', '.join([g.replace('_', ' ').title() for g in genres])}"
        
        if themes:
            prompt += f"\n- Themes: {', '.join([t.replace('_', ' ') for t in themes])}"
        
        if elements:
            prompt += f"\n- Creative Elements: {', '.join([e.replace('_', ' ') for e in elements])}"
        
        # Add genre-specific guidance
        for genre in genres[:2]:  # Limit to 2 genres for prompt size
            if genre in self.story_elements['genres']:
                genre_info = self.story_elements['genres'][genre]
                prompt += f"\n- {genre.replace('_', ' ').title()} Elements: {', '.join([e.replace('_', ' ') for e in genre_info['elements']])}"
        
        phase_guidance = {
            'ideation': "Focus on creative brainstorming, concept development, and imaginative exploration.",
            'planning': "Focus on story structure, character development, and narrative organization.",
            'writing': "Focus on vivid storytelling, engaging prose, and compelling narrative flow.",
            'revision': "Focus on story enhancement, character depth, and narrative refinement."
        }
        
        format_guidance = {
            'short_story': "Create concise, impactful narrative with focused themes and clear story arc.",
            'novel': "Develop complex, multi-layered narrative with rich character development.",
            'screenplay': "Focus on visual storytelling, dialogue, and dramatic structure.",
            'poem': "Emphasize rhythm, imagery, metaphor, and emotional resonance.",
            'dialogue': "Create authentic, character-driven conversations that reveal personality and advance plot."
        }
        
        prompt += f"\n\nPhase Guidance: {phase_guidance.get(phase, 'Provide comprehensive creative guidance.')}"
        prompt += f"\nFormat Guidance: {format_guidance.get(format_type, 'Create engaging narrative content.')}"
        
        return prompt