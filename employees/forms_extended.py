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
    WorkSchedule, EmployeeWorkSetup
)
from leaves.models import LeaveType
from loans.models import EmployeeLoan, LoanInstallment


class EmployeeHealthInsuranceForm(forms.ModelForm):
    """نموذج التأمين الصحي للموظف"""

    class Meta:
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
        super().__init__(*args, **kwargs)
        self.fields['provider'].queryset = ExtendedHealthInsuranceProvider.objects.filter(is_active=True)
        
        # Add required field indicators
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = True
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' required'

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        expiry_date = cleaned_data.get('expiry_date')
        
        if start_date and expiry_date and start_date >= expiry_date:
            raise ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ البداية')
        
        return cleaned_data


class EmployeeSocialInsuranceForm(forms.ModelForm):
    """نموذج التأمينات الاجتماعية للموظف"""

    class Meta:
        model = ExtendedEmployeeSocialInsurance
        fields = [
            'insurance_status', 'start_date', 'subscription_confirmed',
            'job_title', 'social_insurance_number', 'monthly_wage', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'subscription_confirmed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'social_insurance_number': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_wage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'insurance_status': forms.Select(attrs={'class': 'form-select'}),
            'job_title': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['job_title'].queryset = SocialInsuranceJobTitle.objects.filter(is_active=True)
        
        # Make employee_deduction and company_contribution read-only as they're calculated
        if self.instance and self.instance.pk:
            self.fields['employee_deduction'] = forms.DecimalField(
                widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
                required=False,
                initial=self.instance.employee_deduction
            )
            self.fields['company_contribution'] = forms.DecimalField(
                widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
                required=False,
                initial=self.instance.company_contribution
            )


class SalaryComponentForm(forms.ModelForm):
    """نموذج مكون الراتب"""
    
    class Meta:
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
        super().__init__(*args, **kwargs)
        self.fields['component'].queryset = SalaryComponent.objects.filter(is_active=True)


class EmployeeTransportForm(forms.ModelForm):
    """نموذج نقل الموظف"""
    
    class Meta:
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
        super().__init__(*args, **kwargs)
        self.fields['evaluator'].queryset = Employee.objects.filter(is_active=True)


class EmployeeWorkSetupForm(forms.ModelForm):
    """نموذج إعدادات عمل الموظف"""
    
    class Meta:
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
        super().__init__(*args, **kwargs)
        self.fields['work_schedule'].queryset = WorkSchedule.objects.filter(is_active=True)


# =============================================================================
# MANAGEMENT FORMS FOR LOOKUP TABLES
# =============================================================================

class HealthInsuranceProviderForm(forms.ModelForm):
    """نموذج مقدم خدمة التأمين الصحي"""

    class Meta:
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
