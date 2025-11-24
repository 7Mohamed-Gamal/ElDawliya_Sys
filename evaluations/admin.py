from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import EvaluationPeriod, EmployeeEvaluation


@admin.register(EvaluationPeriod)
class EvaluationPeriodAdmin(admin.ModelAdmin):
    """إدارة فترات التقييم"""

    list_display = [
        'period_name',
        'start_date',
        'end_date',
        'is_active',
        'evaluation_count',
        'completed_count',
        'completion_rate',
        'created_at'
    ]

    list_filter = [
        'is_active',
        'start_date',
        'end_date',
        'created_at'
    ]

    search_fields = [
        'period_name'
    ]

    date_hierarchy = 'start_date'

    ordering = ['-start_date']

    readonly_fields = ['created_at']

    fieldsets = (
        ('معلومات الفترة', {
            'fields': ('period_name', 'start_date', 'end_date', 'is_active')
        }),
        ('معلومات النظام', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def evaluation_count(self, obj):
        """عدد التقييمات في الفترة"""
        count = obj.evaluations.count()
        if count > 0:
            url = reverse('admin:evaluations_employeeevaluation_changelist')
            return format_html(
                '<a href="{}?period__period_id__exact={}">{}</a>',
                url, obj.period_id, count
            )
        return count
    evaluation_count.short_description = 'عدد التقييمات'

    def completed_count(self, obj):
        """عدد التقييمات المكتملة"""
        count = obj.evaluations.filter(score__isnull=False).count()
        return count
    completed_count.short_description = 'التقييمات المكتملة'

    def completion_rate(self, obj):
        """معدل الإنجاز"""
        total = obj.evaluations.count()
        completed = obj.evaluations.filter(score__isnull=False).count()

        if total == 0:
            return "0%"

        rate = (completed / total) * 100
        color = 'green' if rate >= 80 else 'orange' if rate >= 50 else 'red'

        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    completion_rate.short_description = 'معدل الإنجاز'

    actions = ['activate_periods', 'deactivate_periods']

    def activate_periods(self, request, queryset):
        """تفعيل الفترات المحددة"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'تم تفعيل {updated} فترة تقييم.')
    activate_periods.short_description = 'تفعيل الفترات المحددة'

    def deactivate_periods(self, request, queryset):
        """إلغاء تفعيل الفترات المحددة"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم إلغاء تفعيل {updated} فترة تقييم.')
    deactivate_periods.short_description = 'إلغاء تفعيل الفترات المحددة'


@admin.register(EmployeeEvaluation)
class EmployeeEvaluationAdmin(admin.ModelAdmin):
    """إدارة تقييمات الموظفين"""

    list_display = [
        'employee_info',
        'period',
        'manager_info',
        'score_display',
        'performance_level_display',
        'status_display',
        'eval_date',
        'created_at'
    ]

    list_filter = [
        'status',
        'period',
        'emp__dept',
        'eval_date',
        'created_at',
        'score',
    ]

    search_fields = [
        'emp__first_name',
        'emp__last_name',
        'emp__emp_code',
        'notes'
    ]

    date_hierarchy = 'eval_date'

    ordering = ['-eval_date', '-score']

    readonly_fields = ['created_at', 'updated_at', 'performance_level_display']

    fieldsets = (
        ('معلومات التقييم', {
            'fields': ('emp', 'period', 'manager_id', 'status')
        }),
        ('تفاصيل التقييم', {
            'fields': ('score', 'performance_level_display', 'eval_date', 'notes')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    autocomplete_fields = ['emp']

    def employee_info(self, obj):
        """معلومات الموظف"""
        if obj.emp:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                f"{obj.emp.first_name} {obj.emp.last_name}",
                obj.emp.emp_code
            )
        return '-'
    employee_info.short_description = 'الموظف'

    def manager_info(self, obj):
        """معلومات المدير"""
        if obj.manager_id:
            try:
                from employees.models import Employee
                manager = Employee.objects.get(emp_id=obj.manager_id)
                return format_html(
                    '{}<br><small>{}</small>',
                    f"{manager.first_name} {manager.last_name}",
                    manager.emp_code
                )
            except Employee.DoesNotExist:
                return f"Manager ID: {obj.manager_id}"
        return '-'
    manager_info.short_description = 'المدير المقيم'

    def score_display(self, obj):
        """عرض الدرجة مع التنسيق"""
        if obj.score is not None:
            color = self._get_score_color(obj.score)
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, obj.score
            )
        return format_html('<span style="color: gray;">غير مكتمل</span>')
    score_display.short_description = 'الدرجة'

    def performance_level_display(self, obj):
        """عرض مستوى الأداء"""
        if obj.score is not None:
            level = obj.performance_level
            color = self._get_score_color(obj.score)
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, level
            )
        return 'غير محدد'
    performance_level_display.short_description = 'مستوى الأداء'

    def status_display(self, obj):
        """عرض الحالة مع التنسيق"""
        status_colors = {
            'draft': 'gray',
            'submitted': 'blue',
            'approved': 'green',
            'rejected': 'red'
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'الحالة'

    def _get_score_color(self, score):
        """تحديد لون الدرجة"""
        if score >= 90:
            return 'green'
        elif score >= 80:
            return 'blue'
        elif score >= 70:
            return 'orange'
        elif score >= 60:
            return 'darkorange'
        else:
            return 'red'

    actions = [
        'approve_evaluations',
        'reject_evaluations',
        'mark_as_submitted',
        'export_selected_evaluations'
    ]

    def approve_evaluations(self, request, queryset):
        """اعتماد التقييمات المحددة"""
        updated = queryset.update(status='approved')
        self.message_user(request, f'تم اعتماد {updated} تقييم.')
    approve_evaluations.short_description = 'اعتماد التقييمات المحددة'

    def reject_evaluations(self, request, queryset):
        """رفض التقييمات المحددة"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'تم رفض {updated} تقييم.')
    reject_evaluations.short_description = 'رفض التقييمات المحددة'

    def mark_as_submitted(self, request, queryset):
        """تحديد كمقدم"""
        updated = queryset.update(status='submitted')
        self.message_user(request, f'تم تحديد {updated} تقييم كمقدم.')
    mark_as_submitted.short_description = 'تحديد كمقدم'

    def export_selected_evaluations(self, request, queryset):
        """تصدير التقييمات المحددة"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="selected_evaluations.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'الموظف', 'الكود', 'الفترة', 'المدير', 'الدرجة',
            'مستوى الأداء', 'الحالة', 'تاريخ التقييم', 'الملاحظات'
        ])

        for evaluation in queryset.select_related('emp', 'period'):
            writer.writerow([
                f"{evaluation.emp.first_name} {evaluation.emp.last_name}" if evaluation.emp else '',
                evaluation.emp.emp_code if evaluation.emp else '',
                evaluation.period.period_name,
                evaluation.get_manager_name(),
                evaluation.score or '',
                evaluation.performance_level if evaluation.score else '',
                evaluation.get_status_display(),
                evaluation.eval_date or '',
                evaluation.notes or ''
            ])

        return response
    export_selected_evaluations.short_description = 'تصدير التقييمات المحددة'

    def get_queryset(self, request):
        """تحسين الاستعلامات"""
        return super().get_queryset(request).select_related(
            'emp', 'period'
        )


# تخصيص عنوان الإدارة
admin.site.site_header = 'إدارة نظام التقييمات'
admin.site.site_title = 'نظام التقييمات'
admin.site.index_title = 'لوحة تحكم التقييمات'
