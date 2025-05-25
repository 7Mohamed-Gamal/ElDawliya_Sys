from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from . import views
from . import web_views
from . import debug_view

# API Documentation Schema
schema_view = get_schema_view(
    openapi.Info(
        title="ElDawliya System API",
        default_version='v1',
        description="""
        API للنظام الإداري للدولية

        يوفر هذا API الوصول إلى:
        - بيانات الموارد البشرية
        - بيانات المخزون
        - إدارة المهام والاجتماعات
        - خدمات الذكاء الاصطناعي باستخدام Gemini

        ## المصادقة
        يدعم API نوعين من المصادقة:
        1. Session Authentication (للواجهات الداخلية)
        2. API Key Authentication (للتطبيقات الخارجية)

        ### استخدام API Key
        أضف Header التالي لطلباتك:
        ```
        Authorization: ApiKey YOUR_API_KEY_HERE
        ```

        ## معدل الطلبات
        - المستخدمين المسجلين: 60 طلب/دقيقة
        - المستخدمين غير المسجلين: 10 طلبات/دقيقة
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@eldawliya.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'api-keys', views.APIKeyViewSet, basename='apikey')
router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'meetings', views.MeetingViewSet, basename='meeting')
router.register(r'conversations', views.GeminiConversationViewSet, basename='conversation')

app_name = 'api'

urlpatterns = [
    # Web Interface URLs
    path('dashboard/', web_views.APIDashboardView.as_view(), name='dashboard'),
    path('create-key/', web_views.create_api_key, name='create_key'),
    path('documentation/', web_views.api_documentation, name='documentation'),
    path('ai/chat-interface/', web_views.ai_chat_interface, name='ai_chat'),
    path('ai/chat-api/', web_views.ai_chat_api, name='ai_chat_api'),
    path('ai/analysis-interface/', web_views.data_analysis_interface, name='data_analysis'),
    path('ai/analysis-api/', web_views.data_analysis_api, name='data_analysis_api'),
    path('usage-stats-page/', web_views.api_usage_stats, name='usage_stats'),

    # AI Configuration URLs
    path('ai/settings/', web_views.ai_settings_view, name='ai_settings'),
    path('ai/add-config/', web_views.add_ai_config, name='add_ai_config'),
    path('ai/edit-config/<int:config_id>/', web_views.edit_ai_config, name='edit_ai_config'),
    path('ai/delete-config/<int:config_id>/', web_views.delete_ai_config, name='delete_ai_config'),
    path('ai/test-config/', web_views.test_ai_config, name='test_ai_config'),

    # API Documentation
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API Status and Health
    path('status/', views.api_status, name='api_status'),
    path('usage-stats/', views.api_usage_stats, name='api_usage_stats_api'),
    
    # Debug endpoints
    path('debug/ai-info/', debug_view.debug_ai_info, name='debug_ai_info'),

    # Gemini AI Endpoints
    path('ai/chat/', views.gemini_chat, name='gemini_chat'),
    path('ai/analyze/', views.gemini_analyze_data, name='gemini_analyze'),

    # ViewSet URLs
    path('', include(router.urls)),
]
