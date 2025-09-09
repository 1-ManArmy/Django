"""
OneLastAI Platform - Agent Serializers
DRF serializers for AI agents, conversations, and messages
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Agent, AgentConversation
from ai_services.models import Message

User = get_user_model()


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for Agent model"""
    
    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'description', 'category', 'ai_provider',
            'system_prompt', 'personality_traits', 'capabilities',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Add computed fields to representation"""
        data = super().to_representation(instance)
        data['display_name'] = instance.get_display_name()
        data['category_display'] = instance.get_category_display()
        data['provider_display'] = instance.get_ai_provider_display()
        return data


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'content', 'sender', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_sender(self, value):
        """Validate sender field"""
        if value not in ['user', 'agent', 'system']:
            raise serializers.ValidationError("Sender must be 'user', 'agent', or 'system'")
        return value


class AgentConversationSerializer(serializers.ModelSerializer):
    """Serializer for AgentConversation model"""
    agent = AgentSerializer(read_only=True)
    agent_id = serializers.IntegerField(write_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentConversation
        fields = [
            'id', 'user', 'agent', 'agent_id', 'title', 'messages',
            'message_count', 'last_message', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        """Get total message count for conversation"""
        return obj.messages.count()
    
    def get_last_message(self, obj):
        """Get the last message in conversation"""
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def validate_agent_id(self, value):
        """Validate that agent exists and is active"""
        try:
            agent = Agent.objects.get(id=value, is_active=True)
            return value
        except Agent.DoesNotExist:
            raise serializers.ValidationError("Agent not found or inactive")


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating conversations"""
    agent_id = serializers.IntegerField()
    
    class Meta:
        model = AgentConversation
        fields = ['agent_id', 'title']
    
    def validate_agent_id(self, value):
        """Validate agent exists and is active"""
        try:
            Agent.objects.get(id=value, is_active=True)
            return value
        except Agent.DoesNotExist:
            raise serializers.ValidationError("Agent not found or inactive")
    
    def create(self, validated_data):
        """Create conversation with validated agent"""
        agent_id = validated_data.pop('agent_id')
        agent = Agent.objects.get(id=agent_id)
        return AgentConversation.objects.create(
            agent=agent,
            **validated_data
        )


class ConversationStatsSerializer(serializers.Serializer):
    """Serializer for conversation statistics"""
    totalConversations = serializers.IntegerField()
    thisWeek = serializers.IntegerField()
    agentsUsed = serializers.IntegerField()
    totalMessages = serializers.IntegerField()
    recentActivity = serializers.IntegerField()


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""
    conversation_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Message
        fields = ['conversation_id', 'content', 'sender', 'metadata']
    
    def validate_sender(self, value):
        """Validate sender field"""
        if value not in ['user', 'agent', 'system']:
            raise serializers.ValidationError("Sender must be 'user', 'agent', or 'system'")
        return value
    
    def validate_content(self, value):
        """Validate message content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty")
        
        # Limit message length
        if len(value) > 10000:
            raise serializers.ValidationError("Message content too long (max 10000 characters)")
        
        return value.strip()


class AgentSelectionSerializer(serializers.ModelSerializer):
    """Lightweight serializer for agent selection lists"""
    
    class Meta:
        model = Agent
        fields = ['id', 'name', 'description', 'category', 'is_active']
    
    def to_representation(self, instance):
        """Add computed fields for UI"""
        data = super().to_representation(instance)
        data['display_name'] = instance.get_display_name()
        data['category_display'] = instance.get_category_display()
        
        # Add UI-specific fields
        category_colors = {
            'conversational': '#3b82f6',  # Blue
            'technical': '#10b981',       # Green
            'creative': '#8b5cf6',        # Purple
            'business': '#f59e0b',        # Amber
        }
        
        category_icons = {
            'conversational': 'fas fa-comments',
            'technical': 'fas fa-code',
            'creative': 'fas fa-palette',
            'business': 'fas fa-briefcase',
        }
        
        data['color'] = category_colors.get(instance.category, '#6b7280')
        data['icon'] = category_icons.get(instance.category, 'fas fa-robot')
        
        return data
