"""
AI Agents Models for OneLastAI Platform.
Manages the 24 specialized AI agents and their interactions.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from ai_services.models import AIServiceConfig, Conversation
import uuid

User = get_user_model()


class AgentCategory(models.Model):
    """Categories for organizing AI agents."""
    
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)  # Icon class name
    color = models.CharField(max_length=7, default='#0066CC')  # Hex color
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _("Agent Category")
        verbose_name_plural = _("Agent Categories")
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.display_name


class Agent(models.Model):
    """The 24 specialized AI agents."""
    
    # Agent identifiers - 27 specialized AI agents
    AGENT_CHOICES = [
        # Conversation Agents (7)
        ('neochat', 'NeoChat - Advanced Conversational AI'),
        ('personax', 'PersonaX - Personality-driven Chat'),
        ('girlfriend', 'Girlfriend - Emotional Companion'),
        ('emotisense', 'EmotiSense - Emotion Analysis'),
        ('callghost', 'CallGhost - Voice Interactions'),
        ('memora', 'Memora - Memory-enhanced AI'),
        ('socialwise', 'SocialWise - Social Intelligence Expert'),
        
        # Technical Agents (7)
        ('configai', 'ConfigAI - Technical Configuration'),
        ('infoseek', 'InfoSeek - Research & Analysis'),
        ('documind', 'DocuMind - Document Processing'),
        ('netscope', 'NetScope - Network Analysis'),
        ('authwise', 'AuthWise - Security Consulting'),
        ('spylens', 'SpyLens - Data Investigation'),
        ('codemaster', 'CodeMaster - Programming Expert'),
        
        # Creative Agents (7)
        ('cinegen', 'CineGen - Video Production'),
        ('contentcrafter', 'ContentCrafter - Content Creation'),
        ('dreamweaver', 'DreamWeaver - Creative Ideation'),
        ('ideaforge', 'IdeaForge - Innovation Catalyst'),
        ('aiblogster', 'AIBlogster - Blog Generation'),
        ('vocamind', 'VocaMind - Voice Synthesis'),
        ('artisan', 'Artisan - Digital Art Creator'),
        
        # Business Agents (6)
        ('datasphere', 'DataSphere - Data Analytics'),
        ('datavision', 'DataVision - Business Intelligence'),
        ('taskmaster', 'TaskMaster - Project Management'),
        ('reportly', 'Reportly - Report Generation'),
        ('dnaforge', 'DNAForge - Growth Optimization'),
        ('carebot', 'CareBot - Health Insights'),
    ]
    
    agent_id = models.CharField(max_length=50, choices=AGENT_CHOICES, unique=True)
    category = models.ForeignKey(AgentCategory, on_delete=models.CASCADE, 
                               related_name='agents')
    name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=200)
    description = models.TextField()
    avatar_url = models.URLField(blank=True)
    personality_prompt = models.TextField()
    system_prompt = models.TextField()
    
    # Configuration
    default_ai_config = models.ForeignKey(AIServiceConfig, on_delete=models.SET_NULL,
                                        null=True, blank=True)
    engine_class = models.CharField(max_length=100, blank=True,
                                  help_text="Python class path for agent engine")
    config_file = models.CharField(max_length=100, blank=True,
                                 help_text="YAML config file path")
    capabilities = models.JSONField(default=list)  # List of capabilities
    supported_features = models.JSONField(default=list)  # Supported features
    tools = models.JSONField(default=list)  # Available tools/functions
    
    # Behavior Settings
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=2000)
    memory_enabled = models.BooleanField(default=True)
    streaming_enabled = models.BooleanField(default=True)
    voice_enabled = models.BooleanField(default=False)
    image_generation = models.BooleanField(default=False)
    video_generation = models.BooleanField(default=False)
    
    # Status and Metadata
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    total_conversations = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("AI Agent")
        verbose_name_plural = _("AI Agents")
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class AgentConversation(models.Model):
    """Extended conversation model specific to agents."""
    
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, 
                                      related_name='agent_conversation')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, 
                            related_name='conversations')
    
    # Agent-specific settings
    personality_override = models.TextField(blank=True)
    custom_instructions = models.TextField(blank=True)
    context_data = models.JSONField(default=dict)  # Additional context
    
    # Performance metrics
    user_rating = models.IntegerField(null=True, blank=True)  # 1-5 stars
    user_feedback = models.TextField(blank=True)
    response_quality_score = models.FloatField(default=0.0)
    
    class Meta:
        verbose_name = _("Agent Conversation")
        verbose_name_plural = _("Agent Conversations")
    
    def __str__(self):
        return f"{self.agent.name} - {self.conversation.title}"


class AgentTool(models.Model):
    """Tools and functions available to agents."""
    
    TOOL_TYPES = [
        ('function', 'Function Call'),
        ('api', 'API Integration'),
        ('database', 'Database Query'),
        ('file', 'File Operation'),
        ('web', 'Web Scraping'),
        ('image', 'Image Processing'),
        ('video', 'Video Processing'),
        ('audio', 'Audio Processing'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    tool_type = models.CharField(max_length=20, choices=TOOL_TYPES)
    description = models.TextField()
    function_definition = models.JSONField()  # OpenAI function definition format
    implementation_code = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    requires_authentication = models.BooleanField(default=False)
    rate_limited = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Agent Tool")
        verbose_name_plural = _("Agent Tools")
    
    def __str__(self):
        return self.name


class AgentToolUsage(models.Model):
    """Track tool usage by agents."""
    
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    tool = models.ForeignKey(AgentTool, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    input_parameters = models.JSONField(default=dict)
    output_result = models.JSONField(default=dict)
    execution_time_ms = models.IntegerField()
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Agent Tool Usage")
        verbose_name_plural = _("Agent Tool Usage")
        ordering = ['-created_at']


class AgentPersonality(models.Model):
    """Personality traits and behaviors for agents."""
    
    agent = models.OneToOneField(Agent, on_delete=models.CASCADE, 
                               related_name='personality')
    
    # Personality traits (0-100 scale)
    friendliness = models.IntegerField(default=50)
    professionalism = models.IntegerField(default=70)
    creativity = models.IntegerField(default=50)
    humor = models.IntegerField(default=30)
    empathy = models.IntegerField(default=50)
    assertiveness = models.IntegerField(default=50)
    patience = models.IntegerField(default=70)
    curiosity = models.IntegerField(default=60)
    
    # Communication style
    formality_level = models.CharField(
        max_length=20,
        choices=[
            ('casual', 'Casual'),
            ('professional', 'Professional'),
            ('formal', 'Formal'),
        ],
        default='professional'
    )
    
    # Response patterns
    average_response_length = models.CharField(
        max_length=20,
        choices=[
            ('brief', 'Brief'),
            ('moderate', 'Moderate'),
            ('detailed', 'Detailed'),
            ('comprehensive', 'Comprehensive'),
        ],
        default='moderate'
    )
    
    # Behavioral preferences
    asks_clarifying_questions = models.BooleanField(default=True)
    provides_examples = models.BooleanField(default=True)
    uses_analogies = models.BooleanField(default=False)
    includes_sources = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _("Agent Personality")
        verbose_name_plural = _("Agent Personalities")
    
    def __str__(self):
        return f"{self.agent.name} Personality"


class AgentKnowledgeBase(models.Model):
    """Knowledge base entries for agents."""
    
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, 
                            related_name='knowledge_base')
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.JSONField(default=list)
    priority = models.IntegerField(default=0)  # Higher = more important
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Agent Knowledge Base")
        verbose_name_plural = _("Agent Knowledge Base")
        ordering = ['-priority', '-updated_at']
    
    def __str__(self):
        return f"{self.agent.name} - {self.title}"


class AgentAnalytics(models.Model):
    """Analytics and performance metrics for agents."""
    
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, 
                            related_name='analytics')
    date = models.DateField(auto_now_add=True)
    
    # Usage metrics
    total_conversations = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)
    
    # Performance metrics
    average_response_time = models.FloatField(default=0.0)
    average_user_rating = models.FloatField(default=0.0)
    completion_rate = models.FloatField(default=0.0)  # % of conversations completed
    
    # Cost metrics
    total_tokens_used = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    
    class Meta:
        verbose_name = _("Agent Analytics")
        verbose_name_plural = _("Agent Analytics")
        unique_together = ['agent', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.agent.name} - {self.date}"
