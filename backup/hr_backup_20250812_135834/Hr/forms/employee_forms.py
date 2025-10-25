from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models.employee.employee_models import Employee
from Hr.models.core.job_models import Job
from Hr.models.car_models import HrCar as Car
from Hr.models.core.department_models import Department


class BinaryImageField(forms.FileField):
    def to_python(self, data):
        if data is None:
            return None
        if isinstance(data, bytes):
            return data
        if hasattr(data, 'read'):
            return data.read()
        return None

    def clean(self, data, initial=None):
        if data is False: # If clear checkbox is checked
            return None
        if not data and initial:
            return initial
        value = super().clean(data, initial)
        if hasattr(value, 'read'):
            return value.read()
        return value


class EmployeeForm(forms.ModelForm):
    """
    Form for creating and editing Employee records, using the modern Employee model.
    """
    # The emp_image field is not a direct model field, so it's handled separately
    # In the new model, this would likely be a FileField in a related model (e.g., EmployeeFile)
    # For now, we will omit it as it doesn't map to the new Employee model directly.

    class Meta:
        model = Employee
        # Use fields from the new Employee model
        fields = [
            'employee_id', 'first_name', 'middle_name', 'last_name',
            'status', 'national_id', 'date_of_birth', 'join_date', 
            'department', 'position'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'join_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(is_active=True)
        self.fields['position'].queryset = Job.objects.filter(is_active=True)


class EmployeeFilterForm(forms.Form):
    """
    Form for filtering employees with enhanced search capabilities.
    """
    search = forms.CharField(
        label=_('البحث السريع'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'بحث بالاسم أو الكود أو الرقم القومي'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label=_('القسم'),
        required=False,
        empty_label=_('جميع الأقسام'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    position = forms.ModelChoiceField(
        queryset=Job.objects.all(),
        label=_('الوظيفة'),
        required=False,
        empty_label=_('جميع الوظائف'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', _('جميع الحالات'))] + list(Employee.STATUS_CHOICES),
        label=_('حالة العمل'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class DepartmentForm(forms.ModelForm):
    """
    Form for creating and editing departments.
    """
    manager = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status=Employee.ACTIVE).order_by('first_name', 'last_name'),
        label=_('مدير القسم'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select select2',
            'data-placeholder': 'اختر مدير القسم أو ابحث بالاسم'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].label_from_instance = lambda obj: obj.full_name
        if self.instance and self.instance.manager:
            self.fields['manager'].initial = self.instance.manager

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
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.RadioSelect(choices=[(True, 'نشط'), (False, 'غير نشط')])
        }


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['jop_code', 'jop_name', 'is_active']
        widgets = {
            'jop_code': forms.NumberInput(attrs={'class': 'form-control'}),
            'jop_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CarForm(forms.ModelForm):
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
    quick_search = forms.CharField(
        label='البحث السريع',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'بحث سريع بأي معلومة (الاسم، الكود، الرقم القومي، الهاتف...)'
        })
    )
    employee_id = forms.CharField(
        label='كود الموظف',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل كود الموظف'})
    )
    full_name = forms.CharField(
        label='الاسم',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'بحث بالاسم الكامل أو جزء منه'})
    )
    national_id = forms.CharField(
        label='الرقم القومي',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'بحث بالرقم القومي'})
    )
    mobile_phone = forms.CharField(
        label='رقم الهاتف',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'بحث برقم الهاتف'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label='القسم',
        required=False,
        empty_label='جميع الأقسام',
        widget=forms.Select(attrs={'class': 'form-select select2', 'data-placeholder': 'اختر القسم'})
    )
    position = forms.ModelChoiceField(
        queryset=Job.objects.all(),
        label='الوظيفة',
        required=False,
        empty_label='جميع الوظائف',
        widget=forms.Select(attrs={'class': 'form-select select2', 'data-placeholder': 'اختر الوظيفة'})
    )
    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + list(Employee.STATUS_CHOICES),
        label='حالة العمل',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    join_date_from = forms.DateField(
        label='تاريخ التعيين من',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    join_date_to = forms.DateField(
        label='تاريخ التعيين إلى',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
