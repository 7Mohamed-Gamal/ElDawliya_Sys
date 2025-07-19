# -*- coding: utf-8 -*-
"""
Employee Service for HRMS
Handles employee business logic and operations
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from Hr.models import (
    Employee, Company, Branch, Department, JobPosition,
    EmployeeDocument, 
    # EmployeeEmergencyContact, EmployeeTraining  # Temporarily commented out
)

logger = logging.getLogger(__name__)


class EmployeeService:
    """
    خدمة إدارة الموظفين - تحتوي على منطق العمل الخاص بالموظفين
    """
    
    @staticmethod
    def create_employee(employee_data, created_by=None):
        """
        إنشاء موظف جديد مع التحقق من صحة البيانات
        """
        try:
            with transaction.atomic():
                # التحقق من عدم تكرار رقم الموظف
                employee_number = employee_data.get('employee_number')
                if employee_number and Employee.objects.filter(employee_number=employee_number).exists():
                    raise ValidationError("رقم الموظف موجود مسبقاً")
                
                # التحقق من عدم تكرار رقم الهوية
                national_id = employee_data.get('national_id')
                if national_id and Employee.objects.filter(national_id=national_id).exists():
                    raise ValidationError("رقم الهوية موجود مسبقاً")
                
                # التحقق من عدم تكرار البريد الإلكتروني
                email = employee_data.get('email')
                if email and Employee.objects.filter(email=email).exists():
                    raise ValidationError("البريد الإلكتروني موجود مسبقاً")
                
                # إضافة معلومات الإنشاء
                if created_by:
                    employee_data['created_by'] = created_by
                
                # إنشاء الموظف
                employee = Employee.objects.create(**employee_data)
                
                logger.info(f"تم إنشاء موظف جديد: {employee.full_name} ({employee.employee_number})")
                return employee
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء الموظف: {str(e)}")
            raise
    
    @staticmethod
    def update_employee(employee_id, employee_data, updated_by=None):
        """
        تحديث بيانات موظف
        """
        try:
            with transaction.atomic():
                employee = Employee.objects.get(id=employee_id)
                
                # التحقق من عدم تكرار رقم الموظف (إذا تم تغييره)
                new_employee_number = employee_data.get('employee_number')
                if (new_employee_number and new_employee_number != employee.employee_number and
                    Employee.objects.filter(employee_number=new_employee_number).exists()):
                    raise ValidationError("رقم الموظف موجود مسبقاً")
                
                # التحقق من عدم تكرار رقم الهوية (إذا تم تغييره)
                new_national_id = employee_data.get('national_id')
                if (new_national_id and new_national_id != employee.national_id and
                    Employee.objects.filter(national_id=new_national_id).exists()):
                    raise ValidationError("رقم الهوية موجود مسبقاً")
                
                # التحقق من عدم تكرار البريد الإلكتروني (إذا تم تغييره)
                new_email = employee_data.get('email')
                if (new_email and new_email != employee.email and
                    Employee.objects.filter(email=new_email).exists()):
                    raise ValidationError("البريد الإلكتروني موجود مسبقاً")
                
                # تحديث البيانات
                for field, value in employee_data.items():
                    if hasattr(employee, field):
                        setattr(employee, field, value)
                
                employee.save()
                
                logger.info(f"تم تحديث بيانات الموظف: {employee.full_name} ({employee.employee_number})")
                return employee
                
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"خطأ في تحديث الموظف: {str(e)}")
            raise
    
    @staticmethod
    def get_employee_by_id(employee_id):
        """
        الحصول على موظف بالمعرف
        """
        try:
            return Employee.objects.select_related(
                'company', 'branch', 'department', 'job_position', 'manager'
            ).get(id=employee_id)
        except Employee.DoesNotExist:
            return None
    
    @staticmethod
    def get_employee_by_number(employee_number):
        """
        الحصول على موظف برقم الموظف
        """
        try:
            return Employee.objects.select_related(
                'company', 'branch', 'department', 'job_position', 'manager'
            ).get(employee_number=employee_number)
        except Employee.DoesNotExist:
            return None
    
    @staticmethod
    def search_employees(search_term, company_id=None, department_id=None, status=None):
        """
        البحث عن الموظفين
        """
        queryset = Employee.objects.select_related(
            'company', 'branch', 'department', 'job_position', 'manager'
        )
        
        # تطبيق الفلاتر
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        # البحث النصي
        if search_term:
            queryset = queryset.filter(
                Q(first_name__icontains=search_term) |
                Q(middle_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(full_name__icontains=search_term) |
                Q(employee_number__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(national_id__icontains=search_term)
            )
        
        return queryset.order_by('employee_number')
    
    @staticmethod
    def get_employees_by_department(department_id, include_subdepartments=False):
        """
        الحصول على موظفي قسم معين
        """
        queryset = Employee.objects.filter(
            department_id=department_id,
            status='active'
        ).select_related('job_position', 'manager')
        
        if include_subdepartments:
            # إضافة موظفي الأقسام الفرعية
            department = Department.objects.get(id=department_id)
            sub_departments = department.get_all_children()
            sub_dept_ids = [dept.id for dept in sub_departments]
            
            if sub_dept_ids:
                queryset = queryset | Employee.objects.filter(
                    department_id__in=sub_dept_ids,
                    status='active'
                ).select_related('job_position', 'manager')
        
        return queryset.order_by('employee_number')
    
    @staticmethod
    def get_employee_hierarchy(employee_id):
        """
        الحصول على الهيكل التنظيمي للموظف (المدير والمرؤوسين)
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            
            # الحصول على المدير المباشر
            manager = employee.manager
            
            # الحصول على المرؤوسين المباشرين
            direct_reports = employee.get_direct_reports()
            
            # الحصول على جميع المرؤوسين
            all_subordinates = employee.get_all_subordinates()
            
            return {
                'employee': employee,
                'manager': manager,
                'direct_reports': direct_reports,
                'all_subordinates': all_subordinates,
                'reports_count': len(direct_reports),
                'subordinates_count': len(all_subordinates)
            }
            
        except Employee.DoesNotExist:
            return None
    
    @staticmethod
    def calculate_service_years(employee_id):
        """
        حساب سنوات الخدمة للموظف
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            return employee.years_of_service
        except Employee.DoesNotExist:
            return None
    
    @staticmethod
    def get_employees_statistics(company_id=None):
        """
        الحصول على إحصائيات الموظفين
        """
        queryset = Employee.objects.all()
        
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # إحصائيات عامة
        total_employees = queryset.count()
        active_employees = queryset.filter(status='active').count()
        inactive_employees = queryset.filter(status='inactive').count()
        on_leave_employees = queryset.filter(status='on_leave').count()
        
        # إحصائيات حسب الجنس
        male_employees = queryset.filter(gender='male').count()
        female_employees = queryset.filter(gender='female').count()
        
        # إحصائيات حسب نوع التوظيف
        full_time = queryset.filter(employment_type='full_time').count()
        part_time = queryset.filter(employment_type='part_time').count()
        contract = queryset.filter(employment_type='contract').count()
        
        # متوسط سنوات الخدمة
        today = date.today()
        employees_with_hire_date = queryset.filter(hire_date__isnull=False)
        
        if employees_with_hire_date.exists():
            total_service_years = sum([
                (today - emp.hire_date).days / 365.25
                for emp in employees_with_hire_date
            ])
            avg_service_years = total_service_years / employees_with_hire_date.count()
        else:
            avg_service_years = 0
        
        return {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': inactive_employees,
            'on_leave_employees': on_leave_employees,
            'male_employees': male_employees,
            'female_employees': female_employees,
            'full_time_employees': full_time,
            'part_time_employees': part_time,
            'contract_employees': contract,
            'average_service_years': round(avg_service_years, 2)
        }
    
    @staticmethod
    def terminate_employee(employee_id, termination_date=None, reason=None, terminated_by=None):
        """
        إنهاء خدمة موظف
        """
        try:
            with transaction.atomic():
                employee = Employee.objects.get(id=employee_id)
                
                if employee.status == 'terminated':
                    raise ValidationError("الموظف منتهي الخدمة مسبقاً")
                
                # تحديث حالة الموظف
                employee.status = 'terminated'
                employee.termination_date = termination_date or date.today()
                
                # إضافة ملاحظة عن سبب الإنهاء
                if reason:
                    current_notes = employee.notes or ""
                    termination_note = f"\nتم إنهاء الخدمة في {employee.termination_date}: {reason}"
                    employee.notes = current_notes + termination_note
                
                employee.save()
                
                logger.info(f"تم إنهاء خدمة الموظف: {employee.full_name} ({employee.employee_number})")
                return employee
                
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"خطأ في إنهاء خدمة الموظف: {str(e)}")
            raise
    
    @staticmethod
    def reactivate_employee(employee_id, reactivated_by=None):
        """
        إعادة تفعيل موظف
        """
        try:
            with transaction.atomic():
                employee = Employee.objects.get(id=employee_id)
                
                if employee.status == 'active':
                    raise ValidationError("الموظف نشط بالفعل")
                
                # تحديث حالة الموظف
                employee.status = 'active'
                employee.termination_date = None
                
                # إضافة ملاحظة عن إعادة التفعيل
                current_notes = employee.notes or ""
                reactivation_note = f"\nتم إعادة تفعيل الموظف في {date.today()}"
                employee.notes = current_notes + reactivation_note
                
                employee.save()
                
                logger.info(f"تم إعادة تفعيل الموظف: {employee.full_name} ({employee.employee_number})")
                return employee
                
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"خطأ في إعادة تفعيل الموظف: {str(e)}")
            raise
    
    @staticmethod
    def export_employees_data(company_id=None, department_id=None, format='csv'):
        """
        تصدير بيانات الموظفين
        """
        queryset = Employee.objects.select_related(
            'company', 'branch', 'department', 'job_position'
        )
        
        # تطبيق الفلاتر
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # إعداد البيانات للتصدير
        export_data = []
        for employee in queryset:
            export_data.append({
                'employee_number': employee.employee_number,
                'full_name': employee.full_name,
                'email': employee.email,
                'phone': employee.phone,
                'mobile': employee.mobile,
                'company': employee.company.name if employee.company else '',
                'branch': employee.branch.name if employee.branch else '',
                'department': employee.department.name if employee.department else '',
                'job_position': employee.job_position.title if employee.job_position else '',
                'hire_date': employee.hire_date,
                'employment_type': employee.get_employment_type_display(),
                'status': employee.get_status_display(),
                'basic_salary': employee.basic_salary,
                'years_of_service': employee.years_of_service,
            })
        
        return export_data
    
    @staticmethod
    def get_upcoming_birthdays(days_ahead=30):
        """
        الحصول على أعياد الميلاد القادمة
        """
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        employees = Employee.objects.filter(
            status='active',
            birth_date__isnull=False
        )
        
        upcoming_birthdays = []
        
        for employee in employees:
            # حساب عيد الميلاد لهذا العام
            birthday_this_year = employee.birth_date.replace(year=today.year)
            
            # إذا فات عيد الميلاد هذا العام، احسب للعام القادم
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            
            # إذا كان عيد الميلاد خلال الفترة المحددة
            if today <= birthday_this_year <= end_date:
                days_until = (birthday_this_year - today).days
                upcoming_birthdays.append({
                    'employee': employee,
                    'birthday': birthday_this_year,
                    'days_until': days_until,
                    'age_turning': today.year - employee.birth_date.year
                })
        
        return sorted(upcoming_birthdays, key=lambda x: x['days_until'])
    
    @staticmethod
    def get_work_anniversaries(days_ahead=30):
        """
        الحصول على ذكريات التوظيف القادمة
        """
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        employees = Employee.objects.filter(
            status='active',
            hire_date__isnull=False
        )
        
        anniversaries = []
        
        for employee in employees:
            # حساب ذكرى التوظيف لهذا العام
            anniversary_this_year = employee.hire_date.replace(year=today.year)
            
            # إذا فاتت الذكرى هذا العام، احسب للعام القادم
            if anniversary_this_year < today:
                anniversary_this_year = anniversary_this_year.replace(year=today.year + 1)
            
            # إذا كانت الذكرى خلال الفترة المحددة
            if today <= anniversary_this_year <= end_date:
                days_until = (anniversary_this_year - today).days
                years_of_service = today.year - employee.hire_date.year
                
                anniversaries.append({
                    'employee': employee,
                    'anniversary': anniversary_this_year,
                    'days_until': days_until,
                    'years_of_service': years_of_service
                })
        
        return sorted(anniversaries, key=lambda x: x['days_until'])
    
    @staticmethod
    def bulk_update_employees(employee_updates, updated_by=None):
        """
        تحديث مجمع للموظفين
        """
        try:
            with transaction.atomic():
                updated_count = 0
                
                for employee_id, update_data in employee_updates.items():
                    try:
                        employee = Employee.objects.get(id=employee_id)
                        
                        for field, value in update_data.items():
                            if hasattr(employee, field):
                                setattr(employee, field, value)
                        
                        employee.save()
                        updated_count += 1
                        
                    except Employee.DoesNotExist:
                        logger.warning(f"الموظف غير موجود: {employee_id}")
                        continue
                
                logger.info(f"تم تحديث {updated_count} موظف بنجاح")
                return updated_count
                
        except Exception as e:
            logger.error(f"خطأ في التحديث المجمع: {str(e)}")
            raise