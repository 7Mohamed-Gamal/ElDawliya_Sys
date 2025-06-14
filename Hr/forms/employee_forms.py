from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models import Employee, Department, Job, Car

class BinaryImageField(forms.FileField):  # Changed from ImageField to FileField
    """
    Custom form field for handling image uploads to BinaryField
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators = []  # Remove default validators that check for file attributes
        
    def to_python(self, data):
        """
        Convert the uploaded file to binary data
        """
        # Return None if no data
        if data is None:
            return None
            
        # If already bytes, return as is
        if isinstance(data, bytes):
            return data
            
        # If clearing the field (checkbox checked)
        if data is False:
            return None
            
        # If it's a file object
        if hasattr(data, 'read'):
            # Read the file content
            return data.read()
            
        return None

    def bound_data(self, data, initial):
        """Handle bound data for the binary field"""
        if data in [False, None]:
            return None
        return data

    def clean(self, data, initial=None):
        # Handle clearing the field
        if data is False:
            return None
        # If no new file is uploaded, return initial value
        if not data and initial:
            return initial
        # Convert file to binary
        value = super().clean(data, initial)
        if value is None:
            return None
        # If it's a file, read it
        if hasattr(value, 'read'):
            return value.read()
        return value
        

class EmployeeForm(forms.ModelForm):
    """
    Form for creating and editing employees
    """
    emp_image = BinaryImageField(
        required=False,
        label=_("صورة الموظف"),
        help_text=_("اختر صورة للموظف (اختياري)"),
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    
    # Add ModelChoiceField for jobs
    jop_name = forms.ModelChoiceField(
        queryset=Job.objects.all(),
        label=_('الوظيفة'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    def clean_emp_image(self):
        """
        Handle the binary image field correctly
        """
        data = self.cleaned_data.get('emp_image')
        return data
        
    class Meta:
        model = Employee
        fields = [
            'emp_id', 'emp_first_name', 'emp_second_name', 'emp_full_name', 'emp_name_english', 'mother_name',
            'national_id', 'date_birth', 'place_birth', 'emp_nationality', 'emp_marital_status',
            'military_service_certificate', 'people_with_special_needs', 'emp_phone1', 'emp_phone2',
            'emp_address', 'governorate', 'emp_type', 'working_condition', 'department',
            'jop_name', 'emp_date_hiring', 'emp_car', 'insurance_status',  # Removed jop_code
            'insurance_salary', 'health_card', 'shift_type','age','emp_image'
        ]
        widgets = {
            'emp_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'emp_first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emp_second_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emp_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emp_name_english': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'date_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'place_birth': forms.TextInput(attrs={'class': 'form-control'}),
            'emp_nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'emp_marital_status': forms.Select(attrs={'class': 'form-select'}),
            'military_service_certificate': forms.Select(attrs={'class': 'form-select'}),
            'people_with_special_needs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'emp_phone1': forms.TextInput(attrs={'class': 'form-control'}),
            'emp_phone2': forms.TextInput(attrs={'class': 'form-control'}),
            'emp_address': forms.TextInput(attrs={'class': 'form-control'}),
            'governorate': forms.TextInput(attrs={'class': 'form-control'}),
            'emp_type': forms.Select(attrs={'class': 'form-select'}),
            'working_condition': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'emp_date_hiring': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'emp_car': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_status': forms.Select(attrs={'class': 'form-select'}),
            'insurance_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'health_card': forms.Select(attrs={'class': 'form-select'}),
            'shift_type': forms.Select(attrs={'class': 'form-select'}),
            'age': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get instance if it exists
        instance = kwargs.get('instance', None)
        
        # Set up job choices from Job model
        jobs = Job.objects.all().order_by('jop_name')
        self.fields['jop_name'].queryset = jobs
        self.fields['jop_name'].label = _('الوظيفة')
        
        # If editing existing employee, set initial job value
        if instance and instance.jop_name:
            try:
                job = Job.objects.get(jop_name=instance.jop_name)
                self.fields['jop_name'].initial = job
            except Job.DoesNotExist:
                pass

        # Split fields into fieldsets for display
        self.fieldsets = [
            (_('المعلومات الأساسية'), [
                'emp_id', 'emp_first_name', 'emp_second_name', 'emp_full_name',
                'emp_name_english', 'mother_name'
            ]),
            (_('معلومات الهوية'), [
                'national_id', 'date_birth', 'place_birth',
                'emp_nationality', 'emp_marital_status','emp_type','people_with_special_needs',
                'emp_address', 'governorate'
            ]),
            (_('بيانات الاتصال'), [
                'emp_phone1', 'emp_phone2'
            ]),
            (_('معلومات العمل'), [
                'working_condition', 'department',
                'jop_name', 'emp_date_hiring'  # Removed jop_code
            ]),
            (_('معلومات السيارة'), [
                'emp_car','shift_type'
            ]),
            (_('معلومات التأمين'), [
                'insurance_status', 'insurance_salary', 'health_card'
            ]),
            (_('مصوغات التعيين'), [
                'military_service_certificate', 'emp_image'
            ]),
        ]

        # Set default values for new instances
        if not instance:
            self.fields['working_condition'].initial = 'سارى'
            self.fields['emp_type'].initial = 'ذكر'
            self.fields['emp_marital_status'].initial = 'أعزب'
            self.fields['insurance_status'].initial = 'غير مؤمن عليه'
            self.fields['health_card'].initial = 'غير موجوده'
            self.fields['shift_type'].initial = 'صباحي'

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Handle job selection properly
        job = self.cleaned_data.get('jop_name')
        if job:
            instance.jop_name = job.jop_name
            instance.jop_code = job.jop_code
        else:
            # Clear job fields if no job selected
            instance.jop_name = None
            instance.jop_code = None

        if commit:
            instance.save()
        return instance


class EmployeeFilterForm(forms.Form):
    """
    Form for filtering employees with enhanced search capabilities
    """
    search = forms.CharField(
        label=_('البحث السريع'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'بحث بالاسم أو الكود أو الرقم القومي'
        })
    )

    name = forms.CharField(
        label=_('الاسم'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label=_('القسم'),
        required=False,
        empty_label=_('جميع الأقسام'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    job = forms.ModelChoiceField(
        queryset=Job.objects.all(),
        label=_('الوظيفة'),
        required=False,
        empty_label=_('جميع الوظائف'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    working_condition = forms.ChoiceField(
        choices=[('', _('جميع الحالات'))] + list(Employee.WORKING_CONDITION_CHOICES),
        label=_('حالة العمل'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    insurance_status = forms.ChoiceField(
        choices=[('', _('جميع حالات التأمين'))] + list(Employee.INSURANCE_STATUS_CHOICES),
        label=_('حالة التأمين'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class DepartmentForm(forms.ModelForm):
    """
    Form for creating and editing departments
    """
    # إضافة حقل مدير القسم
    manager = forms.ModelChoiceField(
        queryset=Employee.objects.filter(working_condition='سارى').order_by('emp_full_name'),
        label=_('مدير القسم'),
        required=False,
        to_field_name='emp_id',  # استخدام حقل emp_id كقيمة
        widget=forms.Select(attrs={
            'class': 'form-select select2',
            'data-placeholder': 'اختر مدير القسم أو ابحث بالاسم'
        })
    )

    # تخصيص طريقة عرض الموظفين في القائمة المنسدلة
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تخصيص طريقة عرض الموظفين في القائمة المنسدلة
        self.fields['manager'].label_from_instance = self.employee_label_from_instance

        # إذا كان إنشاء قسم جديد (وليس تعديل)
        if not self.instance.pk:
            self.fields['dept_code'].required = False
            self.fields['dept_code'].help_text = 'سيتم إنشاء كود القسم تلقائيًا عند الحفظ'
        else:
            # إذا كان تعديل قسم موجود، حاول تعيين مدير القسم
            if self.instance.manager_id:
                try:
                    manager = Employee.objects.get(emp_id=self.instance.manager_id)
                    self.fields['manager'].initial = manager
                except Employee.DoesNotExist:
                    pass

    # دالة لتخصيص طريقة عرض الموظفين في القائمة المنسدلة
    def employee_label_from_instance(self, employee):
        # عرض اسم الموظف ورقمه والوظيفة
        job_info = f" - {employee.jop_name}" if employee.jop_name else ""
        return f"{employee.emp_full_name} ({employee.emp_id}){job_info}"

    # إضافة حقل الحالة
    is_active = forms.ChoiceField(
        choices=[('True', 'نشط'), ('False', 'غير نشط')],
        label=_('الحالة'),
        initial='True',
        widget=forms.RadioSelect()
    )

    # إضافة حقل الملاحظات
    note = forms.CharField(
        label=_('ملاحظات'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = Department
        fields = ['dept_code', 'dept_name', 'manager', 'is_active', 'note']
        widgets = {
            'dept_code': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'placeholder': 'سيتم إنشاؤه تلقائيًا'
            }),
            'dept_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # حفظ مدير القسم
        manager = self.cleaned_data.get('manager')
        if manager:
            instance.manager_id = manager.emp_id
        else:
            instance.manager_id = None

        # تحويل is_active من نص إلى قيمة منطقية
        is_active_value = self.cleaned_data.get('is_active')
        instance.is_active = (is_active_value == 'True')

        if commit:
            instance.save()
        return instance


class JobForm(forms.ModelForm):
    """
    Form for creating and editing jobs
    """
    class Meta:
        model = Job
        fields = ['jop_code', 'jop_name', 'department']
        widgets = {
            'jop_code': forms.NumberInput(attrs={'class': 'form-control'}),
            'jop_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إذا كان إنشاء وظيفة جديدة (وليس تعديل)
        if not self.instance.pk:
            self.fields['jop_code'].required = False
            self.fields['jop_code'].help_text = 'سيتم إنشاء رمز الوظيفة تلقائيًا عند الحفظ'


class CarForm(forms.ModelForm):
    """
    Form for creating and editing cars
    """
    class Meta:
        model = Car
        fields = ['car_id', 'car_name', 'car_type', 'car_number', 'car_license_expiration_date', 'driver_name', 'driver_phone', 'shift_type']
        widgets = {
            'car_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'car_name': forms.TextInput(attrs={'class': 'form-control'}),
            'car_type': forms.TextInput(attrs={'class': 'form-control'}),
            'car_number': forms.TextInput(attrs={'class': 'form-control'}),
            'car_license_expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'shift_type': forms.Select(attrs={'class': 'form-select'}),
        }

class EmployeeSearchForm(forms.Form):
    # البحث السريع العام
    quick_search = forms.CharField(
        label='البحث السريع',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'بحث سريع بأي معلومة (الاسم، الكود، الرقم القومي، الهاتف، العنوان...)',
            'id': 'quick-search'
        })
    )

    # معلومات الهوية
    employee_code = forms.CharField(
        label='كود الموظف',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كود الموظف'
        })
    )
    name = forms.CharField(
        label='الاسم',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'بحث بالاسم الكامل أو جزء منه'
        })
    )
    national_id = forms.CharField(
        label='الرقم القومي',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'بحث بالرقم القومي'
        })
    )

    # معلومات الاتصال
    phone = forms.CharField(
        label='رقم الهاتف',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'بحث برقم الهاتف'
        })
    )
    address = forms.CharField(
        label='العنوان',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'بحث بالعنوان أو المحافظة'
        })
    )

    # معلومات العمل
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label='القسم',
        required=False,
        empty_label='جميع الأقسام',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    job_name = forms.ModelChoiceField(
        queryset=Job.objects.all(),
        label='الوظيفة',
        required=False,
        empty_label='جميع الوظائف',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    working_condition = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + list(Employee.WORKING_CONDITION_CHOICES),
        label='حالة العمل',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # معلومات السيارة
    car = forms.ModelChoiceField(
        queryset=Car.objects.all(),
        label='السيارة',
        required=False,
        empty_label='جميع السيارات',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    shift_type = forms.ChoiceField(
        choices=[('', 'جميع الورديات')] + list(Employee.SHIFT_TYPE_CHOICES),
        label='نوع الوردية',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # معلومات التأمين
    insurance_status = forms.ChoiceField(
        choices=[('', 'جميع حالات التأمين')] + list(Employee.INSURANCE_STATUS_CHOICES),
        label='حالة التأمين',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    insurance_number = forms.CharField(
        label='الرقم التأميني',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'بحث بالرقم التأميني'
        })
    )
    health_card = forms.ChoiceField(
        choices=[('', 'جميع حالات البطاقة الصحية')] + Employee.health_card_choices,
        label='البطاقة الصحية',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # معلومات شخصية
    emp_type = forms.ChoiceField(
        choices=[('', 'الجميع')] + list(Employee.EMP_TYPE_CHOICES),
        label='النوع',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    marital_status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + list(Employee.MARITAL_STATUS_CHOICES),
        label='الحالة الاجتماعية',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # تواريخ
    hire_date_from = forms.DateField(
        label='تاريخ التعيين من',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    hire_date_to = forms.DateField(
        label='تاريخ التعيين إلى',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    birth_date_from = forms.DateField(
        label='تاريخ الميلاد من',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    birth_date_to = forms.DateField(
        label='تاريخ الميلاد إلى',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
