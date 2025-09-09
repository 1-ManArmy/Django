"""
OneLastAI Platform - DataVision Agent Engine
Data visualization and dashboard creation specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DataVisionEngine(BaseAgentEngine):
    """
    DataVision - Data Visualization Engine
    Specializes in creating effective data visualizations and dashboards
    """
    
    def __init__(self):
        super().__init__('datavision')
        self.chart_types = self.initialize_chart_types()
    
    def initialize_chart_types(self) -> Dict[str, Any]:
        """Initialize visualization types and their best use cases."""
        return {
            'comparison': {
                'charts': ['bar_chart', 'column_chart', 'horizontal_bar', 'grouped_bar'],
                'use_cases': ['comparing_categories', 'ranking', 'before_after'],
                'data_types': ['categorical', 'discrete']
            },
            'distribution': {
                'charts': ['histogram', 'box_plot', 'violin_plot', 'density_plot'],
                'use_cases': ['data_spread', 'outliers', 'statistical_summary'],
                'data_types': ['numerical', 'continuous']
            },
            'relationship': {
                'charts': ['scatter_plot', 'bubble_chart', 'correlation_matrix', 'heatmap'],
                'use_cases': ['correlations', 'patterns', 'clustering'],
                'data_types': ['numerical', 'multivariate']
            },
            'temporal': {
                'charts': ['line_chart', 'area_chart', 'time_series', 'gantt_chart'],
                'use_cases': ['trends', 'time_analysis', 'forecasting'],
                'data_types': ['time_series', 'temporal']
            },
            'composition': {
                'charts': ['pie_chart', 'donut_chart', 'stacked_bar', 'treemap'],
                'use_cases': ['part_to_whole', 'hierarchical', 'proportions'],
                'data_types': ['categorical', 'hierarchical']
            },
            'geographic': {
                'charts': ['choropleth_map', 'symbol_map', 'flow_map', 'heat_map'],
                'use_cases': ['spatial_analysis', 'regional_comparison', 'geographic_trends'],
                'data_types': ['geographic', 'spatial']
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with data visualization focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'data_visualization'
            context['user_message'] = message
            
            # Analyze visualization requirements
            viz_analysis = self.analyze_visualization_intent(message)
            context['viz_analysis'] = viz_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build visualization-focused system prompt
            viz_prompt = self.build_visualization_prompt(viz_analysis)
            enhanced_prompt = self.system_prompt + viz_prompt
            
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
            logger.error(f"Error in DataVision engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_visualization_intent(self, message: str) -> Dict[str, Any]:
        """Analyze data visualization intent and requirements."""
        message_lower = message.lower()
        
        # Detect visualization purpose
        purpose_scores = {}
        for purpose, config in self.chart_types.items():
            score = 0
            if purpose in message_lower:
                score += 3
            
            # Check for purpose-specific use cases
            for use_case in config['use_cases']:
                if use_case.replace('_', ' ') in message_lower:
                    score += 2
            
            # Check for chart type mentions
            for chart in config['charts']:
                if chart.replace('_', ' ') in message_lower:
                    score += 1
            
            if score > 0:
                purpose_scores[purpose] = score
        
        # Detect visualization goals
        goals = {
            'exploration': any(word in message_lower for word in 
                               ['explore', 'discover', 'investigate', 'analyze']),
            'presentation': any(word in message_lower for word in 
                                ['present', 'report', 'dashboard', 'display']),
            'communication': any(word in message_lower for word in 
                                 ['communicate', 'explain', 'show', 'demonstrate']),
            'monitoring': any(word in message_lower for word in 
                              ['monitor', 'track', 'watch', 'alert'])
        }
        
        # Detect audience level
        audiences = {
            'technical': any(word in message_lower for word in 
                             ['technical', 'analyst', 'developer', 'expert']),
            'business': any(word in message_lower for word in 
                            ['executive', 'manager', 'stakeholder', 'business']),
            'general': any(word in message_lower for word in 
                           ['general', 'public', 'everyone', 'simple'])
        }
        
        # Detect interactivity needs
        interactivity = {
            'static': any(word in message_lower for word in 
                          ['static', 'print', 'report', 'document']),
            'interactive': any(word in message_lower for word in 
                               ['interactive', 'clickable', 'drill_down', 'filter']),
            'real_time': any(word in message_lower for word in 
                             ['real_time', 'live', 'streaming', 'dynamic'])
        }
        
        primary_purpose = max(purpose_scores.items(), key=lambda x: x[1])[0] \
                         if purpose_scores else 'comparison'
        
        primary_goal = max(goals.items(), key=lambda x: x[1])[0] \
                      if any(goals.values()) else 'presentation'
        
        target_audience = max(audiences.items(), key=lambda x: x[1])[0] \
                         if any(audiences.values()) else 'business'
        
        interaction_level = max(interactivity.items(), key=lambda x: x[1])[0] \
                           if any(interactivity.values()) else 'static'
        
        return {
            'purpose': primary_purpose,
            'goal': primary_goal,
            'audience': target_audience,
            'interactivity': interaction_level,
            'viz_elements': self.extract_viz_elements(message)
        }
    
    def extract_viz_elements(self, message: str) -> List[str]:
        """Extract visualization elements and features mentioned."""
        elements = [
            'color', 'legend', 'axis', 'title', 'labels', 'tooltip',
            'animation', 'filter', 'zoom', 'grid', 'annotation', 'theme'
        ]
        
        message_lower = message.lower()
        detected = [element for element in elements if element in message_lower]
        
        return detected[:8]  # Return up to 8 visualization elements
    
    def build_visualization_prompt(self, viz_analysis: Dict[str, Any]) -> str:
        """Build data visualization focused prompt."""
        purpose = viz_analysis['purpose']
        goal = viz_analysis['goal']
        audience = viz_analysis['audience']
        interactivity = viz_analysis['interactivity']
        elements = viz_analysis.get('viz_elements', [])
        
        prompt = f"\n\nVisualization Focus: {purpose.title()}"
        prompt += f"\n- Goal: {goal.title()}"
        prompt += f"\n- Target Audience: {audience.title()}"
        prompt += f"\n- Interactivity: {interactivity.replace('_', ' ').title()}"
        
        if elements:
            prompt += f"\n- Visual Elements: {', '.join(elements)}"
        
        # Add purpose-specific guidance
        if purpose in self.chart_types:
            purpose_config = self.chart_types[purpose]
            prompt += f"\n- Recommended Charts: {', '.join([c.replace('_', ' ') for c in purpose_config['charts'][:3]])}"
            prompt += f"\n- Best Use Cases: {', '.join([u.replace('_', ' ') for u in purpose_config['use_cases']])}"
        
        goal_guidance = {
            'exploration': "Focus on interactive visualizations that allow data discovery and pattern identification.",
            'presentation': "Focus on clear, polished visualizations suitable for formal presentation.",
            'communication': "Focus on intuitive visualizations that clearly convey key messages to the audience.",
            'monitoring': "Focus on real-time dashboards with alerts and key performance indicators."
        }
        
        audience_guidance = {
            'technical': "Use detailed visualizations with technical accuracy and comprehensive data display.",
            'business': "Use executive-level visualizations focusing on key insights and actionable information.",
            'general': "Use simple, clear visualizations that are easy to understand without technical background."
        }
        
        interactivity_guidance = {
            'static': "Design for print or static display with all necessary information clearly visible.",
            'interactive': "Include hover effects, clickable elements, and user controls for data exploration.",
            'real_time': "Design for live data updates with automatic refresh and dynamic scaling."
        }
        
        prompt += f"\n\nGoal Guidance: {goal_guidance.get(goal, 'Create effective data visualizations.')}"
        prompt += f"\nAudience Guidance: {audience_guidance.get(audience, 'Match visualization to audience needs.')}"
        prompt += f"\nInteractivity Guidance: {interactivity_guidance.get(interactivity, 'Design appropriate interactivity level.')}"
        
        return prompt