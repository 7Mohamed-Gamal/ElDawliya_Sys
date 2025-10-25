from django import forms
from Hr.models.leave.leave_type_models import LeaveType
from Hr.models.employee.employee_models import Employee

class LeaveFilterForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status=Employee.ACTIVE),
        required=False,
        label='الموظف',
        widget=forms.Select(attrs={'class': 'select2'}),
        empty_label='كل الموظفين'
    )
    leave_type = forms.ModelChoiceField(
        queryset=LeaveType.objects.filter(is_active=True),
        required=False,
        label='نوع الإجازة',
        widget=forms.Select(attrs={'class': 'select2'}),
        empty_label='كل الأنواع'
    )
    status = forms.ChoiceField(
        choices=[
            ('', '----'),
            ('pending_approval', 'قيد الانتظار'),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].label_from_instance = lambda obj: obj.full_name
