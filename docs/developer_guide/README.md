# دليل المطور - نظام الدولية

## نظرة عامة

هذا الدليل مخصص للمطورين الذين يعملون على تطوير وصيانة نظام الدولية. يغطي هيكل المشروع، معايير البرمجة، وأفضل الممارسات.

## 🏗️ هيكل المشروع

### التنظيم العام
```
ElDawliya_sys/
├── core/                          # الوحدة الأساسية المشتركة
├── apps/                          # تطبيقات النظام
├── api/                           # واجهات برمجة التطبيقات
├── frontend/                      # الواجهة الأمامية
├── config/                        # إعدادات التكوين
├── docs/                          # التوثيق
├── tests/                         # الاختبارات
├── requirements/                  # متطلبات المشروع
└── deployment/                    # ملفات النشر
```

### الوحدة الأساسية (Core)
```python
# core/models/base.py
from django.db import models
import uuid

class BaseModel(models.Model):
    """النموذج الأساسي المشترك لجميع النماذج"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    class Meta:
        abstract = True
        ordering = ['-created_at']

class AuditableModel(BaseModel):
    """نموذج قابل للمراجعة مع تتبع المستخدم"""
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='%(class)s_created',
        verbose_name='أنشأ بواسطة'
    )
    updated_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='%(class)s_updated',
        verbose_name='حدث بواسطة'
    )
    
    class Meta:
        abstract = True
```

### خدمات الأعمال (Business Services)
```python
# core/services/base.py
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
import logging

class BaseService:
    """الخدمة الأساسية المشتركة"""
    
    def __init__(self, user=None):
        self.user = user
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_permissions(self, permission, obj=None):
        """التحقق من الصلاحيات"""
        if not self.user or not self.user.has_perm(permission, obj):
            raise PermissionDenied(f"ليس لديك صلاحية {permission}")
    
    def log_action(self, action, obj=None, details=None):
        """تسجيل العمليات"""
        from core.models import AuditLog
        AuditLog.objects.create(
            user=self.user,
            action=action,
            content_object=obj,
            details=details or {}
        )
    
    @transaction.atomic
    def create_with_audit(self, model_class, data, permission=None):
        """إنشاء كائن مع التدقيق"""
        if permission:
            self.validate_permissions(permission)
        
        # إضافة معلومات المستخدم
        if hasattr(model_class, 'created_by'):
            data['created_by'] = self.user
        
        instance = model_class.objects.create(**data)
        self.log_action('create', instance)
        
        return instance
    
    @transaction.atomic
    def update_with_audit(self, instance, data, permission=None):
        """تحديث كائن مع التدقيق"""
        if permission:
            self.validate_permissions(permission, instance)
        
        # حفظ القيم القديمة للمقارنة
        old_values = {}
        for field in data.keys():
            if hasattr(instance, field):
                old_values[field] = getattr(instance, field)
        
        # تطبيق التحديثات
        for field, value in data.items():
            setattr(instance, field, value)
        
        if hasattr(instance, 'updated_by'):
            instance.updated_by = self.user
        
        instance.save()
        
        # تسجيل التغييرات
        changes = {
            field: {'old': old_values.get(field), 'new': value}
            for field, value in data.items()
            if old_values.get(field) != value
        }
        
        if changes:
            self.log_action('update', instance, {'changes': changes})
        
        return instance
```

## 🎨 معايير البرمجة

### تسمية الملفات والمتغيرات

#### Python
```python
# أسماء الكلاسات - PascalCase
class EmployeeService:
    pass

class HRManager:
    pass

# أسماء الدوال والمتغيرات - snake_case
def calculate_salary(employee_id):
    basic_salary = 5000
    total_allowances = 1000
    return basic_salary + total_allowances

# الثوابت - UPPER_CASE
MAX_EMPLOYEES_PER_DEPARTMENT = 100
DEFAULT_CURRENCY = 'SAR'
```

#### JavaScript
```javascript
// أسماء المتغيرات والدوال - camelCase
const employeeData = {
    firstName: 'أحمد',
    lastName: 'محمد'
};

function calculateTotalSalary(basicSalary, allowances) {
    return basicSalary + allowances;
}

// أسماء الكلاسات - PascalCase
class EmployeeManager {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
    }
}

// الثوابت - UPPER_CASE
const API_BASE_URL = '/api/v1/';
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
```

### هيكل النماذج (Models)

```python
# apps/hr/models/employee.py
from django.db import models
from core.models import AuditableModel

class Employee(AuditableModel):
    """نموذج الموظف"""
    
    # الحقول الأساسية
    emp_code = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='رقم الموظف',
        help_text='رقم فريد لكل موظف'
    )
    first_name = models.CharField(max_length=50, verbose_name='الاسم الأول')
    last_name = models.CharField(max_length=50, verbose_name='الاسم الأخير')
    
    # معلومات الاتصال
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    phone = models.CharField(max_length=20, verbose_name='رقم الهاتف')
    
    # معلومات العمل
    department = models.ForeignKey(
        'Department',
        on_delete=models.PROTECT,
        related_name='employees',
        verbose_name='القسم'
    )
    job_position = models.ForeignKey(
        'JobPosition',
        on_delete=models.PROTECT,
        related_name='employees',
        verbose_name='المنصب'
    )
    hire_date = models.DateField(verbose_name='تاريخ التوظيف')
    
    class Meta:
        verbose_name = 'موظف'
        verbose_name_plural = 'الموظفين'
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['emp_code']),
            models.Index(fields=['department', 'is_active']),
            models.Index(fields=['hire_date']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.emp_code})"
    
    @property
    def full_name(self):
        """الاسم الكامل"""
        return f"{self.first_name} {self.last_name}"
    
    def get_service_years(self):
        """حساب سنوات الخدمة"""
        from datetime import date
        if not self.hire_date:
            return 0
        
        today = date.today()
        service_period = today - self.hire_date
        return round(service_period.days / 365.25, 1)
    
    def clean(self):
        """التحقق من صحة البيانات"""
        from django.core.exceptions import ValidationError
        from datetime import date
        
        if self.hire_date and self.hire_date > date.today():
            raise ValidationError({
                'hire_date': 'تاريخ التوظيف لا يمكن أن يكون في المستقبل'
            })
    
    def save(self, *args, **kwargs):
        """حفظ مخصص مع التحقق"""
        self.full_clean()
        super().save(*args, **kwargs)
```

### هيكل العروض (Views)

```python
# apps/hr/views/employee_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ..models import Employee, Department, JobPosition
from ..forms import EmployeeForm
from ..services import EmployeeService

@login_required
@permission_required('hr.view_employee', raise_exception=True)
def employee_list(request):
    """قائمة الموظفين مع البحث والفلترة"""
    
    # الحصول على معاملات البحث والفلترة
    search_query = request.GET.get('search', '')
    department_id = request.GET.get('department', '')
    is_active = request.GET.get('is_active', '')
    
    # بناء الاستعلام
    employees = Employee.objects.select_related('department', 'job_position')
    
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(emp_code__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    if is_active:
        employees = employees.filter(is_active=is_active == 'true')
    
    # ترتيب النتائج
    sort_by = request.GET.get('sort', 'first_name')
    if sort_by in ['first_name', 'last_name', 'emp_code', 'hire_date', 'created_at']:
        employees = employees.order_by(sort_by)
    
    # تقسيم الصفحات
    paginator = Paginator(employees, 20)  # 20 موظف في كل صفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # البيانات الإضافية للقالب
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'departments': departments,
        'search_query': search_query,
        'selected_department': department_id,
        'selected_is_active': is_active,
        'sort_by': sort_by,
    }
    
    return render(request, 'hr/employees/list.html', context)

@login_required
@permission_required('hr.add_employee', raise_exception=True)
def employee_create(request):
    """إضافة موظف جديد"""
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                service = EmployeeService(user=request.user)
                employee = service.create_employee(form.cleaned_data)
                
                messages.success(request, f'تم إضافة الموظف {employee.full_name} بنجاح')
                return redirect('hr:employee_detail', pk=employee.pk)
                
            except Exception as e:
                messages.error(request, f'حدث خطأ: {str(e)}')
    else:
        form = EmployeeForm()
    
    context = {
        'form': form,
        'title': 'إضافة موظف جديد',
        'departments': Department.objects.filter(is_active=True),
        'job_positions': JobPosition.objects.filter(is_active=True),
    }
    
    return render(request, 'hr/employees/form.html', context)

@login_required
@permission_required('hr.view_employee', raise_exception=True)
def employee_detail(request, pk):
    """تفاصيل الموظف"""
    
    employee = get_object_or_404(
        Employee.objects.select_related('department', 'job_position'),
        pk=pk
    )
    
    # التحقق من الصلاحيات - يمكن للموظف رؤية بياناته الشخصية
    if not request.user.has_perm('hr.view_all_employees'):
        if not hasattr(request.user, 'employee') or request.user.employee != employee:
            messages.error(request, 'ليس لديك صلاحية لعرض هذه البيانات')
            return redirect('hr:employee_list')
    
    # حساب الإحصائيات
    service_years = employee.get_service_years()
    
    # آخر سجلات الحضور
    recent_attendance = employee.attendance_records.order_by('-attendance_date')[:10]
    
    context = {
        'employee': employee,
        'service_years': service_years,
        'recent_attendance': recent_attendance,
    }
    
    return render(request, 'hr/employees/detail.html', context)

@login_required
@require_http_methods(["POST"])
def employee_toggle_status(request, pk):
    """تفعيل/إيقاف الموظف (AJAX)"""
    
    if not request.user.has_perm('hr.change_employee'):
        return JsonResponse({'success': False, 'error': 'ليس لديك صلاحية'})
    
    try:
        employee = get_object_or_404(Employee, pk=pk)
        service = EmployeeService(user=request.user)
        
        new_status = not employee.is_active
        service.update_employee_status(employee, new_status)
        
        return JsonResponse({
            'success': True,
            'new_status': new_status,
            'message': f'تم {"تفعيل" if new_status else "إيقاف"} الموظف بنجاح'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
```

### هيكل النماذج (Forms)

```python
# apps/hr/forms/employee_forms.py
from django import forms
from django.core.exceptions import ValidationError
from ..models import Employee, Department, JobPosition

class EmployeeForm(forms.ModelForm):
    """نموذج إضافة/تعديل الموظف"""
    
    class Meta:
        model = Employee
        fields = [
            'emp_code', 'first_name', 'last_name', 'email', 'phone',
            'department', 'job_position', 'hire_date'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل الاسم الأول'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل الاسم الأخير'
            }),
            'emp_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'EMP001'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ahmed@company.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '01234567890'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'job_position': forms.Select(attrs={
                'class': 'form-select'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تخصيص خيارات الأقسام والمناصب
        self.fields['department'].queryset = Department.objects.filter(is_active=True)
        self.fields['job_position'].queryset = JobPosition.objects.filter(is_active=True)
        
        # إضافة خيار فارغ
        self.fields['department'].empty_label = "اختر القسم"
        self.fields['job_position'].empty_label = "اختر المنصب"
    
    def clean_emp_code(self):
        """التحقق من رقم الموظف"""
        emp_code = self.cleaned_data.get('emp_code')
        
        if not emp_code:
            raise ValidationError('رقم الموظف مطلوب')
        
        # التحقق من عدم التكرار
        existing = Employee.objects.filter(emp_code=emp_code)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise ValidationError('رقم الموظف موجود مسبقاً')
        
        return emp_code.upper()
    
    def clean_email(self):
        """التحقق من البريد الإلكتروني"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('البريد الإلكتروني مطلوب')
        
        # التحقق من عدم التكرار
        existing = Employee.objects.filter(email=email)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise ValidationError('البريد الإلكتروني موجود مسبقاً')
        
        return email.lower()
    
    def clean_hire_date(self):
        """التحقق من تاريخ التوظيف"""
        from datetime import date
        
        hire_date = self.cleaned_data.get('hire_date')
        
        if hire_date and hire_date > date.today():
            raise ValidationError('تاريخ التوظيف لا يمكن أن يكون في المستقبل')
        
        return hire_date
```

## 🔌 تطوير واجهات برمجة التطبيقات

### هيكل API

```python
# api/v1/hr/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from apps.hr.models import Employee
from .serializers import EmployeeSerializer, EmployeeDetailSerializer
from .permissions import HRPermission
from .filters import EmployeeFilter

class EmployeeViewSet(viewsets.ModelViewSet):
    """API لإدارة الموظفين"""
    
    queryset = Employee.objects.select_related('department', 'job_position')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, HRPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = ['first_name', 'last_name', 'emp_code', 'email']
    ordering_fields = ['created_at', 'hire_date', 'first_name', 'last_name']
    ordering = ['first_name', 'last_name']
    
    def get_serializer_class(self):
        """اختيار المسلسل المناسب حسب العملية"""
        if self.action == 'retrieve':
            return EmployeeDetailSerializer
        return EmployeeSerializer
    
    def get_queryset(self):
        """تخصيص الاستعلام حسب صلاحيات المستخدم"""
        queryset = super().get_queryset()
        
        # إذا لم يكن لديه صلاحية عرض جميع الموظفين
        if not self.request.user.has_perm('hr.view_all_employees'):
            # عرض موظفي نفس القسم فقط
            if hasattr(self.request.user, 'employee'):
                department = self.request.user.employee.department
                queryset = queryset.filter(department=department)
            else:
                # إذا لم يكن موظفاً، لا يعرض أي شيء
                queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """إضافة معلومات المستخدم عند الإنشاء"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """إضافة معلومات المستخدم عند التحديث"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """تفعيل/إيقاف الموظف"""
        employee = self.get_object()
        
        if not request.user.has_perm('hr.change_employee', employee):
            return Response(
                {'error': 'ليس لديك صلاحية لتعديل هذا الموظف'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        employee.is_active = not employee.is_active
        employee.updated_by = request.user
        employee.save()
        
        return Response({
            'success': True,
            'is_active': employee.is_active,
            'message': f'تم {"تفعيل" if employee.is_active else "إيقاف"} الموظف بنجاح'
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """إحصائيات الموظفين"""
        queryset = self.get_queryset()
        
        stats = {
            'total_employees': queryset.count(),
            'active_employees': queryset.filter(is_active=True).count(),
            'inactive_employees': queryset.filter(is_active=False).count(),
            'departments_count': queryset.values('department').distinct().count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """تحديث مجموعة من الموظفين"""
        employee_ids = request.data.get('employee_ids', [])
        update_data = request.data.get('update_data', {})
        
        if not employee_ids:
            return Response(
                {'error': 'يجب تحديد معرفات الموظفين'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # التحقق من الصلاحيات
        if not request.user.has_perm('hr.change_employee'):
            return Response(
                {'error': 'ليس لديك صلاحية لتعديل الموظفين'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # تطبيق التحديثات
        queryset = self.get_queryset().filter(id__in=employee_ids)
        updated_count = queryset.update(**update_data, updated_by=request.user)
        
        return Response({
            'success': True,
            'updated_count': updated_count,
            'message': f'تم تحديث {updated_count} موظف بنجاح'
        })
```

### المسلسلات (Serializers)

```python
# api/v1/hr/serializers.py
from rest_framework import serializers
from apps.hr.models import Employee, Department, JobPosition

class DepartmentSerializer(serializers.ModelSerializer):
    """مسلسل القسم"""
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']

class JobPositionSerializer(serializers.ModelSerializer):
    """مسلسل المنصب"""
    
    class Meta:
        model = JobPosition
        fields = ['id', 'name', 'level']

class EmployeeSerializer(serializers.ModelSerializer):
    """مسلسل الموظف الأساسي"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    job_position_name = serializers.CharField(source='job_position.name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    service_years = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'emp_code', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'department', 'department_name',
            'job_position', 'job_position_name', 'hire_date',
            'is_active', 'service_years', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_service_years(self, obj):
        """حساب سنوات الخدمة"""
        return obj.get_service_years()
    
    def validate_emp_code(self, value):
        """التحقق من رقم الموظف"""
        if not value:
            raise serializers.ValidationError('رقم الموظف مطلوب')
        
        # التحقق من عدم التكرار
        existing = Employee.objects.filter(emp_code=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError('رقم الموظف موجود مسبقاً')
        
        return value.upper()
    
    def validate_email(self, value):
        """التحقق من البريد الإلكتروني"""
        if not value:
            raise serializers.ValidationError('البريد الإلكتروني مطلوب')
        
        # التحقق من عدم التكرار
        existing = Employee.objects.filter(email=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError('البريد الإلكتروني موجود مسبقاً')
        
        return value.lower()

class EmployeeDetailSerializer(EmployeeSerializer):
    """مسلسل تفاصيل الموظف الكاملة"""
    
    department = DepartmentSerializer(read_only=True)
    job_position = JobPositionSerializer(read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    
    class Meta(EmployeeSerializer.Meta):
        fields = EmployeeSerializer.Meta.fields + [
            'created_by_name', 'updated_by_name'
        ]

class EmployeeCreateSerializer(serializers.ModelSerializer):
    """مسلسل إنشاء موظف جديد"""
    
    class Meta:
        model = Employee
        fields = [
            'emp_code', 'first_name', 'last_name', 'email', 'phone',
            'department', 'job_position', 'hire_date'
        ]
    
    def create(self, validated_data):
        """إنشاء موظف جديد مع الخدمات"""
        from apps.hr.services import EmployeeService
        
        request = self.context.get('request')
        service = EmployeeService(user=request.user if request else None)
        
        return service.create_employee(validated_data)
```

## 🧪 كتابة الاختبارات

### اختبارات النماذج

```python
# tests/hr/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import date, timedelta

from apps.hr.models import Employee, Department, JobPosition

class EmployeeModelTest(TestCase):
    """اختبارات نموذج الموظف"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.department = Department.objects.create(
            name='تقنية المعلومات',
            code='IT',
            created_by=self.user
        )
        
        self.job_position = JobPosition.objects.create(
            name='مطور برمجيات',
            level='senior',
            created_by=self.user
        )
    
    def test_create_employee_success(self):
        """اختبار إنشاء موظف بنجاح"""
        employee = Employee.objects.create(
            emp_code='EMP001',
            first_name='أحمد',
            last_name='محمد',
            email='ahmed@company.com',
            phone='01234567890',
            department=self.department,
            job_position=self.job_position,
            hire_date=date.today() - timedelta(days=365),
            created_by=self.user
        )
        
        self.assertEqual(employee.emp_code, 'EMP001')
        self.assertEqual(employee.full_name, 'أحمد محمد')
        self.assertTrue(employee.is_active)
        self.assertEqual(employee.get_service_years(), 1.0)
    
    def test_employee_str_representation(self):
        """اختبار تمثيل النص للموظف"""
        employee = Employee.objects.create(
            emp_code='EMP002',
            first_name='سارة',
            last_name='أحمد',
            email='sara@company.com',
            department=self.department,
            job_position=self.job_position,
            hire_date=date.today(),
            created_by=self.user
        )
        
        expected_str = 'سارة أحمد (EMP002)'
        self.assertEqual(str(employee), expected_str)
    
    def test_duplicate_emp_code_validation(self):
        """اختبار منع تكرار رقم الموظف"""
        Employee.objects.create(
            emp_code='EMP003',
            first_name='محمد',
            last_name='علي',
            email='mohamed@company.com',
            department=self.department,
            job_position=self.job_position,
            hire_date=date.today(),
            created_by=self.user
        )
        
        # محاولة إنشاء موظف آخر بنفس الرقم
        with self.assertRaises(Exception):  # IntegrityError expected
            Employee.objects.create(
                emp_code='EMP003',
                first_name='فاطمة',
                last_name='حسن',
                email='fatima@company.com',
                department=self.department,
                job_position=self.job_position,
                hire_date=date.today(),
                created_by=self.user
            )
    
    def test_future_hire_date_validation(self):
        """اختبار منع تاريخ توظيف في المستقبل"""
        employee = Employee(
            emp_code='EMP004',
            first_name='خالد',
            last_name='سالم',
            email='khalid@company.com',
            department=self.department,
            job_position=self.job_position,
            hire_date=date.today() + timedelta(days=30),  # تاريخ في المستقبل
            created_by=self.user
        )
        
        with self.assertRaises(ValidationError):
            employee.full_clean()
    
    def test_service_years_calculation(self):
        """اختبار حساب سنوات الخدمة"""
        # موظف بخدمة سنتين ونصف
        hire_date = date.today() - timedelta(days=912)  # حوالي 2.5 سنة
        employee = Employee.objects.create(
            emp_code='EMP005',
            first_name='نورا',
            last_name='عبدالله',
            email='nora@company.com',
            department=self.department,
            job_position=self.job_position,
            hire_date=hire_date,
            created_by=self.user
        )
        
        service_years = employee.get_service_years()
        self.assertAlmostEqual(service_years, 2.5, delta=0.1)
```

### اختبارات العروض

```python
# tests/hr/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from apps.hr.models import Employee, Department, JobPosition

class EmployeeViewsTest(TestCase):
    """اختبارات عروض الموظفين"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.client = Client()
        
        # إنشاء مستخدم مع صلاحيات
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # إضافة صلاحيات HR
        content_type = ContentType.objects.get_for_model(Employee)
        permissions = Permission.objects.filter(content_type=content_type)
        self.user.user_permissions.set(permissions)
        
        # إنشاء بيانات أساسية
        self.department = Department.objects.create(
            name='الموارد البشرية',
            code='HR'
        )
        
        self.job_position = JobPosition.objects.create(
            name='مدير موارد بشرية',
            level='manager'
        )
        
        self.employee = Employee.objects.create(
            emp_code='EMP001',
            first_name='أحمد',
            last_name='محمد',
            email='ahmed@company.com',
            phone='01234567890',
            department=self.department,
            job_position=self.job_position,
            hire_date='2023-01-01'
        )
    
    def test_employee_list_view_authenticated(self):
        """اختبار عرض قائمة الموظفين للمستخدم المصرح له"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('hr:employee_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'أحمد محمد')
        self.assertContains(response, 'EMP001')
    
    def test_employee_list_view_unauthenticated(self):
        """اختبار عرض قائمة الموظفين للمستخدم غير المصرح له"""
        response = self.client.get(reverse('hr:employee_list'))
        
        # يجب إعادة توجيه لصفحة تسجيل الدخول
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_employee_create_view_get(self):
        """اختبار عرض نموذج إضافة موظف"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('hr:employee_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'إضافة موظف جديد')
        self.assertContains(response, 'form')
    
    def test_employee_create_view_post_valid(self):
        """اختبار إضافة موظف ببيانات صحيحة"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'emp_code': 'EMP002',
            'first_name': 'سارة',
            'last_name': 'أحمد',
            'email': 'sara@company.com',
            'phone': '01234567891',
            'department': self.department.id,
            'job_position': self.job_position.id,
            'hire_date': '2024-01-01'
        }
        
        response = self.client.post(reverse('hr:employee_create'), data)
        
        # يجب إعادة توجيه بعد الإنشاء الناجح
        self.assertEqual(response.status_code, 302)
        
        # التحقق من إنشاء الموظف
        self.assertTrue(Employee.objects.filter(emp_code='EMP002').exists())
    
    def test_employee_create_view_post_invalid(self):
        """اختبار إضافة موظف ببيانات غير صحيحة"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'emp_code': '',  # رقم فارغ
            'first_name': 'سارة',
            'last_name': 'أحمد',
            'email': 'invalid-email',  # بريد إلكتروني غير صحيح
            'department': self.department.id,
            'job_position': self.job_position.id,
        }
        
        response = self.client.post(reverse('hr:employee_create'), data)
        
        # يجب البقاء في نفس الصفحة مع أخطاء
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
    
    def test_employee_search(self):
        """اختبار البحث في الموظفين"""
        self.client.login(username='testuser', password='testpass123')
        
        # البحث بالاسم
        response = self.client.get(reverse('hr:employee_list'), {'search': 'أحمد'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'أحمد محمد')
        
        # البحث برقم الموظف
        response = self.client.get(reverse('hr:employee_list'), {'search': 'EMP001'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EMP001')
        
        # البحث بنتيجة فارغة
        response = self.client.get(reverse('hr:employee_list'), {'search': 'غير موجود'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'أحمد محمد')
```

### اختبارات API

```python
# tests/api/test_employee_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse

from apps.hr.models import Employee, Department, JobPosition

class EmployeeAPITest(APITestCase):
    """اختبارات API الموظفين"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.department = Department.objects.create(
            name='تقنية المعلومات',
            code='IT'
        )
        
        self.job_position = JobPosition.objects.create(
            name='مطور',
            level='junior'
        )
        
        self.employee = Employee.objects.create(
            emp_code='EMP001',
            first_name='أحمد',
            last_name='محمد',
            email='ahmed@company.com',
            department=self.department,
            job_position=self.job_position,
            hire_date='2023-01-01'
        )
    
    def test_get_employees_authenticated(self):
        """اختبار الحصول على قائمة الموظفين مع المصادقة"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('api:employee-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['emp_code'], 'EMP001')
    
    def test_get_employees_unauthenticated(self):
        """اختبار الحصول على قائمة الموظفين بدون مصادقة"""
        url = reverse('api:employee-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_employee_valid_data(self):
        """اختبار إنشاء موظف ببيانات صحيحة"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'emp_code': 'EMP002',
            'first_name': 'سارة',
            'last_name': 'أحمد',
            'email': 'sara@company.com',
            'phone': '01234567891',
            'department': self.department.id,
            'job_position': self.job_position.id,
            'hire_date': '2024-01-01'
        }
        
        url = reverse('api:employee-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['emp_code'], 'EMP002')
        self.assertTrue(Employee.objects.filter(emp_code='EMP002').exists())
    
    def test_create_employee_invalid_data(self):
        """اختبار إنشاء موظف ببيانات غير صحيحة"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'emp_code': '',  # رقم فارغ
            'first_name': 'سارة',
            'email': 'invalid-email',  # بريد غير صحيح
        }
        
        url = reverse('api:employee-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('emp_code', response.data)
        self.assertIn('email', response.data)
    
    def test_employee_search(self):
        """اختبار البحث في API"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('api:employee-list')
        response = self.client.get(url, {'search': 'أحمد'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # البحث بنتيجة فارغة
        response = self.client.get(url, {'search': 'غير موجود'})
        self.assertEqual(len(response.data['results']), 0)
    
    def test_employee_statistics(self):
        """اختبار إحصائيات الموظفين"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('api:employee-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_employees'], 1)
        self.assertEqual(response.data['active_employees'], 1)
```

## 📝 أفضل الممارسات

### الأمان

```python
# أمثلة على الممارسات الآمنة

# 1. التحقق من الصلاحيات دائماً
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied

@permission_required('hr.view_employee', raise_exception=True)
def employee_view(request):
    # كود العرض
    pass

# 2. تنظيف البيانات المدخلة
from django.utils.html import escape
from django.core.validators import validate_email

def clean_input_data(data):
    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            cleaned_data[key] = escape(value.strip())
        else:
            cleaned_data[key] = value
    return cleaned_data

# 3. استخدام المعاملات المحضرة لقاعدة البيانات
from django.db import connection

def safe_query(employee_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM employees WHERE id = %s",
            [employee_id]
        )
        return cursor.fetchall()

# 4. تشفير البيانات الحساسة
from django.contrib.auth.hashers import make_password, check_password

def hash_sensitive_data(data):
    return make_password(data)

def verify_sensitive_data(data, hashed_data):
    return check_password(data, hashed_data)
```

### الأداء

```python
# تحسين الأداء

# 1. استخدام select_related و prefetch_related
def get_employees_optimized():
    return Employee.objects.select_related(
        'department', 'job_position'
    ).prefetch_related(
        'attendance_records'
    )

# 2. استخدام التخزين المؤقت
from django.core.cache import cache

def get_department_stats(department_id):
    cache_key = f'department_stats_{department_id}'
    stats = cache.get(cache_key)
    
    if not stats:
        stats = {
            'total_employees': Employee.objects.filter(department_id=department_id).count(),
            'active_employees': Employee.objects.filter(
                department_id=department_id, is_active=True
            ).count()
        }
        cache.set(cache_key, stats, 300)  # 5 دقائق
    
    return stats

# 3. استخدام التجميع في قاعدة البيانات
from django.db.models import Count, Avg

def get_department_summary():
    return Department.objects.annotate(
        employee_count=Count('employees'),
        avg_service_years=Avg('employees__service_years')
    )

# 4. تحديد الحقول المطلوبة فقط
def get_employee_names():
    return Employee.objects.only('first_name', 'last_name', 'emp_code')
```

### التوثيق

```python
def calculate_employee_salary(employee_id, month, year):
    """
    حساب راتب الموظف لشهر معين
    
    Args:
        employee_id (int): معرف الموظف
        month (int): الشهر (1-12)
        year (int): السنة
    
    Returns:
        dict: تفاصيل الراتب المحسوب
        {
            'basic_salary': float,
            'allowances': float,
            'deductions': float,
            'net_salary': float
        }
    
    Raises:
        Employee.DoesNotExist: إذا لم يوجد الموظف
        ValueError: إذا كانت قيم الشهر أو السنة غير صحيحة
    
    Example:
        >>> salary = calculate_employee_salary(1, 12, 2024)
        >>> print(salary['net_salary'])
        5500.0
    """
    # كود الدالة
    pass
```

## 🔄 سير العمل التطويري

### Git Workflow

```bash
# 1. إنشاء فرع جديد للميزة
git checkout -b feature/employee-management

# 2. تطوير الميزة مع commits منتظمة
git add .
git commit -m "feat: add employee model and basic views"

# 3. دفع الفرع للمستودع
git push origin feature/employee-management

# 4. إنشاء Pull Request للمراجعة

# 5. دمج الفرع بعد الموافقة
git checkout main
git pull origin main
git merge feature/employee-management
git push origin main

# 6. حذف الفرع المحلي والبعيد
git branch -d feature/employee-management
git push origin --delete feature/employee-management
```

### معايير Commit Messages

```bash
# أنواع الـ commits
feat: ميزة جديدة
fix: إصلاح خطأ
docs: تحديث التوثيق
style: تغييرات التنسيق
refactor: إعادة هيكلة الكود
test: إضافة أو تحديث الاختبارات
chore: مهام الصيانة

# أمثلة
git commit -m "feat: add employee attendance tracking"
git commit -m "fix: resolve salary calculation bug"
git commit -m "docs: update API documentation"
git commit -m "test: add employee model tests"
```

## 📞 الدعم والمساعدة

### للمطورين الجدد:
1. **اقرأ هذا الدليل بالكامل**
2. **راجع الكود الموجود** لفهم الأنماط المستخدمة
3. **ابدأ بالمهام البسيطة** قبل الانتقال للمعقدة
4. **اسأل الفريق** عند الحاجة للمساعدة

### الموارد المفيدة:
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Git Best Practices](https://git-scm.com/book)

### جهات الاتصال:
- **Lead Developer**: lead@company.com
- **DevOps Team**: devops@company.com
- **Code Review**: review@company.com

---

**مرحباً بك في فريق تطوير نظام الدولية! 🚀**