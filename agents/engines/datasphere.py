"""
OneLastAI Platform - DataSphere Agent Engine
Advanced data analysis and insights specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DataSphereEngine(BaseAgentEngine):
    """
    DataSphere - Data Analysis Engine
    Specializes in data analysis, statistical insights, and data interpretation
    """
    
    def __init__(self):
        super().__init__('datasphere')
        self.analysis_types = self.initialize_analysis_types()
    
    def initialize_analysis_types(self) -> Dict[str, Any]:
        """Initialize data analysis types and methodologies."""
        return {
            'descriptive': {
                'methods': ['summary_statistics', 'frequency_analysis', 'distribution_analysis'],
                'outputs': ['means', 'medians', 'modes', 'ranges', 'percentiles'],
                'visualizations': ['histograms', 'box_plots', 'scatter_plots']
            },
            'diagnostic': {
                'methods': ['correlation_analysis', 'regression_analysis', 'variance_analysis'],
                'outputs': ['correlations', 'causations', 'relationships', 'patterns'],
                'visualizations': ['correlation_matrices', 'regression_plots', 'heatmaps']
            },
            'predictive': {
                'methods': ['machine_learning', 'time_series', 'forecasting'],
                'outputs': ['predictions', 'trends', 'forecasts', 'probabilities'],
                'visualizations': ['trend_lines', 'forecast_charts', 'prediction_intervals']
            },
            'prescriptive': {
                'methods': ['optimization', 'simulation', 'decision_analysis'],
                'outputs': ['recommendations', 'strategies', 'action_plans'],
                'visualizations': ['decision_trees', 'optimization_charts', 'scenario_comparisons']
            },
            'exploratory': {
                'methods': ['clustering', 'dimensionality_reduction', 'anomaly_detection'],
                'outputs': ['clusters', 'patterns', 'anomalies', 'insights'],
                'visualizations': ['cluster_plots', 'pca_plots', 'anomaly_charts']
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with data analysis focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'data_analysis'
            context['user_message'] = message
            
            # Analyze data requirements
            data_analysis = self.analyze_data_intent(message)
            context['data_analysis'] = data_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build data-focused system prompt
            data_prompt = self.build_data_prompt(data_analysis)
            enhanced_prompt = self.system_prompt + data_prompt
            
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
            logger.error(f"Error in DataSphere engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_data_intent(self, message: str) -> Dict[str, Any]:
        """Analyze data analysis intent and requirements."""
        message_lower = message.lower()
        
        # Detect analysis type
        type_scores = {}
        for analysis_type, config in self.analysis_types.items():
            score = 0
            if analysis_type in message_lower:
                score += 3
            
            # Check for method-specific indicators
            for method in config['methods']:
                if method.replace('_', ' ') in message_lower:
                    score += 2
            
            for output in config['outputs']:
                if output in message_lower:
                    score += 1
            
            if score > 0:
                type_scores[analysis_type] = score
        
        # Detect data characteristics
        data_types = {
            'numerical': any(word in message_lower for word in 
                             ['numbers', 'metrics', 'measurements', 'quantities']),
            'categorical': any(word in message_lower for word in 
                               ['categories', 'groups', 'classifications', 'labels']),
            'temporal': any(word in message_lower for word in 
                            ['time', 'dates', 'trends', 'seasonal', 'timeline']),
            'textual': any(word in message_lower for word in 
                           ['text', 'sentiment', 'nlp', 'language', 'comments'])
        }
        
        # Detect complexity level
        complexity = {
            'simple': any(word in message_lower for word in 
                          ['simple', 'basic', 'quick', 'overview']),
            'intermediate': any(word in message_lower for word in 
                                ['detailed', 'thorough', 'comprehensive']),
            'advanced': any(word in message_lower for word in 
                            ['advanced', 'complex', 'sophisticated', 'deep'])
        }
        
        # Detect output preferences
        outputs = {
            'statistical': any(word in message_lower for word in 
                               ['statistics', 'stats', 'numbers', 'calculations']),
            'visual': any(word in message_lower for word in 
                          ['chart', 'graph', 'plot', 'visualization', 'visual']),
            'narrative': any(word in message_lower for word in 
                             ['explain', 'story', 'insights', 'interpretation'])
        }
        
        primary_type = max(type_scores.items(), key=lambda x: x[1])[0] \
                      if type_scores else 'descriptive'
        
        primary_data_type = max(data_types.items(), key=lambda x: x[1])[0] \
                           if any(data_types.values()) else 'numerical'
        
        complexity_level = max(complexity.items(), key=lambda x: x[1])[0] \
                          if any(complexity.values()) else 'intermediate'
        
        preferred_outputs = [k for k, v in outputs.items() if v]
        
        return {
            'analysis_type': primary_type,
            'data_type': primary_data_type,
            'complexity': complexity_level,
            'output_preferences': preferred_outputs,
            'statistical_terms': self.extract_statistical_terms(message)
        }
    
    def extract_statistical_terms(self, message: str) -> List[str]:
        """Extract statistical and analytical terms mentioned."""
        terms = [
            'mean', 'median', 'mode', 'variance', 'deviation', 'correlation',
            'regression', 'distribution', 'probability', 'confidence', 'significance',
            'hypothesis', 'sample', 'population', 'outliers', 'clustering'
        ]
        
        message_lower = message.lower()
        detected = [term for term in terms if term in message_lower]
        
        return detected[:8]  # Return up to 8 statistical terms
    
    def build_data_prompt(self, data_analysis: Dict[str, Any]) -> str:
        """Build data analysis focused prompt."""
        analysis_type = data_analysis['analysis_type']
        data_type = data_analysis['data_type']
        complexity = data_analysis['complexity']
        outputs = data_analysis.get('output_preferences', [])
        terms = data_analysis.get('statistical_terms', [])
        
        prompt = f"\n\nData Analysis Focus: {analysis_type.title()}"
        prompt += f"\n- Data Type: {data_type.title()}"
        prompt += f"\n- Complexity Level: {complexity.title()}"
        
        if outputs:
            prompt += f"\n- Output Preferences: {', '.join(outputs)}"
        
        if terms:
            prompt += f"\n- Statistical Terms: {', '.join(terms)}"
        
        # Add analysis-specific guidance
        if analysis_type in self.analysis_types:
            type_config = self.analysis_types[analysis_type]
            prompt += f"\n- Recommended Methods: {', '.join([m.replace('_', ' ') for m in type_config['methods'][:3]])}"
            prompt += f"\n- Expected Outputs: {', '.join(type_config['outputs'][:3])}"
        
        complexity_guidance = {
            'simple': "Provide clear, straightforward analysis with basic insights and easy-to-understand explanations.",
            'intermediate': "Balance technical accuracy with accessibility, providing detailed insights with proper context.",
            'advanced': "Use sophisticated analytical methods, technical terminology, and comprehensive statistical analysis."
        }
        
        type_guidance = {
            'descriptive': "Focus on summarizing and describing the current state of the data.",
            'diagnostic': "Focus on understanding why certain patterns or relationships exist in the data.",
            'predictive': "Focus on forecasting future trends and outcomes based on historical data.",
            'prescriptive': "Focus on recommending specific actions based on data-driven insights.",
            'exploratory': "Focus on discovering hidden patterns and unexpected insights in the data."
        }
        
        prompt += f"\n\nComplexity Guidance: {complexity_guidance.get(complexity, 'Match analysis to appropriate complexity level.')}"
        prompt += f"\nAnalysis Guidance: {type_guidance.get(analysis_type, 'Provide comprehensive data analysis.')}"
        
        return prompt