"""
Extended Employee Forms for Comprehensive HR Management
"""
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import Employee
from .models_extended import (
    ExtendedHealthInsuranceProvider, ExtendedEmployeeHealthInsurance,
    SocialInsuranceJobTitle, ExtendedEmployeeSocialInsurance,
    SalaryComponent, EmployeeSalaryComponent,
    EmployeeLeaveBalance, Vehicle, PickupPoint, EmployeeTransport,
    EvaluationCriteria, EmployeePerformanceEvaluation, EvaluationScore,
    WorkSchedule, EmployeeWorkSetup, ExtendedEmployeeDocument, EmployeeDocumentCategory
)
from apps.hr.leaves.models import LeaveType
from loans.models import EmployeeLoan, LoanInstallment


class EmployeeHealthInsuranceForm(forms.ModelForm):
    """نموذج التأمين الصحي للموظف"""

    class Meta:
        """Meta class"""
        model = ExtendedEmployeeHealthInsurance
        fields = [
            'provider', 'insurance_status', 'insurance_type', 'insurance_number',
            'start_date', 'expiry_date', 'num_dependents', 'dependent_names',
            'coverage_details', 'monthly_premium', 'employee_contribution',
            'company_contribution', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'num_dependents': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'dependent_names': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'أدخل أسماء المعالين مفصولة بفواصل'}),
            'coverage_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'monthly_premium': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'employee_contribution': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'company_contribution': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'provider': forms.Select(attrs={'class': 'form-select'}),
            'insurance_status': forms.Select(attrs={'class': 'form-select'}),
            'insurance_type': forms.Select(attrs={'class': 'form-select'}),
            'insurance_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        self.fields['provider'].queryset = ExtendedHealthInsuranceProvider.objects.filter(is_active=True)

        # Add required field indicators
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = True
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' required'

    def clean(self):
        """clean function"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        expiry_date = cleaned_data.get('expiry_date')

        if start_date and expiry_date and start_date >= expiry_date:
            raise ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ البداية')

        return cleaned_data


class EmployeeSocialInsuranceForm(forms.ModelForm):
    """نموذج التأمينات الاجتماعية للموظف"""

    class Meta:
        """Meta class"""
        model = ExtendedEmployeeSocialInsurance
        fields = [
            'insurance_status', 'start_date', 'subscription_confirmed',
            'job_title', 'social_insurance_number', 'monthly_wage',
            'deduction_percentage', 'employee_deduction', 'company_contribution',
            's1_field', 'incoming_document_number', 'incoming_document_date', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'incoming_document_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'subscription_confirmed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            's1_field': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'social_insurance_number': forms.TextInput(attrs={'class': 'form-control'}),
            'incoming_document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_wage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deduction_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'employee_deduction': forms.NumberInput(attrs={'class': 'form-control readonly-field', 'step': '0.01', 'readonly': True}),
            'company_contribution': forms.NumberInput(attrs={'class': 'form-control readonly-field', 'step': '0.01', 'readonly': True}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'insurance_status': forms.Select(attrs={'class': 'form-select'}),
            'job_title': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        # Set queryset for job_title to only active titles
        self.fields['job_title'].queryset = SocialInsuranceJobTitle.objects.filter(is_active=True)

        # Add labels
        self.fields['insurance_status'].label = 'حالة التأمين'
        self.fields['start_date'].label = 'تاريخ بداية الاشتراك'
        self.fields['subscription_confirmed'].label = 'تأكيد الاشتراك'
        self.fields['job_title'].label = 'المسمى الوظيفي في التأمينات'
        self.fields['social_insurance_number'].label = 'رقم التأمينات الاجتماعية'
        self.fields['monthly_wage'].label = 'الأجر الشهري'
        self.fields['deduction_percentage'].label = 'نسبة الخصم (%)'
        self.fields['employee_deduction'].label = 'خصم الموظف'
        self.fields['company_contribution'].label = 'مساهمة الشركة'
        self.fields['s1_field'].label = 'حقل S1'
        self.fields['incoming_document_number'].label = 'رقم الوثيقة الواردة'
        self.fields['incoming_document_date'].label = 'تاريخ الوثيقة الواردة'
        self.fields['notes'].label = 'ملاحظات'

        # Add help text
        self.fields['deduction_percentage'].help_text = 'النسبة المئوية للخصم من الراتب (افتراضي: 9%)'
        self.fields['employee_deduction'].help_text = 'يتم حسابه تلقائياً: الراتب × نسبة الخصم'
        self.fields['company_contribution'].help_text = 'يتم حسابه تلقائياً بناءً على المسمى الوظيفي'

    def clean(self):
        """clean function"""
        cleaned_data = super().clean()
        monthly_wage = cleaned_data.get('monthly_wage')
        deduction_percentage = cleaned_data.get('deduction_percentage')
        job_title = cleaned_data.get('job_title')

        if monthly_wage and deduction_percentage:
            # Calculate employee deduction
            employee_deduction = monthly_wage * (deduction_percentage / 100)
            cleaned_data['employee_deduction'] = employee_deduction

            # Calculate company contribution based on job title
            if job_title and hasattr(job_title, 'company_contribution_percentage'):
                company_contribution = monthly_wage * (job_title.company_contribution_percentage / 100)
            else:
                # Default company contribution rate (12% for Saudi)
                from decimal import Decimal
                company_contribution = monthly_wage * Decimal('0.12')
            cleaned_data['company_contribution'] = company_contribution

        return cleaned_data


class EmployeeDocumentForm(forms.ModelForm):
    """نموذج وثائق الموظف"""

    class Meta:
        """Meta class"""
        model = ExtendedEmployeeDocument
        fields = [
            'category', 'document_name', 'document_file', 'document_date',
            'expiry_date', 'notes'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'document_name': forms.TextInput(attrs={'class': 'form-control'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
            'document_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        # Set queryset for category to only active categories
        from .models_extended import EmployeeDocumentCategory
        self.fields['category'].queryset = EmployeeDocumentCategory.objects.filter(is_active=True)

        # Add labels
        self.fields['category'].label = 'فئة الوثيقة'
        self.fields['document_name'].label = 'اسم الوثيقة'
        self.fields['document_file'].label = 'ملف الوثيقة'
        self.fields['document_date'].label = 'تاريخ الوثيقة'
        self.fields['expiry_date'].label = 'تاريخ انتهاء الصلاحية'
        self.fields['notes'].label = 'ملاحظات'

        # Add help text
        self.fields['document_file'].help_text = 'الملفات المسموحة: PDF, DOC, DOCX, JPG, JPEG, PNG'
        self.fields['expiry_date'].help_text = 'اختياري - للوثائق التي لها تاريخ انتهاء صلاحية'

    def clean_document_file(self):
        """clean_document_file function"""
        document_file = self.cleaned_data.get('document_file')
        category = self.cleaned_data.get('category')

        if document_file and category:
            # Check file size
            max_size_mb = category.max_file_size_mb
            if document_file.size > max_size_mb * 1024 * 1024:
                raise forms.ValidationError(f'حجم الملف كبير جداً. الحد الأقصى المسموح: {max_size_mb} ميجابايت')

            # Check file extension
            file_extension = document_file.name.split('.')[-1].lower()
            allowed_extensions = category.get_allowed_extensions_list()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(f'نوع الملف غير مسموح. الأنواع المسموحة: {", ".join(allowed_extensions)}')

        return document_file


class EmployeeDocumentCategoryForm(forms.ModelForm):
    """نموذج فئات وثائق الموظف"""

    class Meta:
        """Meta class"""
        model = EmployeeDocumentCategory
        fields = [
            'category_name', 'category_code', 'description', 'is_required',
            'max_file_size_mb', 'allowed_extensions', 'is_active', 'sort_order'
        ]
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category_code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_file_size_mb': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '100'}),
            'allowed_extensions': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)

        # Add labels
        self.fields['category_name'].label = 'اسم الفئة'
        self.fields['category_code'].label = 'رمز الفئة'
        self.fields['description'].label = 'الوصف'
        self.fields['is_required'].label = 'مطلوب'
        self.fields['max_file_size_mb'].label = 'الحد الأقصى لحجم الملف (ميجابايت)'
        self.fields['allowed_extensions'].label = 'الامتدادات المسموحة'
        self.fields['is_active'].label = 'نشط'
        self.fields['sort_order'].label = 'ترتيب العرض'

        # Add help text
        self.fields['category_code'].help_text = 'رمز فريد للفئة (أحرف إنجليزية وأرقام فقط)'
        self.fields['allowed_extensions'].help_text = 'مفصولة بفاصلة، مثل: pdf,doc,docx,jpg,png'
        self.fields['max_file_size_mb'].help_text = 'بالميجابايت (افتراضي: 10 ميجابايت)'


class SalaryComponentForm(forms.ModelForm):
    """نموذج مكون الراتب"""

    class Meta:
        """Meta class"""
        model = SalaryComponent
        fields = [
            'component_name', 'component_code', 'component_type',
            'calculation_type', 'default_value', 'is_taxable',
            'is_social_insurance_applicable', 'description'
        ]
        widgets = {
            'component_name': forms.TextInput(attrs={'class': 'form-control'}),
            'component_code': forms.TextInput(attrs={'class': 'form-control'}),
            'component_type': forms.Select(attrs={'class': 'form-select'}),
            'calculation_type': forms.Select(attrs={'class': 'form-select'}),
            'default_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_taxable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_social_insurance_applicable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EmployeeSalaryComponentForm(forms.ModelForm):
    """نموذج مكونات راتب الموظف"""

    class Meta:
        """Meta class"""
        model = EmployeeSalaryComponent
        fields = [
            'component', 'amount', 'percentage', 'effective_date',
            'end_date', 'is_active', 'notes'
        ]
        widgets = {
            'component': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'max': '100'}),
            'effective_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        self.fields['component'].queryset = SalaryComponent.objects.filter(is_active=True)


class EmployeeTransportForm(forms.ModelForm):
    """نموذج نقل الموظف"""

    class Meta:
        """Meta class"""
        model = EmployeeTransport
        fields = [
            'vehicle', 'pickup_point', 'pickup_time', 'effective_date',
            'end_date', 'is_active', 'notes'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'pickup_point': forms.Select(attrs={'class': 'form-select'}),
            'pickup_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(vehicle_status='active')
        self.fields['pickup_point'].queryset = PickupPoint.objects.filter(is_active=True)

        # Add vehicle details display
        self.fields['supervisor_name'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            required=False,
            label='اسم المشرف'
        )
        self.fields['supervisor_phone'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            required=False,
            label='هاتف المشرف'
        )
        self.fields['driver_name'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            required=False,
            label='اسم السائق'
        )
        self.fields['driver_phone'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            required=False,
            label='هاتف السائق'
        )

    def clean(self):
        """clean function"""
        cleaned_data = super().clean()
        vehicle = cleaned_data.get('vehicle')

        if vehicle:
            # Auto-populate vehicle details
            cleaned_data['supervisor_name'] = vehicle.supervisor_name
            cleaned_data['supervisor_phone'] = vehicle.supervisor_phone
            cleaned_data['driver_name'] = vehicle.driver_name
            cleaned_data['driver_phone'] = vehicle.driver_phone

        return cleaned_data


class EmployeePerformanceEvaluationForm(forms.ModelForm):
    """نموذج تقييم أداء الموظف"""

    class Meta:
        """Meta class"""
        model = EmployeePerformanceEvaluation
        fields = [
            'evaluator', 'evaluation_period_start', 'evaluation_period_end',
            'evaluation_date', 'strengths', 'areas_for_improvement',
            'goals_next_period', 'employee_comments', 'evaluator_comments', 'status'
        ]
        widgets = {
            'evaluator': forms.Select(attrs={'class': 'form-select'}),
            'evaluation_period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'evaluation_period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'evaluation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'areas_for_improvement': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'goals_next_period': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'employee_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'evaluator_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        self.fields['evaluator'].queryset = Employee.objects.filter(is_active=True)


class EmployeeWorkSetupForm(forms.ModelForm):
    """نموذج إعدادات عمل الموظف"""

    class Meta:
        """Meta class"""
        model = EmployeeWorkSetup
        fields = [
            'work_schedule', 'effective_date', 'end_date', 'overtime_rate',
            'late_deduction_rate', 'absence_deduction_rate', 'is_active', 'notes'
        ]
        widgets = {
            'work_schedule': forms.Select(attrs={'class': 'form-select'}),
            'effective_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'overtime_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'late_deduction_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'absence_deduction_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """__init__ function"""
        super().__init__(*args, **kwargs)
        self.fields['work_schedule'].queryset = WorkSchedule.objects.filter(is_active=True)


# =============================================================================
# MANAGEMENT FORMS FOR LOOKUP TABLES
# =============================================================================

class HealthInsuranceProviderForm(forms.ModelForm):
    """نموذج مقدم خدمة التأمين الصحي"""

    class Meta:
        """Meta class"""
        model = ExtendedHealthInsuranceProvider
        fields = [
            'provider_name', 'provider_code', 'contact_person',
            'phone', 'email', 'address', 'is_active'
        ]
        widgets = {
            'provider_name': forms.TextInput(attrs={'class': 'form-control'}),
            'provider_code': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SocialInsuranceJobTitleForm(forms.ModelForm):
    """نموذج مسمى وظيفة في التأمينات الاجتماعية"""

    class Meta:
        """Meta class"""
        model = SocialInsuranceJobTitle
        fields = [
            'job_code', 'job_title', 'insurable_wage_amount',
            'employee_deduction_percentage', 'company_contribution_percentage', 'is_active'
        ]
        widgets = {
            'job_code': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'insurable_wage_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'employee_deduction_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'max': '100'}),
            'company_contribution_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'max': '100'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VehicleForm(forms.ModelForm):
    """نموذج المركبة"""

    class Meta:
        """Meta class"""
        model = Vehicle
        fields = [
            'vehicle_number', 'vehicle_model', 'vehicle_year', 'capacity',
            'route_info', 'supervisor_name', 'supervisor_phone',
            'driver_name', 'driver_phone', 'driver_license',
            'vehicle_status', 'insurance_expiry', 'license_expiry', 'notes'
        ]
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_model': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1990', 'max': '2030'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'route_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supervisor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'supervisor_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_license': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_status': forms.Select(attrs={'class': 'form-select'}),
            'insurance_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'license_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PickupPointForm(forms.ModelForm):
    """نموذج نقطة التجميع"""

    class Meta:
        """Meta class"""
        model = PickupPoint
        fields = [
            'point_name', 'point_code', 'address', 'latitude',
            'longitude', 'is_active', 'notes'
        ]
        widgets = {
            'point_name': forms.TextInput(attrs={'class': 'form-control'}),
            'point_code': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class WorkScheduleForm(forms.ModelForm):
    """نموذج جدول العمل"""

    class Meta:
        """Meta class"""
        model = WorkSchedule
        fields = [
            'schedule_name', 'schedule_code', 'daily_hours', 'weekly_hours',
            'start_time', 'end_time', 'break_duration', 'is_flexible',
            'overtime_applicable', 'is_active', 'description'
        ]
        widgets = {
            'schedule_name': forms.TextInput(attrs={'class': 'form-control'}),
            'schedule_code': forms.TextInput(attrs={'class': 'form-control'}),
            'daily_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25', 'min': '1', 'max': '24'}),
            'weekly_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25', 'min': '1', 'max': '168'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'break_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_flexible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'overtime_applicable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EvaluationCriteriaForm(forms.ModelForm):
    """نموذج معيار التقييم"""

    class Meta:
        """Meta class"""
        model = EvaluationCriteria
        fields = [
            'criteria_name', 'criteria_code', 'description', 'max_score',
            'weight', 'is_active', 'sort_order'
        ]
        widgets = {
            'criteria_name': forms.TextInput(attrs={'class': 'form-control'}),
            'criteria_code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.1'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


# =============================================================================
# FORMSETS FOR DYNAMIC COMPONENTS
# =============================================================================

# Salary Components Formset
EmployeeSalaryComponentFormSet = inlineformset_factory(
    Employee,
    EmployeeSalaryComponent,
    form=EmployeeSalaryComponentForm,
    extra=1,
    can_delete=True,
    fields=['component', 'amount', 'percentage', 'effective_date', 'end_date', 'is_active', 'notes']
)

# Leave Balances Formset (for display only, calculated automatically)
EmployeeLeaveBalanceFormSet = inlineformset_factory(
    Employee,
    EmployeeLeaveBalance,
    fields=['leave_type', 'year', 'opening_balance', 'accrued_balance', 'carried_forward'],
    extra=0,
    can_delete=False
)

# Evaluation Scores Formset
EvaluationScoreFormSet = inlineformset_factory(
    EmployeePerformanceEvaluation,
    EvaluationScore,
    fields=['criteria', 'score', 'comments'],
    extra=0,
    can_delete=False
)
