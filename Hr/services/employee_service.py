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
    EmployeeDocument, EmployeeEmergencyContact, EmployeeTraining
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
                if Employee.objects.filter(employee_number=employee_data.get('employee_number')).exists():
                    raise ValidationError("رقم الموظف موجود مسبقاً")
                
                # التحقق من عدم تكرار رقم الهوية
                national_id = employee_data.get('national_id')
                if national_id and Employee.objects.filter(national_id=national_id).exists():
                    raise ValidationError("رقم الهوية موجود مسبقاً")
                
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
        تحديث بيانات الموظف
        """
        try:
            with transaction.atomic():
                employee = Employee.objects.get(id=employee_id)
                
                # التحقق من عدم تكرار رقم الموظف (إذا تم تغييره)
                new_employee_number = employee_data.get('employee_number')
                if (new_employee_number and 
                    new_employee_number != employee.employee_number and
                    Employee.objects.filter(employee_number=new_employee_number).exists()):
                    raise ValidationError("رقم الموظف موجود مسبقاً")
                
                # التحقق من عدم تكرار رقم الهوية (إذا تم تغييره)
                new_national_id = employee_data.get('national_id')
                if (new_national_id and 
                    new_national_id != employee.national_id and
                    Employee.objects.filter(national_id=new_national_id).exists()):
                    raise ValidationError("رقم الهوية موجود مسبقاً")
                
                # تحديث البيانات
                for field, value in employee_data.items():
                    if hasattr(employee, field):
                        setattr(employee, field, value)
                
                employee.save()
                
                logger.info(f"تم تحديث بيانات الموظف: {employee.full_name}")
                return employee
                
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"خطأ في تحديث الموظف: {str(e)}")
            raise
    
    @staticmethod
    def deactivate_employee(employee_id, termination_date=None, termination_reason=None, terminated_by=None):
        """
        إلغاء تفعيل الموظف (إنهاء الخدمة)
        """
        try:
            with transaction.atomic():
                employee = Employee.objects.get(id=employee_id)
                
                employee.employment_status = 'terminated'
                employee.termination_date = termination_date or date.today()
                employee.termination_reason = termination_reason
                employee.is_active = False
                employee.save()
                
                logger.info(f"تم إنهاء خدمة الموظف: {employee.full_name}")
                return employee
                
        except Employee.DoesNotExist:
            raise ValidationError("الموظف غير موجود")
        except Exception as e:
            logger.error(f"خطأ في إنهاء خدمة الموظف: {str(e)}")
            raise
    
    @staticmethod
    def calculate_service_years(employee):
        """
        حساب سنوات الخدمة للموظف
        """
        if not employee.hire_date:
            return 0
        
        end_date = employee.termination_date or date.today()
        service_period = end_date - employee.hire_date
        return round(service_period.days / 365.25, 2)
    
    @staticmethod
    def calculate_age(employee):
        """
        حساب عمر الموظف
        """
        if not employee.date_of_birth:
            return None
        
        today = date.today()
        age = today.year - employee.date_of_birth.year
        
        # تعديل العمر إذا لم يحن عيد الميلاد بعد
        if today.month < employee.date_of_birth.month or \
           (today.month == employee.date_of_birth.month and today.day < employee.date_of_birth.day):
            age -= 1
        
        return age
    
    @staticmethod
    def get_employees_by_department(department_id, include_inactive=False):
        """
        الحصول على موظفي قسم معين
        """
        queryset = Employee.objects.filter(department_id=department_id)
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset.select_related('department', 'job_position', 'manager')
    
    @staticmethod
    def get_employees_by_branch(branch_id, include_inactive=False):
        """
        الحصول على موظفي فرع معين
        """
        queryset = Employee.objects.filter(branch_id=branch_id)
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset.select_related('branch', 'department', 'job_position')
    
    @staticmethod
    def search_employees(search_term, filters=None):
        """
        البحث في الموظفين
        """
        queryset = Employee.objects.all()
        
        if search_term:
            queryset = queryset.filter(
                Q(employee_number__icontains=search_term) |
                Q(full_name__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(national_id__icontains=search_term)
            )
        
        if filters:
            if filters.get('department'):
                queryset = queryset.filter(department_id=filters['department'])
            
            if filters.get('job_position'):
                queryset = queryset.filter(job_position_id=filters['job_position'])
            
            if filters.get('employment_type'):
                queryset = queryset.filter(employment_type=filters['employment_type'])
            
            if filters.get('status'):
                queryset = queryset.filter(employment_status=filters['status'])
            
            if filters.get('hire_date_from'):
                queryset = queryset.filter(hire_date__gte=filters['hire_date_from'])
            
            if filters.get('hire_date_to'):
                queryset = queryset.filter(hire_date__lte=filters['hire_date_to'])
        
        return queryset.select_related('department', 'job_position', 'branch')
    
    @staticmethod
    def get_employee_statistics():
        """
        الحصول على إحصائيات الموظفين
        """
        total_employees = Employee.objects.filter(is_active=True).count()
        
        stats = {
            'total_employees': total_employees,
            'by_department': Employee.objects.filter(is_active=True)
                .values('department__name')
                .annotate(count=Count('id'))
                .order_by('-count'),
            
            'by_employment_type': Employee.objects.filter(is_active=True)
                .values('employment_type')
                .annotate(count=Count('id')),
            
            'by_gender': Employee.objects.filter(is_active=True)
                .values('gender')
                .annotate(count=Count('id')),
            
            'new_hires_this_month': Employee.objects.filter(
                hire_date__year=date.today().year,
                hire_date__month=date.today().month,
                is_active=True
            ).count(),
            
            'probation_employees': Employee.objects.filter(
                employment_status='probation',
                is_active=True
            ).count(),
        }
        
        # حساب متوسط العمر
        employees_with_birth_date = Employee.objects.filter(
            is_active=True,
            date_of_birth__isnull=False
        )
        
        if employees_with_birth_date.exists():
            total_age = sum(EmployeeService.calculate_age(emp) for emp in employees_with_birth_date)
            stats['average_age'] = round(total_age / employees_with_birth_date.count(), 1)
        else:
            stats['average_age'] = 0
        
        return stats
    
    @staticmethod
    def get_upcoming_birthdays(days_ahead=30):
        """
        الحصول على أعياد الميلاد القادمة
        """
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        employees = Employee.objects.filter(
            is_active=True,
            date_of_birth__isnull=False
        )
        
        upcoming_birthdays = []
        
        for employee in employees:
            # حساب عيد الميلاد لهذا العام
            birthday_this_year = employee.date_of_birth.replace(year=today.year)
            
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
                    'age_turning': today.year - employee.date_of_birth.year
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
            is_active=True,
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
    def export_employee_data(employee_ids=None, format='csv'):
        """
        تصدير بيانات الموظفين
        """
        queryset = Employee.objects.all()
        
        if employee_ids:
            queryset = queryset.filter(id__in=employee_ids)
        
        queryset = queryset.select_related('department', 'job_position', 'branch')
        
        # سيتم تنفيذ منطق التصدير هنا
        # يمكن استخدام pandas أو csv module
        
        return queryset
    
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