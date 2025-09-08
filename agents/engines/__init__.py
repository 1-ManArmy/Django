"""
Agent Factory for OneLastAI Platform.
Creates and manages AI agent instances.
"""

from typing import Dict, Type, Optional
from .base import AgentEngine
from .conversational import (
    NeoChatAgent, PersonaXAgent, GirlfriendAgent, 
    EmotiSenseAgent, CallGhostAgent, MemoraAgent
)
from .technical import (
    ConfigAIAgent, InfoSeekAgent, DocuMindAgent,
    NetScopeAgent, AuthWiseAgent, SpyLensAgent
)
from .creative import (
    CineGenAgent, ContentCrafterAgent, DreamWeaverAgent,
    IdeaForgeAgent, AIBlogsterAgent, VocaMindAgent
)
from .business import (
    DataSphereAgent, DataVisionAgent, TaskMasterAgent,
    ReportlyAgent, DNAForgeAgent, CareBotAgent
)
import logging

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory class for creating AI agent instances."""
    
    # Registry of all available agents
    _agents: Dict[str, Type[AgentEngine]] = {
        # Conversational Agents
        'neochat': NeoChatAgent,
        'personax': PersonaXAgent,
        'girlfriend': GirlfriendAgent,
        'emotisense': EmotiSenseAgent,
        'callghost': CallGhostAgent,
        'memora': MemoraAgent,
        
        # Technical Agents
        'configai': ConfigAIAgent,
        'infoseek': InfoSeekAgent,
        'documind': DocuMindAgent,
        'netscope': NetScopeAgent,
        'authwise': AuthWiseAgent,
        'spylens': SpyLensAgent,
        
        # Creative Agents
        'cinegen': CineGenAgent,
        'contentcrafter': ContentCrafterAgent,
        'dreamweaver': DreamWeaverAgent,
        'ideaforge': IdeaForgeAgent,
        'aiblogster': AIBlogsterAgent,
        'vocamind': VocaMindAgent,
        
        # Business Agents
        'datasphere': DataSphereAgent,
        'datavision': DataVisionAgent,
        'taskmaster': TaskMasterAgent,
        'reportly': ReportlyAgent,
        'dnaforge': DNAForgeAgent,
        'carebot': CareBotAgent,
    }
    
    @classmethod
    def create_agent(cls, agent_id: str) -> AgentEngine:
        """Create an agent instance by ID."""
        if agent_id not in cls._agents:
            raise ValueError(f"Agent '{agent_id}' is not available. "
                           f"Available agents: {list(cls._agents.keys())}")
        
        agent_class = cls._agents[agent_id]
        try:
            return agent_class(agent_id)
        except Exception as e:
            logger.error(f"Failed to create agent '{agent_id}': {e}")
            raise
    
    @classmethod
    def get_available_agents(cls) -> Dict[str, str]:
        """Get list of available agents with their class names."""
        return {
            agent_id: agent_class.__name__ 
            for agent_id, agent_class in cls._agents.items()
        }
    
    @classmethod
    def is_agent_available(cls, agent_id: str) -> bool:
        """Check if an agent is available."""
        return agent_id in cls._agents
    
    @classmethod
    def register_agent(cls, agent_id: str, agent_class: Type[AgentEngine]):
        """Register a new agent class."""
        cls._agents[agent_id] = agent_class
        logger.info(f"Registered agent '{agent_id}': {agent_class.__name__}")
    
    @classmethod
    def get_agents_by_category(cls) -> Dict[str, list]:
        """Get agents organized by category."""
        from .base import ConversationalAgent, TechnicalAgent, CreativeAgent, BusinessAgent
        
        categories = {
            'conversational': [],
            'technical': [],
            'creative': [],
            'business': []
        }
        
        for agent_id, agent_class in cls._agents.items():
            if issubclass(agent_class, ConversationalAgent):
                categories['conversational'].append(agent_id)
            elif issubclass(agent_class, TechnicalAgent):
                categories['technical'].append(agent_id)
            elif issubclass(agent_class, CreativeAgent):
                categories['creative'].append(agent_id)
            elif issubclass(agent_class, BusinessAgent):
                categories['business'].append(agent_id)
        
        return categories


class AgentManager:
    """Manager class for agent lifecycle and caching."""
    
    def __init__(self):
        self._agent_cache: Dict[str, AgentEngine] = {}
        self._max_cache_size = 50
    
    def get_agent(self, agent_id: str) -> AgentEngine:
        """Get agent instance with caching."""
        if agent_id in self._agent_cache:
            return self._agent_cache[agent_id]
        
        # Create new agent
        agent = AgentFactory.create_agent(agent_id)
        
        # Cache management
        if len(self._agent_cache) >= self._max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self._agent_cache))
            del self._agent_cache[oldest_key]
        
        self._agent_cache[agent_id] = agent
        logger.info(f"Cached agent '{agent_id}'")
        
        return agent
    
    def clear_cache(self):
        """Clear the agent cache."""
        self._agent_cache.clear()
        logger.info("Agent cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            'cached_agents': len(self._agent_cache),
            'max_cache_size': self._max_cache_size,
            'cache_usage': len(self._agent_cache) / self._max_cache_size * 100
        }
    
    async def process_message(self, agent_id: str, message: str, 
                            conversation_id: str = None, user=None, 
                            **kwargs) -> Dict:
        """Process message through specified agent."""
        try:
            agent = self.get_agent(agent_id)
            return await agent.process_message(
                message, conversation_id, user, **kwargs
            )
        except Exception as e:
            logger.error(f"Error processing message with agent '{agent_id}': {e}")
            return {
                'error': 'Agent processing failed',
                'message': str(e),
                'agent_id': agent_id
            }
    
    async def process_message_stream(self, agent_id: str, message: str,
                                   conversation_id: str = None, user=None,
                                   **kwargs):
        """Process message with streaming response."""
        try:
            agent = self.get_agent(agent_id)
            async for chunk in agent.process_message_stream(
                message, conversation_id, user, **kwargs
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Error streaming with agent '{agent_id}': {e}")
            yield {
                'error': 'Agent streaming failed',
                'message': str(e),
                'agent_id': agent_id
            }


# Global agent manager instance
agent_manager = AgentManager()


def get_agent_info() -> Dict:
    """Get comprehensive information about all agents."""
    agents_by_category = AgentFactory.get_agents_by_category()
    available_agents = AgentFactory.get_available_agents()
    cache_stats = agent_manager.get_cache_stats()
    
    return {
        'total_agents': len(available_agents),
        'agents_by_category': agents_by_category,
        'available_agents': available_agents,
        'cache_stats': cache_stats,
        'categories': {
            'conversational': 'Specialized in natural conversation and interaction',
            'technical': 'Expert in technical tasks and problem-solving',
            'creative': 'Focused on creative tasks and content generation',
            'business': 'Designed for business analysis and operations'
        }
    }