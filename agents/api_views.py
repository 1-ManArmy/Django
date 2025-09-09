"""
OneLastAI Platform - Agents API Views
REST API endpoints for conversation and message management
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import Agent, AgentConversation
from ai_services.models import Message
from .serializers import (
    AgentConversationSerializer,
    MessageSerializer,
    ConversationStatsSerializer
)


class ConversationViewSet(viewsets.ModelViewSet):
    """API viewset for managing conversations"""
    serializer_class = AgentConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter conversations by current user"""
        return AgentConversation.objects.filter(
            user=self.request.user
        ).select_related('agent', 'user').prefetch_related('messages')
    
    def perform_create(self, serializer):
        """Set user when creating conversation"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get conversation statistics for the user"""
        user = request.user
        
        # Base queryset
        conversations = AgentConversation.objects.filter(user=user)
        
        # Total conversations
        total_conversations = conversations.count()
        
        # This week's conversations
        week_ago = timezone.now() - timedelta(days=7)
        this_week = conversations.filter(created_at__gte=week_ago).count()
        
        # Unique agents used
        agents_used = conversations.values('agent').distinct().count()
        
        # Total messages
        total_messages = Message.objects.filter(
            conversation__user=user
        ).count()
        
        # Recent activity (last 7 days)
        recent_activity = conversations.filter(
            updated_at__gte=week_ago
        ).count()
        
        stats_data = {
            'totalConversations': total_conversations,
            'thisWeek': this_week,
            'agentsUsed': agents_used,
            'totalMessages': total_messages,
            'recentActivity': recent_activity,
        }
        
        serializer = ConversationStatsSerializer(data=stats_data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a conversation"""
        conversation = self.get_object()
        conversation.is_archived = True
        conversation.save()
        
        return Response({'status': 'archived'})
    
    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """Unarchive a conversation"""
        conversation = self.get_object()
        conversation.is_archived = False
        conversation.save()
        
        return Response({'status': 'unarchived'})
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export conversation as JSON or text"""
        conversation = self.get_object()
        export_format = request.query_params.get('format', 'json')
        
        messages = conversation.messages.all().order_by('created_at')
        
        if export_format == 'text':
            # Export as readable text
            content = f"Conversation: {conversation.title}\n"
            content += f"Agent: {conversation.agent.get_display_name()}\n"
            content += f"Started: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"Last Updated: {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += "=" * 50 + "\n\n"
            
            for message in messages:
                sender = "You" if message.sender == 'user' else conversation.agent.get_display_name()
                content += f"{sender} [{message.created_at.strftime('%H:%M')}]:\n"
                content += f"{message.content}\n\n"
            
            return Response({
                'content': content,
                'filename': f"conversation_{conversation.id}.txt"
            })
        
        else:
            # Export as JSON
            serializer = self.get_serializer(conversation)
            return Response({
                'conversation': serializer.data,
                'filename': f"conversation_{conversation.id}.json"
            })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search conversations by content"""
        query = request.query_params.get('q', '')
        agent_id = request.query_params.get('agent_id')
        
        if not query:
            return Response([])
        
        # Search in conversation titles and message content
        conversations = self.get_queryset()
        
        conversations = conversations.filter(
            Q(title__icontains=query) |
            Q(messages__content__icontains=query)
        ).distinct()
        
        if agent_id:
            conversations = conversations.filter(agent_id=agent_id)
        
        serializer = self.get_serializer(conversations, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """API viewset for managing messages"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter messages by user's conversations"""
        return Message.objects.filter(
            conversation__user=self.request.user
        ).select_related('conversation', 'conversation__agent')
    
    def create(self, request, *args, **kwargs):
        """Create a new message in a conversation"""
        conversation_id = request.data.get('conversation_id')
        
        try:
            conversation = AgentConversation.objects.get(
                id=conversation_id,
                user=request.user
            )
        except AgentConversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create the message
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = serializer.save(conversation=conversation)
        
        # Update conversation's updated_at timestamp
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=['updated_at'])
        
        return Response(
            self.get_serializer(message).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate an AI response message"""
        message = self.get_object()
        
        if message.sender != 'agent':
            return Response(
                {'error': 'Can only regenerate agent messages'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implement AI response regeneration
        # This would involve calling the AI service again with the same context
        
        return Response({
            'message': 'Message regeneration not yet implemented',
            'status': 'pending'
        })
    
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add reaction to a message"""
        message = self.get_object()
        reaction = request.data.get('reaction')
        
        if not reaction:
            return Response(
                {'error': 'Reaction is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Store reaction in message metadata
        if not message.metadata:
            message.metadata = {}
        
        if 'reactions' not in message.metadata:
            message.metadata['reactions'] = {}
        
        message.metadata['reactions'][str(request.user.id)] = reaction
        message.save(update_fields=['metadata'])
        
        return Response({'status': 'reaction added'})
    
    @action(detail=False, methods=['get'])
    def conversation_messages(self, request):
        """Get all messages for a specific conversation"""
        conversation_id = request.query_params.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'conversation_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = AgentConversation.objects.get(
                id=conversation_id,
                user=request.user
            )
        except AgentConversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        messages = self.get_queryset().filter(
            conversation=conversation
        ).order_by('created_at')
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)