"""Debug view for diagnosing AI configuration issues"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import traceback
import os

from .models import AIProvider, AIConfiguration
from .services import GeminiService

@login_required
def debug_ai_info(request):
    """Debug view to get information about AI providers and configurations"""
    try:
        # Check providers
        providers = list(AIProvider.objects.all().values('id', 'name', 'display_name', 'is_active'))
        
        # Check user configurations
        user_configs = list(AIConfiguration.objects.filter(
            user=request.user
        ).values('id', 'provider_id', 'model_name', 'is_active', 'is_default'))
        
        # Check environment
        env_api_key = os.getenv('GEMINI_API_KEY')
        env_api_key_exists = bool(env_api_key)
        if env_api_key and len(env_api_key) > 5:
            env_api_key = env_api_key[:5] + '...'
        
        # Test GeminiService
        gemini_service = GeminiService(user=request.user)
        
        # Get debug info
        gemini_debug = {
            'is_configured': gemini_service.is_configured,
            'api_key_exists': bool(gemini_service.api_key),
            'model_name': gemini_service.model_name,
            'config_source': gemini_service.config_source,
            'api_key_fragment': gemini_service.api_key[:5] + '...' if gemini_service.api_key and len(gemini_service.api_key) > 5 else None
        }
        
        return JsonResponse({
            'success': True,
            'providers': providers,
            'user_configs': user_configs,
            'env_api_key_exists': env_api_key_exists,
            'env_api_key': env_api_key,
            'gemini_debug': gemini_debug
        })
    except Exception as e:
        error_traceback = traceback.format_exc()
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': error_traceback
        })
