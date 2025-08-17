"""
أمر إنشاء قوالب التقارير الافتراضية
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Hr.models_reports import ReportCategory, ReportTemplate

User = get_user_model()


class Command(BaseCommand):
    help = 'إنشاء قوالب التقارير الافتراضية'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('بدء إنشاء قوالب التقارير الافتراضية...'))

        # إنشاء الفئات
        categories = self.create_categories()
        
        # إنشاء القوالب
        self.create_templates(categories)
        
        self.stdout.write(self.style.SUCCESS('تم إنشاء قوالب التقارير الافتراضية بنجاح'))

    def create_categories(self):
        """إنشاء فئات التقارير"""
        categories_data = [
            {
                'name': 'تقارير الموظفين',
                'name_english': 'Employee Reports',
                'description': 'تقارير متعلقة ببيانات الموظفين',
                'icon': 'fas fa-users',
                'color': '#007bff',
                'order': 1
            },
            {
                'name': 'تقارير الحضور',
                'name_english': 'Attendance Reports',
                'description': 'تقارير الحضور والانصراف',
                'icon': 'fas fa-clock',
                'color': '#28a745',
                'order': 2
            },
            {
                'name': 'تقارير الرواتب',
                'name_english': 'Payroll Reports',
                'description': 'تقارير الرواتب والمستحقات',
                'icon': 'fas fa-money-bill-wave',
                'color': '#17a2b8',
                'order': 3
            },
            {
                'name': 'تقارير الإجازات',
                'name_english': 'Leave Reports',
                'description': 'تقارير الإجازات والطلبات',
                'icon': 'fas fa-calendar-alt',
                'color': '#ffc107',
                'order': 4
            },
            {
                'name': 'التقارير التحليلية',
                'name_english': 'Analytics Reports',
                'description': 'تقارير تحليلية وإحصائية',
                'icon': 'fas fa-chart-bar',
                'color': '#6f42c1',
                'order': 5
            }
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = ReportCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            
            if created:
                self.stdout.write(f'تم إنشاء فئة: {category.name}')
            else:
                self.stdout.write(f'الفئة موجودة: {category.name}')

        return categories

    def create_templates(self, categories):
        """إنشاء قوالب التقارير"""
        
        # الحصول على مستخدم النظام
        admin_user = User.objects.filter(is_superuser=True).first()
        
        templates_data = [
            # تقارير الموظفين
            {
                'category': categories['تقارير الموظفين'],
                'name': 'قائمة الموظفين الشاملة',
                'name_english': 'Comprehensive Employee List',
                'description': 'تقرير شامل بجميع بيانات الموظفين',
                'report_type': 'employee',
                'supported_formats': ['pdf', 'excel', 'csv'],
                'default_format': 'excel',
                'is_public': True,
                'query_config': {
                    'fields': ['employee_number', 'full_name', 'department', 'job_position', 'hire_date', 'phone', 'email', 'status'],
                    'order_by': ['department', 'full_name']
                },
                'filter_config': {
                    'department': {'type': 'select', 'required': False},
                    'job_position': {'type': 'select', 'required': False},
                    'hire_date_from': {'type': 'date', 'required': False},
                    'hire_date_to': {'type': 'date', 'required': False},
                    'search': {'type': 'text', 'required': False}
                }
            },
            {
                'category': categories['تقارير الموظفين'],
                'name': 'الموظفين الجدد',
                'name_english': 'New Employees',
                'description': 'تقرير بالموظفين المعينين حديثاً',
                'report_type': 'employee',
                'supported_formats': ['pdf', 'excel'],
                'default_format': 'pdf',
                'is_public': True,
                'query_config': {
                    'fields': ['employee_number', 'full_name', 'department', 'job_position', 'hire_date'],
                    'order_by': ['-hire_date']
                },
                'filter_config': {
                    'hire_date_from': {'type': 'date', 'required': True},
                    'hire_date_to': {'type': 'date', 'required': True}
                }
            },
            
            # تقارير الحضور
            {
                'category': categories['تقارير الحضور'],
                'name': 'تقرير الحضور اليومي',
                'name_english': 'Daily Attendance Report',
                'description': 'تقرير حضور الموظفين لفترة محددة',
                'report_type': 'attendance',
                'supported_formats': ['pdf', 'excel', 'csv'],
                'default_format': 'excel',
                'is_public': True,
                'query_config': {
                    'fields': ['employee_name', 'employee_number', 'date', 'check_in', 'check_out', 'total_hours', 'overtime_hours', 'late_minutes', 'status'],
                    'order_by': ['date', 'employee_name']
                },
                'filter_config': {
                    'date_from': {'type': 'date', 'required': True},
                    'date_to': {'type': 'date', 'required': True},
                    'department': {'type': 'select', 'required': False},
                    'employee': {'type': 'select', 'required': False}
                }
            },
            {
                'category': categories['تقارير الحضور'],
                'name': 'تقرير التأخير والغياب',
                'name_english': 'Late and Absence Report',
                'description': 'تقرير بحالات التأخير والغياب',
                'report_type': 'attendance',
                'supported_formats': ['pdf', 'excel'],
                'default_format': 'pdf',
                'is_public': True,
                'query_config': {
                    'fields': ['employee_name', 'employee_number', 'date', 'check_in', 'late_minutes', 'status'],
                    'order_by': ['-late_minutes', 'date']
                },
                'filter_config': {
                    'date_from': {'type': 'date', 'required': True},
                    'date_to': {'type': 'date', 'required': True},
                    'department': {'type': 'select', 'required': False}
                }
            },
            
            # تقارير الرواتب
            {
                'category': categories['تقارير الرواتب'],
                'name': 'كشف الرواتب الشهري',
                'name_english': 'Monthly Payroll Report',
                'description': 'كشف رواتب الموظفين لشهر محدد',
                'report_type': 'payroll',
                'supported_formats': ['pdf', 'excel'],
                'default_format': 'excel',
                'is_public': False,
                'required_permissions': ['Hr.view_payroll'],
                'query_config': {
                    'fields': ['employee_name', 'employee_number', 'department', 'basic_salary', 'allowances', 'deductions', 'net_salary'],
                    'order_by': ['department', 'employee_name']
                },
                'filter_config': {
                    'month': {'type': 'select', 'required': True},
                    'year': {'type': 'select', 'required': True},
                    'department': {'type': 'select', 'required': False}
                }
            },
            {
                'category': categories['تقارير الرواتب'],
                'name': 'ملخص تكاليف الرواتب',
                'name_english': 'Payroll Cost Summary',
                'description': 'ملخص إجمالي تكاليف الرواتب',
                'report_type': 'payroll',
                'supported_formats': ['pdf', 'excel'],
                'default_format': 'pdf',
                'is_public': False,
                'required_permissions': ['Hr.view_payroll', 'Hr.view_reports_summary'],
                'query_config': {
                    'fields': ['department', 'basic_salary', 'allowances', 'deductions', 'net_salary'],
                    'order_by': ['department']
                },
                'filter_config': {
                    'month': {'type': 'select', 'required': True},
                    'year': {'type': 'select', 'required': True}
                }
            },
            
            # تقارير الإجازات
            {
                'category': categories['تقارير الإجازات'],
                'name': 'تقرير طلبات الإجازات',
                'name_english': 'Leave Requests Report',
                'description': 'تقرير بطلبات الإجازات لفترة محددة',
                'report_type': 'leave',
                'supported_formats': ['pdf', 'excel', 'csv'],
                'default_format': 'excel',
                'is_public': True,
                'query_config': {
                    'fields': ['employee_name', 'employee_number', 'leave_type', 'start_date', 'end_date', 'days_count', 'status', 'reason'],
                    'order_by': ['-start_date', 'employee_name']
                },
                'filter_config': {
                    'date_from': {'type': 'date', 'required': True},
                    'date_to': {'type': 'date', 'required': True},
                    'leave_type': {'type': 'select', 'required': False},
                    'status': {'type': 'select', 'required': False},
                    'employee': {'type': 'select', 'required': False}
                }
            },
            {
                'category': categories['تقارير الإجازات'],
                'name': 'أرصدة الإجازات',
                'name_english': 'Leave Balances',
                'description': 'تقرير بأرصدة إجازات الموظفين',
                'report_type': 'leave',
                'supported_formats': ['pdf', 'excel'],
                'default_format': 'excel',
                'is_public': True,
                'query_config': {
                    'fields': ['employee_name', 'employee_number', 'leave_type', 'total_balance', 'used_balance', 'remaining_balance'],
                    'order_by': ['employee_name', 'leave_type']
                },
                'filter_config': {
                    'department': {'type': 'select', 'required': False},
                    'leave_type': {'type': 'select', 'required': False}
                }
            },
            
            # التقارير التحليلية
            {
                'category': categories['التقارير التحليلية'],
                'name': 'لوحة المؤشرات الرئيسية',
                'name_english': 'KPI Dashboard',
                'description': 'تقرير تحليلي بالمؤشرات الرئيسية للموارد البشرية',
                'report_type': 'analytics',
                'supported_formats': ['pdf', 'html'],
                'default_format': 'html',
                'is_public': True,
                'query_config': {
                    'fields': ['employee_stats', 'attendance_stats', 'leave_stats'],
                    'order_by': []
                },
                'filter_config': {}
            }
        ]

        for template_data in templates_data:
            template, created = ReportTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    **template_data,
                    'created_by': admin_user
                }
            )
            
            if created:
                self.stdout.write(f'تم إنشاء قالب: {template.name}')
            else:
                self.stdout.write(f'القالب موجود: {template.name}')