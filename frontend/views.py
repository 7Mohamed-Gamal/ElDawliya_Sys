"""
Frontend views for ElDawliya System.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view."""
    template_name = 'pages/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('لوحة التحكم'),
            'breadcrumbs': [
                {'title': _('الرئيسية'), 'url': '/'},
                {'title': _('لوحة التحكم'), 'active': True},
            ],
        })
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view."""
    template_name = 'pages/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('الملف الشخصي'),
            'breadcrumbs': [
                {'title': _('الرئيسية'), 'url': '/'},
                {'title': _('الملف الشخصي'), 'active': True},
            ],
        })
        return context


class ProfileEditView(LoginRequiredMixin, TemplateView):
    """Edit user profile view."""
    template_name = 'pages/profile_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('تعديل الملف الشخصي'),
            'breadcrumbs': [
                {'title': _('الرئيسية'), 'url': '/'},
                {'title': _('الملف الشخصي'), 'url': '/profile/'},
                {'title': _('تعديل'), 'active': True},
            ],
        })
        return context


class ReportsView(LoginRequiredMixin, TemplateView):
    """Reports listing view."""
    template_name = 'pages/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('التقارير'),
            'breadcrumbs': [
                {'title': _('الرئيسية'), 'url': '/'},
                {'title': _('التقارير'), 'active': True},
            ],
        })
        return context


class ReportDetailView(LoginRequiredMixin, TemplateView):
    """Individual report view."""
    template_name = 'pages/report_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report_type = kwargs.get('report_type')
        context.update({
            'page_title': _('تقرير %(type)s') % {'type': report_type},
            'report_type': report_type,
            'breadcrumbs': [
                {'title': _('الرئيسية'), 'url': '/'},
                {'title': _('التقارير'), 'url': '/reports/'},
                {'title': report_type, 'active': True},
            ],
        })
        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    """System settings view."""
    template_name = 'pages/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('الإعدادات'),
            'breadcrumbs': [
                {'title': _('الرئيسية'), 'url': '/'},
                {'title': _('الإعدادات'), 'active': True},
            ],
        })
        return context


class HelpView(LoginRequiredMixin, TemplateView):
    """Help and documentation view."""
    template_name = 'pages/help.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('المساعدة'),
            'breadcrumbs': [
                {'title': _('الرئيسية'), 'url': '/'},
                {'title': _('المساعدة'), 'active': True},
            ],
        })
        return context


class SupportView(LoginRequiredMixin, TemplateView):
    """Support and contact view."""
    template_name = 'pages/support.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('الدعم الفني'),
            'breadcrumbs': [
                {'title': _('الرئيسية'), 'url': '/'},
                {'title': _('الدعم الفني'), 'active': True},
            ],
        })
        return context


# Error handlers
def error_400(request, exception=None):
    """Handle 400 Bad Request errors."""
    return render(request, 'errors/400.html', status=400)


def error_403(request, exception=None):
    """Handle 403 Forbidden errors."""
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    """Handle 404 Not Found errors."""
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """Handle 500 Internal Server Error."""
    return render(request, 'errors/500.html', status=500)