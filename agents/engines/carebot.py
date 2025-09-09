"""
OneLastAI Platform - CareBot Agent Engine
Healthcare and medical assistance specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CareBotEngine(BaseAgentEngine):
    """
    CareBot - Healthcare Assistance Engine
    Specializes in healthcare information, medical guidance, and wellness support
    """
    
    def __init__(self):
        super().__init__('carebot')
        self.healthcare_domains = self.initialize_healthcare_domains()
    
    def initialize_healthcare_domains(self) -> Dict[str, Any]:
        """Initialize healthcare domains and their characteristics."""
        return {
            'general_health': {
                'topics': ['wellness', 'prevention', 'lifestyle', 'nutrition', 'exercise'],
                'guidance_types': ['educational', 'preventive', 'lifestyle_recommendations'],
                'disclaimer_level': 'moderate'
            },
            'symptoms': {
                'topics': ['symptom_analysis', 'possible_causes', 'when_to_seek_care'],
                'guidance_types': ['informational', 'triage_guidance', 'care_recommendations'],
                'disclaimer_level': 'high'
            },
            'medications': {
                'topics': ['drug_information', 'interactions', 'side_effects', 'adherence'],
                'guidance_types': ['educational', 'safety_information', 'adherence_support'],
                'disclaimer_level': 'high'
            },
            'chronic_conditions': {
                'topics': ['disease_management', 'lifestyle_modifications', 'monitoring'],
                'guidance_types': ['management_strategies', 'lifestyle_support', 'monitoring_guidance'],
                'disclaimer_level': 'high'
            },
            'mental_health': {
                'topics': ['emotional_wellbeing', 'stress_management', 'coping_strategies'],
                'guidance_types': ['supportive', 'educational', 'resource_referral'],
                'disclaimer_level': 'high'
            },
            'emergency': {
                'topics': ['urgent_care', 'emergency_signs', 'first_aid'],
                'guidance_types': ['emergency_guidance', 'immediate_actions', 'care_seeking'],
                'disclaimer_level': 'critical'
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with healthcare focus and appropriate disclaimers."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'healthcare_assistance'
            context['user_message'] = message
            
            # Analyze healthcare requirements
            healthcare_analysis = self.analyze_healthcare_intent(message)
            context['healthcare_analysis'] = healthcare_analysis
            
            # Check for emergency indicators
            if self.detect_emergency(message):
                return self.handle_emergency_response()
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build healthcare-focused system prompt
            healthcare_prompt = self.build_healthcare_prompt(healthcare_analysis)
            enhanced_prompt = self.system_prompt + healthcare_prompt
            
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
            
            # Add appropriate medical disclaimer
            response_with_disclaimer = self.add_medical_disclaimer(
                response, healthcare_analysis['domain']
            )
            
            return self.postprocess_response(response_with_disclaimer, context)
            
        except Exception as e:
            logger.error(f"Error in CareBot engine: {e}")
            return self.handle_error(e, context)
    
    def detect_emergency(self, message: str) -> bool:
        """Detect potential emergency situations."""
        emergency_keywords = [
            'chest pain', 'difficulty breathing', 'unconscious', 'severe bleeding',
            'heart attack', 'stroke', 'suicide', 'overdose', 'emergency',
            'call 911', 'ambulance', 'life threatening'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in emergency_keywords)
    
    def handle_emergency_response(self) -> str:
        """Handle emergency situations with appropriate response."""
        return (
            "🚨 **EMERGENCY DETECTED** 🚨\n\n"
            "If this is a medical emergency, please:\n"
            "• Call emergency services immediately (911 in US, 112 in EU)\n"
            "• Contact your local emergency number\n"
            "• Go to the nearest emergency room\n"
            "• Call poison control if needed\n\n"
            "I cannot provide emergency medical care. Please seek immediate professional help."
        )
    
    def analyze_healthcare_intent(self, message: str) -> Dict[str, Any]:
        """Analyze healthcare assistance intent and domain."""
        message_lower = message.lower()
        
        # Detect healthcare domain
        domain_scores = {}
        for domain, config in self.healthcare_domains.items():
            score = 0
            domain_name = domain.replace('_', ' ')
            if domain_name in message_lower:
                score += 3
            
            # Check for domain-specific topics
            for topic in config['topics']:
                if topic.replace('_', ' ') in message_lower:
                    score += 2
            
            if score > 0:
                domain_scores[domain] = score
        
        # Detect user type
        user_types = {
            'patient': any(word in message_lower for word in 
                           ['i_have', 'my_symptoms', 'i_feel', 'experiencing']),
            'caregiver': any(word in message_lower for word in 
                             ['caring_for', 'my_family', 'helping', 'caregiver']),
            'professional': any(word in message_lower for word in 
                                ['clinical', 'medical_professional', 'healthcare_worker']),
            'researcher': any(word in message_lower for word in 
                              ['research', 'study', 'evidence', 'literature'])
        }
        
        # Detect information needs
        needs = {
            'educational': any(word in message_lower for word in 
                               ['learn', 'understand', 'explain', 'information']),
            'guidance': any(word in message_lower for word in 
                            ['advice', 'recommendation', 'guidance', 'help']),
            'support': any(word in message_lower for word in 
                           ['support', 'coping', 'manage', 'deal_with']),
            'resources': any(word in message_lower for word in 
                             ['resources', 'where_to_find', 'services', 'programs'])
        }
        
        # Detect urgency level
        urgency = {
            'routine': any(word in message_lower for word in 
                           ['general', 'routine', 'regular', 'preventive']),
            'concerning': any(word in message_lower for word in 
                              ['worried', 'concerned', 'unusual', 'changed']),
            'urgent': any(word in message_lower for word in 
                          ['urgent', 'serious', 'severe', 'worsening'])
        }
        
        primary_domain = max(domain_scores.items(), key=lambda x: x[1])[0] \
                        if domain_scores else 'general_health'
        
        user_type = max(user_types.items(), key=lambda x: x[1])[0] \
                   if any(user_types.values()) else 'patient'
        
        primary_need = max(needs.items(), key=lambda x: x[1])[0] \
                      if any(needs.values()) else 'educational'
        
        urgency_level = max(urgency.items(), key=lambda x: x[1])[0] \
                       if any(urgency.values()) else 'routine'
        
        return {
            'domain': primary_domain,
            'user_type': user_type,
            'need': primary_need,
            'urgency': urgency_level,
            'medical_terms': self.extract_medical_terms(message)
        }
    
    def extract_medical_terms(self, message: str) -> List[str]:
        """Extract medical and healthcare terms mentioned."""
        terms = [
            'symptoms', 'diagnosis', 'treatment', 'medication', 'therapy',
            'prevention', 'wellness', 'health', 'condition', 'disease',
            'pain', 'fever', 'infection', 'chronic', 'acute'
        ]
        
        message_lower = message.lower()
        detected = [term for term in terms if term in message_lower]
        
        return detected[:8]  # Return up to 8 medical terms
    
    def build_healthcare_prompt(self, healthcare_analysis: Dict[str, Any]) -> str:
        """Build healthcare focused prompt with appropriate medical guidelines."""
        domain = healthcare_analysis['domain']
        user_type = healthcare_analysis['user_type']
        need = healthcare_analysis['need']
        urgency = healthcare_analysis['urgency']
        terms = healthcare_analysis.get('medical_terms', [])
        
        prompt = f"\n\nHealthcare Focus: {domain.replace('_', ' ').title()}"
        prompt += f"\n- User Type: {user_type.title()}"
        prompt += f"\n- Information Need: {need.title()}"
        prompt += f"\n- Urgency Level: {urgency.title()}"
        
        if terms:
            prompt += f"\n- Medical Terms: {', '.join(terms)}"
        
        # Add domain-specific guidance
        if domain in self.healthcare_domains:
            domain_config = self.healthcare_domains[domain]
            prompt += f"\n- Key Topics: {', '.join([t.replace('_', ' ') for t in domain_config['topics'][:3]])}"
            prompt += f"\n- Guidance Types: {', '.join([g.replace('_', ' ') for g in domain_config['guidance_types']])}"
        
        # Medical guidelines
        prompt += "\n\nMedical Guidelines:"
        prompt += "\n- Always emphasize consulting healthcare professionals for medical decisions"
        prompt += "\n- Provide educational information, not diagnostic or treatment advice"
        prompt += "\n- Include appropriate medical disclaimers"
        prompt += "\n- Encourage professional medical consultation for symptoms"
        prompt += "\n- Be supportive while maintaining professional boundaries"
        
        need_guidance = {
            'educational': "Provide clear, evidence-based health information with reliable sources.",
            'guidance': "Offer general guidance while emphasizing the need for professional medical advice.",
            'support': "Provide emotional support and coping strategies while encouraging professional help.",
            'resources': "Direct to appropriate healthcare resources, services, and professional support."
        }
        
        urgency_guidance = {
            'routine': "Provide comprehensive educational information for general health topics.",
            'concerning': "Encourage consulting healthcare professionals while providing supportive information.",
            'urgent': "Strongly recommend immediate professional medical consultation or emergency care."
        }
        
        prompt += f"\n\nNeed Guidance: {need_guidance.get(need, 'Provide appropriate healthcare information.')}"
        prompt += f"\nUrgency Guidance: {urgency_guidance.get(urgency, 'Match response to urgency level.')}"
        
        return prompt
    
    def add_medical_disclaimer(self, response: str, domain: str) -> str:
        """Add appropriate medical disclaimer based on domain."""
        disclaimers = {
            'general_health': "\n\n*This information is for educational purposes only and is not a substitute for professional medical advice.*",
            'symptoms': "\n\n⚠️ **Medical Disclaimer**: This information is not a substitute for professional medical diagnosis. Please consult a healthcare provider for proper evaluation of symptoms.",
            'medications': "\n\n⚠️ **Important**: This information is educational only. Always consult your healthcare provider or pharmacist before making any medication decisions.",
            'chronic_conditions': "\n\n⚠️ **Medical Disclaimer**: This information is educational and should not replace your healthcare provider's guidance for managing your condition.",
            'mental_health': "\n\n💙 **Support Notice**: If you're experiencing mental health crisis, please contact a mental health professional or crisis helpline immediately.",
            'emergency': "\n\n🚨 **Emergency Disclaimer**: This is not emergency medical advice. For medical emergencies, call emergency services immediately."
        }
        
        disclaimer = disclaimers.get(domain, disclaimers['general_health'])
        return response + disclaimer