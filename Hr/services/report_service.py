"""
خدمة التقارير والتحليلات للموارد البشرية
"""

from django.db.models import Count, Q, Avg, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
import json

from Hr.models.employee.employee_models import Employee
from Hr.models.organization.department_models import Department
from Hr.models.organization.position_models import Position
from Hr.models.attendance.attendance_record_models import AttendanceRecord
from Hr.models.payroll.employee_salary_structure_models import EmployeeSalaryStructure


class ReportService:
    """خدمة إنشاء التقارير والتحليلات"""
    
    @staticmethod
    def get_employee_summary_report(filters=None):
        """
        إنشاء تقرير ملخص الموظفين
        """
        if filters is None:
            filters = {}
        
        # بناء الاستعلام الأساسي
        queryset = Employee.objects.all()
        
        # تطبيق الفلاتر
        if filters.get('department'):
            queryset = queryset.filter(department_id=filters['department'])
        
        if filters.get('branch'):
            queryset = queryset.filter(branch_id=filters['branch'])
        
        if filters.get('position'):
            queryset = queryset.filter(position_id=filters['position'])
        
        if filters.get('status'):
            is_active = filters['status'] == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        # تطبيق فلاتر التاريخ
        if filters.get('start_date'):
            queryset = queryset.filter(hire_date__gte=filters['start_date'])
        
        if filters.get('end_date'):
            queryset = queryset.filter(hire_date__lte=filters['end_date'])
        
        # الإحصائيات الأساسية
        total_employees = queryset.count()
        active_employees = queryset.filter(is_active=True).count()
        inactive_employees = queryset.filter(is_active=False).count()
        
        # التوزيع حسب القسم
        department_distribution = queryset.values(
            'department__name_ar'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # التوزيع حسب الوظيفة
        position_distribution = queryset.values(
            'position__name_ar'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # التوزيع حسب الجنس
        gender_distribution = queryset.values(
            'gender'
        ).annotate(
            count=Count('id')
        )
        
        # الموظفين الجدد (آخر 30 يوم)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        new_employees = queryset.filter(
            hire_date__gte=thirty_days_ago
        ).count()
        
        return {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': inactive_employees,
            'new_employees': new_employees,
            'departments_count': Department.objects.count(),
            'positions_count': Position.objects.count(),
            'department_distribution': list(department_distribution),
            'position_distribution': list(position_distribution),
            'gender_distribution': list(gender_distribution),
            'employees': list(queryset.values(
                'full_name_ar',
                'employee_number',
                'department__name_ar',
                'position__name_ar',
                'hire_date',
                'is_active'
            )[:100])  # أول 100 موظف
        }
    
    @staticmethod
    def get_employee_details_report(filters=None):
        """
        إنشاء تقرير تفاصيل الموظفين
        """
        if filters is None:
            filters = {}
        
        # بناء الاستعلام
        queryset = Employee.objects.select_related(
            'department',
            'position',
            'branch'
        )
        
        # تطبيق الفلاتر
        if filters.get('department'):
            queryset = queryset.filter(department_id=filters['department'])
        
        if filters.get('branch'):
            queryset = queryset.filter(branch_id=filters['branch'])
        
        if filters.get('position'):
            queryset = queryset.filter(position_id=filters['position'])
        
        if filters.get('status'):
            is_active = filters['status'] == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        # تطبيق فلاتر التاريخ
        if filters.get('start_date'):
            queryset = queryset.filter(hire_date__gte=filters['start_date'])
        
        if filters.get('end_date'):
            queryset = queryset.filter(hire_date__lte=filters['end_date'])
        
        employees_data = []
        for employee in queryset:
            employees_data.append({
                'full_name': employee.full_name_ar,
                'employee_number': employee.employee_number,
                'national_id': employee.national_id,
                'department': employee.department.name_ar if employee.department else '',
                'position': employee.position.name_ar if employee.position else '',
                'branch': employee.branch.name_ar if employee.branch else '',
                'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else '',
                'birth_date': employee.birth_date.strftime('%Y-%m-%d') if employee.birth_date else '',
                'gender': employee.get_gender_display(),
                'nationality': employee.nationality,
                'phone': employee.phone,
                'email': employee.email,
                'address': employee.address,
                'is_active': employee.is_active,
                'created_at': employee.created_at.strftime('%Y-%m-%d') if employee.created_at else ''
            })
        
        return {
            'total_employees': queryset.count(),
            'employees': employees_data
        }
    
    @staticmethod
    def get_organizational_structure_report():
        """
        إنشاء تقرير الهيكل التنظيمي
        """
        departments = Department.objects.annotate(
            employee_count=Count('employees')
        ).order_by('name_ar')
        
        structure_data = []
        for dept in departments:
            # الحصول على الوظائف في هذا القسم
            positions = Position.objects.filter(
                employees__department=dept
            ).annotate(
                employee_count=Count('employees')
            ).distinct()
            
            dept_data = {
                'department_name': dept.name_ar,
                'department_code': dept.code,
                'employee_count': dept.employee_count,
                'positions': []
            }
            
            for position in positions:
                dept_data['positions'].append({
                    'position_name': position.name_ar,
                    'position_code': position.code,
                    'employee_count': position.employee_count
                })
            
            structure_data.append(dept_data)
        
        return {
            'total_departments': departments.count(),
            'total_employees': Employee.objects.count(),
            'structure': structure_data
        }
    
    @staticmethod
    def get_new_employees_report(filters=None):
        """
        إنشاء تقرير الموظفين الجدد
        """
        if filters is None:
            filters = {}
        
        # تحديد الفترة الافتراضية (آخر 30 يوم)
        if not filters.get('start_date'):
            filters['start_date'] = timezone.now().date() - timedelta(days=30)
        
        if not filters.get('end_date'):
            filters['end_date'] = timezone.now().date()
        
        # بناء الاستعلام
        queryset = Employee.objects.filter(
            hire_date__gte=filters['start_date'],
            hire_date__lte=filters['end_date']
        ).select_related('department', 'position')
        
        # تطبيق الفلاتر الإضافية
        if filters.get('department'):
            queryset = queryset.filter(department_id=filters['department'])
        
        if filters.get('branch'):
            queryset = queryset.filter(branch_id=filters['branch'])
        
        # الإحصائيات
        total_new = queryset.count()
        
        # التوزيع حسب القسم
        dept_distribution = queryset.values(
            'department__name_ar'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # التوزيع حسب الشهر
        monthly_distribution = queryset.extra(
            select={'month': "strftime('%%Y-%%m', hire_date)"}
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        employees_data = []
        for employee in queryset.order_by('-hire_date'):
            employees_data.append({
                'full_name': employee.full_name_ar,
                'employee_number': employee.employee_number,
                'department': employee.department.name_ar if employee.department else '',
                'position': employee.position.name_ar if employee.position else '',
                'hire_date': employee.hire_date.strftime('%Y-%m-%d'),
                'phone': employee.phone,
                'email': employee.email
            })
        
        return {
            'total_new_employees': total_new,
            'period_start': filters['start_date'].strftime('%Y-%m-%d'),
            'period_end': filters['end_date'].strftime('%Y-%m-%d'),
            'department_distribution': list(dept_distribution),
            'monthly_distribution': list(monthly_distribution),
            'employees': employees_data
        }
    
    @staticmethod
    def get_demographics_report(filters=None):
        """
        إنشاء تقرير التركيبة السكانية
        """
        if filters is None:
            filters = {}
        
        # بناء الاستعلام
        queryset = Employee.objects.all()
        
        # تطبيق الفلاتر
        if filters.get('department'):
            queryset = queryset.filter(department_id=filters['department'])
        
        if filters.get('status'):
            is_active = filters['status'] == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        # التوزيع حسب الجنس
        gender_distribution = queryset.values('gender').annotate(
            count=Count('id')
        )
        
        # التوزيع حسب الجنسية
        nationality_distribution = queryset.values('nationality').annotate(
            count=Count('id')
        ).order_by('-count')[:10]  # أعلى 10 جنسيات
        
        # التوزيع العمري
        today = timezone.now().date()
        age_groups = {
            '18-25': 0,
            '26-35': 0,
            '36-45': 0,
            '46-55': 0,
            '56+': 0
        }
        
        for employee in queryset.filter(birth_date__isnull=False):
            age = (today - employee.birth_date).days // 365
            if 18 <= age <= 25:
                age_groups['18-25'] += 1
            elif 26 <= age <= 35:
                age_groups['26-35'] += 1
            elif 36 <= age <= 45:
                age_groups['36-45'] += 1
            elif 46 <= age <= 55:
                age_groups['46-55'] += 1
            elif age > 55:
                age_groups['56+'] += 1
        
        # التوزيع حسب المؤهل العلمي
        education_distribution = queryset.values('education_level').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'total_employees': queryset.count(),
            'gender_distribution': list(gender_distribution),
            'nationality_distribution': list(nationality_distribution),
            'age_distribution': [
                {'age_group': k, 'count': v} for k, v in age_groups.items()
            ],
            'education_distribution': list(education_distribution)
        }
    
    @staticmethod
    def get_birthdays_anniversaries_report(filters=None):
        """
        إنشاء تقرير أعياد الميلاد وذكريات التوظيف
        """
        if filters is None:
            filters = {}
        
        # تحديد الفترة (الشهر الحالي افتراضياً)
        today = timezone.now().date()
        if not filters.get('start_date'):
            filters['start_date'] = today.replace(day=1)
        
        if not filters.get('end_date'):
            next_month = today.replace(day=28) + timedelta(days=4)
            filters['end_date'] = next_month - timedelta(days=next_month.day)
        
        # أعياد الميلاد
        birthdays = Employee.objects.filter(
            birth_date__month__gte=filters['start_date'].month,
            birth_date__month__lte=filters['end_date'].month,
            is_active=True
        ).select_related('department', 'position').order_by('birth_date__day')
        
        # ذكريات التوظيف
        anniversaries = Employee.objects.filter(
            hire_date__month__gte=filters['start_date'].month,
            hire_date__month__lte=filters['end_date'].month,
            is_active=True
        ).select_related('department', 'position').order_by('hire_date__day')
        
        birthdays_data = []
        for employee in birthdays:
            years_old = (today - employee.birth_date).days // 365 if employee.birth_date else 0
            birthdays_data.append({
                'full_name': employee.full_name_ar,
                'employee_number': employee.employee_number,
                'department': employee.department.name_ar if employee.department else '',
                'birth_date': employee.birth_date.strftime('%Y-%m-%d') if employee.birth_date else '',
                'age': years_old,
                'phone': employee.phone,
                'email': employee.email
            })
        
        anniversaries_data = []
        for employee in anniversaries:
            years_service = (today - employee.hire_date).days // 365 if employee.hire_date else 0
            anniversaries_data.append({
                'full_name': employee.full_name_ar,
                'employee_number': employee.employee_number,
                'department': employee.department.name_ar if employee.department else '',
                'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else '',
                'years_of_service': years_service,
                'phone': employee.phone,
                'email': employee.email
            })
        
        return {
            'period_start': filters['start_date'].strftime('%Y-%m-%d'),
            'period_end': filters['end_date'].strftime('%Y-%m-%d'),
            'birthdays_count': len(birthdays_data),
            'anniversaries_count': len(anniversaries_data),
            'birthdays': birthdays_data,
            'anniversaries': anniversaries_data
        }
    
    @staticmethod
    def get_attendance_analytics(filters=None):
        """
        إنشاء تحليلات الحضور
        """
        if filters is None:
            filters = {}
        
        # تحديد الفترة (الشهر الحالي افتراضياً)
        today = timezone.now().date()
        if not filters.get('start_date'):
            filters['start_date'] = today.replace(day=1)
        
        if not filters.get('end_date'):
            filters['end_date'] = today
        
        # بناء الاستعلام
        attendance_records = AttendanceRecord.objects.filter(
            date__gte=filters['start_date'],
            date__lte=filters['end_date']
        )
        
        # تطبيق الفلاتر
        if filters.get('department'):
            attendance_records = attendance_records.filter(
                employee__department_id=filters['department']
            )
        
        # الإحصائيات الأساسية
        total_records = attendance_records.count()
        present_records = attendance_records.filter(status='present').count()
        absent_records = attendance_records.filter(status='absent').count()
        late_records = attendance_records.filter(is_late=True).count()
        
        # معدل الحضور
        attendance_rate = (present_records / total_records * 100) if total_records > 0 else 0
        
        # التوزيع حسب القسم
        dept_attendance = attendance_records.values(
            'employee__department__name_ar'
        ).annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent'))
        ).order_by('-total')
        
        return {
            'period_start': filters['start_date'].strftime('%Y-%m-%d'),
            'period_end': filters['end_date'].strftime('%Y-%m-%d'),
            'total_records': total_records,
            'present_records': present_records,
            'absent_records': absent_records,
            'late_records': late_records,
            'attendance_rate': round(attendance_rate, 2),
            'department_attendance': list(dept_attendance)
        }
    
    @staticmethod
    def get_salary_analytics(filters=None):
        """
        إنشاء تحليلات الرواتب
        """
        if filters is None:
            filters = {}
        
        # بناء الاستعلام
        salary_structures = EmployeeSalaryStructure.objects.filter(
            is_active=True
        ).select_related('employee', 'employee__department', 'employee__position')
        
        # تطبيق الفلاتر
        if filters.get('department'):
            salary_structures = salary_structures.filter(
                employee__department_id=filters['department']
            )
        
        # الإحصائيات الأساسية
        total_employees = salary_structures.count()
        total_basic_salary = salary_structures.aggregate(
            total=Sum('basic_salary')
        )['total'] or 0
        
        avg_basic_salary = salary_structures.aggregate(
            avg=Avg('basic_salary')
        )['avg'] or 0
        
        # التوزيع حسب القسم
        dept_salaries = salary_structures.values(
            'employee__department__name_ar'
        ).annotate(
            count=Count('id'),
            total_salary=Sum('basic_salary'),
            avg_salary=Avg('basic_salary')
        ).order_by('-avg_salary')
        
        # التوزيع حسب الوظيفة
        position_salaries = salary_structures.values(
            'employee__position__name_ar'
        ).annotate(
            count=Count('id'),
            total_salary=Sum('basic_salary'),
            avg_salary=Avg('basic_salary')
        ).order_by('-avg_salary')
        
        return {
            'total_employees': total_employees,
            'total_basic_salary': float(total_basic_salary),
            'avg_basic_salary': float(avg_basic_salary),
            'department_salaries': [
                {
                    'department': item['employee__department__name_ar'],
                    'count': item['count'],
                    'total_salary': float(item['total_salary'] or 0),
                    'avg_salary': float(item['avg_salary'] or 0)
                }
                for item in dept_salaries
            ],
            'position_salaries': [
                {
                    'position': item['employee__position__name_ar'],
                    'count': item['count'],
                    'total_salary': float(item['total_salary'] or 0),
                    'avg_salary': float(item['avg_salary'] or 0)
                }
                for item in position_salaries
            ]
        }
    
    @staticmethod
    def export_report_to_excel(report_data, report_type):
        """
        تصدير التقرير إلى Excel
        """
        try:
            import pandas as pd
            from io import BytesIO
            
            # إنشاء ملف Excel
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # إضافة البيانات حسب نوع التقرير
                if report_type == 'employee_summary':
                    # ملخص الموظفين
                    summary_df = pd.DataFrame([{
                        'المؤشر': 'إجمالي الموظفين',
                        'القيمة': report_data['total_employees']
                    }, {
                        'المؤشر': 'الموظفين النشطين',
                        'القيمة': report_data['active_employees']
                    }, {
                        'المؤشر': 'الموظفين غير النشطين',
                        'القيمة': report_data['inactive_employees']
                    }])
                    summary_df.to_excel(writer, sheet_name='الملخص', index=False)
                    
                    # التوزيع حسب القسم
                    if report_data['department_distribution']:
                        dept_df = pd.DataFrame(report_data['department_distribution'])
                        dept_df.to_excel(writer, sheet_name='التوزيع حسب القسم', index=False)
                
                elif report_type == 'employee_details':
                    # تفاصيل الموظفين
                    employees_df = pd.DataFrame(report_data['employees'])
                    employees_df.to_excel(writer, sheet_name='تفاصيل الموظفين', index=False)
                
                # يمكن إضافة المزيد من أنواع التقارير هنا
            
            output.seek(0)
            return output.getvalue()
            
        except ImportError:
            raise Exception("مكتبة pandas غير مثبتة. يرجى تثبيتها لتصدير Excel")
        except Exception as e:
            raise Exception(f"خطأ في تصدير Excel: {str(e)}")
    
    @staticmethod
    def export_report_to_pdf(report_data, report_type):
        """
        تصدير التقرير إلى PDF
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from io import BytesIO
            
            # إنشاء ملف PDF
            output = BytesIO()
            doc = SimpleDocTemplate(output, pagesize=A4)
            
            # إعداد الأنماط
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # وسط
            )
            
            # محتوى التقرير
            story = []
            
            # العنوان
            title_map = {
                'employee_summary': 'تقرير ملخص الموظفين',
                'employee_details': 'تقرير تفاصيل الموظفين',
                'org_structure': 'تقرير الهيكل التنظيمي',
                'new_employees': 'تقرير الموظفين الجدد',
                'demographics': 'تقرير التركيبة السكانية',
                'birthdays_anniversaries': 'تقرير أعياد الميلاد والذكريات'
            }
            
            title = title_map.get(report_type, 'تقرير الموظفين')
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
            # إضافة البيانات حسب نوع التقرير
            if report_type == 'employee_summary':
                # جدول الملخص
                summary_data = [
                    ['المؤشر', 'القيمة'],
                    ['إجمالي الموظفين', str(report_data['total_employees'])],
                    ['الموظفين النشطين', str(report_data['active_employees'])],
                    ['الموظفين غير النشطين', str(report_data['inactive_employees'])],
                    ['الموظفين الجدد', str(report_data['new_employees'])]
                ]
                
                summary_table = Table(summary_data)
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(summary_table)
            
            # بناء PDF
            doc.build(story)
            output.seek(0)
            return output.getvalue()
            
        except ImportError:
            raise Exception("مكتبة reportlab غير مثبتة. يرجى تثبيتها لتصدير PDF")
        except Exception as e:
            raise Exception(f"خطأ في تصدير PDF: {str(e)}")