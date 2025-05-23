from django import forms
from Hr.models.leave_models import LeaveType
from Hr.models.employee_model import Employee

class LeaveFilterForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        required=False,
        label='الموظف',
        widget=forms.Select(attrs={'class': 'select2'})
    )
    leave_type = forms.ModelChoiceField(
        queryset=LeaveType.objects.all(),
        required=False,
        label='نوع الإجازة',
        widget=forms.Select(attrs={'class': 'select2'})
    )
    status = forms.ChoiceField(
        choices=[
            ('', '----'),
            ('pending', 'قيد الانتظار'),
            ('approved', 'تمت الموافقة'),
            ('rejected', 'مرفوضة'),
            ('cancelled', 'ملغاة'),
        ],
        required=False,
        label='الحالة'
    )
    date_from = forms.DateField(
        required=False,
        label='من تاريخ',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        label='إلى تاريخ',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
