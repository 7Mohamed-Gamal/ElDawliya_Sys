"""
Core API v1 views
عروض API الأساسية للإصدار الأول
"""

import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import APIKey, APIUsageLog
from ..serializers import UserSerializer, APIKeySerializer
from ..permissions import HasAPIAccess, ModulePermission
from ..pagination import StandardResultsSetPagination
from ..throttling import APIKeyRateThrottle
from core.services.base import BaseService

User = get_user_model()
logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user management
    مجموعة عروض إدارة المستخدمين
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [APIKeyRateThrottle]

    def get_queryset(self):
        """Return users based on permissions"""
        if self.request.user.is_staff:
            return User.objects.all().select_related()  # TODO: Add appropriate select_related fields.select_related()
        else:
            return User.objects.filter(id=self.request.user.id).prefetch_related()  # TODO: Add appropriate prefetch_related fields

    @swagger_auto_schema(
        operation_description="Get current user profile",
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user information"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update current user profile",
        request_body=UserSerializer,
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for API key management
    مجموعة عروض إدارة مفاتيح API
    """
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated, HasAPIAccess]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return API keys for the current user"""
        return APIKey.objects.filter(user=self.request.user).prefetch_related()  # TODO: Add appropriate prefetch_related fields

    def perform_create(self, serializer):
        """Create API key for the current user"""
        import secrets
        api_key = secrets.token_urlsafe(32)
        serializer.save(user=self.request.user, key=api_key)

    @swagger_auto_schema(
        operation_description="Regenerate API key",
        responses={200: APIKeySerializer}
    )
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate API key"""
        api_key_obj = self.get_object()

        # Generate new key
        import secrets
        new_key = secrets.token_urlsafe(32)
        api_key_obj.key = new_key
        api_key_obj.save()

        serializer = self.get_serializer(api_key_obj)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get API key usage statistics",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'total_requests': openapi.Schema(type=openapi.TYPE_INTEGER),
                'requests_today': openapi.Schema(type=openapi.TYPE_INTEGER),
                'last_used': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )}
    )
    @action(detail=True, methods=['get'])
    def usage_stats(self, request, pk=None):
        """Get usage statistics for API key"""
        api_key_obj = self.get_object()

        # Get usage statistics
        from django.db.models import Count
        from datetime import datetime, timedelta

        today = datetime.now().date()

        stats = {
            'total_requests': APIUsageLog.objects.filter(api_key=api_key_obj).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count(),
            'requests_today': APIUsageLog.objects.filter(
                api_key=api_key_obj,
                timestamp__date=today
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.count(),
            'last_used': api_key_obj.last_used.isoformat() if api_key_obj.last_used else None,
            'created_at': api_key_obj.created_at.isoformat(),
            'expires_at': api_key_obj.expires_at.isoformat() if api_key_obj.expires_at else None,
        }

        return Response(stats)


class APIStatusView(APIView):
    """
    API status and health information
    معلومات حالة وصحة API
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get API status and health information",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'version': openapi.Schema(type=openapi.TYPE_STRING),
                'timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                'services': openapi.Schema(type=openapi.TYPE_OBJECT),
            }
        )}
    )
    def get(self, request):
        """Get API status"""
        from core.services.integrations import IntegrationService

        integration_service = IntegrationService()

        return Response({
            'status': 'healthy',
            'version': 'v1',
            'timestamp': timezone.now().isoformat(),
            'services': {
                'database': True,  # If we reach here, DB is working
                'cache': self._check_cache(),
                'ai_services': integration_service.check_ai_services(),
            },
            'user': {
                'username': request.user.username,
                'is_authenticated': request.user.is_authenticated,
                'permissions': {
                    'is_staff': request.user.is_staff,
                    'is_superuser': request.user.is_superuser,
                }
            }
        })

    def _check_cache(self):
        """Check if cache is working"""
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 60)
            return cache.get('health_check') == 'ok'
        except Exception:
            return False


class HealthCheckView(APIView):
    """
    Detailed health check for monitoring
    فحص صحة مفصل للمراقبة
    """
    permission_classes = []  # Public endpoint for monitoring

    def get(self, request):
        """Perform health checks"""
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {
                'database': self._check_database(),
                'cache': self._check_cache(),
                'disk_space': self._check_disk_space(),
                'memory': self._check_memory(),
            }
        }

        # Determine overall status
        if not all(health_status['checks'].values()):
            health_status['status'] = 'unhealthy'
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(health_status)

    def _check_database(self):
        """Check database connectivity"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def _check_cache(self):
        """Check cache connectivity"""
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 60)
            return cache.get('health_check') == 'ok'
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False

    def _check_disk_space(self):
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            free_percent = (free / total) * 100
            return free_percent > 10  # At least 10% free space
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return False

    def _check_memory(self):
        """Check available memory"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.percent < 90  # Less than 90% memory usage
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return True  # Assume OK if psutil not available


class UsageStatsView(APIView):
    """
    API usage statistics
    إحصائيات استخدام API
    """
    permission_classes = [IsAuthenticated, HasAPIAccess]

    @swagger_auto_schema(
        operation_description="Get API usage statistics",
        manual_parameters=[
            openapi.Parameter(
                'days',
                openapi.IN_QUERY,
                description="Number of days to include in statistics",
                type=openapi.TYPE_INTEGER,
                default=30
            )
        ]
    )
    def get(self, request):
        """Get API usage statistics for the current user"""
        from django.db.models import Count, Avg
        from datetime import datetime, timedelta

        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)

        user_logs = APIUsageLog.objects.filter(
            user=request.user,
            timestamp__gte=start_date
        ).prefetch_related()  # TODO: Add appropriate prefetch_related fields

        stats = {
            'period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': datetime.now().isoformat(),
            },
            'total_requests': user_logs.count(),
            'avg_response_time': user_logs.aggregate(
                Avg('response_time')
            )['response_time__avg'] or 0,
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
            'requests_by_status': list(
                user_logs.values('status_code')
                .annotate(count=Count('id'))
                .order_by('status_code')
            ),
            'error_rate': (
                user_logs.filter(status_code__gte=400).count() /
                max(user_logs.count(), 1) * 100
            )
        }

        return Response(stats)


class LogoutView(APIView):
    """
    Logout view that blacklists JWT tokens
    عرض تسجيل الخروج الذي يضع رموز JWT في القائمة السوداء
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout and blacklist JWT token",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )}
    )
    def post(self, request):
        """Logout user and blacklist token"""
        try:
            # Get JWT token from request
            token = getattr(request, 'jwt_token', None)

            if token:
                # Blacklist the token
                from django.core.cache import cache
                import hashlib

                token_hash = hashlib.sha256(str(token).encode()).hexdigest()
                blacklist_key = f"jwt_blacklist_{token_hash}"

                # Blacklist until token expiration
                cache.set(blacklist_key, True, 3600 * 24)  # 24 hours

            return Response({
                'message': 'تم تسجيل الخروج بنجاح'
            })

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response({
                'message': 'حدث خطأ أثناء تسجيل الخروج'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
