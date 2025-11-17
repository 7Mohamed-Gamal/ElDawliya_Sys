"""
Debug views for API testing and development.
These views should only be accessible in DEBUG mode.
"""
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@permission_classes([AllowAny])
def api_health_check(request):
    """
    Simple health check endpoint to verify API is running.
    """
    return Response({
        'status': 'ok',
        'message': 'API is running',
        'debug_mode': settings.DEBUG,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_debug_info(request):
    """
    Debug information endpoint.
    Only accessible when DEBUG=True.
    """
    if not settings.DEBUG:
        return Response({
            'error': 'Debug mode is disabled'
        }, status=status.HTTP_403_FORBIDDEN)
    
    return Response({
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': getattr(request.user, 'email', None),
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
        },
        'request': {
            'method': request.method,
            'path': request.path,
            'content_type': request.content_type,
        },
        'settings': {
            'DEBUG': settings.DEBUG,
            'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
            'DATABASES': {
                name: {
                    'ENGINE': db.get('ENGINE'),
                    'NAME': db.get('NAME'),
                    'HOST': db.get('HOST'),
                }
                for name, db in settings.DATABASES.items()
            },
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_version(request):
    """
    Get API version information.
    """
    return Response({
        'version': '1.0.0',
        'api_name': 'ElDawliya System API',
        'description': 'API للنظام الإداري للدولية',
    })


@require_http_methods(["GET"])
def debug_database_connection(request):
    """
    Test database connection.
    Only accessible when DEBUG=True.
    """
    if not settings.DEBUG:
        return JsonResponse({
            'error': 'Debug mode is disabled'
        }, status=403)
    
    from django.db import connections
    from django.db.utils import OperationalError
    
    results = {}
    for name in connections:
        try:
            connection = connections[name]
            connection.ensure_connection()
            results[name] = {
                'status': 'connected',
                'vendor': connection.vendor,
                'settings': {
                    'ENGINE': connection.settings_dict.get('ENGINE'),
                    'NAME': connection.settings_dict.get('NAME'),
                    'HOST': connection.settings_dict.get('HOST'),
                    'PORT': connection.settings_dict.get('PORT'),
                }
            }
        except OperationalError as e:
            results[name] = {
                'status': 'error',
                'error': str(e)
            }
    
    return JsonResponse({
        'databases': results
    })


@require_http_methods(["GET"])
def debug_installed_apps(request):
    """
    List all installed Django apps.
    Only accessible when DEBUG=True.
    """
    if not settings.DEBUG:
        return JsonResponse({
            'error': 'Debug mode is disabled'
        }, status=403)

    from django.apps import apps

    installed_apps = []
    for app_config in apps.get_app_configs():
        installed_apps.append({
            'name': app_config.name,
            'label': app_config.label,
            'verbose_name': app_config.verbose_name,
            'path': app_config.path,
        })

    return JsonResponse({
        'installed_apps': installed_apps,
        'count': len(installed_apps)
    })


@require_http_methods(["GET"])
def debug_ai_info(request):
    """
    Get AI configuration and status information.
    Only accessible when DEBUG=True.
    """
    if not settings.DEBUG:
        return JsonResponse({
            'error': 'Debug mode is disabled'
        }, status=403)

    try:
        from api.models import AIConfiguration, AIProvider

        # Get all AI providers
        providers = AIProvider.objects.all()
        providers_data = []
        for provider in providers:
            providers_data.append({
                'id': provider.id,
                'name': provider.name,
                'provider_type': provider.provider_type,
                'is_active': provider.is_active,
                'created_at': provider.created_at.isoformat() if hasattr(provider, 'created_at') else None,
            })

        # Get AI configurations
        configurations = AIConfiguration.objects.all()
        configs_data = []
        for config in configurations:
            configs_data.append({
                'id': config.id,
                'provider': config.provider.name if hasattr(config, 'provider') else None,
                'model_name': config.model_name if hasattr(config, 'model_name') else None,
                'is_active': config.is_active if hasattr(config, 'is_active') else None,
            })

        return JsonResponse({
            'providers': providers_data,
            'configurations': configs_data,
            'gemini_api_key_configured': bool(getattr(settings, 'GEMINI_API_KEY', None)),
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'gemini_api_key_configured': bool(getattr(settings, 'GEMINI_API_KEY', None)),
        })

