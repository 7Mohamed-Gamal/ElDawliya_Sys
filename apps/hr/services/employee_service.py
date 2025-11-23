"""
خدمة إدارة الموظفين
Employee Management Service
"""
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from core.services.base import BaseService
from core.models.hr import Employee, Department, JobPosition, EmployeeDocument


class EmployeeService(BaseService):
    """
    خدمة إدارة جميع عمليات الموظفين
    Comprehensive employee management service
    """
    
    def create_employee(self, data):
        """
        إنشاء موظف جديد
        Create new employee with full validation
        """
        self.check_permission('hr.add_employee')
        
        required_fields = ['first_name', 'last_name', 'emp_code', 'department_id', 'job_position_id']
        self.validate_required_fields(data, required_fields)
        
        try:
            with transaction.atomic():
                # Check if employee code already exists
                if Employee.objects.filter(emp_code=data['emp_code']).exists():
                    return self.format_response(
                        success=False,
                        message=f"رقم الموظف {data['emp_code']} موجود بالفعل"
                    )
                
                # Validate department and job position
                department = Department.objects.get(id=data['department_id'])
                job_position = JobPosition.objects.get(id=data['job_position_id'])
                
                # Create employee
                employee_data = self.clean_data(data, [
                    'first_name', 'last_name', 'emp_code', 'email', 'phone',
                    'hire_date', 'birth_date', 'national_id', 'passport_number',
                    'address', 'emergency_contact', 'emergency_phone', 'gender',
                    'marital_status', 'nationality', 'religion', 'blood_type'
                ])
                
                employee = Employee.objects.create(
                    department=department,
                    job_position=job_position,
                    manager_id=data.get('manager_id'),
                    **employee_data,
                    created_by=self.user,
                    updated_by=self.user
                )
                
                # Create user account if requested
                if data.get('create_user_account'):
                    user_account = self._create_user_account(employee, data.get('user_data', {}))
                    employee.user = user_account
                    employee.save()
                
                # Add employee documents if provided
                if data.get('documents'):
                    self._add_employee_documents(employee, data['documents'])
                
                # Log the action
                self.log_action(
                    action='create',
                    resource='employee',
                    content_object=employee,
                    new_values=employee_data,
                    message=f'تم إنشاء موظف جديد: {employee.get_full_name()}'
                )
                
                # Send welcome notification
                if employee.email:
                    self._send_welcome_notification(employee)
                
                return self.format_response(
                    data={
                        'employee_id': employee.id,
                        'emp_code': employee.emp_code,
                        'full_name': employee.get_full_name()
                    },
                    message='تم إنشاء الموظف بنجاح'
                )
                
        except Department.DoesNotExist:
            return self.format_response(
                success=False,
                message='القسم المحدد غير موجود'
            )
        except JobPosition.DoesNotExist:
            return self.format_response(
                success=False,
                message='المنصب الوظيفي المحدد غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'create_employee', 'employee', data)
    
    def update_employee(self, employee_id, data):
        """
        تحديث بيانات الموظف
        Update employee information
        """
        self.check_permission('hr.change_employee')
        
        try:
            employee = Employee.objects.get(id=employee_id)
            
            # Check object-level permission
            self.check_object_permission('hr.change_employee', employee)
            
            # Get old values for audit
            old_values, new_values = self.get_model_changes(employee, data)
            
            # Update employee data
            allowed_fields = [
                'first_name', 'last_name', 'email', 'phone', 'address',
                'emergency_contact', 'emergency_phone', 'department_id',
                'job_position_id', 'manager_id', 'emp_status'
            ]
            
            for field, value in data.items():
                if field in allowed_fields and hasattr(employee, field):
                    setattr(employee, field, value)
            
            employee.updated_by = self.user
            employee.save()
            
            # Log the action
            self.log_action(
                action='update',
                resource='employee',
                content_object=employee,
                old_values=old_values,
                new_values=new_values,
                message=f'تم تحديث بيانات الموظف: {employee.get_full_name()}'
            )
            
            # Invalidate cache
            self.invalidate_cache(f'employee_{employee_id}_*')
            
            return self.format_response(
                data={
                    'employee_id': employee.id,
                    'updated_fields': list(new_values.keys())
                },
                message='تم تحديث بيانات الموظف بنجاح'
            )
            
        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'update_employee', f'employee/{employee_id}', data)
    
    def get_employee(self, employee_id, include_relations=True):
        """
        الحصول على بيانات الموظف
        Get employee details
        """
        self.check_permission('hr.view_employee')
        
        try:
            cache_key = self.cache_key('employee', employee_id, 'details')
            
            def get_employee_data():
                queryset = Employee.objects.select_related(
                    'department', 'job_position', 'manager', 'user'
                )
                
                if include_relations:
                    queryset = queryset.prefetch_related(
                        'documents', 'salary_records', 'attendance_records'
                    )
                
                employee = queryset.get(id=employee_id)
                
                # Check object-level permission
                self.check_object_permission('hr.view_employee', employee)
                
                return {
                    'id': employee.id,
                    'emp_code': employee.emp_code,
                    'first_name': employee.first_name,
                    'last_name': employee.last_name,
                    'full_name': employee.get_full_name(),
                    'email': employee.email,
                    'phone': employee.phone,
                    'hire_date': employee.hire_date,
                    'birth_date': employee.birth_date,
                    'department': {
                        'id': employee.department.id,
                        'name': employee.department.name,
                        'name_ar': employee.department.name_ar,
                    } if employee.department else None,
                    'job_position': {
                        'id': employee.job_position.id,
                        'title': employee.job_position.title,
                        'title_ar': employee.job_position.title_ar,
                    } if employee.job_position else None,
                    'manager': {
                        'id': employee.manager.id,
                        'name': employee.manager.get_full_name(),
                    } if employee.manager else None,
                    'emp_status': employee.emp_status,
                    'service_years': self.calculate_service_years(employee),
                    'is_active': employee.is_active,
                }
            
            employee_data = self.get_from_cache(cache_key)
            if not employee_data:
                employee_data = get_employee_data()
                self.set_cache(cache_key, employee_data, 300)  # 5 minutes
            
            return self.format_response(
                data=employee_data,
                message='تم الحصول على بيانات الموظف بنجاح'
            )
            
        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_employee', f'employee/{employee_id}')
    
    def search_employees(self, filters=None, page=1, page_size=20):
        """
        البحث في الموظفين
        Search employees with filters
        """
        self.check_permission('hr.view_employee')
        
        try:
            queryset = Employee.objects.select_related(
                'department', 'job_position', 'manager'
            ).filter(is_active=True)
            
            # Apply filters
            if filters:
                if filters.get('department_id'):
                    queryset = queryset.filter(department_id=filters['department_id'])
                
                if filters.get('job_position_id'):
                    queryset = queryset.filter(job_position_id=filters['job_position_id'])
                
                if filters.get('emp_status'):
                    queryset = queryset.filter(emp_status=filters['emp_status'])
                
                if filters.get('search_term'):
                    term = filters['search_term']
                    queryset = queryset.filter(
                        Q(first_name__icontains=term) |
                        Q(last_name__icontains=term) |
                        Q(emp_code__icontains=term) |
                        Q(email__icontains=term)
                    )
                
                if filters.get('hire_date_from'):
                    queryset = queryset.filter(hire_date__gte=filters['hire_date_from'])
                
                if filters.get('hire_date_to'):
                    queryset = queryset.filter(hire_date__lte=filters['hire_date_to'])
            
            # Apply user-level filtering if not admin
            if not self.user.is_superuser and not self.user.has_perm('hr.view_all_employees'):
                # Show only employees from same department
                user_employee = getattr(self.user, 'employee', None)
                if user_employee and user_employee.department:
                    queryset = queryset.filter(department=user_employee.department)
            
            # Order by name
            queryset = queryset.order_by('first_name', 'last_name')
            
            # Paginate results
            paginated_data = self.paginate_queryset(queryset, page, page_size)
            
            # Format employee data
            employees = []
            for emp in paginated_data['results']:
                employees.append({
                    'id': emp.id,
                    'emp_code': emp.emp_code,
                    'full_name': emp.get_full_name(),
                    'email': emp.email,
                    'phone': emp.phone,
                    'department': emp.department.name_ar if emp.department else '',
                    'job_position': emp.job_position.title_ar if emp.job_position else '',
                    'hire_date': emp.hire_date,
                    'emp_status': emp.emp_status,
                    'service_years': self.calculate_service_years(emp),
                })
            
            paginated_data['results'] = employees
            
            return self.format_response(
                data=paginated_data,
                message='تم البحث في الموظفين بنجاح'
            )
            
        except Exception as e:
            return self.handle_exception(e, 'search_employees', 'employees', filters)
    
    def calculate_service_years(self, employee):
        """
        حساب سنوات الخدمة
        Calculate employee service years
        """
        if not employee.hire_date:
            return 0
        
        today = date.today()
        service_period = today - employee.hire_date
        return round(service_period.days / 365.25, 1)
    
    def get_department_employees(self, department_id, include_inactive=False):
        """
        الحصول على موظفي القسم
        Get department employees
        """
        self.check_permission('hr.view_employee')
        
        try:
            cache_key = self.cache_key('department', department_id, 'employees', include_inactive)
            
            def get_employees():
                queryset = Employee.objects.filter(department_id=department_id)
                
                if not include_inactive:
                    queryset = queryset.filter(is_active=True)
                
                return list(queryset.select_related('job_position').values(
                    'id', 'emp_code', 'first_name', 'last_name', 'email',
                    'job_position__title_ar', 'emp_status', 'hire_date'
                ))
            
            employees = self.get_from_cache(cache_key)
            if employees is None:
                employees = get_employees()
                self.set_cache(cache_key, employees, 600)  # 10 minutes
            
            return self.format_response(
                data=employees,
                message='تم الحصول على موظفي القسم بنجاح'
            )
            
        except Exception as e:
            return self.handle_exception(e, 'get_department_employees', f'department/{department_id}')
    
    def deactivate_employee(self, employee_id, reason=None, last_working_day=None):
        """
        إلغاء تفعيل الموظف
        Deactivate employee (termination)
        """
        self.check_permission('hr.change_employee')
        
        try:
            employee = Employee.objects.get(id=employee_id)
            
            # Check object-level permission
            self.check_object_permission('hr.change_employee', employee)
            
            if not employee.is_active:
                return self.format_response(
                    success=False,
                    message='الموظف غير مفعل بالفعل'
                )
            
            with transaction.atomic():
                # Update employee status
                employee.is_active = False
                employee.emp_status = 'terminated'
                employee.termination_date = last_working_day or timezone.now().date()
                employee.termination_reason = reason
                employee.updated_by = self.user
                employee.save()
                
                # Deactivate user account if exists
                if employee.user:
                    employee.user.is_active = False
                    employee.user.save()
                
                # Log the action
                self.log_action(
                    action='update',
                    resource='employee_deactivation',
                    content_object=employee,
                    details={
                        'reason': reason,
                        'last_working_day': last_working_day.isoformat() if last_working_day else None
                    },
                    message=f'تم إلغاء تفعيل الموظف: {employee.get_full_name()}'
                )
                
                # Send notification
                if employee.email:
                    self._send_termination_notification(employee, reason)
                
                # Invalidate cache
                self.invalidate_cache(f'employee_{employee_id}_*')
                self.invalidate_cache(f'department_{employee.department_id}_employees_*')
            
            return self.format_response(
                message='تم إلغاء تفعيل الموظف بنجاح'
            )
            
        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'deactivate_employee', f'employee/{employee_id}', {
                'reason': reason,
                'last_working_day': last_working_day
            })
    
    def get_employee_summary(self, department_id=None):
        """
        الحصول على ملخص الموظفين
        Get employee summary statistics
        """
        self.check_permission('hr.view_employee')
        
        try:
            from django.db.models import Count, Q
            
            cache_key = self.cache_key('employees', 'summary', department_id or 'all')
            
            def get_summary():
                queryset = Employee.objects.all()
                
                if department_id:
                    queryset = queryset.filter(department_id=department_id)
                
                summary = queryset.aggregate(
                    total_employees=Count('id'),
                    active_employees=Count('id', filter=Q(is_active=True)),
                    inactive_employees=Count('id', filter=Q(is_active=False)),
                    male_employees=Count('id', filter=Q(gender='male', is_active=True)),
                    female_employees=Count('id', filter=Q(gender='female', is_active=True)),
                )
                
                # Get status breakdown
                status_breakdown = queryset.filter(is_active=True).values('emp_status').annotate(
                    count=Count('id')
                ).order_by('emp_status')
                
                summary['status_breakdown'] = list(status_breakdown)
                
                return summary
            
            summary = self.get_from_cache(cache_key)
            if summary is None:
                summary = get_summary()
                self.set_cache(cache_key, summary, 1800)  # 30 minutes
            
            return self.format_response(
                data=summary,
                message='تم الحصول على ملخص الموظفين بنجاح'
            )
            
        except Exception as e:
            return self.handle_exception(e, 'get_employee_summary', 'employees_summary')
    
    def _create_user_account(self, employee, user_data):
        """إنشاء حساب مستخدم للموظف"""
        username = user_data.get('username') or employee.emp_code
        email = user_data.get('email') or employee.email
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            username = f"{employee.emp_code}_{employee.id}"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=employee.first_name,
            last_name=employee.last_name,
            password=user_data.get('password', 'temp123456'),
            is_active=True
        )
        
        return user
    
    def _add_employee_documents(self, employee, documents):
        """إضافة وثائق الموظف"""
        for doc_data in documents:
            EmployeeDocument.objects.create(
                employee=employee,
                document_type=doc_data['document_type'],
                document_number=doc_data.get('document_number'),
                issue_date=doc_data.get('issue_date'),
                expiry_date=doc_data.get('expiry_date'),
                issuing_authority=doc_data.get('issuing_authority'),
                file_path=doc_data.get('file_path'),
                created_by=self.user,
                updated_by=self.user
            )
    
    def _send_welcome_notification(self, employee):
        """إرسال إشعار ترحيب للموظف الجديد"""
        try:
            self.send_notification(
                recipient=employee.user if employee.user else employee,
                template_name='employee_welcome',
                context={
                    'employee': employee,
                    'department': employee.department,
                    'job_position': employee.job_position,
                },
                channels=['email'] if employee.email else []
            )
        except Exception as e:
            self.logger.warning(f"Failed to send welcome notification: {e}")
    
    def _send_termination_notification(self, employee, reason):
        """إرسال إشعار إنهاء الخدمة"""
        try:
            self.send_notification(
                recipient=employee.user if employee.user else employee,
                template_name='employee_termination',
                context={
                    'employee': employee,
                    'reason': reason,
                    'termination_date': employee.termination_date,
                },
                channels=['email'] if employee.email else []
            )
        except Exception as e:
            self.logger.warning(f"Failed to send termination notification: {e}")