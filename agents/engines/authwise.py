"""
OneLastAI Platform - AuthWise Agent Engine
Authentication and authorization security specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AuthWiseEngine(BaseAgentEngine):
    """
    AuthWise - Authentication & Authorization Engine
    Specializes in security, access control, and identity management
    """
    
    def __init__(self):
        super().__init__('authwise')
        self.auth_methods = self.initialize_auth_methods()
    
    def initialize_auth_methods(self) -> Dict[str, Any]:
        """Initialize authentication and authorization methods."""
        return {
            'authentication': {
                'password': {'strength': 'medium', 'convenience': 'high', 'security': 'medium'},
                'mfa': {'strength': 'high', 'convenience': 'medium', 'security': 'high'},
                'biometric': {'strength': 'very_high', 'convenience': 'high', 'security': 'very_high'},
                'sso': {'strength': 'medium', 'convenience': 'very_high', 'security': 'medium'},
                'oauth': {'strength': 'high', 'convenience': 'high', 'security': 'high'}
            },
            'authorization': {
                'rbac': 'role_based_access_control',
                'abac': 'attribute_based_access_control',
                'dac': 'discretionary_access_control',
                'mac': 'mandatory_access_control'
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with security and authentication focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'authentication_security'
            context['user_message'] = message
            
            # Analyze security intent
            security_analysis = self.analyze_security_intent(message)
            context['security_analysis'] = security_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build security-focused system prompt
            security_prompt = self.build_security_prompt(security_analysis)
            enhanced_prompt = self.system_prompt + security_prompt
            
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
            logger.error(f"Error in AuthWise engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_security_intent(self, message: str) -> Dict[str, Any]:
        """Analyze security and authentication related intent."""
        message_lower = message.lower()
        
        # Identify security domains
        domains = {
            'authentication': any(word in message_lower for word in 
                                  ['login', 'password', 'auth', 'signin', 'mfa']),
            'authorization': any(word in message_lower for word in 
                                 ['permission', 'access', 'role', 'authorize']),
            'security': any(word in message_lower for word in 
                            ['security', 'secure', 'vulnerability', 'threat']),
            'compliance': any(word in message_lower for word in 
                              ['compliance', 'gdpr', 'hipaa', 'regulation']),
            'encryption': any(word in message_lower for word in 
                              ['encrypt', 'decrypt', 'crypto', 'key', 'ssl'])
        }
        
        # Identify action types
        actions = {
            'implement': any(word in message_lower for word in 
                             ['implement', 'setup', 'configure', 'deploy']),
            'audit': any(word in message_lower for word in 
                         ['audit', 'review', 'assess', 'evaluate']),
            'troubleshoot': any(word in message_lower for word in 
                                ['problem', 'issue', 'error', 'fail', 'broken']),
            'improve': any(word in message_lower for word in 
                           ['improve', 'enhance', 'strengthen', 'upgrade'])
        }
        
        return {
            'primary_domain': max(domains.items(), key=lambda x: x[1])[0] 
                             if any(domains.values()) else 'authentication',
            'action': max(actions.items(), key=lambda x: x[1])[0] 
                     if any(actions.values()) else 'implement',
            'all_domains': {k: v for k, v in domains.items() if v},
            'security_keywords': self.extract_security_keywords(message)
        }
    
    def extract_security_keywords(self, message: str) -> List[str]:
        """Extract security-related keywords from the message."""
        security_terms = [
            'jwt', 'oauth', 'saml', 'ldap', 'active_directory', 'sso',
            'firewall', 'encryption', 'hash', 'token', 'certificate',
            'vpn', 'api_key', 'session', 'cookie', 'csrf', 'xss'
        ]
        
        message_lower = message.lower()
        found_terms = [term for term in security_terms 
                      if term.replace('_', ' ') in message_lower or term in message_lower]
        
        return found_terms[:6]  # Return up to 6 security keywords
    
    def build_security_prompt(self, security_analysis: Dict[str, Any]) -> str:
        """Build security-focused system prompt."""
        domain = security_analysis['primary_domain']
        action = security_analysis['action']
        keywords = security_analysis.get('security_keywords', [])
        
        prompt = f"\n\nSecurity Focus: {domain.title()} {action.title()}"
        
        if keywords:
            prompt += f"\n- Technologies: {', '.join(keywords)}"
        
        domain_guidance = {
            'authentication': "Focus on identity verification, login security, and authentication methods.",
            'authorization': "Focus on access control, permissions, and role-based security.",
            'security': "Focus on overall security posture, threat mitigation, and best practices.",
            'compliance': "Focus on regulatory requirements, compliance frameworks, and audit preparation.",
            'encryption': "Focus on data protection, cryptographic methods, and secure communication."
        }
        
        action_guidance = {
            'implement': "Provide step-by-step implementation guidance with security best practices.",
            'audit': "Focus on security assessment, vulnerability identification, and compliance checking.",
            'troubleshoot': "Diagnose security issues and provide remediation strategies.",
            'improve': "Identify security enhancements and optimization opportunities."
        }
        
        prompt += f"\n\nDomain Guidance: {domain_guidance.get(domain, 'Provide comprehensive security guidance.')}"
        prompt += f"\nAction Guidance: {action_guidance.get(action, 'Provide appropriate security assistance.')}"
        
        return prompt