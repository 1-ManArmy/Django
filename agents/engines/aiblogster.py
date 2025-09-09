"""
OneLastAI Platform - AIBlogster Agent Engine
AI-powered blogging and content optimization specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AIBlogsterEngine(BaseAgentEngine):
    """
    AIBlogster - AI Blogging Engine
    Specializes in blog content creation, SEO optimization, and content strategy
    """
    
    def __init__(self):
        super().__init__('aiblogster')
        self.blog_formats = self.initialize_blog_formats()
    
    def initialize_blog_formats(self) -> Dict[str, Any]:
        """Initialize blog formats and content strategies."""
        return {
            'how_to_guide': {
                'structure': ['introduction', 'materials_needed', 'step_by_step', 'tips', 'conclusion'],
                'seo_focus': 'long_tail_keywords',
                'engagement': 'practical_value'
            },
            'listicle': {
                'structure': ['engaging_intro', 'numbered_points', 'explanations', 'conclusion'],
                'seo_focus': 'numbered_keywords',
                'engagement': 'scannable_format'
            },
            'thought_leadership': {
                'structure': ['compelling_hook', 'expert_insights', 'supporting_evidence', 'call_to_action'],
                'seo_focus': 'industry_keywords',
                'engagement': 'authority_building'
            },
            'news_analysis': {
                'structure': ['news_summary', 'analysis', 'implications', 'expert_opinion'],
                'seo_focus': 'trending_keywords',
                'engagement': 'timeliness_relevance'
            },
            'case_study': {
                'structure': ['challenge', 'solution', 'implementation', 'results', 'lessons'],
                'seo_focus': 'solution_keywords',
                'engagement': 'real_world_examples'
            },
            'comparison': {
                'structure': ['options_overview', 'criteria', 'detailed_comparison', 'recommendation'],
                'seo_focus': 'vs_keywords',
                'engagement': 'decision_support'
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with AI blogging focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'ai_blogging'
            context['user_message'] = message
            
            # Analyze blogging intent
            blog_analysis = self.analyze_blogging_intent(message)
            context['blog_analysis'] = blog_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build blogging-focused system prompt
            blog_prompt = self.build_blogging_prompt(blog_analysis)
            enhanced_prompt = self.system_prompt + blog_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-6:])
            
            messages.append({'role': 'user', 'content': message})
            
            # Optimize for content creation
            params = self.get_ai_parameters()
            params['temperature'] = 0.75  # Balanced creativity and coherence
            
            response = ai_service.chat_completion(
                messages=messages,
                **params
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in AIBlogster engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_blogging_intent(self, message: str) -> Dict[str, Any]:
        """Analyze blogging intent and content requirements."""
        message_lower = message.lower()
        
        # Detect blog format
        format_scores = {}
        for blog_format, config in self.blog_formats.items():
            score = 0
            format_name = blog_format.replace('_', ' ')
            if format_name in message_lower:
                score += 3
            
            # Check for format indicators
            if blog_format == 'how_to_guide' and any(word in message_lower for word in ['how to', 'tutorial', 'guide']):
                score += 2
            elif blog_format == 'listicle' and any(word in message_lower for word in ['list', 'top', 'best']):
                score += 2
            elif blog_format == 'comparison' and any(word in message_lower for word in ['vs', 'versus', 'compare']):
                score += 2
            
            if score > 0:
                format_scores[blog_format] = score
        
        # Detect content goals
        goals = {
            'seo_optimization': any(word in message_lower for word in 
                                    ['seo', 'search', 'ranking', 'traffic']),
            'engagement': any(word in message_lower for word in 
                              ['engage', 'viral', 'shares', 'comments']),
            'education': any(word in message_lower for word in 
                             ['educate', 'teach', 'inform', 'explain']),
            'conversion': any(word in message_lower for word in 
                              ['convert', 'sales', 'leads', 'cta'])
        }
        
        # Detect target audience
        audiences = {
            'beginners': any(word in message_lower for word in 
                             ['beginner', 'new', 'introduction', 'basics']),
            'professionals': any(word in message_lower for word in 
                                 ['professional', 'expert', 'advanced']),
            'general': any(word in message_lower for word in 
                           ['everyone', 'general', 'broad', 'all'])
        }
        
        primary_format = max(format_scores.items(), key=lambda x: x[1])[0] \
                        if format_scores else 'thought_leadership'
        
        primary_goal = max(goals.items(), key=lambda x: x[1])[0] \
                      if any(goals.values()) else 'engagement'
        
        primary_audience = max(audiences.items(), key=lambda x: x[1])[0] \
                          if any(audiences.values()) else 'general'
        
        return {
            'format': primary_format,
            'goal': primary_goal,
            'audience': primary_audience,
            'keywords': self.extract_seo_keywords(message),
            'content_length': self.estimate_content_length(message)
        }
    
    def extract_seo_keywords(self, message: str) -> List[str]:
        """Extract potential SEO keywords from the message."""
        import re
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Focus on content-relevant terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'blog', 'post', 'write', 'create'
        }
        
        keywords = [word for word in words 
                   if len(word) > 3 and word not in stop_words]
        
        return keywords[:12]  # Return top 12 potential keywords
    
    def estimate_content_length(self, message: str) -> str:
        """Estimate desired content length from context clues."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['short', 'brief', 'quick']):
            return 'short'  # 300-600 words
        elif any(word in message_lower for word in ['long', 'detailed', 'comprehensive']):
            return 'long'  # 1500+ words
        else:
            return 'medium'  # 800-1200 words
    
    def build_blogging_prompt(self, blog_analysis: Dict[str, Any]) -> str:
        """Build AI blogging focused prompt."""
        blog_format = blog_analysis['format']
        goal = blog_analysis['goal']
        audience = blog_analysis['audience']
        keywords = blog_analysis.get('keywords', [])
        length = blog_analysis.get('content_length', 'medium')
        
        prompt = f"\n\nBlog Focus: {blog_format.replace('_', ' ').title()} Format"
        prompt += f"\n- Primary Goal: {goal.replace('_', ' ').title()}"
        prompt += f"\n- Target Audience: {audience.title()}"
        prompt += f"\n- Content Length: {length.title()}"
        
        if keywords:
            prompt += f"\n- SEO Keywords: {', '.join(keywords[:8])}"
        
        # Add format-specific guidance
        if blog_format in self.blog_formats:
            format_config = self.blog_formats[blog_format]
            prompt += f"\n- Structure: {' → '.join(format_config['structure'])}"
            prompt += f"\n- SEO Strategy: {format_config['seo_focus'].replace('_', ' ')}"
            prompt += f"\n- Engagement Focus: {format_config['engagement'].replace('_', ' ')}"
        
        goal_guidance = {
            'seo_optimization': "Optimize for search engines with strategic keyword placement and SEO best practices.",
            'engagement': "Create compelling, shareable content that encourages reader interaction and social sharing.",
            'education': "Focus on clear explanations, practical value, and actionable insights for readers.",
            'conversion': "Include strategic calls-to-action and persuasive elements to drive desired actions."
        }
        
        audience_guidance = {
            'beginners': "Use clear, jargon-free language with detailed explanations and foundational concepts.",
            'professionals': "Assume domain knowledge and focus on advanced insights, trends, and industry expertise.",
            'general': "Balance accessibility with depth, making content valuable for diverse reader backgrounds."
        }
        
        length_guidance = {
            'short': "Focus on key points, be concise, and provide immediate value (300-600 words).",
            'medium': "Balance depth with readability, include examples and actionable insights (800-1200 words).",
            'long': "Provide comprehensive coverage with detailed analysis, examples, and thorough exploration (1500+ words)."
        }
        
        prompt += f"\n\nGoal Guidance: {goal_guidance.get(goal, 'Create engaging, valuable blog content.')}"
        prompt += f"\nAudience Guidance: {audience_guidance.get(audience, 'Write for your target audience.')}"
        prompt += f"\nLength Guidance: {length_guidance.get(length, 'Match content depth to purpose.')}"
        
        return prompt