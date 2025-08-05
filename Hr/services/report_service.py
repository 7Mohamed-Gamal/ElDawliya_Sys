"""
خدمة التقارير الشاملة
"""

import os
import json
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
from datetime import datetime, timedelta
from django.db import models
from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO
import logging

# استيراد النماذج
from ..models import Employee, Department, JobPosition, Company, Branch
from ..models_reports import (
    ReportCategory, ReportTemplate, ReportInstance, 
    ScheduledReport, ReportFavorite, ReportShare
)
# استيراد النماذج المتاحة
try:
    from ..models import AttendanceRecord
except ImportError:
    AttendanceRecord = None

try:
    from ..models import LeaveRequest
except ImportError:
    LeaveRequest = None

# PayrollRecord سيتم إنشاؤه لاحقاً
PayrollRecord = None

logger = logging.getLogger(__name__)

User = get_user_model()


class ReportService:
    """خدمة التقارير الشاملة"""
    
    def __init__(self):
        self.supported_formats = ['pdf', 'excel', 'csv', 'html', 'json']
        self.report_generators = {
            'employee': self._generate_employee_report,
            'attendance': self._generate_attendance_report,
            'payroll': self._generate_payroll_report,
            'leave': self._generate_leave_report,
            'performance': self._generate_performance_report,
            'analytics': self._generate_analytics_report,
            'custom': self._generate_custom_report,
        }
    
    def get_available_templates(self, user, category=None):
        """الحصول على القوالب المتاحة للمستخدم"""
        try:
            templates = ReportTemplate.objects.filter(is_active=True)
            
            if category:
                templates = templates.filter(category=category)
            
            # فلترة حسب الصلاحيات
            user_templates = []
            for template in templates:
                if self._check_template_permissions(template, user):
                    user_templates.append(template)
            
            return user_templates
        except Exception as e:
            logger.error(f"خطأ في الحصول على القوالب: {e}")
            return []
    
    def _check_template_permissions(self, template, user):
        """فحص صلاحيات المستخدم للقالب"""
        try:
            # فحص الصلاحيات المطلوبة
            if template.required_permissions:
                for permission in template.required_permissions:
                    if not user.has_perm(permission):
                        return False
            
            # فحص الأقسام المسموحة
            if template.allowed_departments:
                user_department = getattr(user, 'employee', None)
                if user_department:
                    dept_id = str(user_department.department.id)
                    if dept_id not in template.allowed_departments:
                        return False
            
            return True
        except Exception as e:
            logger.error(f"خطأ في فحص الصلاحيات: {e}")
            return False
    
    def generate_report(self, template_id, user, parameters=None, output_format='pdf'):
        """إنتاج تقرير جديد"""
        try:
            template = ReportTemplate.objects.get(id=template_id, is_active=True)
            
            # فحص الصلاحيات
            if not self._check_template_permissions(template, user):
                raise PermissionError("ليس لديك صلاحية لإنتاج هذا التقرير")
            
            # إنشاء مثيل التقرير
            instance = ReportInstance.objects.create(
                template=template,
                name=f"{template.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                parameters=parameters or {},
                output_format=output_format,
                created_by=user
            )
            
            # بدء المعالجة
            instance.mark_as_processing()
            
            try:
                # إنتاج البيانات
                data = self._generate_report_data(template, parameters)
                
                # إنتاج الملف
                file_path, file_size = self._generate_report_file(
                    template, data, output_format, instance.id
                )
                
                # تحديث المثيل
                instance.mark_as_completed(
                    file_path=file_path,
                    record_count=len(data) if isinstance(data, list) else 0,
                    file_size=file_size
                )
                
                # زيادة عداد الاستخدام
                template.increment_usage()
                
                return instance
                
            except Exception as e:
                instance.mark_as_failed(str(e))
                raise
                
        except Exception as e:
            logger.error(f"خطأ في إنتاج التقرير: {e}")
            raise
    
    def _generate_report_data(self, template, parameters):
        """إنتاج بيانات التقرير"""
        try:
            generator = self.report_generators.get(template.report_type)
            if not generator:
                raise ValueError(f"نوع التقرير غير مدعوم: {template.report_type}")
            
            return generator(template, parameters)
        except Exception as e:
            logger.error(f"خطأ في إنتاج بيانات التقرير: {e}")
            raise
    
    def _generate_employee_report(self, template, parameters):
        """إنتاج تقرير الموظفين"""
        try:
            queryset = Employee.objects.select_related(
                'department', 'job_position', 'company', 'branch'
            ).filter(is_active=True)
            
            # تطبيق الفلاتر
            if parameters:
                if parameters.get('department_id'):
                    queryset = queryset.filter(department_id=parameters['department_id'])
                
                if parameters.get('job_position_id'):
                    queryset = queryset.filter(job_position_id=parameters['job_position_id'])
                
                if parameters.get('hire_date_from'):
                    queryset = queryset.filter(hire_date__gte=parameters['hire_date_from'])
                
                if parameters.get('hire_date_to'):
                    queryset = queryset.filter(hire_date__lte=parameters['hire_date_to'])
                
                if parameters.get('search'):
                    search = parameters['search']
                    queryset = queryset.filter(
                        Q(first_name__icontains=search) |
                        Q(last_name__icontains=search) |
                        Q(employee_number__icontains=search)
                    )
            
            # تحويل إلى قائمة
            data = []
            for employee in queryset:
                data.append({
                    'employee_number': employee.employee_number,
                    'full_name': employee.get_full_name(),
                    'department': employee.department.name if employee.department else '',
                    'job_position': employee.job_position.name if employee.job_position else '',
                    'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else '',
                    'phone': employee.phone or '',
                    'email': employee.email or '',
                    'status': 'نشط' if employee.is_active else 'غير نشط',
                })
            
            return data
        except Exception as e:
            logger.error(f"خطأ في تقرير الموظفين: {e}")
            raise
    
    def _generate_attendance_report(self, template, parameters):
        """إنتاج تقرير الحضور"""
        try:
            if not AttendanceRecord:
                return []  # إرجاع قائمة فارغة إذا لم يكن النموذج متاحاً
            
            # الحصول على تاريخ البداية والنهاية
            date_from = parameters.get('date_from', timezone.now().date() - timedelta(days=30))
            date_to = parameters.get('date_to', timezone.now().date())
            
            if isinstance(date_from, str):
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            if isinstance(date_to, str):
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            queryset = AttendanceRecord.objects.select_related('employee').filter(
                date__range=[date_from, date_to]
            )
            
            # تطبيق الفلاتر
            if parameters.get('employee_id'):
                queryset = queryset.filter(employee_id=parameters['employee_id'])
            
            if parameters.get('department_id'):
                queryset = queryset.filter(employee__department_id=parameters['department_id'])
            
            # تجميع البيانات
            data = []
            for record in queryset:
                data.append({
                    'employee_name': record.employee.get_full_name(),
                    'employee_number': record.employee.employee_number,
                    'date': record.date.strftime('%Y-%m-%d'),
                    'check_in': record.check_in.strftime('%H:%M') if record.check_in else '',
                    'check_out': record.check_out.strftime('%H:%M') if record.check_out else '',
                    'total_hours': str(record.total_hours) if record.total_hours else '',
                    'overtime_hours': str(record.overtime_hours) if record.overtime_hours else '',
                    'late_minutes': record.late_minutes or 0,
                    'status': record.get_status_display(),
                })
            
            return data
        except Exception as e:
            logger.error(f"خطأ في تقرير الحضور: {e}")
            raise
    
    def _generate_payroll_report(self, template, parameters):
        """إنتاج تقرير الرواتب"""
        try:
            if not PayrollRecord:
                return []  # إرجاع قائمة فارغة إذا لم يكن النموذج متاحاً
            
            # الحصول على الشهر والسنة
            month = parameters.get('month', timezone.now().month)
            year = parameters.get('year', timezone.now().year)
            
            queryset = PayrollRecord.objects.select_related('employee').filter(
                month=month, year=year
            )
            
            # تطبيق الفلاتر
            if parameters.get('department_id'):
                queryset = queryset.filter(employee__department_id=parameters['department_id'])
            
            # تجميع البيانات
            data = []
            total_basic_salary = 0
            total_allowances = 0
            total_deductions = 0
            total_net_salary = 0
            
            for record in queryset:
                data.append({
                    'employee_name': record.employee.get_full_name(),
                    'employee_number': record.employee.employee_number,
                    'department': record.employee.department.name if record.employee.department else '',
                    'basic_salary': float(record.basic_salary),
                    'allowances': float(record.total_allowances),
                    'deductions': float(record.total_deductions),
                    'net_salary': float(record.net_salary),
                })
                
                total_basic_salary += float(record.basic_salary)
                total_allowances += float(record.total_allowances)
                total_deductions += float(record.total_deductions)
                total_net_salary += float(record.net_salary)
            
            # إضافة الإجماليات
            data.append({
                'employee_name': 'الإجمالي',
                'employee_number': '',
                'department': '',
                'basic_salary': total_basic_salary,
                'allowances': total_allowances,
                'deductions': total_deductions,
                'net_salary': total_net_salary,
            })
            
            return data
        except Exception as e:
            logger.error(f"خطأ في تقرير الرواتب: {e}")
            raise
    
    def _generate_leave_report(self, template, parameters):
        """إنتاج تقرير الإجازات"""
        try:
            if not LeaveRequest:
                return []  # إرجاع قائمة فارغة إذا لم يكن النموذج متاحاً
            
            # الحصول على تاريخ البداية والنهاية
            date_from = parameters.get('date_from', timezone.now().date() - timedelta(days=365))
            date_to = parameters.get('date_to', timezone.now().date())
            
            if isinstance(date_from, str):
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            if isinstance(date_to, str):
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            queryset = LeaveRequest.objects.select_related(
                'employee', 'leave_type'
            ).filter(
                start_date__range=[date_from, date_to]
            )
            
            # تطبيق الفلاتر
            if parameters.get('employee_id'):
                queryset = queryset.filter(employee_id=parameters['employee_id'])
            
            if parameters.get('leave_type_id'):
                queryset = queryset.filter(leave_type_id=parameters['leave_type_id'])
            
            if parameters.get('status'):
                queryset = queryset.filter(status=parameters['status'])
            
            # تجميع البيانات
            data = []
            for request in queryset:
                data.append({
                    'employee_name': request.employee.get_full_name(),
                    'employee_number': request.employee.employee_number,
                    'leave_type': request.leave_type.name,
                    'start_date': request.start_date.strftime('%Y-%m-%d'),
                    'end_date': request.end_date.strftime('%Y-%m-%d'),
                    'days_count': request.days_count,
                    'status': request.get_status_display(),
                    'reason': request.reason or '',
                })
            
            return data
        except Exception as e:
            logger.error(f"خطأ في تقرير الإجازات: {e}")
            raise
    
    def _generate_performance_report(self, template, parameters):
        """إنتاج تقرير الأداء"""
        # TODO: تنفيذ تقرير الأداء عند إنشاء نظام التقييمات
        return []
    
    def _generate_analytics_report(self, template, parameters):
        """إنتاج تقرير تحليلي"""
        try:
            data = {}
            
            # إحصائيات الموظفين
            data['employee_stats'] = {
                'total_employees': Employee.objects.filter(is_active=True).count(),
                'by_department': list(
                    Employee.objects.filter(is_active=True)
                    .values('department__name')
                    .annotate(count=Count('id'))
                ),
                'by_job_position': list(
                    Employee.objects.filter(is_active=True)
                    .values('job_position__name')
                    .annotate(count=Count('id'))
                ),
            }
            
            # إحصائيات الحضور (آخر 30 يوم)
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            attendance_stats = AttendanceRecord.objects.filter(
                date__gte=thirty_days_ago
            ).aggregate(
                avg_attendance_rate=Avg('attendance_rate'),
                total_late_minutes=Sum('late_minutes'),
                total_overtime_hours=Sum('overtime_hours')
            )
            
            data['attendance_stats'] = attendance_stats
            
            # إحصائيات الإجازات (آخر سنة)
            one_year_ago = timezone.now().date() - timedelta(days=365)
            leave_stats = LeaveRequest.objects.filter(
                start_date__gte=one_year_ago
            ).aggregate(
                total_requests=Count('id'),
                approved_requests=Count('id', filter=Q(status='approved')),
                total_days=Sum('days_count')
            )
            
            data['leave_stats'] = leave_stats
            
            return [data]  # إرجاع كقائمة للتوافق مع باقي التقارير
        except Exception as e:
            logger.error(f"خطأ في التقرير التحليلي: {e}")
            raise
    
    def _generate_custom_report(self, template, parameters):
        """إنتاج تقرير مخصص"""
        # TODO: تنفيذ التقارير المخصصة
        return []
    
    def _generate_report_file(self, template, data, output_format, instance_id):
        """إنتاج ملف التقرير"""
        try:
            if output_format == 'excel':
                return self._generate_excel_file(template, data, instance_id)
            elif output_format == 'csv':
                return self._generate_csv_file(template, data, instance_id)
            elif output_format == 'pdf':
                return self._generate_pdf_file(template, data, instance_id)
            elif output_format == 'html':
                return self._generate_html_file(template, data, instance_id)
            elif output_format == 'json':
                return self._generate_json_file(template, data, instance_id)
            else:
                raise ValueError(f"صيغة غير مدعومة: {output_format}")
        except Exception as e:
            logger.error(f"خطأ في إنتاج ملف التقرير: {e}")
            raise
    
    def _generate_excel_file(self, template, data, instance_id):
        """إنتاج ملف Excel"""
        try:
            if not PANDAS_AVAILABLE:
                raise ImportError("مكتبة pandas غير متاحة")
            
            # إنشاء DataFrame
            df = pd.DataFrame(data)
            
            # إنشاء ملف Excel في الذاكرة
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=template.name[:31], index=False)
            
            # حفظ الملف
            filename = f"report_{instance_id}.xlsx"
            file_path = f"reports/{filename}"
            
            buffer.seek(0)
            saved_path = default_storage.save(file_path, ContentFile(buffer.getvalue()))
            file_size = buffer.tell()
            
            return saved_path, file_size
        except Exception as e:
            logger.error(f"خطأ في إنتاج ملف Excel: {e}")
            raise
    
    def _generate_csv_file(self, template, data, instance_id):
        """إنتاج ملف CSV"""
        try:
            if not PANDAS_AVAILABLE:
                # إنشاء CSV يدوياً بدون pandas
                import csv
                buffer = BytesIO()
                
                if data and isinstance(data[0], dict):
                    # كتابة CSV يدوياً
                    csv_content = ""
                    headers = list(data[0].keys())
                    csv_content += ",".join(headers) + "\n"
                    
                    for row in data:
                        csv_content += ",".join([str(row.get(col, '')) for col in headers]) + "\n"
                    
                    buffer.write(csv_content.encode('utf-8-sig'))
                else:
                    buffer.write("لا توجد بيانات".encode('utf-8-sig'))
            else:
                # إنشاء DataFrame
                df = pd.DataFrame(data)
                
                # إنشاء ملف CSV في الذاكرة
                csv_content = df.to_csv(index=False, encoding='utf-8-sig')
                buffer.write(csv_content.encode('utf-8-sig'))
            
            # حفظ الملف
            filename = f"report_{instance_id}.csv"
            file_path = f"reports/{filename}"
            
            buffer.seek(0)
            saved_path = default_storage.save(file_path, ContentFile(buffer.getvalue()))
            file_size = buffer.tell()
            
            return saved_path, file_size
        except Exception as e:
            logger.error(f"خطأ في إنتاج ملف CSV: {e}")
            raise
    
    def _generate_pdf_file(self, template, data, instance_id):
        """إنتاج ملف PDF"""
        try:
            # TODO: تنفيذ إنتاج PDF باستخدام ReportLab أو WeasyPrint
            # حالياً سنرجع ملف HTML
            return self._generate_html_file(template, data, instance_id)
        except Exception as e:
            logger.error(f"خطأ في إنتاج ملف PDF: {e}")
            raise
    
    def _generate_html_file(self, template, data, instance_id):
        """إنتاج ملف HTML"""
        try:
            # إنشاء محتوى HTML
            context = {
                'template': template,
                'data': data,
                'generated_at': timezone.now(),
            }
            
            html_content = render_to_string('Hr/reports/report_template.html', context)
            
            # حفظ الملف
            filename = f"report_{instance_id}.html"
            file_path = f"reports/{filename}"
            
            saved_path = default_storage.save(
                file_path, 
                ContentFile(html_content.encode('utf-8'))
            )
            file_size = len(html_content.encode('utf-8'))
            
            return saved_path, file_size
        except Exception as e:
            logger.error(f"خطأ في إنتاج ملف HTML: {e}")
            raise
    
    def _generate_json_file(self, template, data, instance_id):
        """إنتاج ملف JSON"""
        try:
            # إنشاء محتوى JSON
            json_data = {
                'template': {
                    'name': template.name,
                    'type': template.report_type,
                    'generated_at': timezone.now().isoformat(),
                },
                'data': data
            }
            
            json_content = json.dumps(json_data, ensure_ascii=False, indent=2)
            
            # حفظ الملف
            filename = f"report_{instance_id}.json"
            file_path = f"reports/{filename}"
            
            saved_path = default_storage.save(
                file_path, 
                ContentFile(json_content.encode('utf-8'))
            )
            file_size = len(json_content.encode('utf-8'))
            
            return saved_path, file_size
        except Exception as e:
            logger.error(f"خطأ في إنتاج ملف JSON: {e}")
            raise
    
    def get_user_reports(self, user, limit=20):
        """الحصول على تقارير المستخدم"""
        try:
            return ReportInstance.objects.filter(
                created_by=user
            ).select_related('template').order_by('-created_at')[:limit]
        except Exception as e:
            logger.error(f"خطأ في الحصول على تقارير المستخدم: {e}")
            return []
    
    def add_to_favorites(self, user, template_id, parameters=None, name=None):
        """إضافة تقرير للمفضلة"""
        try:
            template = ReportTemplate.objects.get(id=template_id)
            favorite, created = ReportFavorite.objects.get_or_create(
                user=user,
                template=template,
                defaults={
                    'parameters': parameters or {},
                    'name': name
                }
            )
            return favorite
        except Exception as e:
            logger.error(f"خطأ في إضافة التقرير للمفضلة: {e}")
            raise
    
    def get_user_favorites(self, user):
        """الحصول على التقارير المفضلة للمستخدم"""
        try:
            return ReportFavorite.objects.filter(
                user=user
            ).select_related('template').order_by('-created_at')
        except Exception as e:
            logger.error(f"خطأ في الحصول على المفضلة: {e}")
            return []
    
    def share_report(self, instance_id, shared_by, shared_with_ids, message=None, expires_days=30):
        """مشاركة تقرير"""
        try:
            instance = ReportInstance.objects.get(id=instance_id)
            
            # فحص الصلاحيات
            if instance.created_by != shared_by:
                raise PermissionError("ليس لديك صلاحية لمشاركة هذا التقرير")
            
            expires_at = timezone.now() + timedelta(days=expires_days) if expires_days else None
            
            shares = []
            for user_id in shared_with_ids:
                try:
                    shared_with = User.objects.get(id=user_id)
                    share = ReportShare.objects.create(
                        instance=instance,
                        shared_by=shared_by,
                        shared_with=shared_with,
                        message=message,
                        expires_at=expires_at
                    )
                    shares.append(share)
                except User.DoesNotExist:
                    continue
            
            return shares
        except Exception as e:
            logger.error(f"خطأ في مشاركة التقرير: {e}")
            raise


# إنشاء مثيل الخدمة
report_service = ReportService()