"""
OneLastAI Platform - Agent Views
Web interface views for agent interactions and conversations
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count

from .models import Agent, AgentConversation
from ai_services.models import Message


def agent_list(request):
    """Display list of available AI agents"""
    agents = Agent.objects.filter(is_active=True).order_by('category', 'name')
    
    # Group agents by category
    agents_by_category = {}
    for agent in agents:
        category = agent.get_category_display()
        if category not in agents_by_category:
            agents_by_category[category] = []
        agents_by_category[category].append(agent)
    
    context = {
        'agents': agents,
        'agents_by_category': agents_by_category,
        'page_title': 'AI Agents',
        'page_description': 'Choose from our collection of specialized AI agents'
    }
    return render(request, 'agents/list.html', context)


def agent_detail(request, agent_id):
    """Display detailed information about a specific agent"""
    agent = get_object_or_404(Agent, id=agent_id, is_active=True)
    
    # Get recent conversations with this agent (if user is authenticated)
    recent_conversations = []
    if request.user.is_authenticated:
        recent_conversations = AgentConversation.objects.filter(
            user=request.user,
            agent=agent
        ).order_by('-updated_at')[:5]
    
    context = {
        'agent': agent,
        'recent_conversations': recent_conversations,
        'page_title': agent.get_display_name(),
        'page_description': agent.description
    }
    return render(request, 'agents/detail.html', context)


def chat_interface(request):
    """Chat interface for selecting and chatting with agents"""
    agents = Agent.objects.filter(is_active=True)
    
    context = {
        'agents': agents,
        'page_title': 'Chat with AI Agents',
        'page_description': 'Select an AI agent and start chatting'
    }
    return render(request, 'agents/chat.html', context)


@login_required
def agent_chat(request, agent_id):
    """Individual agent chat page"""
    agent = get_object_or_404(Agent, id=agent_id, is_active=True)
    
    # Get or create conversation
    conversation_id = request.GET.get('conversation')
    conversation = None
    
    if conversation_id:
        try:
            conversation = AgentConversation.objects.get(
                id=conversation_id,
                user=request.user,
                agent=agent
            )
        except AgentConversation.DoesNotExist:
            pass
    
    # If no valid conversation, redirect to general chat with agent selected
    if not conversation:
        return redirect(f'/agents/chat/?agent={agent_id}')
    
    context = {
        'agent': agent,
        'conversation': conversation,
        'page_title': f'Chat with {agent.get_display_name()}',
        'page_description': f'Conversation with {agent.get_display_name()}'
    }
    return render(request, 'agents/chat.html', context)


@login_required
def conversation_list(request):
    """List all conversations for the current user"""
    conversations = AgentConversation.objects.filter(
        user=request.user
    ).select_related('agent').order_by('-updated_at')
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        conversations = conversations.filter(
            Q(title__icontains=search_query) |
            Q(agent__name__icontains=search_query) |
            Q(messages__content__icontains=search_query)
        ).distinct()
    
    # Filter by agent
    agent_filter = request.GET.get('agent')
    if agent_filter:
        conversations = conversations.filter(agent_id=agent_filter)
    
    # Pagination
    paginator = Paginator(conversations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available agents for filter
    available_agents = Agent.objects.filter(
        id__in=conversations.values_list('agent_id', flat=True).distinct()
    )
    
    context = {
        'conversations': page_obj,
        'search_query': search_query,
        'agent_filter': agent_filter,
        'available_agents': available_agents,
        'page_title': 'My Conversations',
        'page_description': 'Manage your chat conversations'
    }
    return render(request, 'agents/conversations.html', context)


@login_required
def conversation_history(request):
    """Conversation history page with advanced features"""
    context = {
        'page_title': 'Conversation History',
        'page_description': 'Browse and manage your chat conversations with AI agents'
    }
    return render(request, 'agents/history.html', context)


@login_required
def conversation_detail(request, conversation_id):
    """Display detailed view of a conversation"""
    conversation = get_object_or_404(
        AgentConversation,
        id=conversation_id,
        user=request.user
    )
    
    # Get messages with pagination
    messages = conversation.messages.order_by('created_at')
    paginator = Paginator(messages, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'conversation': conversation,
        'messages': page_obj,
        'page_title': conversation.title,
        'page_description': f'Conversation with {conversation.agent.get_display_name()}'
    }
    return render(request, 'agents/conversation_detail.html', context)


@login_required
def voice_chat(request, agent_id):
    """Voice chat interface (premium feature)"""
    agent = get_object_or_404(Agent, id=agent_id, is_active=True)
    
    # Check if user has voice features
    subscription = getattr(request.user, 'subscription', None)
    if not subscription or not subscription.plan.voice_agents_enabled:
        messages.error(request, 'Voice chat requires a premium subscription.')
        return redirect('agents:list')
    
    context = {
        'agent': agent,
        'page_title': f'Voice Chat with {agent.get_display_name()}',
        'page_description': f'Voice conversation with {agent.get_display_name()}'
    }
    return render(request, 'agents/voice_chat.html', context)
