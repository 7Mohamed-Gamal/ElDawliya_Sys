# =============================================================================
# ElDawliya HR Management System - Leave Management Forms
# =============================================================================
# Forms for leave management (Leave Types, Requests, Balances)
# Supports RTL Arabic interface and modern Django patterns
# =============================================================================

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, Column, Submit, HTML
from crispy_forms.bootstrap import Field, FormActions
from datetime import date, timedelta
from decimal import Decimal

from Hr.models import (
    LeaveType, EmployeeLeaveBalance, LeaveRequest,
    Employee, Company
)


class LeaveTypeForm(forms.ModelForm):
    """نموذج إنشاء وتحديث نوع الإجازة"""
    
    class Meta:
        model = LeaveType
        fields = [
            'company', 'name', 'code', 'description', 'calculation_type',
            'max_days_per_year', 'max_consecutive_days', 'min_notice_days',
            'is_paid', 'affects_attendance', 'carry_forward', 'requires_approval', 'is_active'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم نوع الإجازة'),
                'dir': 'rtl'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('كود نوع الإجازة'),
                'maxlength': '20'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('وصف نوع الإجازة'),
                'dir': 'rtl'
            }),
            'calculation_type': forms.Select(attrs={'class': 'form-select'}),
            'max_days_per_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('الحد الأقصى للأيام في السنة'),
                'min': '0'
            }),
            'max_consecutive_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('الحد الأقصى للأيام المتتالية'),
                'min': '0'
            }),
            'min_notice_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('الحد الأدنى لأيام الإشعار المسبق'),
                'min': '0'
            }),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'affects_attendance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'carry_forward': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        
        # Set default values
        if not self.instance.pk:
            self.fields['is_paid'].initial = True
            self.fields['affects_attendance'].initial = True
            self.fields['requires_approval'].initial = True
            self.fields['is_active'].initial = True
        
        self.helper.layout = Layout(
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-calendar-alt me-2"></i>معلومات نوع الإجازة الأساسية</h4>'),
                Row(
                    Column('company', css_class='col-md-6'),
                    Column('name', css_class='col-md-6'),
                ),
                Row(
                    Column('code', css_class='col-md-6'),
                    Column('calculation_type', css_class='col-md-6'),
                ),
                'description',
                css_class='card-body mb-3'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-calendar-check me-2"></i>قواعد الإجازة</h4>'),
                Row(
                    Column('max_days_per_year', css_class='col-md-4'),
                    Column('max_consecutive_days', css_class='col-md-4'),
                    Column('min_notice_days', css_class='col-md-4'),
                ),
                css_class='card-body mb-3'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-cog me-2"></i>إعدادات الإجازة</h4>'),
                Row(
                    Column('is_paid', css_class='col-md-3'),
                    Column('affects_attendance', css_class='col-md-3'),
                    Column('carry_forward', css_class='col-md-3'),
                    Column('requires_approval', css_class='col-md-3'),
                ),
                'is_active',
                css_class='card-body mb-3'
            ),
            FormActions(
                Submit('submit', _('حفظ نوع الإجازة'), css_class='btn btn-primary'),
                HTML('<a href="{% url "hr:leavetype_list" %}" class="btn btn-secondary ms-2">إلغاء</a>'),
                css_class='text-center'
            )
        )

    def clean_code(self):
        code = self.cleaned_data.get('code')
        company = self.cleaned_data.get('company')
        
        if code and company:
            qs = LeaveType.objects.filter(company=company, code=code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(_('كود نوع الإجازة موجود مسبقاً في هذه الشركة'))
        
        return code


class EmployeeLeaveBalanceForm(forms.ModelForm):
    """نموذج إدارة رصيد إجازات الموظف"""
    
    class Meta:
        model = EmployeeLeaveBalance
        fields = [
            'employee', 'leave_type', 'year', 'allocated_days',
            'carried_forward'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('السنة'),
                'min': '2020',
                'max': '2030'
            }),
            'allocated_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('الأيام المخصصة'),
                'step': '0.5',
                'min': '0'
            }),
            'carried_forward': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('الأيام المرحلة'),
                'step': '0.5',
                'min': '0'
            })
        }

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
        
        if employee:
            self.fields['employee'].initial = employee
            # Filter leave types by employee's company
            self.fields['leave_type'].queryset = LeaveType.objects.filter(
                company=employee.company, is_active=True
            )
        
        # Set default year to current year
        if not self.instance.pk:
            self.fields['year'].initial = date.today().year
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            'employee',
            Row(
                Column('leave_type', css_class='col-md-6'),
                Column('year', css_class='col-md-6'),
            ),
            Row(
                Column('allocated_days', css_class='col-md-6'),
                Column('carried_forward', css_class='col-md-6'),
            ),
            FormActions(
                Submit('submit', _('حفظ الرصيد'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        leave_type = cleaned_data.get('leave_type')
        year = cleaned_data.get('year')
        
        if employee and leave_type and year:
            # Check for duplicate balance records
            qs = EmployeeLeaveBalance.objects.filter(
                employee=employee,
                leave_type=leave_type,
                year=year
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise ValidationError(_('رصيد الإجازة لهذا الموظف والنوع والسنة موجود مسبقاً'))
        
        return cleaned_data


class LeaveRequestForm(forms.ModelForm):
    """نموذج طلب الإجازة"""
    
    class Meta:
        model = LeaveRequest
        fields = [
            'employee', 'leave_type', 'start_date', 'end_date',
            'reason', 'emergency_contact', 'replacement_employee', 'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('اذكر سبب طلب الإجازة'),
                'dir': 'rtl'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('رقم الهاتف للتواصل في حالة الطوارئ'),
                'dir': 'rtl'
            }),
            'replacement_employee': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('ملاحظات إضافية'),
                'dir': 'rtl'
            })
        }

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
        
        if employee:
            self.fields['employee'].initial = employee
            # Filter leave types by employee's company
            self.fields['leave_type'].queryset = LeaveType.objects.filter(
                company=employee.company, is_active=True
            )
            # Filter replacement employees from same department
            self.fields['replacement_employee'].queryset = Employee.objects.filter(
                department=employee.department,
                status='active'
            ).exclude(pk=employee.pk)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        
        self.helper.layout = Layout(
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-calendar-plus me-2"></i>معلومات طلب الإجازة</h4>'),
                'employee',
                'leave_type',
                Row(
                    Column('start_date', css_class='col-md-6'),
                    Column('end_date', css_class='col-md-6'),
                ),
                HTML('<div class="alert alert-info mt-2"><i class="fas fa-info-circle me-2"></i>عدد الأيام المطلوبة: <span id="days-count">0</span> يوم</div>'),
                'reason',
                css_class='card-body mb-3'
            ),
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-users me-2"></i>معلومات إضافية</h4>'),
                'emergency_contact',
                'replacement_employee',
                'notes',
                css_class='card-body mb-3'
            ),
            FormActions(
                Submit('submit', _('تقديم طلب الإجازة'), css_class='btn btn-primary btn-lg'),
                HTML('<a href="{% url "hr:leave_request_list" %}" class="btn btn-secondary btn-lg ms-2">إلغاء</a>'),
                css_class='text-center'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        leave_type = cleaned_data.get('leave_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            # Check date order
            if start_date > end_date:
                raise ValidationError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية'))
            
            # Check minimum notice period
            if leave_type and leave_type.min_notice_days > 0:
                notice_date = date.today() + timedelta(days=leave_type.min_notice_days)
                if start_date < notice_date:
                    raise ValidationError(
                        _('يجب تقديم الطلب قبل {} يوم على الأقل من تاريخ البداية').format(
                            leave_type.min_notice_days
                        )
                    )
            
            # Check maximum consecutive days
            if leave_type and leave_type.max_consecutive_days > 0:
                days_requested = (end_date - start_date).days + 1
                if days_requested > leave_type.max_consecutive_days:
                    raise ValidationError(
                        _('لا يمكن طلب أكثر من {} يوم متتالي لهذا النوع من الإجازة').format(
                            leave_type.max_consecutive_days
                        )
                    )
            
            # Check available balance
            if employee and leave_type:
                try:
                    balance = EmployeeLeaveBalance.objects.get(
                        employee=employee,
                        leave_type=leave_type,
                        year=start_date.year
                    )
                    days_requested = Decimal(str((end_date - start_date).days + 1))
                    if balance.remaining_days < days_requested:
                        raise ValidationError(
                            _('الرصيد المتاح ({} يوم) غير كافي للأيام المطلوبة ({} يوم)').format(
                                balance.remaining_days, days_requested
                            )
                        )
                except EmployeeLeaveBalance.DoesNotExist:
                    raise ValidationError(_('لا يوجد رصيد إجازة محدد لهذا النوع في هذه السنة'))
        
        return cleaned_data


class LeaveRequestApprovalForm(forms.ModelForm):
    """نموذج الموافقة على طلب الإجازة"""
    
    class Meta:
        model = LeaveRequest
        fields = ['status', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'rejection_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('اذكر سبب الرفض (في حالة الرفض)'),
                'dir': 'rtl'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limit status choices to approval/rejection only
        self.fields['status'].choices = [
            ('approved', _('موافق عليه')),
            ('rejected', _('مرفوض'))
        ]
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            Div(
                HTML('<h4 class="mb-3"><i class="fas fa-check-circle me-2"></i>قرار الموافقة</h4>'),
                'status',
                'rejection_reason',
                css_class='card-body'
            ),
            FormActions(
                Submit('submit', _('حفظ القرار'), css_class='btn btn-primary'),
                css_class='text-center'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if status == 'rejected' and not rejection_reason:
            raise ValidationError(_('يجب ذكر سبب الرفض عند رفض الطلب'))
        
        return cleaned_data


class LeaveReportForm(forms.Form):
    """نموذج تقرير الإجازات"""
    
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_active=True),
        required=False,
        empty_label=_('جميع الشركات'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status='active'),
        required=False,
        empty_label=_('جميع الموظفين'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    leave_type = forms.ModelChoiceField(
        queryset=LeaveType.objects.filter(is_active=True),
        required=False,
        empty_label=_('جميع أنواع الإجازات'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', _('جميع الحالات'))] + LeaveRequest.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default date range (current year)
        today = date.today()
        year_start = today.replace(month=1, day=1)
        self.fields['start_date'].initial = year_start
        self.fields['end_date'].initial = today
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'row g-3'
        
        self.helper.layout = Layout(
            Row(
                Column('company', css_class='col-md-2'),
                Column('employee', css_class='col-md-2'),
                Column('leave_type', css_class='col-md-2'),
                Column('status', css_class='col-md-2'),
                Column('start_date', css_class='col-md-2'),
                Column('end_date', css_class='col-md-2'),
            ),
            Row(
                Column(
                    Submit('generate_report', _('إنشاء التقرير'), css_class='btn btn-primary'),
                    Submit('export_excel', _('تصدير Excel'), css_class='btn btn-success ms-2'),
                    css_class='col-12 text-center'
                )
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية'))
        
        return cleaned_data
