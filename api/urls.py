"""
Main API URL Configuration with versioning support
تكوين URLs الرئيسي لـ API مع دعم الإصدارات
"""

from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from . import web_views
from . import debug_view

# API Documentation Schema
schema_view = get_schema_view(
    openapi.Info(
        title="ElDawliya System API",
        default_version='v1',
        description="""
        # API للنظام الإداري للدولية

        يوفر هذا API الوصول الشامل إلى جميع وحدات النظام:

        ## الوحدات المتاحة
        - **الموارد البشرية (HR)**: إدارة الموظفين، الحضور، الرواتب، الإجازات، التقييمات
        - **المخزون (Inventory)**: إدارة المنتجات، المخازن، حركات المخزون
        - **المشتريات (Procurement)**: أوامر الشراء، الموردين، العقود
        - **المشاريع (Projects)**: إدارة المشاريع، المهام، الاجتماعات
        - **التقارير (Reports)**: تقارير شاملة وتحليلات متقدمة
        - **الذكاء الاصطناعي (AI)**: خدمات التحليل والمحادثة الذكية

        ## المصادقة والأمان
        يدعم API طرق مصادقة متعددة:

        ### 1. JWT Authentication (الموصى به)
        ```
        Authorization: Bearer YOUR_JWT_TOKEN
        ```

        ### 2. API Key Authentication
        ```
        Authorization: ApiKey YOUR_API_KEY
        ```

        ### 3. Session Authentication (للواجهات الداخلية)
        يستخدم cookies الجلسة العادية

        ## التحكم في معدل الطلبات
        - **المستخدمين العاديين**: 1000 طلب/ساعة
        - **مفاتيح API الأساسية**: 1000 طلب/ساعة
        - **مفاتيح API المميزة**: 5000 طلب/ساعة
        - **مفاتيح API المؤسسية**: 10000 طلب/ساعة

        ## الإصدارات
        - **v1**: الإصدار الحالي المستقر
        - **v2**: قيد التطوير (متاح للاختبار)

        ## أمثلة الاستخدام

        ### الحصول على قائمة الموظفين
        ```
        GET /api/v1/hr/employees/
        Authorization: Bearer YOUR_JWT_TOKEN
        ```

        ### إنشاء موظف جديد
        ```
        POST /api/v1/hr/employees/
        Content-Type: application/json
        Authorization: Bearer YOUR_JWT_TOKEN

        {
            "first_name": "أحمد",
            "last_name": "محمد",
            "email": "ahmed@company.com",
            "department_id": 1,
            "job_position_id": 1,
            "hire_date": "2024-01-01"
        }
        ```

        ### البحث في المنتجات
        ```
        GET /api/v1/inventory/products/?search=laptop&category=electronics
        Authorization: ApiKey YOUR_API_KEY
        ```

        ## معالجة الأخطاء
        جميع الأخطاء تُرجع بتنسيق JSON موحد:
        ```json
        {
            "error": true,
            "message": "رسالة الخطأ باللغة العربية",
            "details": {},
            "status_code": 400,
            "timestamp": "2024-01-01T12:00:00Z"
        }
        ```

        ## الدعم والمساعدة
        - البريد الإلكتروني: api-support@eldawliya.com
        - التوثيق الكامل: [رابط التوثيق]
        - أمثلة الكود: [رابط المستودع]
        """,
        terms_of_service="https://eldawliya.com/api/terms/",
        contact=openapi.Contact(
            name="فريق دعم API",
            email="api-support@eldawliya.com",
            url="https://eldawliya.com/support/"
        ),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=[
        path('api/v1/', include('api.v1.urls')),
    ],
)

app_name = 'api'

urlpatterns = [
    # API Versions
    path('v1/', include('api.v1.urls', namespace='v1')),
    # path('v2/', include('api.v2.urls', namespace='v2')),  # Future version

    # Web Interface URLs (for API management)
    path('dashboard/', web_views.APIDashboardView.as_view(), name='dashboard'),
    path('create-key/', web_views.create_api_key, name='create_key'),
    path('documentation/', web_views.api_documentation, name='documentation'),

    # AI Web Interface
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

    # Debug endpoints (development only)
    path('debug/ai-info/', debug_view.debug_ai_info, name='debug_ai_info'),

    # Legacy endpoints (redirect to v1)
    path('status/', include('api.v1.urls')),  # Redirect legacy status to v1
]
