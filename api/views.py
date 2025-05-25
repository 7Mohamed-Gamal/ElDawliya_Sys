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
    GeminiMessageSerializer, APIUsageLogSerializer, EmployeeSerializer,
    DepartmentSerializer, ProductSerializer, CategorySerializer,
    TaskSerializer, MeetingSerializer, GeminiChatRequestSerializer,
    GeminiChatResponseSerializer, GeminiAnalysisRequestSerializer,
    GeminiAnalysisResponseSerializer
)
from .services import GeminiService, DataAnalysisService
from .authentication import APIKeyAuthentication
from .permissions import HasAPIAccess

# Import models from other apps
from Hr.models.employee_model import Employee
from Hr.models.department_models import Department
from inventory.models import TblProducts, TblCategories
from tasks.models import Task
from meetings.models import Meeting

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


# HR Views
class EmployeeViewSet(APIUsageLogMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for employee data"""
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """Return employees with optional filtering"""
        queryset = Employee.objects.all()

        # Filter by department
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department__dept_name__icontains=department)

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(emp_status=status_filter)

        # Search by name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(emp_name__icontains=search) |
                Q(emp_email__icontains=search)
            )

        return queryset.select_related('department')


class DepartmentViewSet(APIUsageLogMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for department data"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [UserRateThrottle]


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
