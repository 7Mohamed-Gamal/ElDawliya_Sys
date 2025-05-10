from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models import Employee, Department, Job, Car


class EmployeeForm(forms.ModelForm):
    """
    Form for creating and editing employees
    """
    class Meta:
        model = Employee
        fields = [
            'emp_id', 'emp_first_name', 'emp_second_name', 'emp_full_name', 'emp_name_english', 'mother_name',
            'national_id', 'date_birth', 'place_birth', 'emp_nationality', 'emp_marital_status',
            'military_service_certificate', 'people_with_special_needs', 'emp_phone1', 'emp_phone2',
            'emp_address', 'governorate', 'emp_type', 'working_condition', 'department',
            'jop_code', 'jop_name', 'emp_date_hiring', 'emp_car', 'insurance_status',
            'insurance_salary', 'health_card', 'shift_type'
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
            'jop_code': forms.NumberInput(attrs={'class': 'form-control'}),
            'jop_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emp_date_hiring': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'emp_car': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_status': forms.Select(attrs={'class': 'form-select'}),
            'insurance_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'health_card': forms.Select(attrs={'class': 'form-select'}),
            'shift_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        # استدعاء super() method أولاً
        super().__init__(*args, **kwargs)

        # الحصول على instance إذا كان موجوداً
        instance = kwargs.get('instance', None)

        # التأكد من أن جميع الحقول موجودة في النموذج
        for field_name in self.Meta.fields:
            if field_name not in self.fields:
                print(f"Warning: Field {field_name} is missing from the form")

        # طباعة القيم لتشخيص المشكلة
        if instance:
            print(f"Loading instance with ID: {instance.emp_id}")
            for field_name in self.fields:
                if hasattr(instance, field_name):
                    field_value = getattr(instance, field_name)
                    print(f"{field_name}: {field_value}")
                    # التأكد من أن القيمة الأولية للحقل تم تعيينها بشكل صحيح
                    if field_name in self.initial:
                        print(f"  Initial value: {self.initial[field_name]}")
                    else:
                        print(f"  No initial value set")

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

        # تعيين قيم افتراضية للحقول المهمة للإنشاء الجديد فقط
        if not instance:
            self.fields['working_condition'].initial = 'سارى'
            self.fields['emp_type'].initial = 'ذكر'
            self.fields['emp_marital_status'].initial = 'أعزب'
            self.fields['insurance_status'].initial = 'غير مؤمن عليه'
            self.fields['health_card'].initial = 'غير موجوده'
            self.fields['shift_type'].initial = 'صباحي'


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
