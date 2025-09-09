"""
OneLastAI Platform - CodeMaster Agent Engine
Advanced coding and software development specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CodeMasterEngine(BaseAgentEngine):
    """
    CodeMaster - Advanced Coding Engine
    Specializes in software development, code analysis, and programming guidance
    """
    
    def __init__(self):
        super().__init__('codemaster')
        self.programming_languages = self.initialize_programming_languages()
    
    def initialize_programming_languages(self) -> Dict[str, Any]:
        """Initialize programming language capabilities and specializations."""
        return {
            'python': {
                'strengths': ['ai_ml', 'web_development', 'data_analysis', 'automation'],
                'frameworks': ['django', 'flask', 'fastapi', 'tensorflow', 'pytorch'],
                'best_practices': ['pep8', 'type_hints', 'docstrings', 'testing']
            },
            'javascript': {
                'strengths': ['frontend', 'backend', 'mobile', 'real_time'],
                'frameworks': ['react', 'vue', 'angular', 'nodejs', 'express'],
                'best_practices': ['es6+', 'async_await', 'modules', 'testing']
            },
            'typescript': {
                'strengths': ['large_scale', 'type_safety', 'enterprise'],
                'frameworks': ['angular', 'react', 'nestjs', 'deno'],
                'best_practices': ['strict_typing', 'interfaces', 'generics']
            },
            'java': {
                'strengths': ['enterprise', 'scalability', 'cross_platform'],
                'frameworks': ['spring', 'spring_boot', 'hibernate'],
                'best_practices': ['solid_principles', 'design_patterns', 'clean_code']
            },
            'csharp': {
                'strengths': ['enterprise', 'web', 'desktop', 'games'],
                'frameworks': ['dotnet', 'asp_net', 'blazor', 'unity'],
                'best_practices': ['clean_architecture', 'dependency_injection']
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with advanced coding focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'advanced_coding'
            context['user_message'] = message
            
            # Analyze coding intent and requirements
            coding_analysis = self.analyze_coding_intent(message)
            context['coding_analysis'] = coding_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build coding-focused system prompt
            coding_prompt = self.build_coding_prompt(coding_analysis)
            enhanced_prompt = self.system_prompt + coding_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-6:])
            
            messages.append({'role': 'user', 'content': message})
            
            # Optimize parameters for code generation
            params = self.get_ai_parameters()
            params['temperature'] = 0.3  # Lower for more precise code
            
            response = ai_service.chat_completion(
                messages=messages,
                **params
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in CodeMaster engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_coding_intent(self, message: str) -> Dict[str, Any]:
        """Analyze coding intent, language, and complexity."""
        message_lower = message.lower()
        
        # Detect programming languages
        detected_languages = []
        for lang, config in self.programming_languages.items():
            if lang in message_lower or any(fw in message_lower for fw in config['frameworks']):
                detected_languages.append(lang)
        
        # Determine coding activities
        activities = {
            'development': any(word in message_lower for word in 
                               ['create', 'build', 'develop', 'implement']),
            'debugging': any(word in message_lower for word in 
                             ['debug', 'fix', 'error', 'bug', 'issue']),
            'optimization': any(word in message_lower for word in 
                                ['optimize', 'improve', 'refactor', 'performance']),
            'review': any(word in message_lower for word in 
                          ['review', 'analyze', 'audit', 'check']),
            'learning': any(word in message_lower for word in 
                            ['learn', 'understand', 'explain', 'tutorial'])
        }
        
        # Assess complexity level
        complexity_indicators = {
            'advanced': any(word in message_lower for word in 
                            ['advanced', 'complex', 'enterprise', 'scalable']),
            'intermediate': any(word in message_lower for word in 
                                ['intermediate', 'moderate', 'standard']),
            'beginner': any(word in message_lower for word in 
                            ['beginner', 'simple', 'basic', 'easy'])
        }
        
        return {
            'languages': detected_languages if detected_languages else ['general'],
            'primary_activity': max(activities.items(), key=lambda x: x[1])[0] 
                               if any(activities.values()) else 'development',
            'complexity': max(complexity_indicators.items(), key=lambda x: x[1])[0] 
                         if any(complexity_indicators.values()) else 'intermediate',
            'code_patterns': self.detect_code_patterns(message)
        }
    
    def detect_code_patterns(self, message: str) -> List[str]:
        """Detect specific coding patterns and concepts mentioned."""
        patterns = [
            'api', 'rest', 'graphql', 'database', 'orm', 'mvc', 'mvvm',
            'microservices', 'docker', 'kubernetes', 'ci_cd', 'testing',
            'authentication', 'authorization', 'security', 'encryption',
            'caching', 'optimization', 'algorithm', 'data_structure'
        ]
        
        message_lower = message.lower()
        detected = [pattern for pattern in patterns 
                   if pattern.replace('_', ' ') in message_lower or pattern in message_lower]
        
        return detected[:8]  # Return up to 8 patterns
    
    def build_coding_prompt(self, coding_analysis: Dict[str, Any]) -> str:
        """Build advanced coding focused prompt."""
        languages = coding_analysis['languages']
        activity = coding_analysis['primary_activity']
        complexity = coding_analysis['complexity']
        patterns = coding_analysis.get('code_patterns', [])
        
        prompt = f"\n\nCoding Focus: {activity.title()} - {complexity.title()} Level"
        
        if languages != ['general']:
            prompt += f"\n- Languages: {', '.join([l.title() for l in languages])}"
            
            # Add language-specific guidance
            for lang in languages[:2]:  # Limit to 2 languages for prompt size
                if lang in self.programming_languages:
                    lang_info = self.programming_languages[lang]
                    prompt += f"\n- {lang.title()} Focus: {', '.join(lang_info['strengths'])}"
        
        if patterns:
            prompt += f"\n- Technical Areas: {', '.join(patterns)}"
        
        activity_guidance = {
            'development': "Focus on clean code, best practices, scalable architecture, and comprehensive implementation.",
            'debugging': "Focus on systematic debugging, root cause analysis, and effective problem-solving strategies.",
            'optimization': "Focus on performance improvements, code efficiency, and scalability enhancements.",
            'review': "Focus on code quality assessment, security analysis, and architectural evaluation.",
            'learning': "Focus on clear explanations, practical examples, and progressive skill building."
        }
        
        complexity_guidance = {
            'advanced': "Provide enterprise-level solutions with advanced patterns and comprehensive architecture.",
            'intermediate': "Balance functionality with clarity, using established patterns and best practices.",
            'beginner': "Focus on clarity, simplicity, and foundational understanding with detailed explanations."
        }
        
        prompt += f"\n\nActivity Guidance: {activity_guidance.get(activity, 'Provide comprehensive coding assistance.')}"
        prompt += f"\nComplexity Guidance: {complexity_guidance.get(complexity, 'Match appropriate complexity level.')}"
        
        return prompt