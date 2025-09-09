"""
OneLastAI Platform - TaskMaster Agent Engine
Productivity and task management optimization specialist
"""
from .base import BaseAgentEngine
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class TaskMasterEngine(BaseAgentEngine):
    """
    TaskMaster - Productivity Engine
    Specializes in task management, productivity optimization, and workflow improvement
    """
    
    def __init__(self):
        super().__init__('taskmaster')
        self.productivity_systems = self.initialize_productivity_systems()
    
    def initialize_productivity_systems(self) -> Dict[str, Any]:
        """Initialize productivity methodologies and systems."""
        return {
            'gtd': {
                'name': 'Getting Things Done',
                'principles': ['capture', 'clarify', 'organize', 'reflect', 'engage'],
                'tools': ['inbox', 'contexts', 'next_actions', 'someday_maybe'],
                'best_for': ['complex_workflows', 'multiple_projects', 'knowledge_workers']
            },
            'kanban': {
                'name': 'Kanban Method',
                'principles': ['visualize_workflow', 'limit_wip', 'manage_flow', 'continuous_improvement'],
                'tools': ['boards', 'cards', 'columns', 'wip_limits'],
                'best_for': ['team_collaboration', 'visual_learners', 'continuous_workflow']
            },
            'pomodoro': {
                'name': 'Pomodoro Technique',
                'principles': ['time_boxing', 'focused_work', 'regular_breaks', 'tracking'],
                'tools': ['timer', 'task_list', 'break_schedule', 'progress_tracking'],
                'best_for': ['focus_issues', 'procrastination', 'time_awareness']
            },
            'eisenhower': {
                'name': 'Eisenhower Matrix',
                'principles': ['urgency_vs_importance', 'quadrant_classification', 'delegation', 'elimination'],
                'tools': ['matrix', 'prioritization', 'delegation_list', 'elimination_criteria'],
                'best_for': ['prioritization', 'decision_making', 'overwhelm']
            },
            'scrum': {
                'name': 'Scrum Framework',
                'principles': ['sprints', 'daily_standups', 'retrospectives', 'iterative_improvement'],
                'tools': ['sprint_board', 'backlog', 'burndown_charts', 'user_stories'],
                'best_for': ['agile_teams', 'software_development', 'iterative_work']
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process message with productivity and task management focus."""
        if not self.validate_input(message):
            return self.handle_error(ValueError("Invalid input"), context)
        
        try:
            context = self.preprocess_message(message, context)
            context['conversation_type'] = 'productivity_management'
            context['user_message'] = message
            
            # Analyze productivity requirements
            productivity_analysis = self.analyze_productivity_intent(message)
            context['productivity_analysis'] = productivity_analysis
            
            from ai_services.services import AIServiceFactory
            ai_service = AIServiceFactory.get_service('openai')
            
            # Build productivity-focused system prompt
            productivity_prompt = self.build_productivity_prompt(productivity_analysis)
            enhanced_prompt = self.system_prompt + productivity_prompt
            
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
            logger.error(f"Error in TaskMaster engine: {e}")
            return self.handle_error(e, context)
    
    def analyze_productivity_intent(self, message: str) -> Dict[str, Any]:
        """Analyze productivity and task management intent."""
        message_lower = message.lower()
        
        # Detect productivity system preference
        system_scores = {}
        for system_key, system_config in self.productivity_systems.items():
            score = 0
            system_name = system_config['name'].lower()
            
            if system_key in message_lower or system_name in message_lower:
                score += 3
            
            # Check for system-specific principles and tools
            for principle in system_config['principles']:
                if principle.replace('_', ' ') in message_lower:
                    score += 2
            
            for tool in system_config['tools']:
                if tool.replace('_', ' ') in message_lower:
                    score += 1
            
            if score > 0:
                system_scores[system_key] = score
        
        # Detect productivity challenges
        challenges = {
            'overwhelm': any(word in message_lower for word in 
                             ['overwhelmed', 'too_much', 'stressed', 'overloaded']),
            'procrastination': any(word in message_lower for word in 
                                   ['procrastinate', 'delay', 'postpone', 'avoid']),
            'focus': any(word in message_lower for word in 
                         ['focus', 'concentration', 'distracted', 'attention']),
            'organization': any(word in message_lower for word in 
                                ['organize', 'messy', 'chaotic', 'structure']),
            'time_management': any(word in message_lower for word in 
                                   ['time', 'schedule', 'deadline', 'urgent'])
        }
        
        # Detect work context
        contexts = {
            'individual': any(word in message_lower for word in 
                              ['personal', 'individual', 'solo', 'myself']),
            'team': any(word in message_lower for word in 
                        ['team', 'group', 'collaboration', 'together']),
            'project': any(word in message_lower for word in 
                           ['project', 'initiative', 'campaign', 'goal']),
            'daily': any(word in message_lower for word in 
                         ['daily', 'routine', 'habits', 'regular'])
        }
        
        # Detect improvement areas
        improvements = {
            'efficiency': any(word in message_lower for word in 
                              ['efficient', 'faster', 'streamline', 'optimize']),
            'quality': any(word in message_lower for word in 
                           ['quality', 'better', 'improve', 'enhance']),
            'balance': any(word in message_lower for word in 
                           ['balance', 'work_life', 'sustainable', 'wellness']),
            'growth': any(word in message_lower for word in 
                          ['learn', 'develop', 'skill', 'growth'])
        }
        
        primary_system = max(system_scores.items(), key=lambda x: x[1])[0] \
                        if system_scores else 'gtd'
        
        main_challenge = max(challenges.items(), key=lambda x: x[1])[0] \
                        if any(challenges.values()) else 'organization'
        
        work_context = max(contexts.items(), key=lambda x: x[1])[0] \
                      if any(contexts.values()) else 'individual'
        
        improvement_focus = max(improvements.items(), key=lambda x: x[1])[0] \
                           if any(improvements.values()) else 'efficiency'
        
        return {
            'system': primary_system,
            'challenge': main_challenge,
            'context': work_context,
            'improvement': improvement_focus,
            'productivity_terms': self.extract_productivity_terms(message)
        }
    
    def extract_productivity_terms(self, message: str) -> List[str]:
        """Extract productivity and task management terms mentioned."""
        terms = [
            'priority', 'deadline', 'goal', 'milestone', 'task', 'project',
            'schedule', 'planning', 'workflow', 'process', 'automation',
            'delegation', 'collaboration', 'review', 'tracking', 'metrics'
        ]
        
        message_lower = message.lower()
        detected = [term for term in terms if term in message_lower]
        
        return detected[:8]  # Return up to 8 productivity terms
    
    def build_productivity_prompt(self, productivity_analysis: Dict[str, Any]) -> str:
        """Build productivity and task management focused prompt."""
        system = productivity_analysis['system']
        challenge = productivity_analysis['challenge']
        context = productivity_analysis['context']
        improvement = productivity_analysis['improvement']
        terms = productivity_analysis.get('productivity_terms', [])
        
        prompt = f"\n\nProductivity Focus: {system.upper()} System"
        prompt += f"\n- Main Challenge: {challenge.replace('_', ' ').title()}"
        prompt += f"\n- Work Context: {context.title()}"
        prompt += f"\n- Improvement Goal: {improvement.title()}"
        
        if terms:
            prompt += f"\n- Key Terms: {', '.join(terms)}"
        
        # Add system-specific guidance
        if system in self.productivity_systems:
            system_config = self.productivity_systems[system]
            prompt += f"\n- System: {system_config['name']}"
            prompt += f"\n- Core Principles: {', '.join([p.replace('_', ' ') for p in system_config['principles'][:3]])}"
            prompt += f"\n- Key Tools: {', '.join([t.replace('_', ' ') for t in system_config['tools'][:3]])}"
        
        challenge_guidance = {
            'overwhelm': "Focus on breaking down tasks, prioritization techniques, and workload management strategies.",
            'procrastination': "Focus on motivation techniques, task breakdown, and accountability systems.",
            'focus': "Focus on attention management, distraction elimination, and deep work practices.",
            'organization': "Focus on systems thinking, workflow design, and structured approaches.",
            'time_management': "Focus on scheduling techniques, time estimation, and deadline management."
        }
        
        context_guidance = {
            'individual': "Provide personal productivity strategies and self-management techniques.",
            'team': "Focus on collaboration tools, team workflows, and coordination strategies.",
            'project': "Focus on project management methodologies and goal achievement frameworks.",
            'daily': "Focus on habit formation, routine optimization, and consistency strategies."
        }
        
        improvement_guidance = {
            'efficiency': "Focus on automation, streamlining processes, and eliminating waste.",
            'quality': "Focus on standards, review processes, and continuous improvement.",
            'balance': "Focus on sustainable practices, boundaries, and holistic productivity.",
            'growth': "Focus on skill development, learning systems, and capability building."
        }
        
        prompt += f"\n\nChallenge Guidance: {challenge_guidance.get(challenge, 'Address productivity challenges systematically.')}"
        prompt += f"\nContext Guidance: {context_guidance.get(context, 'Adapt strategies to work context.')}"
        prompt += f"\nImprovement Guidance: {improvement_guidance.get(improvement, 'Focus on sustainable productivity improvement.')}"
        
        return prompt