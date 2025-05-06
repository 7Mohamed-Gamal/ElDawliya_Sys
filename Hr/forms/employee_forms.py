from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models import Employee, Department, Job, Car


class EmployeeForm(forms.Form):
    """
    Form for creating and editing employees
    """
    # المعلومات الأساسية
    emp_id = forms.IntegerField(
        label=_('رقم الموظف'),
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    emp_first_name = forms.CharField(
        label=_('الاسم الأول'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    emp_second_name = forms.CharField(
        label=_('الاسم الثاني'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    emp_full_name = forms.CharField(
        label=_('الاسم الكامل'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    emp_name_english = forms.CharField(
        label=_('الاسم بالإنجليزية'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mother_name = forms.CharField(
        label=_('اسم الأم'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # معلومات الهوية
    national_id = forms.CharField(
        label=_('الرقم القومي'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date_birth = forms.DateField(
        label=_('تاريخ الميلاد'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    place_birth = forms.CharField(
        label=_('محل الميلاد'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    emp_nationality = forms.CharField(
        label=_('الجنسية'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    emp_marital_status = forms.ChoiceField(
        label=_('الحالة الاجتماعية'),
        choices=Employee.MARITAL_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    military_service_certificate = forms.ChoiceField(
        label=_('شهادة الخدمة العسكرية'),
        choices=Employee.MILITARY_SERVICE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    people_with_special_needs = forms.BooleanField(
        label=_('ذوي الاحتياجات الخاصة'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # بيانات الاتصال
    emp_phone1 = forms.CharField(
        label=_('رقم الهاتف 1'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    emp_phone2 = forms.CharField(
        label=_('رقم الهاتف 2'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    emp_address = forms.CharField(
        label=_('العنوان'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    governorate = forms.CharField(
        label=_('المحافظة'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # معلومات العمل
    emp_type = forms.ChoiceField(
        label=_('نوع الموظف'),
        choices=Employee.EMP_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    working_condition = forms.ChoiceField(
        label=_('حالة العمل'),
        choices=Employee.WORKING_CONDITION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    department = forms.ModelChoiceField(
        label=_('القسم'),
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    jop_code = forms.IntegerField(
        label=_('كود الوظيفة'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    jop_name = forms.CharField(
        label=_('اسم الوظيفة'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    emp_date_hiring = forms.DateField(
        label=_('تاريخ التعيين'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    # معلومات السيارة
    emp_car = forms.CharField(
        label=_('السيارة'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # معلومات التأمين
    insurance_status = forms.ChoiceField(
        label=_('حالة التأمين'),
        choices=Employee.INSURANCE_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    insurance_salary = forms.DecimalField(
        label=_('راتب التأمين'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    health_card = forms.ChoiceField(
        label=_('بطاقة صحية'),
        choices=Employee.health_card_choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    shift_type = forms.ChoiceField(
        label=_('نوع المناوبة'),
        choices=Employee.SHIFT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # تقسيم الحقول إلى مجموعات للعرض في الواجهة
        self.fieldsets = [
            (_('المعلومات الأساسية'), [
                'emp_id', 'emp_first_name', 'emp_second_name', 'emp_full_name',
                'emp_name_english', 'mother_name'
            ]),
            (_('معلومات الهوية'), [
                'national_id', 'date_birth', 'place_birth',
                'emp_nationality', 'emp_marital_status', 'military_service_certificate',
                'people_with_special_needs'
            ]),
            (_('بيانات الاتصال'), [
                'emp_phone1', 'emp_phone2', 'emp_address', 'governorate'
            ]),
            (_('معلومات العمل'), [
                'emp_type', 'working_condition', 'department',
                'jop_code', 'jop_name', 'emp_date_hiring'
            ]),
            (_('معلومات السيارة'), [
                'emp_car'
            ]),
            (_('معلومات التأمين'), [
                'insurance_status', 'insurance_salary', 'health_card', 'shift_type'
            ]),
        ]

        # تعيين قيم افتراضية للحقول المهمة
        self.fields['working_condition'].initial = 'سارى'  # سارى
        self.fields['emp_type'].initial = 'ذكر'  # ذكر
        self.fields['emp_marital_status'].initial = 'أعزب'  # أعزب
        self.fields['insurance_status'].initial = 'غير مؤمن عليه'  # غير مؤمن عليه
        self.fields['health_card'].initial = 'غير موجوده'  # غير موجوده
        self.fields['shift_type'].initial = 'صباحي'  # صباحي

    def save(self):
        """
        Save the form data to create a new Employee instance
        """
        data = self.cleaned_data
        employee = Employee(
            emp_id=data['emp_id'],
            emp_first_name=data['emp_first_name'],
            emp_second_name=data['emp_second_name'],
            emp_full_name=data['emp_full_name'],
            emp_name_english=data.get('emp_name_english', ''),
            mother_name=data.get('mother_name', ''),
            national_id=data.get('national_id', ''),
            date_birth=data.get('date_birth'),
            place_birth=data.get('place_birth', ''),
            emp_nationality=data.get('emp_nationality', ''),
            emp_marital_status=data.get('emp_marital_status', ''),
            military_service_certificate=data.get('military_service_certificate', ''),
            people_with_special_needs=data.get('people_with_special_needs', False),
            emp_phone1=data.get('emp_phone1', ''),
            emp_phone2=data.get('emp_phone2', ''),
            emp_address=data.get('emp_address', ''),
            governorate=data.get('governorate', ''),
            emp_type=data.get('emp_type', ''),
            working_condition=data.get('working_condition', ''),
            department=data.get('department'),
            jop_code=data.get('jop_code'),
            jop_name=data.get('jop_name', ''),
            emp_date_hiring=data.get('emp_date_hiring'),
            emp_car=data.get('emp_car', ''),
            insurance_status=data.get('insurance_status', ''),
            insurance_salary=data.get('insurance_salary'),
            health_card=data.get('health_card', ''),
            shift_type=data.get('shift_type', '')
        )
        employee.save()
        return employee


class EmployeeFilterForm(forms.Form):
    """
    Form for filtering employees
    """
    name = forms.CharField(
        label=_('الاسم'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label=_('القسم'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    jop_name = forms.CharField(
        label=_('الوظيفة'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    working_condition = forms.ChoiceField(
        choices=[('', _('الكل'))] + list(Employee.WORKING_CONDITION_CHOICES),
        label=_('حالة العمل'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class DepartmentForm(forms.ModelForm):
    """
    Form for creating and editing departments
    """
    # إضافة حقل مدير القسم
    manager = forms.ModelChoiceField(
        queryset=Employee.objects.filter(working_condition='سارى'),
        label=_('مدير القسم'),
        required=False,
        to_field_name='emp_id',  # استخدام حقل emp_id كقيمة
        widget=forms.Select(attrs={'class': 'form-select select2'})
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            'placeholder': 'بحث بالاسم'
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
    insurance_number = forms.CharField(
        label='الرقم التأميني',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'بحث بالرقم التأميني'
        })
    )
