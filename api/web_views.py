"""
Web views for API interface
واجهات الويب لـ API
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import secrets

from .models import APIKey, GeminiConversation, GeminiMessage, APIUsageLog, AIProvider, AIConfiguration
from .services import GeminiService, DataAnalysisService


class APIDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard for API management"""
    template_name = 'api/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get user's API keys
        api_keys = APIKey.objects.filter(user=self.request.user, is_active=True)

        # Get user's conversations
        conversations = GeminiConversation.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-updated_at')[:5]

        # Get usage stats
        usage_logs = APIUsageLog.objects.filter(user=self.request.user)
        total_requests = usage_logs.count()

        # Check Gemini availability with the user's API key
        gemini_service = GeminiService(user=self.request.user)
        gemini_available = gemini_service.is_available()

        context.update({
            'api_keys': api_keys,
            'conversations': conversations,
            'total_requests': total_requests,
            'gemini_available': gemini_available,
        })

        return context


@login_required
def create_api_key(request):
    """Create a new API key for the user"""
    if request.method == 'POST':
        name = request.POST.get('name', 'Default API Key')

        # Generate API key
        api_key = secrets.token_urlsafe(32)

        # Create API key object
        APIKey.objects.create(
            user=request.user,
            name=name,
            key=api_key
        )

        messages.success(request, f'تم إنشاء مفتاح API بنجاح: {api_key}')
        return redirect('api:dashboard')

    return render(request, 'api/create_key.html')


@login_required
def api_documentation(request):
    """API documentation page"""
    return render(request, 'api/documentation.html')


@login_required
def ai_chat_interface(request):
    """AI chat interface"""
    conversations = GeminiConversation.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-updated_at')

    # Check Gemini availability with the user's API key
    gemini_service = GeminiService(user=request.user)
    
    # Debug info
    is_configured = gemini_service.is_configured
    api_key_exists = bool(gemini_service.api_key)
    config_source = gemini_service.config_source
    
    context = {
        'conversations': conversations,
        'gemini_available': gemini_service.is_available(),
        'debug_info': {
            'is_configured': is_configured,
            'api_key_exists': api_key_exists,
            'config_source': config_source,
        }
    }

    return render(request, 'api/ai_chat.html', context)


@csrf_exempt
@login_required
def ai_chat_api(request):
    """API endpoint for AI chat"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            conversation_id = data.get('conversation_id')

            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)

            # Use Gemini service with user's configurations
            gemini_service = GeminiService(user=request.user)
            
            # Debug info
            is_configured = gemini_service.is_configured
            api_key_exists = bool(gemini_service.api_key)
            model_name = gemini_service.model_name

            if not gemini_service.is_available():
                return JsonResponse({
                    'error': f'Gemini AI is not available. Debug: configured={is_configured}, api_exists={api_key_exists}, model={model_name}'
                }, status=503)

            try:
                result = gemini_service.chat_with_context(
                    user=request.user,
                    message=message,
                    conversation_id=conversation_id
                )
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                return JsonResponse({
                    'error': f'Error processing chat: {str(e)}',
                    'traceback': error_traceback
                }, status=500)

            if result['success']:
                return JsonResponse({
                    'response': result['response'],
                    'conversation_id': result['conversation_id'],
                    'tokens_used': result['tokens_used']
                })
            else:
                return JsonResponse({'error': result.get('error', 'Unknown error')}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def data_analysis_interface(request):
    """Data analysis interface"""
    return render(request, 'api/data_analysis.html')


@csrf_exempt
@login_required
def data_analysis_api(request):
    """API endpoint for data analysis"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            data_type = data.get('data_type', '')
            analysis_type = data.get('analysis_type', 'summary')
            filters = data.get('filters', {})

            if not data_type:
                return JsonResponse({'error': 'Data type is required'}, status=400)

            # Use analysis service with user's configurations
            analysis_service = DataAnalysisService(user=request.user)

            if data_type == 'employees':
                result = analysis_service.analyze_employees(filters)
            elif data_type == 'inventory':
                result = analysis_service.analyze_inventory(filters)
            else:
                return JsonResponse({'error': f'Analysis for {data_type} is not supported'}, status=400)

            if result.get('success'):
                return JsonResponse({
                    'analysis': result['analysis'],
                    'data_summary': result['data_summary'],
                    'insights': result['insights'],
                    'recommendations': result['recommendations']
                })
            else:
                return JsonResponse({'error': result.get('error', 'Analysis failed')}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def api_usage_stats(request):
    """API usage statistics page"""
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta

    # Get usage stats for the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)

    user_logs = APIUsageLog.objects.filter(
        user=request.user,
        timestamp__gte=thirty_days_ago
    )

    stats = {
        'total_requests': user_logs.count(),
        'avg_response_time': user_logs.aggregate(Avg('response_time'))['response_time__avg'] or 0,
        'requests_by_endpoint': list(
            user_logs.values('endpoint')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        ),
        'error_rate': user_logs.filter(status_code__gte=400).count() / max(user_logs.count(), 1) * 100
    }

    context = {
        'stats': stats,
        'user_logs': user_logs.order_by('-timestamp')[:20]
    }

    return render(request, 'api/usage_stats.html', context)


@login_required
def ai_settings_view(request):
    """صفحة إعدادات الذكاء الاصطناعي"""
    user_configs = AIConfiguration.objects.filter(user=request.user)
    providers = AIProvider.objects.filter(is_active=True)

    context = {
        'user_configs': user_configs,
        'providers': providers,
    }

    return render(request, 'api/ai_settings.html', context)


@login_required
def add_ai_config(request):
    """إضافة إعداد ذكاء اصطناعي جديد"""
    if request.method == 'POST':
        provider_id = request.POST.get('provider')
        api_key = request.POST.get('api_key')
        model_name = request.POST.get('model_name', 'gemini-1.5-flash')
        max_tokens = int(request.POST.get('max_tokens', 1000))
        temperature = float(request.POST.get('temperature', 0.7))
        is_default = request.POST.get('is_default') == 'on'

        try:
            provider = AIProvider.objects.get(id=provider_id)

            # تحقق من وجود إعداد مسبق لنفس المقدم
            existing_config = AIConfiguration.objects.filter(
                user=request.user,
                provider=provider
            ).first()

            if existing_config:
                # تحديث الإعداد الموجود
                existing_config.api_key = api_key
                existing_config.model_name = model_name
                existing_config.max_tokens = max_tokens
                existing_config.temperature = temperature
                existing_config.is_default = is_default
                existing_config.is_active = True
                existing_config.save()
                messages.success(request, f'تم تحديث إعدادات {provider.display_name} بنجاح!')
            else:
                # إنشاء إعداد جديد
                AIConfiguration.objects.create(
                    user=request.user,
                    provider=provider,
                    api_key=api_key,
                    model_name=model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    is_default=is_default
                )
                messages.success(request, f'تم إضافة إعدادات {provider.display_name} بنجاح!')

            return redirect('api:ai_settings')

        except AIProvider.DoesNotExist:
            messages.error(request, 'مقدم الخدمة غير موجود!')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    providers = AIProvider.objects.filter(is_active=True)
    context = {'providers': providers}

    return render(request, 'api/add_ai_config.html', context)


@login_required
def edit_ai_config(request, config_id):
    """تعديل إعداد ذكاء اصطناعي"""
    config = get_object_or_404(AIConfiguration, id=config_id, user=request.user)

    if request.method == 'POST':
        config.api_key = request.POST.get('api_key', config.api_key)
        config.model_name = request.POST.get('model_name', config.model_name)
        config.max_tokens = int(request.POST.get('max_tokens', config.max_tokens))
        config.temperature = float(request.POST.get('temperature', config.temperature))
        config.is_default = request.POST.get('is_default') == 'on'
        config.is_active = request.POST.get('is_active') == 'on'

        try:
            config.save()
            messages.success(request, f'تم تحديث إعدادات {config.provider.display_name} بنجاح!')
            return redirect('api:ai_settings')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    context = {'config': config}
    return render(request, 'api/edit_ai_config.html', context)


@login_required
def delete_ai_config(request, config_id):
    """حذف إعداد ذكاء اصطناعي"""
    config = get_object_or_404(AIConfiguration, id=config_id, user=request.user)

    if request.method == 'POST':
        provider_name = config.provider.display_name
        config.delete()
        messages.success(request, f'تم حذف إعدادات {provider_name} بنجاح!')

    return redirect('api:ai_settings')


@csrf_exempt
@login_required
def test_ai_config(request):
    """اختبار إعداد الذكاء الاصطناعي"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            config_id = data.get('config_id')
            test_message = data.get('message', 'مرحبا، هذا اختبار للاتصال')

            config = AIConfiguration.objects.get(id=config_id, user=request.user)

            # اختبار الاتصال حسب نوع المقدم
            if config.provider.name == 'gemini':
                # اختبار Gemini
                import google.generativeai as genai
                genai.configure(api_key=config.api_key)
                model = genai.GenerativeModel(config.model_name)

                response = model.generate_content(
                    test_message,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=config.max_tokens,
                        temperature=config.temperature,
                    )
                )

                return JsonResponse({
                    'success': True,
                    'response': response.text,
                    'provider': config.provider.display_name,
                    'model': config.model_name
                })

            elif config.provider.name == 'openai':
                # اختبار OpenAI (يتطلب تثبيت openai)
                try:
                    import openai
                    openai.api_key = config.api_key

                    response = openai.ChatCompletion.create(
                        model=config.model_name,
                        messages=[{"role": "user", "content": test_message}],
                        max_tokens=config.max_tokens,
                        temperature=config.temperature
                    )

                    return JsonResponse({
                        'success': True,
                        'response': response.choices[0].message.content,
                        'provider': config.provider.display_name,
                        'model': config.model_name
                    })
                except ImportError:
                    return JsonResponse({
                        'success': False,
                        'error': 'مكتبة OpenAI غير مثبتة. قم بتثبيتها باستخدام: pip install openai'
                    })

            else:
                return JsonResponse({
                    'success': False,
                    'error': f'اختبار {config.provider.display_name} غير مدعوم حالياً'
                })

        except AIConfiguration.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'الإعداد غير موجود'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'طريقة غير مدعومة'})
