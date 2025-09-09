"""
OneLastAI Platform - EmotiSense Agent Engine
Advanced emotion analysis and emotional intelligence specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class EmotiSenseEngine(BaseAgentEngine):
    """
    EmotiSense - Emotion Analysis Engine
    Specializes in detecting, analyzing, and responding to emotional patterns
    """
    
    def __init__(self):
        super().__init__('emotisense')
        self.emotion_patterns = self.load_emotion_patterns()
    
    def load_emotion_patterns(self) -> Dict[str, List[str]]:
        """Load emotion detection patterns."""
        return {
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'elated', 'cheerful'],
            'sadness': ['sad', 'depressed', 'down', 'blue', 'melancholy', 'grief'],
            'anger': ['angry', 'furious', 'mad', 'irritated', 'frustrated', 'rage'],
            'fear': ['scared', 'afraid', 'anxious', 'worried', 'nervous', 'terrified'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned'],
            'disgust': ['disgusted', 'revolted', 'sick', 'appalled', 'repulsed'],
            'trust': ['trust', 'confident', 'secure', 'faithful', 'reliable'],
            'anticipation': ['excited', 'eager', 'hopeful', 'expectant', 'optimistic']
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with advanced emotion analysis."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'emotion_analysis'
            context['user_message'] = message
            
            # Perform comprehensive emotion analysis
            emotion_analysis = self.analyze_emotions_comprehensive(message)
            context['emotion_analysis'] = emotion_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build emotion-aware system prompt
            emotion_prompt = self.build_emotion_analysis_prompt(emotion_analysis)
            enhanced_prompt = self.system_prompt + emotion_prompt
            
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
            logger.error(f"Error in EmotiSense engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_emotions_comprehensive(self, message: str) -> Dict[str, Any]:
        """Perform comprehensive emotion analysis."""
        message_lower = message.lower()
        
        # Detect primary emotions
        detected_emotions = {}
        for emotion, keywords in self.emotion_patterns.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                detected_emotions[emotion] = score
        
        # Determine primary and secondary emotions
        sorted_emotions = sorted(detected_emotions.items(), key=lambda x: x[1], reverse=True)
        
        analysis = {
            'primary_emotion': sorted_emotions[0][0] if sorted_emotions else 'neutral',
            'secondary_emotion': sorted_emotions[1][0] if len(sorted_emotions) > 1 else None,
            'emotion_intensity': self.calculate_intensity(message),
            'emotional_complexity': len(detected_emotions),
            'detected_emotions': detected_emotions
        }
        
        return analysis
    
    def calculate_intensity(self, message: str) -> str:
        """Calculate emotional intensity based on linguistic cues."""
        intensity_indicators = {
            'high': ['extremely', 'incredibly', 'absolutely', 'totally', '!!!', 'CAPS'],
            'medium': ['very', 'really', 'quite', 'pretty', '!!'],
            'low': ['somewhat', 'slightly', 'a bit', 'kind of', '!']
        }
        
        message_upper = message.upper()
        caps_ratio = sum(1 for c in message if c.isupper()) / len(message) if message else 0
        
        if caps_ratio > 0.3 or any(indicator in message.lower() for indicator in intensity_indicators['high']):
            return 'high'
        elif any(indicator in message.lower() for indicator in intensity_indicators['medium']):
            return 'medium'
        else:
            return 'low'
    
    def build_emotion_analysis_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build emotion-analysis-focused response prompt."""
        primary = analysis['primary_emotion']
        intensity = analysis['intensity']
        complexity = analysis['emotional_complexity']
        
        prompt = f"\n\nEmotion Analysis Results:"
        prompt += f"\n- Primary emotion detected: {primary}"
        prompt += f"\n- Emotional intensity: {intensity}"
        prompt += f"\n- Emotional complexity: {complexity} different emotions detected"
        
        if analysis.get('secondary_emotion'):
            prompt += f"\n- Secondary emotion: {analysis['secondary_emotion']}"
        
        prompt += "\n\nRespond with emotional intelligence, acknowledging the detected emotions and providing appropriate support or guidance."
        
        return prompt