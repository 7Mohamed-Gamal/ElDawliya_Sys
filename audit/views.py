import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog


class AuditLogMixin(UserPassesTestMixin):
    """Mixin to restrict audit log views to staff and admins."""
    
    def test_func(self):
        """Test if user has permission to view audit logs."""
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or 
            self.request.user.is_superuser or
            self.request.user.has_perm('audit.view_auditlog')
        )


class AuditLogListView(AuditLogMixin, ListView):
    """View for listing audit logs."""
    model = AuditLog
    template_name = 'audit/auditlog_list.html'
    context_object_name = 'audit_logs'
    paginate_by = 50
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter queryset based on search parameters."""
        queryset = super().get_queryset()
        
        # Get filter parameters from GET request
        user_id = self.request.GET.get('user')
        action = self.request.GET.get('action')
        app_name = self.request.GET.get('app_name')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        search = self.request.GET.get('search')
        
        # Apply filters if they exist
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        if action:
            queryset = queryset.filter(action=action)
            
        if app_name:
            queryset = queryset.filter(app_name=app_name)
            
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
            
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
            
        if search:
            queryset = queryset.filter(
                Q(object_repr__icontains=search) | 
                Q(action_details__icontains=search) |
                Q(user__username__icontains=search) |
                Q(ip_address__icontains=search)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add extra context for filtering."""
        context = super().get_context_data(**kwargs)
        
        # Add action choices for filtering
        context['action_choices'] = AuditLog.ACTION_CHOICES
        
        # Add app names for filtering
        context['app_names'] = AuditLog.objects.values_list('app_name', flat=True).distinct()
        
        # Add current filters to context
        context['current_filters'] = {
            'user': self.request.GET.get('user'),
            'action': self.request.GET.get('action'),
            'app_name': self.request.GET.get('app_name'),
            'date_from': self.request.GET.get('date_from'),
            'date_to': self.request.GET.get('date_to'),
            'search': self.request.GET.get('search'),
        }
        
        return context


class AuditLogDetailView(AuditLogMixin, DetailView):
    """View for displaying audit log details."""
    model = AuditLog
    template_name = 'audit/auditlog_detail.html'
    context_object_name = 'audit_log'
    
    def get_context_data(self, **kwargs):
        """Add formatted change data to context."""
        context = super().get_context_data(**kwargs)
        
        # Format change data for display if it exists
        audit_log = context['audit_log']
        if audit_log.change_data:
            try:
                # If already a string, try to parse as JSON
                if isinstance(audit_log.change_data, str):
                    context['change_data_formatted'] = json.loads(audit_log.change_data)
                else:
                    # If a dictionary or other object, use as is
                    context['change_data_formatted'] = audit_log.change_data
            except (json.JSONDecodeError, TypeError):
                # If can't parse, use as-is
                context['change_data_formatted'] = audit_log.change_data
        
        return context


def export_audit_logs(request):
    """Export filtered audit logs to JSON."""
    # Check permissions
    if not (request.user.is_staff or request.user.is_superuser or request.user.has_perm('audit.view_auditlog')):
        return HttpResponse(status=403)
    
    # Get filter parameters from GET request
    user_id = request.GET.get('user')
    action = request.GET.get('action')
    app_name = request.GET.get('app_name')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    # Start with all logs
    queryset = AuditLog.objects.all().order_by('-timestamp')
    
    # Apply filters if they exist
    if user_id:
        queryset = queryset.filter(user_id=user_id)
        
    if action:
        queryset = queryset.filter(action=action)
        
    if app_name:
        queryset = queryset.filter(app_name=app_name)
        
    if date_from:
        queryset = queryset.filter(timestamp__gte=date_from)
        
    if date_to:
        queryset = queryset.filter(timestamp__lte=date_to)
        
    if search:
        queryset = queryset.filter(
            Q(object_repr__icontains=search) | 
            Q(action_details__icontains=search) |
            Q(user__username__icontains=search) |
            Q(ip_address__icontains=search)
        )
    
    # Limit to reasonable number to avoid memory issues
    queryset = queryset[:1000]
    
    # Convert to list of dictionaries
    logs_data = []
    for log in queryset:
        log_dict = {
            'id': log.id,
            'user': log.user.username if log.user else _('مستخدم غير معروف'),
            'action': log.get_action_display(),
            'timestamp': log.timestamp.isoformat(),
            'ip_address': log.ip_address,
            'app_name': log.app_name,
            'object_repr': log.object_repr,
            'action_details': log.action_details,
        }
        logs_data.append(log_dict)
    
    return JsonResponse({'audit_logs': logs_data})
