"""
OneLastAI Platform - ContentCrafter Agent Engine
Advanced content creation and marketing specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ContentCrafterEngine(BaseAgentEngine):
    """
    ContentCrafter - Content Creation Engine
    Specializes in marketing content, copywriting, and content strategy
    """
    
    def __init__(self):
        super().__init__('contentcrafter')
        self.content_types = self.initialize_content_types()
    
    def initialize_content_types(self) -> Dict[str, Any]:
        """Initialize content types and their characteristics."""
        return {
            'blog_post': {
                'structure': ['headline', 'intro', 'body', 'conclusion', 'cta'],
                'tone_options': ['informative', 'conversational', 'authoritative'],
                'seo_focus': True
            },
            'social_media': {
                'structure': ['hook', 'content', 'engagement', 'hashtags'],
                'tone_options': ['casual', 'trendy', 'professional'],
                'seo_focus': False
            },
            'email_marketing': {
                'structure': ['subject', 'preheader', 'body', 'cta'],
                'tone_options': ['personal', 'promotional', 'informative'],
                'seo_focus': False
            },
            'sales_copy': {
                'structure': ['headline', 'problem', 'solution', 'benefits', 'cta'],
                'tone_options': ['persuasive', 'urgent', 'trustworthy'],
                'seo_focus': False
            },
            'product_description': {
                'structure': ['title', 'features', 'benefits', 'specifications'],
                'tone_options': ['descriptive', 'compelling', 'technical'],
                'seo_focus': True
            },
            'press_release': {
                'structure': ['headline', 'lead', 'body', 'boilerplate', 'contact'],
                'tone_options': ['formal', 'newsworthy', 'professional'],
                'seo_focus': True
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with content creation focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'content_creation'
            context['user_message'] = message
            
            # Analyze content creation intent
            content_analysis = self.analyze_content_intent(message)
            context['content_analysis'] = content_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build content-focused system prompt
            content_prompt = self.build_content_prompt(content_analysis)
            enhanced_prompt = self.system_prompt + content_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-6:])
            
            messages.append({'role': 'user', 'content': message})
            
            # Optimize for creative content generation
            params = self.get_ai_parameters()
            params['temperature'] = 0.8  # Balanced creativity and coherence
            
            response = ai_service.chat_completion(
                messages=messages,
                **params
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in ContentCrafter engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_content_intent(self, message: str) -> Dict[str, Any]:
        """Analyze content creation intent and requirements."""
        message_lower = message.lower()
        
        # Detect content type
        type_scores = {}
        for content_type, config in self.content_types.items():
            score = 0
            type_name = content_type.replace('_', ' ')
            if type_name in message_lower or content_type in message_lower:
                score += 3
            for element in config['structure']:
                if element in message_lower:
                    score += 1
            if score > 0:
                type_scores[content_type] = score
        
        # Detect content purpose
        purposes = {
            'marketing': any(word in message_lower for word in 
                             ['marketing', 'promote', 'sell', 'campaign']),
            'educational': any(word in message_lower for word in 
                               ['educate', 'teach', 'explain', 'guide']),
            'entertainment': any(word in message_lower for word in 
                                 ['entertain', 'engage', 'fun', 'story']),
            'informational': any(word in message_lower for word in 
                                 ['inform', 'news', 'update', 'announce'])
        }
        
        # Detect target audience
        audiences = {
            'business': any(word in message_lower for word in 
                            ['business', 'professional', 'corporate', 'b2b']),
            'consumer': any(word in message_lower for word in 
                            ['consumer', 'customer', 'b2c', 'general']),
            'technical': any(word in message_lower for word in 
                             ['technical', 'developer', 'expert', 'advanced']),
            'general': any(word in message_lower for word in 
                           ['general', 'everyone', 'broad', 'mass'])
        }
        
        primary_type = max(type_scores.items(), key=lambda x: x[1])[0] \
                      if type_scores else 'blog_post'
        
        primary_purpose = max(purposes.items(), key=lambda x: x[1])[0] \
                         if any(purposes.values()) else 'informational'
        
        primary_audience = max(audiences.items(), key=lambda x: x[1])[0] \
                          if any(audiences.values()) else 'general'
        
        return {
            'content_type': primary_type,
            'purpose': primary_purpose,
            'audience': primary_audience,
            'keywords': self.extract_content_keywords(message),
            'tone_requirements': self.detect_tone_requirements(message)
        }
    
    def extract_content_keywords(self, message: str) -> List[str]:
        """Extract keywords for content optimization."""
        import re
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Filter content-relevant words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'create', 'write', 'make', 'content'
        }
        
        keywords = [word for word in words 
                   if len(word) > 3 and word not in stop_words]
        
        return keywords[:10]  # Return top 10 keywords
    
    def detect_tone_requirements(self, message: str) -> List[str]:
        """Detect required tone and style from the message."""
        tones = [
            'professional', 'casual', 'formal', 'friendly', 'authoritative',
            'conversational', 'persuasive', 'informative', 'engaging',
            'creative', 'technical', 'emotional', 'urgent', 'trustworthy'
        ]
        
        message_lower = message.lower()
        detected_tones = [tone for tone in tones if tone in message_lower]
        
        return detected_tones[:3]  # Return up to 3 tone requirements
    
    def build_content_prompt(self, content_analysis: Dict[str, Any]) -> str:
        """Build content creation focused prompt."""
        content_type = content_analysis['content_type']
        purpose = content_analysis['purpose']
        audience = content_analysis['audience']
        keywords = content_analysis.get('keywords', [])
        tones = content_analysis.get('tone_requirements', [])
        
        prompt = f"\n\nContent Creation Focus: {content_type.replace('_', ' ').title()}"
        prompt += f"\n- Purpose: {purpose.title()} content"
        prompt += f"\n- Target Audience: {audience.title()}"
        
        if tones:
            prompt += f"\n- Tone Requirements: {', '.join(tones)}"
        
        if keywords:
            prompt += f"\n- Key Topics: {', '.join(keywords[:5])}"
        
        # Add content type specific guidance
        if content_type in self.content_types:
            type_config = self.content_types[content_type]
            prompt += f"\n- Structure: {' → '.join(type_config['structure'])}"
            
            if type_config.get('seo_focus'):
                prompt += "\n- SEO Optimization: Include relevant keywords naturally"
        
        purpose_guidance = {
            'marketing': "Focus on persuasive language, clear benefits, and strong calls-to-action.",
            'educational': "Focus on clear explanations, structured information, and learning outcomes.",
            'entertainment': "Focus on engaging storytelling, humor, and audience engagement.",
            'informational': "Focus on accuracy, clarity, and comprehensive information delivery."
        }
        
        audience_guidance = {
            'business': "Use professional language, focus on ROI and business value.",
            'consumer': "Use accessible language, focus on benefits and emotional appeal.",
            'technical': "Use precise terminology, provide detailed specifications and examples.",
            'general': "Use clear, jargon-free language accessible to all readers."
        }
        
        prompt += f"\n\nPurpose Guidance: {purpose_guidance.get(purpose, 'Create engaging, valuable content.')}"
        prompt += f"\nAudience Guidance: {audience_guidance.get(audience, 'Match content to audience needs.')}"
        
        return prompt