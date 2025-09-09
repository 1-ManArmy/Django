"""
OneLastAI Platform - Reportly Agent Engine
Business reporting and documentation specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ReportlyEngine(BaseAgentEngine):
    """
    Reportly - Business Reporting Engine
    Specializes in creating comprehensive business reports and documentation
    """
    
    def __init__(self):
        super().__init__('reportly')
        self.report_types = self.initialize_report_types()
    
    def initialize_report_types(self) -> Dict[str, Any]:
        """Initialize business report types and their characteristics."""
        return {
            'financial': {
                'sections': ['executive_summary', 'revenue_analysis', 'expense_breakdown', 'profitability', 'forecasts'],
                'metrics': ['revenue', 'costs', 'profit_margins', 'roi', 'cash_flow'],
                'audience': ['executives', 'investors', 'finance_teams']
            },
            'performance': {
                'sections': ['kpi_summary', 'trend_analysis', 'benchmark_comparison', 'recommendations'],
                'metrics': ['kpis', 'targets', 'variances', 'trends', 'benchmarks'],
                'audience': ['management', 'department_heads', 'stakeholders']
            },
            'market_analysis': {
                'sections': ['market_overview', 'competitive_landscape', 'opportunities', 'threats'],
                'metrics': ['market_size', 'growth_rate', 'market_share', 'competitor_analysis'],
                'audience': ['strategy_teams', 'marketing', 'executives']
            },
            'operational': {
                'sections': ['process_efficiency', 'resource_utilization', 'quality_metrics', 'improvement_areas'],
                'metrics': ['efficiency_ratios', 'utilization_rates', 'quality_scores', 'cycle_times'],
                'audience': ['operations_managers', 'process_owners', 'quality_teams']
            },
            'project': {
                'sections': ['project_status', 'milestone_progress', 'risk_assessment', 'next_steps'],
                'metrics': ['completion_percentage', 'budget_variance', 'timeline_adherence', 'resource_allocation'],
                'audience': ['project_managers', 'sponsors', 'team_members']
            },
            'compliance': {
                'sections': ['regulatory_overview', 'compliance_status', 'audit_findings', 'action_plans'],
                'metrics': ['compliance_scores', 'audit_results', 'violation_counts', 'remediation_progress'],
                'audience': ['compliance_officers', 'auditors', 'legal_teams']
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with business reporting focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'business_reporting'
            context['user_message'] = message
            
            # Analyze reporting requirements
            report_analysis = self.analyze_report_intent(message)
            context['report_analysis'] = report_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build reporting-focused system prompt
            report_prompt = self.build_report_prompt(report_analysis)
            enhanced_prompt = self.system_prompt + report_prompt
            
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
            logger.error(f"Error in Reportly engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_report_intent(self, message: str) -> Dict[str, Any]:
        """Analyze business reporting intent and requirements."""
        message_lower = message.lower()
        
        # Detect report type
        type_scores = {}
        for report_type, config in self.report_types.items():
            score = 0
            type_name = report_type.replace('_', ' ')
            if type_name in message_lower or report_type in message_lower:
                score += 3
            
            # Check for type-specific sections and metrics
            for section in config['sections']:
                if section.replace('_', ' ') in message_lower:
                    score += 2
            
            for metric in config['metrics']:
                if metric.replace('_', ' ') in message_lower:
                    score += 1
            
            if score > 0:
                type_scores[report_type] = score
        
        # Detect report purpose
        purposes = {
            'decision_making': any(word in message_lower for word in 
                                   ['decision', 'choose', 'select', 'evaluate']),
            'monitoring': any(word in message_lower for word in 
                              ['monitor', 'track', 'watch', 'observe']),
            'communication': any(word in message_lower for word in 
                                 ['communicate', 'inform', 'update', 'share']),
            'compliance': any(word in message_lower for word in 
                              ['comply', 'audit', 'regulation', 'requirement'])
        }
        
        # Detect format preferences
        formats = {
            'detailed': any(word in message_lower for word in 
                            ['detailed', 'comprehensive', 'thorough', 'complete']),
            'summary': any(word in message_lower for word in 
                           ['summary', 'brief', 'overview', 'highlights']),
            'executive': any(word in message_lower for word in 
                             ['executive', 'high_level', 'strategic', 'leadership']),
            'technical': any(word in message_lower for word in 
                             ['technical', 'detailed_analysis', 'deep_dive'])
        }
        
        # Detect urgency level
        urgency = {
            'urgent': any(word in message_lower for word in 
                          ['urgent', 'asap', 'immediate', 'rush']),
            'routine': any(word in message_lower for word in 
                           ['routine', 'regular', 'scheduled', 'periodic']),
            'ad_hoc': any(word in message_lower for word in 
                          ['ad_hoc', 'one_time', 'special', 'custom'])
        }
        
        primary_type = max(type_scores.items(), key=lambda x: x[1])[0] \
                      if type_scores else 'performance'
        
        primary_purpose = max(purposes.items(), key=lambda x: x[1])[0] \
                         if any(purposes.values()) else 'communication'
        
        preferred_format = max(formats.items(), key=lambda x: x[1])[0] \
                          if any(formats.values()) else 'summary'
        
        urgency_level = max(urgency.items(), key=lambda x: x[1])[0] \
                       if any(urgency.values()) else 'routine'
        
        return {
            'type': primary_type,
            'purpose': primary_purpose,
            'format': preferred_format,
            'urgency': urgency_level,
            'business_terms': self.extract_business_terms(message)
        }
    
    def extract_business_terms(self, message: str) -> List[str]:
        """Extract business and reporting terms mentioned."""
        terms = [
            'revenue', 'profit', 'roi', 'kpi', 'metrics', 'analysis',
            'benchmark', 'forecast', 'budget', 'variance', 'trend', 'growth',
            'performance', 'efficiency', 'quality', 'compliance', 'risk'
        ]
        
        message_lower = message.lower()
        detected = [term for term in terms if term in message_lower]
        
        return detected[:8]  # Return up to 8 business terms
    
    def build_report_prompt(self, report_analysis: Dict[str, Any]) -> str:
        """Build business reporting focused prompt."""
        report_type = report_analysis['type']
        purpose = report_analysis['purpose']
        format_type = report_analysis['format']
        urgency = report_analysis['urgency']
        terms = report_analysis.get('business_terms', [])
        
        prompt = f"\n\nReport Focus: {report_type.replace('_', ' ').title()} Report"
        prompt += f"\n- Purpose: {purpose.replace('_', ' ').title()}"
        prompt += f"\n- Format: {format_type.title()}"
        prompt += f"\n- Urgency: {urgency.replace('_', ' ').title()}"
        
        if terms:
            prompt += f"\n- Business Terms: {', '.join(terms)}"
        
        # Add report-specific guidance
        if report_type in self.report_types:
            type_config = self.report_types[report_type]
            prompt += f"\n- Key Sections: {', '.join([s.replace('_', ' ') for s in type_config['sections'][:3]])}"
            prompt += f"\n- Important Metrics: {', '.join([m.replace('_', ' ') for m in type_config['metrics'][:3]])}"
            prompt += f"\n- Target Audience: {', '.join([a.replace('_', ' ') for a in type_config['audience']])}"
        
        purpose_guidance = {
            'decision_making': "Structure the report to clearly present options, analysis, and recommendations for decision makers.",
            'monitoring': "Focus on tracking metrics, identifying trends, and highlighting areas requiring attention.",
            'communication': "Emphasize clear messaging, key insights, and actionable information for stakeholders.",
            'compliance': "Ensure thorough documentation, regulatory alignment, and audit trail completeness."
        }
        
        format_guidance = {
            'detailed': "Provide comprehensive analysis with supporting data, methodology, and detailed explanations.",
            'summary': "Focus on key insights, main findings, and high-level recommendations in concise format.",
            'executive': "Emphasize strategic implications, business impact, and executive-level recommendations.",
            'technical': "Include detailed methodology, technical analysis, and comprehensive data documentation."
        }
        
        urgency_guidance = {
            'urgent': "Prioritize critical information, immediate actions, and time-sensitive insights.",
            'routine': "Follow standard reporting format with consistent structure and regular update patterns.",
            'ad_hoc': "Focus on specific questions or issues with customized analysis and targeted insights."
        }
        
        prompt += f"\n\nPurpose Guidance: {purpose_guidance.get(purpose, 'Create comprehensive business reports.')}"
        prompt += f"\nFormat Guidance: {format_guidance.get(format_type, 'Match report format to audience needs.')}"
        prompt += f"\nUrgency Guidance: {urgency_guidance.get(urgency, 'Balance thoroughness with timeline requirements.')}"
        
        return prompt