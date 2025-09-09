"""
OneLastAI Platform - NetScope Agent Engine
Network analysis and monitoring specialist for connectivity and security
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class NetScopeEngine(BaseAgentEngine):
    """
    NetScope - Network Analysis Engine
    Specializes in network monitoring, security analysis, and connectivity optimization
    """
    
    def __init__(self):
        super().__init__('netscope')
        self.network_layers = self.initialize_network_layers()
    
    def initialize_network_layers(self) -> Dict[str, Any]:
        """Initialize network analysis layers and focus areas."""
        return {
            'physical': {
                'components': ['cables', 'switches', 'routers', 'access_points'],
                'metrics': ['signal_strength', 'connectivity', 'hardware_status']
            },
            'data_link': {
                'components': ['mac_addresses', 'vlans', 'switches'],
                'metrics': ['frame_errors', 'collision_rate', 'bandwidth_utilization']
            },
            'network': {
                'components': ['ip_addresses', 'routing', 'subnets'],
                'metrics': ['latency', 'packet_loss', 'routing_efficiency']
            },
            'transport': {
                'components': ['tcp_udp', 'ports', 'connections'],
                'metrics': ['connection_count', 'throughput', 'error_rate']
            },
            'application': {
                'components': ['services', 'protocols', 'apis'],
                'metrics': ['response_time', 'availability', 'performance']
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with network analysis focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'network_analysis'
            context['user_message'] = message
            
            # Analyze network intent
            network_analysis = self.analyze_network_intent(message)
            context['network_analysis'] = network_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build network-focused system prompt
            network_prompt = self.build_network_prompt(network_analysis)
            enhanced_prompt = self.system_prompt + network_prompt
            
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
            logger.error(f"Error in NetScope engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_network_intent(self, message: str) -> Dict[str, Any]:
        """Analyze network-related intent and focus areas."""
        message_lower = message.lower()
        
        # Identify network layers of interest
        layer_focus = []
        for layer, config in self.network_layers.items():
            if any(comp in message_lower for comp in config['components']):
                layer_focus.append(layer)
        
        # Determine analysis type
        analysis_types = {
            'monitoring': any(word in message_lower for word in 
                              ['monitor', 'watch', 'track', 'observe']),
            'troubleshooting': any(word in message_lower for word in 
                                   ['problem', 'issue', 'error', 'fail', 'slow']),
            'optimization': any(word in message_lower for word in 
                                ['optimize', 'improve', 'enhance', 'speed']),
            'security': any(word in message_lower for word in 
                            ['security', 'attack', 'breach', 'vulnerability']),
            'configuration': any(word in message_lower for word in 
                                 ['configure', 'setup', 'install', 'deploy'])
        }
        
        return {
            'layer_focus': layer_focus if layer_focus else ['network'],
            'analysis_type': max(analysis_types.items(), key=lambda x: x[1])[0] 
                            if any(analysis_types.values()) else 'monitoring',
            'all_types': {k: v for k, v in analysis_types.items() if v},
            'network_indicators': self.extract_network_indicators(message)
        }
    
    def extract_network_indicators(self, message: str) -> List[str]:
        """Extract network-related indicators from the message."""
        network_terms = [
            'ip', 'dns', 'dhcp', 'tcp', 'udp', 'http', 'https', 'ssh', 'ftp',
            'ping', 'traceroute', 'bandwidth', 'latency', 'throughput',
            'firewall', 'router', 'switch', 'gateway', 'subnet', 'vlan'
        ]
        
        message_lower = message.lower()
        found_terms = [term for term in network_terms if term in message_lower]
        
        return found_terms[:8]  # Return up to 8 network indicators
    
    def build_network_prompt(self, network_analysis: Dict[str, Any]) -> str:
        """Build network analysis focused prompt."""
        layers = network_analysis['layer_focus']
        analysis_type = network_analysis['analysis_type']
        indicators = network_analysis.get('network_indicators', [])
        
        prompt = f"\n\nNetwork Analysis Focus: {analysis_type.title()}"
        prompt += f"\n- Target layers: {', '.join([l.replace('_', ' ').title() for l in layers])}"
        
        if indicators:
            prompt += f"\n- Network components: {', '.join(indicators)}"
        
        type_guidance = {
            'monitoring': "Focus on network performance metrics, status monitoring, and real-time analysis.",
            'troubleshooting': "Focus on problem diagnosis, root cause analysis, and solution recommendations.",
            'optimization': "Focus on performance improvements, bottleneck identification, and efficiency gains.",
            'security': "Focus on security assessment, threat detection, and vulnerability analysis.",
            'configuration': "Focus on network setup, configuration best practices, and deployment strategies."
        }
        
        prompt += f"\n\nGuidance: {type_guidance.get(analysis_type, 'Provide comprehensive network analysis.')}"
        
        return prompt