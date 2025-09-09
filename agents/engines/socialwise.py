"""
OneLastAI Platform - SocialWise Agent Engine
Social media strategy and networking intelligence specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SocialWiseEngine(BaseAgentEngine):
    """
    SocialWise - Social Media Strategy Engine
    Specializes in social media optimization, networking, and digital presence
    """
    
    def __init__(self):
        super().__init__('socialwise')
        self.social_platforms = self.initialize_social_platforms()
    
    def initialize_social_platforms(self) -> Dict[str, Any]:
        """Initialize social platform characteristics and strategies."""
        return {
            'twitter': {
                'character_limit': 280,
                'best_times': ['9-10am', '7-9pm'],
                'content_style': 'concise_engaging',
                'hashtag_optimal': 2
            },
            'linkedin': {
                'character_limit': 3000,
                'best_times': ['8-9am', '12-1pm', '5-6pm'],
                'content_style': 'professional_insightful',
                'hashtag_optimal': 5
            },
            'instagram': {
                'character_limit': 2200,
                'best_times': ['11am-1pm', '7-9pm'],
                'content_style': 'visual_storytelling',
                'hashtag_optimal': 11
            },
            'facebook': {
                'character_limit': 63206,
                'best_times': ['1-3pm', '3-4pm'],
                'content_style': 'community_focused',
                'hashtag_optimal': 3
            },
            'tiktok': {
                'character_limit': 2200,
                'best_times': ['6-10am', '7-9pm'],
                'content_style': 'trendy_creative',
                'hashtag_optimal': 5
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with social media strategy focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'social_media_strategy'
            context['user_message'] = message
            
            # Analyze social media intent
            social_intent = self.analyze_social_intent(message)
            context['social_intent'] = social_intent
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build social strategy system prompt
            social_prompt = self.build_social_strategy_prompt(social_intent)
            enhanced_prompt = self.system_prompt + social_prompt
            
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
            logger.error(f"Error in SocialWise engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_social_intent(self, message: str) -> Dict[str, Any]:
        """Analyze social media related intent."""
        message_lower = message.lower()
        
        # Detect target platforms
        platforms = []
        for platform in self.social_platforms.keys():
            if platform in message_lower:
                platforms.append(platform)
        
        # Detect intent types
        intents = {
            'content_creation': any(word in message_lower for word in 
                                    ['create', 'write', 'post', 'content']),
            'strategy': any(word in message_lower for word in 
                            ['strategy', 'plan', 'approach', 'campaign']),
            'optimization': any(word in message_lower for word in 
                                ['optimize', 'improve', 'enhance', 'boost']),
            'analytics': any(word in message_lower for word in 
                             ['analyze', 'metrics', 'performance', 'stats']),
            'engagement': any(word in message_lower for word in 
                              ['engage', 'interact', 'community', 'followers']),
            'hashtags': any(word in message_lower for word in ['hashtag', 'tag', '#'])
        }
        
        # Determine primary intent
        primary = 'general'
        if any(intents.values()):
            primary = max(intents.items(), key=lambda x: x[1])[0]
        
        return {
            'target_platforms': platforms if platforms else ['general'],
            'primary_intent': primary,
            'all_intents': {k: v for k, v in intents.items() if v}
        }
    
    def build_social_strategy_prompt(self, social_intent: Dict[str, Any]) -> str:
        """Build social media strategy focused prompt."""
        platforms = social_intent['target_platforms']
        intent = social_intent['primary_intent']
        
        prompt = "\n\nSocial Media Strategy Focus:"
        
        if platforms != ['general']:
            prompt += f"\n- Target Platforms: {', '.join(platforms)}"
            for platform in platforms:
                if platform in self.social_platforms:
                    platform_info = self.social_platforms[platform]
                    prompt += f"\n  - {platform.title()}: {platform_info['content_style']} style, optimal hashtags: {platform_info['hashtag_optimal']}"
        
        intent_guidance = {
            'content_creation': "Focus on creating engaging, platform-appropriate content that resonates with target audiences.",
            'strategy': "Develop comprehensive social media strategies with clear goals, timelines, and success metrics.",
            'optimization': "Provide actionable optimization tips for better reach, engagement, and conversion rates.",
            'analytics': "Help interpret social media metrics and provide data-driven insights for improvement.",
            'engagement': "Focus on community building strategies and authentic audience engagement techniques.",
            'hashtags': "Provide strategic hashtag recommendations based on platform best practices and trending topics."
        }
        
        prompt += f"\n- Primary Focus: {intent_guidance.get(intent, 'Provide comprehensive social media guidance.')}"
        
        return prompt