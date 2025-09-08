"""
Base AI Service classes for OneLastAI Platform.
Provides unified interface for different AI providers.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator
from django.conf import settings
from django.core.cache import cache
import openai
import anthropic
import google.generativeai as genai
import httpx
import logging

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass


class RateLimitError(AIServiceError):
    """Raised when rate limit is exceeded."""
    pass


class ModelNotAvailableError(AIServiceError):
    """Raised when requested model is not available."""
    pass


class BaseAIService(ABC):
    """Abstract base class for AI services."""
    
    def __init__(self, provider: str, model: str, **config):
        self.provider = provider
        self.model = model
        self.config = config
        self.setup_client()
    
    @abstractmethod
    def setup_client(self):
        """Setup the API client for the specific provider."""
        pass
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text response from the AI model."""
        pass
    
    @abstractmethod
    async def generate_chat(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate chat response from the AI model."""
        pass
    
    def get_cache_key(self, content: str) -> str:
        """Generate cache key for responses."""
        import hashlib
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"ai_response:{self.provider}:{self.model}:{content_hash}"
    
    def cache_response(self, key: str, response: Dict[str, Any], timeout: int = 3600):
        """Cache AI response."""
        cache.set(key, response, timeout)
    
    def get_cached_response(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached AI response."""
        return cache.get(key)


class OpenAIService(BaseAIService):
    """OpenAI API service implementation."""
    
    def setup_client(self):
        """Setup OpenAI client."""
        self.client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )
    
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using OpenAI."""
        try:
            response = await self.client.completions.create(
                model=self.model,
                prompt=prompt,
                max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 1000)),
                temperature=kwargs.get('temperature', self.config.get('temperature', 0.7)),
                top_p=kwargs.get('top_p', self.config.get('top_p', 1.0)),
                frequency_penalty=kwargs.get('frequency_penalty', 
                                           self.config.get('frequency_penalty', 0.0)),
                presence_penalty=kwargs.get('presence_penalty', 
                                          self.config.get('presence_penalty', 0.0)),
            )
            
            return {
                'text': response.choices[0].text,
                'tokens_used': response.usage.total_tokens,
                'model': response.model,
                'provider': self.provider,
            }
        except Exception as e:
            logger.error(f"OpenAI text generation error: {e}")
            raise AIServiceError(f"OpenAI API error: {str(e)}")
    
    async def generate_chat(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate chat response using OpenAI."""
        try:
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 1000)),
                temperature=kwargs.get('temperature', self.config.get('temperature', 0.7)),
                top_p=kwargs.get('top_p', self.config.get('top_p', 1.0)),
                frequency_penalty=kwargs.get('frequency_penalty', 
                                           self.config.get('frequency_penalty', 0.0)),
                presence_penalty=kwargs.get('presence_penalty', 
                                          self.config.get('presence_penalty', 0.0)),
                stream=kwargs.get('stream', False),
            )
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            return {
                'content': response.choices[0].message.content,
                'role': response.choices[0].message.role,
                'tokens_used': response.usage.total_tokens,
                'model': response.model,
                'provider': self.provider,
                'response_time_ms': response_time_ms,
            }
        except Exception as e:
            logger.error(f"OpenAI chat generation error: {e}")
            raise AIServiceError(f"OpenAI API error: {str(e)}")
    
    async def generate_chat_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming chat response."""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 1000)),
                temperature=kwargs.get('temperature', self.config.get('temperature', 0.7)),
                stream=True,
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise AIServiceError(f"OpenAI streaming error: {str(e)}")


class AnthropicService(BaseAIService):
    """Anthropic Claude API service implementation."""
    
    def setup_client(self):
        """Setup Anthropic client."""
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )
    
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using Anthropic Claude."""
        try:
            response = await self.client.completions.create(
                model=self.model,
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
                max_tokens_to_sample=kwargs.get('max_tokens', 
                                              self.config.get('max_tokens', 1000)),
                temperature=kwargs.get('temperature', self.config.get('temperature', 0.7)),
                top_p=kwargs.get('top_p', self.config.get('top_p', 1.0)),
            )
            
            return {
                'text': response.completion,
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0,
                'model': response.model,
                'provider': self.provider,
            }
        except Exception as e:
            logger.error(f"Anthropic text generation error: {e}")
            raise AIServiceError(f"Anthropic API error: {str(e)}")
    
    async def generate_chat(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate chat response using Anthropic Claude."""
        try:
            start_time = time.time()
            
            response = await self.client.messages.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 1000)),
                temperature=kwargs.get('temperature', self.config.get('temperature', 0.7)),
                top_p=kwargs.get('top_p', self.config.get('top_p', 1.0)),
            )
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            return {
                'content': response.content[0].text,
                'role': 'assistant',
                'tokens_used': response.usage.total_tokens,
                'model': response.model,
                'provider': self.provider,
                'response_time_ms': response_time_ms,
            }
        except Exception as e:
            logger.error(f"Anthropic chat generation error: {e}")
            raise AIServiceError(f"Anthropic API error: {str(e)}")


class GoogleAIService(BaseAIService):
    """Google AI (Gemini) service implementation."""
    
    def setup_client(self):
        """Setup Google AI client."""
        genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
        self.client = genai.GenerativeModel(self.model)
    
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using Google AI."""
        try:
            response = await self.client.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get('max_tokens', 
                                               self.config.get('max_tokens', 1000)),
                    temperature=kwargs.get('temperature', 
                                         self.config.get('temperature', 0.7)),
                    top_p=kwargs.get('top_p', self.config.get('top_p', 1.0)),
                )
            )
            
            return {
                'text': response.text,
                'tokens_used': response.usage_metadata.total_token_count if response.usage_metadata else 0,
                'model': self.model,
                'provider': self.provider,
            }
        except Exception as e:
            logger.error(f"Google AI text generation error: {e}")
            raise AIServiceError(f"Google AI API error: {str(e)}")
    
    async def generate_chat(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate chat response using Google AI."""
        try:
            start_time = time.time()
            
            # Convert messages to Google AI format
            chat_history = []
            current_message = None
            
            for message in messages[:-1]:
                if message['role'] == 'user':
                    chat_history.append({
                        'role': 'user',
                        'parts': [message['content']]
                    })
                elif message['role'] == 'assistant':
                    chat_history.append({
                        'role': 'model',
                        'parts': [message['content']]
                    })
            
            # Get the latest message
            if messages:
                current_message = messages[-1]['content']
            
            chat = self.client.start_chat(history=chat_history)
            response = await chat.send_message_async(current_message)
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            return {
                'content': response.text,
                'role': 'assistant',
                'tokens_used': response.usage_metadata.total_token_count if response.usage_metadata else 0,
                'model': self.model,
                'provider': self.provider,
                'response_time_ms': response_time_ms,
            }
        except Exception as e:
            logger.error(f"Google AI chat generation error: {e}")
            raise AIServiceError(f"Google AI API error: {str(e)}")


class AIServiceFactory:
    """Factory class to create appropriate AI service instances."""
    
    _services = {
        'openai': OpenAIService,
        'anthropic': AnthropicService,
        'google': GoogleAIService,
    }
    
    @classmethod
    def create_service(cls, provider: str, model: str, **config) -> BaseAIService:
        """Create an AI service instance."""
        if provider not in cls._services:
            raise ModelNotAvailableError(f"Provider '{provider}' is not supported")
        
        service_class = cls._services[provider]
        return service_class(provider, model, **config)
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available providers."""
        return list(cls._services.keys())


class AIServiceManager:
    """Manager class for AI services with caching and rate limiting."""
    
    def __init__(self):
        self.services = {}
    
    def get_service(self, provider: str, model: str, **config) -> BaseAIService:
        """Get or create AI service instance."""
        service_key = f"{provider}:{model}"
        
        if service_key not in self.services:
            self.services[service_key] = AIServiceFactory.create_service(
                provider, model, **config
            )
        
        return self.services[service_key]
    
    async def generate_response(self, provider: str, model: str, messages: List[Dict], 
                              **kwargs) -> Dict[str, Any]:
        """Generate AI response with caching and error handling."""
        service = self.get_service(provider, model, **kwargs)
        
        # Check cache if enabled
        if kwargs.get('use_cache', True):
            cache_key = service.get_cache_key(str(messages))
            cached_response = service.get_cached_response(cache_key)
            if cached_response:
                logger.info(f"Cache hit for {provider}:{model}")
                return cached_response
        
        try:
            # Generate response
            if len(messages) == 1 and messages[0]['role'] == 'user':
                response = await service.generate_text(messages[0]['content'], **kwargs)
            else:
                response = await service.generate_chat(messages, **kwargs)
            
            # Cache response if enabled
            if kwargs.get('use_cache', True):
                cache_key = service.get_cache_key(str(messages))
                service.cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            logger.error(f"AI service error: {e}")
            raise


# Global AI service manager instance
ai_service_manager = AIServiceManager()
