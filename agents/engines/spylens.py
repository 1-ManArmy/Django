"""
OneLastAI Platform - SpyLens Agent Engine
Surveillance and monitoring intelligence specialist for security analysis
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SpyLensEngine(BaseAgentEngine):
    """
    SpyLens - Surveillance & Monitoring Engine
    Specializes in security monitoring, threat detection, and intelligence analysis
    """
    
    def __init__(self):
        super().__init__('spylens')
        self.monitoring_domains = self.initialize_monitoring_domains()
    
    def initialize_monitoring_domains(self) -> Dict[str, Any]:
        """Initialize monitoring and surveillance domains."""
        return {
            'network_security': {
                'focus': ['intrusion_detection', 'anomaly_analysis', 'traffic_monitoring'],
                'indicators': ['unusual_patterns', 'suspicious_connections', 'data_exfiltration']
            },
            'application_security': {
                'focus': ['code_analysis', 'runtime_monitoring', 'vulnerability_assessment'],
                'indicators': ['injection_attempts', 'privilege_escalation', 'data_breaches']
            },
            'user_behavior': {
                'focus': ['access_patterns', 'activity_analysis', 'behavioral_anomalies'],
                'indicators': ['unusual_access', 'privilege_abuse', 'insider_threats']
            },
            'infrastructure': {
                'focus': ['system_monitoring', 'performance_analysis', 'availability_tracking'],
                'indicators': ['service_degradation', 'resource_exhaustion', 'system_failures']
            },
            'compliance': {
                'focus': ['audit_trails', 'policy_enforcement', 'regulatory_monitoring'],
                'indicators': ['policy_violations', 'compliance_gaps', 'audit_issues']
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with surveillance and monitoring focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'surveillance_monitoring'
            context['user_message'] = message
            
            # Analyze monitoring intent
            monitoring_analysis = self.analyze_monitoring_intent(message)
            context['monitoring_analysis'] = monitoring_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build surveillance-focused system prompt
            surveillance_prompt = self.build_surveillance_prompt(monitoring_analysis)
            enhanced_prompt = self.system_prompt + surveillance_prompt
            
            messages = [
                {'role': 'system', 'content': enhanced_prompt}
            ]
            
            if 'recent_history' in context:
                messages.extend(context['recent_history'][-6:])
            
            messages.append({'role': 'user', 'content': message})
            
            # Use parameters optimized for analytical precision
            params = self.get_ai_parameters()
            params['temperature'] = 0.6  # Lower temperature for analytical work
            
            response = ai_service.chat_completion(
                messages=messages,
                **params
            )
            
            return self.postprocess_response(response, context)
            
        except Exception as e:
            logger.error(f"Error in SpyLens engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_monitoring_intent(self, message: str) -> Dict[str, Any]:
        """Analyze surveillance and monitoring intent."""
        message_lower = message.lower()
        
        # Identify monitoring domains
        domain_matches = {}
        for domain, config in self.monitoring_domains.items():
            score = 0
            for focus_area in config['focus']:
                if any(word in message_lower for word in focus_area.split('_')):
                    score += 1
            if score > 0:
                domain_matches[domain] = score
        
        # Determine monitoring activities
        activities = {
            'detection': any(word in message_lower for word in 
                             ['detect', 'identify', 'find', 'discover']),
            'analysis': any(word in message_lower for word in 
                            ['analyze', 'examine', 'investigate', 'assess']),
            'monitoring': any(word in message_lower for word in 
                              ['monitor', 'watch', 'track', 'observe']),
            'alerting': any(word in message_lower for word in 
                            ['alert', 'notify', 'warn', 'signal']),
            'response': any(word in message_lower for word in 
                            ['respond', 'react', 'mitigate', 'block'])
        }
        
        # Determine threat levels
        threat_indicators = {
            'critical': any(word in message_lower for word in 
                            ['critical', 'severe', 'emergency', 'breach']),
            'high': any(word in message_lower for word in 
                        ['high', 'serious', 'major', 'attack']),
            'medium': any(word in message_lower for word in 
                          ['medium', 'moderate', 'suspicious', 'anomaly']),
            'low': any(word in message_lower for word in 
                       ['low', 'minor', 'informational', 'baseline'])
        }
        
        primary_domain = max(domain_matches.items(), key=lambda x: x[1])[0] \
                        if domain_matches else 'network_security'
        
        primary_activity = max(activities.items(), key=lambda x: x[1])[0] \
                          if any(activities.values()) else 'monitoring'
        
        threat_level = max(threat_indicators.items(), key=lambda x: x[1])[0] \
                      if any(threat_indicators.values()) else 'medium'
        
        return {
            'primary_domain': primary_domain,
            'activity': primary_activity,
            'threat_level': threat_level,
            'domain_scores': domain_matches,
            'surveillance_indicators': self.extract_surveillance_indicators(message)
        }
    
    def extract_surveillance_indicators(self, message: str) -> List[str]:
        """Extract surveillance and security indicators from message."""
        indicators = [
            'logs', 'alerts', 'events', 'incidents', 'anomalies', 'patterns',
            'signatures', 'hashes', 'ips', 'domains', 'urls', 'processes',
            'connections', 'sessions', 'users', 'files', 'registry', 'network'
        ]
        
        message_lower = message.lower()
        found_indicators = [indicator for indicator in indicators 
                           if indicator in message_lower]
        
        return found_indicators[:8]  # Return up to 8 indicators
    
    def build_surveillance_prompt(self, monitoring_analysis: Dict[str, Any]) -> str:
        """Build surveillance and monitoring focused prompt."""
        domain = monitoring_analysis['primary_domain']
        activity = monitoring_analysis['activity']
        threat_level = monitoring_analysis['threat_level']
        indicators = monitoring_analysis.get('surveillance_indicators', [])
        
        prompt = f"\n\nSurveillance Focus: {domain.replace('_', ' ').title()}"
        prompt += f"\n- Activity: {activity.title()} operations"
        prompt += f"\n- Threat Level: {threat_level.upper()}"
        
        if indicators:
            prompt += f"\n- Key Indicators: {', '.join(indicators)}"
        
        domain_config = self.monitoring_domains.get(domain, {})
        if domain_config.get('focus'):
            prompt += f"\n- Focus Areas: {', '.join([f.replace('_', ' ') for f in domain_config['focus']])}"
        
        activity_guidance = {
            'detection': "Focus on identifying threats, anomalies, and security incidents.",
            'analysis': "Focus on deep investigation, pattern analysis, and forensic examination.",
            'monitoring': "Focus on continuous surveillance, real-time tracking, and status monitoring.",
            'alerting': "Focus on notification systems, escalation procedures, and alert management.",
            'response': "Focus on incident response, threat mitigation, and remediation actions."
        }
        
        threat_guidance = {
            'critical': "CRITICAL PRIORITY: Immediate attention required, potential active threat.",
            'high': "HIGH PRIORITY: Significant security concern requiring prompt investigation.",
            'medium': "MEDIUM PRIORITY: Notable activity that warrants investigation.",
            'low': "LOW PRIORITY: Informational or baseline monitoring activity."
        }
        
        prompt += f"\n\nActivity Guidance: {activity_guidance.get(activity, 'Provide comprehensive surveillance support.')}"
        prompt += f"\nThreat Context: {threat_guidance.get(threat_level, 'Standard monitoring procedures.')}"
        
        return prompt