import time
import logging
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import APIKey, GeminiConversation, GeminiMessage, APIUsageLog, AIProvider, AIConfiguration
from .serializers import (
    UserSerializer, APIKeySerializer, GeminiConversationSerializer,
    GeminiMessageSerializer, APIUsageLogSerializer, ProductSerializer, CategorySerializer,
    TaskSerializer, MeetingSerializer, GeminiChatRequestSerializer,
    GeminiChatResponseSerializer, GeminiAnalysisRequestSerializer,
    GeminiAnalysisResponseSerializer
)
from .services import GeminiService, DataAnalysisService
from .authentication import APIKeyAuthentication
from .permissions import HasAPIAccess

# Temporarily disabled - will be replaced with new modular HR apps
# from Hr.models.employee.employee_models import Employee
# from Hr.models.core.department_models import Department
# EmployeeSerializer and DepartmentSerializer temporarily removed
from inventory.models import TblProducts, TblCategories
from tasks.models import Task
from meetings.models import Meeting

# Import core services
from core.data_integration import data_integration_service
from core.permissions import UnifiedPermissionService
from core.reporting import reporting_service

User = get_user_model()
logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API responses"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class APIUsageLogMixin:
    """Mixin to log API usage"""

    def log_api_usage(self, request, response, start_time):
        """Log API usage for monitoring"""
        try:
            end_time = time.time()
            response_time = end_time - start_time

            # Get user and API key from request
            user = request.user if request.user.is_authenticated else None
            api_key = getattr(request, 'api_key', None)

            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            # Create log entry
            APIUsageLog.objects.create(
                user=user,
                api_key=api_key,
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
                response_time=response_time,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception as e:
            logger.error(f"Error logging API usage: {str(e)}")

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to add usage logging"""
        start_time = time.time()
        response = super().dispatch(request, *args, **kwargs)
        self.log_api_usage(request, response, start_time)
        return response


# API Key Management Views
class APIKeyViewSet(APIUsageLogMixin, viewsets.ModelViewSet):
    """ViewSet for managing API keys"""
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return API keys for the current user"""
        return APIKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create API key for the current user"""
        import secrets
        api_key = secrets.token_urlsafe(32)
        serializer.save(user=self.request.user, key=api_key)


# User Management Views
class UserViewSet(APIUsageLogMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for user information"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return users based on permissions"""
        if self.request.user.is_staff:
            return User.objects.all()
        else:
            return User.objects.filter(id=self.request.user.id)


# HR Views - temporarily disabled
# class EmployeeViewSet(APIUsageLogMixin, viewsets.ReadOnlyModelViewSet):
#     """ViewSet for employee data"""
#     # Temporarily disabled - will be replaced with new modular HR apps

# class DepartmentViewSet(APIUsageLogMixin, viewsets.ReadOnlyModelViewSet):
#     """ViewSet for department data"""
#     # Temporarily disabled - will be replaced with new modular HR apps


# Inventory Views
class ProductViewSet(APIUsageLogMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for product data"""
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """Return products with optional filtering"""
        queryset = TblProducts.objects.all()

        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(cat_name__icontains=category)

        # Filter low stock items
        low_stock = self.request.query_params.get('low_stock', None)
        if low_stock and low_stock.lower() == 'true':
            from django.db import models as django_models
            queryset = queryset.filter(qte_in_stock__lte=django_models.F('minimum_threshold'))

        # Search by name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(product_name__icontains=search)

        return queryset.select_related('cat')


class CategoryViewSet(APIUsageLogMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for category data"""
    queryset = TblCategories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserRateThrottle]


# Task Management Views
class TaskViewSet(APIUsageLogMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for task data"""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """Return tasks with optional filtering"""
        queryset = Task.objects.all()

        # Filter by assigned user
        assigned_to = self.request.query_params.get('assigned_to', None)
        if assigned_to:
            queryset = queryset.filter(assigned_to__username=assigned_to)

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by priority
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset.select_related('assigned_to', 'created_by')


# Meeting Management Views
class MeetingViewSet(APIUsageLogMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for meeting data"""
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """Return meetings with optional filtering"""
        queryset = Meeting.objects.all()

        # Filter by organizer
        organizer = self.request.query_params.get('organizer', None)
        if organizer:
            queryset = queryset.filter(organizer__username=organizer)

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related('organizer')


# Gemini AI Views
class GeminiConversationViewSet(APIUsageLogMixin, viewsets.ModelViewSet):
    """ViewSet for Gemini conversations"""
    serializer_class = GeminiConversationSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """Return conversations for the current user"""
        return GeminiConversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create conversation for the current user"""
        serializer.save(user=self.request.user)


@swagger_auto_schema(
    method='post',
    request_body=GeminiChatRequestSerializer,
    responses={200: GeminiChatResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, HasAPIAccess])
def gemini_chat(request):
    """Chat with Gemini AI"""
    serializer = GeminiChatRequestSerializer(data=request.data)
    if serializer.is_valid():
        gemini_service = GeminiService()

        if not gemini_service.is_available():
            return Response({
                'error': 'Gemini AI service is not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        result = gemini_service.chat_with_context(
            user=request.user,
            message=serializer.validated_data['message'],
            conversation_id=serializer.validated_data.get('conversation_id'),
            temperature=serializer.validated_data.get('temperature', 0.7),
            max_tokens=serializer.validated_data.get('max_tokens', 1000)
        )

        if result['success']:
            response_data = {
                'response': result['response'],
                'conversation_id': result['conversation_id'],
                'tokens_used': result['tokens_used'],
                'model': serializer.validated_data.get('model', 'gemini-1.5-flash')
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result.get('error', 'Unknown error occurred')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=GeminiAnalysisRequestSerializer,
    responses={200: GeminiAnalysisResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, HasAPIAccess])
def gemini_analyze_data(request):
    """Analyze system data with Gemini AI"""
    serializer = GeminiAnalysisRequestSerializer(data=request.data)
    if serializer.is_valid():
        analysis_service = DataAnalysisService()

        data_type = serializer.validated_data['data_type']
        analysis_type = serializer.validated_data['analysis_type']
        filters = serializer.validated_data.get('filters', {})

        # Route to appropriate analysis method
        if data_type == 'employees':
            result = analysis_service.analyze_employees(filters)
        elif data_type == 'inventory':
            result = analysis_service.analyze_inventory(filters)
        else:
            return Response({
                'error': f'Analysis for {data_type} is not yet implemented'
            }, status=status.HTTP_501_NOT_IMPLEMENTED)

        if result.get('success'):
            return Response({
                'analysis': result['analysis'],
                'data_summary': result['data_summary'],
                'insights': result['insights'],
                'recommendations': result['recommendations']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result.get('error', 'Analysis failed')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_status(request):
    """Get API status and health check"""
    gemini_service = GeminiService()

    return Response({
        'status': 'healthy',
        'version': '1.0.0',
        'services': {
            'gemini_ai': gemini_service.is_available(),
            'database': True,  # If we reach here, DB is working
        },
        'user': {
            'username': request.user.username,
            'is_authenticated': request.user.is_authenticated,
            'permissions': {
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser,
            }
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasAPIAccess])
def api_usage_stats(request):
    """Get API usage statistics for the current user"""
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
        'requests_by_day': list(
            user_logs.extra({'day': 'date(timestamp)'})
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        ),
        'error_rate': user_logs.filter(status_code__gte=400).count() / max(user_logs.count(), 1) * 100
    }

    return Response(stats, status=status.HTTP_200_OK)


# Unified Data Integration API Endpoints
# نقاط النهاية الموحدة لتكامل البيانات

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_unified_data(request, employee_id):
    """
    Get unified employee data with all related information
    جلب البيانات الموحدة للموظف مع جميع المعلومات المرتبطة
    """
    permission_service = UnifiedPermissionService(request.user)

    if not permission_service.can_access_employee_data(employee_id):
        return Response(
            {'error': 'ليس لديك صلاحية للوصول لبيانات هذا الموظف'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get employee with all relations
    employee = data_integration_service.get_employee_with_relations(employee_id)
    if not employee:
        return Response(
            {'error': 'الموظف غير موجود'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get unified tasks
    unified_tasks = data_integration_service.get_employee_tasks_unified(employee_id)

    # Serialize employee data
    employee_data = EmployeeSerializer(employee).data

    # Add unified data
    employee_data['unified_tasks'] = unified_tasks
    employee_data['task_statistics'] = {
        'total_tasks': len(unified_tasks),
        'active_tasks': len([t for t in unified_tasks if t['status'] in ['pending', 'in_progress']]),
        'completed_tasks': len([t for t in unified_tasks if t['status'] == 'completed']),
        'overdue_tasks': len([t for t in unified_tasks if t['due_date'] and t['due_date'] < timezone.now().date() and t['status'] in ['pending', 'in_progress']])
    }

    return Response(employee_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_analytics(request, department_id):
    """
    Get comprehensive department analytics
    جلب التحليلات الشاملة للقسم
    """
    permission_service = UnifiedPermissionService(request.user)

    if not permission_service.has_module_permission('hr', 'view'):
        return Response(
            {'error': 'ليس لديك صلاحية لعرض تحليلات الأقسام'},
            status=status.HTTP_403_FORBIDDEN
        )

    analytics = data_integration_service.get_department_analytics(department_id)
    if not analytics:
        return Response(
            {'error': 'القسم غير موجود'},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(analytics, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_cross_module_data(request):
    """
    Validate data consistency across modules
    التحقق من صحة البيانات عبر الوحدات
    """
    data = request.data.get('data', {})
    module = request.data.get('module', '')

    if not module:
        return Response(
            {'error': 'يجب تحديد الوحدة'},
            status=status.HTTP_400_BAD_REQUEST
        )

    permission_service = UnifiedPermissionService(request.user)
    if not permission_service.has_module_permission(module, 'view'):
        return Response(
            {'error': f'ليس لديك صلاحية للوصول لوحدة {module}'},
            status=status.HTTP_403_FORBIDDEN
        )

    errors = data_integration_service.validate_cross_module_data(data, module)

    return Response({
        'valid': len(errors) == 0,
        'errors': errors
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions_summary(request):
    """
    Get comprehensive summary of user permissions
    جلب ملخص شامل لصلاحيات المستخدم
    """
    permission_service = UnifiedPermissionService(request.user)
    permissions = permission_service.get_user_permissions_summary()

    return Response(permissions, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def accessible_departments(request):
    """
    Get list of departments user can access
    جلب قائمة الأقسام التي يمكن للمستخدم الوصول إليها
    """
    permission_service = UnifiedPermissionService(request.user)
    departments = permission_service.get_user_accessible_departments()

    department_data = DepartmentSerializer(departments, many=True).data

    return Response(department_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_integration_cache(request):
    """
    Clear data integration cache (admin only)
    مسح ذاكرة التخزين المؤقت لتكامل البيانات (للمديرين فقط)
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'هذه العملية متاحة للمديرين فقط'},
            status=status.HTTP_403_FORBIDDEN
        )

    data_integration_service.clear_all_cache()

    return Response(
        {'message': 'تم مسح ذاكرة التخزين المؤقت بنجاح'},
        status=status.HTTP_200_OK
    )


# Enhanced Reporting API Endpoints
# نقاط نهاية API للتقارير المحسنة

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """
    Get comprehensive dashboard data
    جلب بيانات لوحة التحكم الشاملة
    """
    try:
        date_range = request.GET.get('date_range', '30d')

        # Validate date range
        valid_ranges = ['7d', '30d', '90d', '1y']
        if date_range not in valid_ranges:
            return Response(
                {'error': f'نطاق التاريخ غير صحيح. القيم المسموحة: {", ".join(valid_ranges)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        dashboard_data = reporting_service.get_dashboard_data(
            user=request.user,
            date_range=date_range
        )

        return Response(dashboard_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return Response(
            {'error': 'حدث خطأ أثناء جلب بيانات لوحة التحكم'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_custom_report(request):
    """
    Generate a custom report based on configuration
    إنشاء تقرير مخصص بناءً على التكوين
    """
    try:
        report_config = request.data

        # Validate required fields
        if not isinstance(report_config, dict):
            return Response(
                {'error': 'تكوين التقرير يجب أن يكون كائن JSON'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set default values
        report_config.setdefault('type', 'summary')
        report_config.setdefault('date_range', '30d')
        report_config.setdefault('modules', ['all'])
        report_config.setdefault('format', 'json')

        report_data = reporting_service.generate_custom_report(
            report_config=report_config,
            user=request.user
        )

        return Response(report_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error generating custom report: {e}")
        return Response(
            {'error': 'حدث خطأ أثناء إنشاء التقرير المخصص'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_report(request):
    """
    Export report in specified format
    تصدير التقرير بالتنسيق المحدد
    """
    try:
        report_data = request.data.get('report_data')
        format_type = request.data.get('format', 'json')

        if not report_data:
            return Response(
                {'error': 'بيانات التقرير مطلوبة'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if format_type not in reporting_service.supported_formats:
            return Response(
                {'error': f'تنسيق غير مدعوم. التنسيقات المدعومة: {", ".join(reporting_service.supported_formats)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return reporting_service.export_report(report_data, format_type)

    except Exception as e:
        logger.error(f"Error exporting report: {e}")
        return Response(
            {'error': 'حدث خطأ أثناء تصدير التقرير'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_templates(request):
    """
    Get available report templates
    جلب قوالب التقارير المتاحة
    """
    templates = [
        {
            'id': 'employee_summary',
            'name': 'ملخص الموظفين',
            'description': 'تقرير شامل عن الموظفين والأقسام',
            'modules': ['employee'],
            'chart_types': ['pie', 'bar'],
            'default_date_range': '30d'
        },
        {
            'id': 'task_performance',
            'name': 'أداء المهام',
            'description': 'تحليل أداء المهام ومعدلات الإنجاز',
            'modules': ['task'],
            'chart_types': ['line', 'bar'],
            'default_date_range': '30d'
        },
        {
            'id': 'meeting_analytics',
            'name': 'تحليل الاجتماعات',
            'description': 'إحصائيات الاجتماعات والحضور',
            'modules': ['meeting'],
            'chart_types': ['pie', 'bar'],
            'default_date_range': '30d'
        },
        {
            'id': 'inventory_status',
            'name': 'حالة المخزون',
            'description': 'تقرير شامل عن حالة المخزون والمنتجات',
            'modules': ['inventory'],
            'chart_types': ['doughnut', 'bar'],
            'default_date_range': '7d'
        },
        {
            'id': 'purchase_analysis',
            'name': 'تحليل المشتريات',
            'description': 'تحليل طلبات الشراء والموردين',
            'modules': ['purchase'],
            'chart_types': ['bar', 'line'],
            'default_date_range': '90d'
        },
        {
            'id': 'comprehensive_overview',
            'name': 'نظرة عامة شاملة',
            'description': 'تقرير شامل لجميع وحدات النظام',
            'modules': ['all'],
            'chart_types': ['pie', 'bar', 'line'],
            'default_date_range': '30d'
        }
    ]

    return Response({
        'templates': templates,
        'supported_formats': reporting_service.supported_formats,
        'supported_chart_types': reporting_service.chart_types,
        'available_date_ranges': ['7d', '30d', '90d', '1y']
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_reporting_cache(request):
    """
    Clear reporting cache (admin only)
    مسح ذاكرة التخزين المؤقت للتقارير (للمديرين فقط)
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'هذه العملية متاحة للمديرين فقط'},
            status=status.HTTP_403_FORBIDDEN
        )

    reporting_service.clear_cache()

    return Response(
        {'message': 'تم مسح ذاكرة التخزين المؤقت للتقارير بنجاح'},
        status=status.HTTP_200_OK
    )
