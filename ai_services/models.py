"""
AI Services Models for OneLastAI Platform.
Handles different AI providers, models, and configurations.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import uuid
import json

User = get_user_model()


class AIProvider(models.Model):
    """AI service providers like OpenAI, Anthropic, etc."""
    
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google AI'),
        ('runwayml', 'RunwayML'),
        ('huggingface', 'Hugging Face'),
        ('cohere', 'Cohere'),
        ('stability', 'Stability AI'),
    ]
    
    name = models.CharField(max_length=50, choices=PROVIDER_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    api_endpoint = models.URLField()
    is_active = models.BooleanField(default=True)
    rate_limit_per_minute = models.IntegerField(default=60)
    rate_limit_per_hour = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("AI Provider")
        verbose_name_plural = _("AI Providers")
    
    def __str__(self):
        return self.display_name


class AIModel(models.Model):
    """Available AI models from different providers."""
    
    MODEL_TYPE_CHOICES = [
        ('text', 'Text Generation'),
        ('chat', 'Chat Completion'),
        ('image', 'Image Generation'),
        ('video', 'Video Generation'),
        ('audio', 'Audio Generation'),
        ('voice', 'Voice Synthesis'),
        ('embedding', 'Text Embedding'),
        ('moderation', 'Content Moderation'),
    ]
    
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, 
                               related_name='models')
    name = models.CharField(max_length=100)
    model_id = models.CharField(max_length=100)  # API model identifier
    model_type = models.CharField(max_length=20, choices=MODEL_TYPE_CHOICES)
    description = models.TextField(blank=True)
    max_tokens = models.IntegerField(default=4000)
    cost_per_1k_tokens = models.DecimalField(max_digits=10, decimal_places=6, 
                                           default=0.000000)
    context_window = models.IntegerField(default=4000)
    supports_streaming = models.BooleanField(default=True)
    supports_function_calling = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("AI Model")
        verbose_name_plural = _("AI Models")
        unique_together = ['provider', 'model_id']
    
    def __str__(self):
        return f"{self.provider.display_name} - {self.name}"


class AIServiceConfig(models.Model):
    """Configuration for AI services."""
    
    name = models.CharField(max_length=100, unique=True)
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    temperature = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)]
    )
    max_tokens = models.IntegerField(default=1000)
    top_p = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    frequency_penalty = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-2.0), MaxValueValidator(2.0)]
    )
    presence_penalty = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-2.0), MaxValueValidator(2.0)]
    )
    system_prompt = models.TextField(blank=True)
    custom_parameters = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("AI Service Config")
        verbose_name_plural = _("AI Service Configs")
    
    def __str__(self):
        return self.name


class Conversation(models.Model):
    """User conversations with AI agents."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='conversations')
    agent_name = models.CharField(max_length=100)  # Agent identifier
    title = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='active')
    ai_config = models.ForeignKey(AIServiceConfig, on_delete=models.SET_NULL, 
                                null=True, blank=True)
    total_tokens_used = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, 
                                   default=0.000000)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.agent_name} - {self.title[:50]}"


class Message(models.Model):
    """Individual messages in conversations."""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
        ('function', 'Function'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, 
                                   related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=8, decimal_places=6, default=0.000000)
    response_time_ms = models.IntegerField(null=True, blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class AIServiceUsage(models.Model):
    """Track usage statistics for AI services."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='ai_usage')
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total_requests = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, 
                                   default=0.000000)
    average_response_time_ms = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _("AI Service Usage")
        verbose_name_plural = _("AI Service Usage")
        unique_together = ['user', 'provider', 'model', 'date']
    
    def __str__(self):
        return f"{self.user.email} - {self.provider.name} - {self.date}"


class AIServiceHealth(models.Model):
    """Monitor AI service health and availability."""
    
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('unhealthy', 'Unhealthy'),
        ('maintenance', 'Maintenance'),
    ]
    
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, 
                               related_name='health_checks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response_time_ms = models.IntegerField()
    error_message = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("AI Service Health")
        verbose_name_plural = _("AI Service Health Checks")
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"{self.provider.name} - {self.status} - {self.checked_at}"


class AgentTemplate(models.Model):
    """Templates for different AI agents with their personalities and configs."""
    
    AGENT_CATEGORIES = [
        ('conversation', 'Conversational'),
        ('technical', 'Technical'),
        ('creative', 'Creative'),
        ('business', 'Business'),
        ('specialized', 'Specialized'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=AGENT_CATEGORIES)
    avatar_url = models.URLField(blank=True)
    personality_prompt = models.TextField()
    default_config = models.ForeignKey(AIServiceConfig, on_delete=models.SET_NULL, 
                                     null=True, blank=True)
    capabilities = models.JSONField(default=list, blank=True)
    supported_features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Agent Template")
        verbose_name_plural = _("Agent Templates")
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.display_name
