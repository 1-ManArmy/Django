"""
OneLastAI Platform - VocaMind Agent Engine
Voice and audio content optimization specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class VocaMindEngine(BaseAgentEngine):
    """
    VocaMind - Voice & Audio Engine
    Specializes in voice optimization, audio content, and speech enhancement
    """
    
    def __init__(self):
        super().__init__('vocamind')
        self.audio_formats = self.initialize_audio_formats()
    
    def initialize_audio_formats(self) -> Dict[str, Any]:
        """Initialize audio content formats and voice optimization strategies."""
        return {
            'podcast': {
                'duration_ranges': ['15-30min', '30-60min', '60+ min'],
                'structure': ['intro', 'main_content', 'segments', 'outro'],
                'voice_style': 'conversational_engaging',
                'pacing': 'moderate_with_pauses'
            },
            'audiobook': {
                'duration_ranges': ['chapter_based', 'full_length'],
                'structure': ['introduction', 'chapters', 'conclusion'],
                'voice_style': 'clear_narrative',
                'pacing': 'steady_consistent'
            },
            'voiceover': {
                'duration_ranges': ['15-60sec', '1-5min', '5+ min'],
                'structure': ['hook', 'message', 'call_to_action'],
                'voice_style': 'professional_persuasive',
                'pacing': 'dynamic_varied'
            },
            'presentation': {
                'duration_ranges': ['5-15min', '15-30min', '30+ min'],
                'structure': ['opening', 'main_points', 'conclusion', 'q_and_a'],
                'voice_style': 'authoritative_clear',
                'pacing': 'measured_emphatic'
            },
            'meditation': {
                'duration_ranges': ['5-10min', '10-20min', '20+ min'],
                'structure': ['introduction', 'guided_content', 'closure'],
                'voice_style': 'calm_soothing',
                'pacing': 'slow_relaxed'
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with voice and audio focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'voice_audio_optimization'
            context['user_message'] = message
            
            # Analyze voice and audio intent
            voice_analysis = self.analyze_voice_intent(message)
            context['voice_analysis'] = voice_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build voice-focused system prompt
            voice_prompt = self.build_voice_prompt(voice_analysis)
            enhanced_prompt = self.system_prompt + voice_prompt
            
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
            logger.error(f"Error in VocaMind engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_voice_intent(self, message: str) -> Dict[str, Any]:
        """Analyze voice and audio optimization intent."""
        message_lower = message.lower()
        
        # Detect audio format
        format_scores = {}
        for audio_format, config in self.audio_formats.items():
            score = 0
            if audio_format in message_lower:
                score += 3
            
            # Check for format-specific indicators
            format_indicators = {
                'podcast': ['episode', 'show', 'interview', 'discussion'],
                'audiobook': ['book', 'narration', 'story', 'chapter'],
                'voiceover': ['commercial', 'ad', 'announcement', 'video'],
                'presentation': ['speech', 'talk', 'lecture', 'conference'],
                'meditation': ['meditation', 'relaxation', 'mindfulness', 'calm']
            }
            
            if audio_format in format_indicators:
                for indicator in format_indicators[audio_format]:
                    if indicator in message_lower:
                        score += 1
            
            if score > 0:
                format_scores[audio_format] = score
        
        # Detect voice optimization goals
        goals = {
            'clarity': any(word in message_lower for word in 
                           ['clarity', 'clear', 'articulation', 'pronunciation']),
            'engagement': any(word in message_lower for word in 
                              ['engaging', 'captivating', 'interesting', 'compelling']),
            'persuasion': any(word in message_lower for word in 
                              ['persuasive', 'convincing', 'influential', 'selling']),
            'emotion': any(word in message_lower for word in 
                           ['emotional', 'feeling', 'mood', 'tone', 'atmosphere']),
            'accessibility': any(word in message_lower for word in 
                                 ['accessible', 'inclusive', 'diverse', 'barrier_free'])
        }
        
        # Detect voice characteristics
        characteristics = {
            'pace': self.detect_pace_preference(message_lower),
            'tone': self.detect_tone_preference(message_lower),
            'style': self.detect_style_preference(message_lower)
        }
        
        primary_format = max(format_scores.items(), key=lambda x: x[1])[0] \
                        if format_scores else 'presentation'
        
        primary_goal = max(goals.items(), key=lambda x: x[1])[0] \
                      if any(goals.values()) else 'clarity'
        
        return {
            'format': primary_format,
            'goal': primary_goal,
            'characteristics': characteristics,
            'audio_elements': self.extract_audio_elements(message)
        }
    
    def detect_pace_preference(self, message_lower: str) -> str:
        """Detect preferred speaking pace."""
        if any(word in message_lower for word in ['fast', 'quick', 'rapid', 'energetic']):
            return 'fast'
        elif any(word in message_lower for word in ['slow', 'calm', 'relaxed', 'measured']):
            return 'slow'
        else:
            return 'moderate'
    
    def detect_tone_preference(self, message_lower: str) -> str:
        """Detect preferred vocal tone."""
        if any(word in message_lower for word in ['formal', 'professional', 'business']):
            return 'formal'
        elif any(word in message_lower for word in ['casual', 'friendly', 'conversational']):
            return 'casual'
        elif any(word in message_lower for word in ['warm', 'caring', 'empathetic']):
            return 'warm'
        else:
            return 'neutral'
    
    def detect_style_preference(self, message_lower: str) -> str:
        """Detect preferred vocal style."""
        if any(word in message_lower for word in ['authoritative', 'confident', 'expert']):
            return 'authoritative'
        elif any(word in message_lower for word in ['storytelling', 'narrative', 'story']):
            return 'narrative'
        elif any(word in message_lower for word in ['educational', 'teaching', 'instructional']):
            return 'educational'
        else:
            return 'conversational'
    
    def extract_audio_elements(self, message: str) -> List[str]:
        """Extract audio-specific elements mentioned."""
        elements = [
            'pacing', 'intonation', 'emphasis', 'pauses', 'rhythm',
            'volume', 'pitch', 'articulation', 'breathing', 'inflection',
            'music', 'sound_effects', 'ambient_sound', 'transitions'
        ]
        
        message_lower = message.lower()
        detected = [element for element in elements 
                   if element.replace('_', ' ') in message_lower]
        
        return detected[:8]  # Return up to 8 audio elements
    
    def build_voice_prompt(self, voice_analysis: Dict[str, Any]) -> str:
        """Build voice and audio optimization focused prompt."""
        audio_format = voice_analysis['format']
        goal = voice_analysis['goal']
        characteristics = voice_analysis['characteristics']
        elements = voice_analysis.get('audio_elements', [])
        
        prompt = f"\n\nVoice Focus: {audio_format.title()} Optimization"
        prompt += f"\n- Primary Goal: {goal.title()}"
        prompt += f"\n- Pace: {characteristics['pace']}"
        prompt += f"\n- Tone: {characteristics['tone']}"
        prompt += f"\n- Style: {characteristics['style']}"
        
        if elements:
            prompt += f"\n- Audio Elements: {', '.join([e.replace('_', ' ') for e in elements])}"
        
        # Add format-specific guidance
        if audio_format in self.audio_formats:
            format_config = self.audio_formats[audio_format]
            prompt += f"\n- Voice Style: {format_config['voice_style'].replace('_', ' ')}"
            prompt += f"\n- Pacing Guide: {format_config['pacing'].replace('_', ' ')}"
        
        goal_guidance = {
            'clarity': "Focus on clear articulation, proper pronunciation, and easy comprehension.",
            'engagement': "Focus on dynamic delivery, varied intonation, and audience connection.",
            'persuasion': "Focus on confident delivery, strategic emphasis, and compelling presentation.",
            'emotion': "Focus on emotional expression, appropriate mood setting, and authentic feeling.",
            'accessibility': "Focus on inclusive delivery, clear speech patterns, and universal comprehension."
        }
        
        prompt += f"\n\nGoal Guidance: {goal_guidance.get(goal, 'Optimize voice for effective audio communication.')}"
        
        return prompt