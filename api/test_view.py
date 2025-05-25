from django.shortcuts import render
from .models import AIProvider, AIConfiguration

def test_ai_settings_view(request):
    """صفحة إعدادات الذكاء الاصطناعي للاختبار فقط"""
    user_configs = AIConfiguration.objects.filter(is_active=True)
    providers = AIProvider.objects.filter(is_active=True)

    context = {
        'user_configs': user_configs,
        'providers': providers,
    }

    return render(request, 'api/ai_settings.html', context)
