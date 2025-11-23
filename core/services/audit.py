"""
خدمة التدقيق والمراجعة
Audit Service for tracking system activities
"""
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from core.models.audit import AuditLog, SystemLog, LoginAttempt
from .base import BaseService


class AuditService(BaseService):
    """
    خدمة التدقيق والمراجعة
    Service for managing audit logs and system monitoring
    """
    
    def log_user_action(self, action, resource, content_object=None, 
                       old_values=None, new_values=None, details=None, 
                       result='success', message=None):
        """
        تسجيل عمل المستخدم
        Log user action with full context
        """
        return AuditLog.log_action(
            user=self.user,
            action=action,
            resource=resource,
            content_object=content_object,
            old_values=old_values,
            new_values=new_values,
            details=details,
            result=result,
            message=message,
            request=self.request
        )
    
    def log_system_event(self, level, category, module, message, 
                        function=None, details=None, exception=None):
        """
        تسجيل حدث النظام
        Log system event or error
        """
        return SystemLog.log(
            level=level,
            category=category,
            module=module,
            message=message,
            function=function,
            details=details,
            exception=exception,
            user=self.user
        )
    
    def log_login_attempt(self, username, success, failure_reason=None):
        """
        تسجيل محاولة تسجيل دخول
        Log login attempt for security monitoring
        """
        ip_address = self._get_client_ip()
        user_agent = self._get_user_agent()
        session_key = self._get_session_key()
        
        return LoginAttempt.log_attempt(
            username=username,
            ip_address=ip_address,
            success=success,
            user_agent=user_agent,
            failure_reason=failure_reason,
            session_key=session_key
        )
    
    def get_user_activity_log(self, user=None, start_date=None, end_date=None, 
                             action=None, page=1, page_size=20):
        """
        الحصول على سجل نشاط المستخدم
        Get user activity log with filtering
        """
        queryset = AuditLog.objects.all()
        
        if user:
            queryset = queryset.filter(user=user)
        elif self.user and not self.user.is_superuser:
            queryset = queryset.filter(user=self.user)
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        if action:
            queryset = queryset.filter(action=action)
        
        queryset = queryset.select_related('user', 'content_type')
        
        return self.paginate_queryset(queryset, page, page_size)
    
    def get_system_logs(self, level=None, category=None, module=None, 
                       resolved=None, start_date=None, end_date=None,
                       page=1, page_size=20):
        """
        الحصول على سجلات النظام
        Get system logs with filtering
        """
        self.check_permission('core.view_systemlog')
        
        queryset = SystemLog.objects.all()
        
        if level:
            queryset = queryset.filter(level=level)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if module:
            queryset = queryset.filter(module=module)
        
        if resolved is not None:
            queryset = queryset.filter(resolved=resolved)
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        queryset = queryset.select_related('user', 'resolved_by')
        
        return self.paginate_queryset(queryset, page, page_size)
    
    def get_login_attempts(self, username=None, ip_address=None, success=None,
                          start_date=None, end_date=None, page=1, page_size=20):
        """
        الحصول على محاولات تسجيل الدخول
        Get login attempts with filtering
        """
        self.check_permission('core.view_loginattempt')
        
        queryset = LoginAttempt.objects.all()
        
        if username:
            queryset = queryset.filter(username__icontains=username)
        
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        
        if success is not None:
            queryset = queryset.filter(success=success)
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return self.paginate_queryset(queryset, page, page_size)
    
    def get_security_summary(self, days=30):
        """
        الحصول على ملخص الأمان
        Get security summary for dashboard
        """
        self.check_permission('core.view_security_summary')
        
        from django.db.models import Count, Q
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Login attempts summary
        login_stats = LoginAttempt.objects.filter(
            created_at__gte=start_date
        ).aggregate(
            total_attempts=Count('id'),
            successful_logins=Count('id', filter=Q(success=True)),
            failed_logins=Count('id', filter=Q(success=False))
        )
        
        # System errors summary
        error_stats = SystemLog.objects.filter(
            created_at__gte=start_date,
            level__in=['error', 'critical']
        ).aggregate(
            total_errors=Count('id'),
            unresolved_errors=Count('id', filter=Q(resolved=False))
        )
        
        # User activity summary
        activity_stats = AuditLog.objects.filter(
            created_at__gte=start_date
        ).aggregate(
            total_actions=Count('id'),
            failed_actions=Count('id', filter=Q(result='failure'))
        )
        
        return {
            'period_days': days,
            'login_stats': login_stats,
            'error_stats': error_stats,
            'activity_stats': activity_stats,
        }
    
    def resolve_system_log(self, log_id, resolution_note=None):
        """
        حل مشكلة في سجل النظام
        Mark system log as resolved
        """
        self.check_permission('core.change_systemlog')
        
        try:
            log_entry = SystemLog.objects.get(id=log_id)
            log_entry.mark_resolved(resolved_by=self.user)
            
            self.log_user_action(
                action='update',
                resource=f'system_log/{log_id}',
                content_object=log_entry,
                message=f'تم حل المشكلة: {resolution_note}' if resolution_note else 'تم حل المشكلة'
            )
            
            return self.format_response(
                data={'log_id': log_id},
                message='تم حل المشكلة بنجاح'
            )
            
        except SystemLog.DoesNotExist:
            return self.format_response(
                success=False,
                message='سجل النظام غير موجود'
            )
    
    def cleanup_old_logs(self, days_to_keep=90):
        """
        تنظيف السجلات القديمة
        Clean up old log entries
        """
        self.check_permission('core.delete_auditlog')
        
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # Clean audit logs
        audit_deleted = AuditLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        # Clean system logs (keep errors longer)
        system_deleted = SystemLog.objects.filter(
            created_at__lt=cutoff_date,
            level__in=['debug', 'info'],
            resolved=True
        ).delete()
        
        # Clean login attempts
        login_deleted = LoginAttempt.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        self.log_user_action(
            action='delete',
            resource='audit_cleanup',
            details={
                'days_to_keep': days_to_keep,
                'audit_logs_deleted': audit_deleted[0],
                'system_logs_deleted': system_deleted[0],
                'login_attempts_deleted': login_deleted[0],
            },
            message=f'تم تنظيف السجلات الأقدم من {days_to_keep} يوم'
        )
        
        return self.format_response(
            data={
                'audit_logs_deleted': audit_deleted[0],
                'system_logs_deleted': system_deleted[0],
                'login_attempts_deleted': login_deleted[0],
            },
            message='تم تنظيف السجلات القديمة بنجاح'
        )
    
    def _get_client_ip(self):
        """الحصول على عنوان IP للعميل"""
        if not self.request:
            return None
            
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_user_agent(self):
        """الحصول على معلومات المتصفح"""
        if not self.request:
            return None
        return self.request.META.get('HTTP_USER_AGENT', '')
    
    def _get_session_key(self):
        """الحصول على مفتاح الجلسة"""
        if not self.request or not hasattr(self.request, 'session'):
            return None
        return self.request.session.session_key