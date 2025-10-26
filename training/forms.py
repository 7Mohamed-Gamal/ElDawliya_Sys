"""
نماذج (Forms) نظام التدريب
Training Management Forms
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date
from .models import TrainingProvider, TrainingCourse, EmployeeTraining
from employees.models import Employee


class TrainingProviderForm(forms.ModelForm):
    """نموذج إضافة/تعديل مزود تدريب"""
    
    class Meta:
        model = TrainingProvider
        fields = ['provider_name', 'contact_person', 'phone', 'email']
        widgets = {
            'provider_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم مزود التدريب',
                'required': True
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الشخص المسؤول'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني'
            }),
        }
        labels = {
            'provider_name': 'اسم مزود التدريب',
            'contact_person': 'الشخص المسؤول',
            'phone': 'الهاتف',
            'email': 'البريد الإلكتروني',
        }

    def clean_provider_name(self):
        provider_name = self.cleaned_data.get('provider_name')
        if provider_name and len(provider_name) < 3:
            raise ValidationError('اسم مزود التدريب يجب أن يكون 3 أحرف على الأقل')
        return provider_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists (excluding current instance)
            qs = TrainingProvider.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('هذا البريد الإلكتروني مسجل بالفعل')
        return email


class TrainingCourseForm(forms.ModelForm):
    """نموذج إضافة/تعديل دورة تدريبية"""
    
    class Meta:
        model = TrainingCourse
        fields = [
            'course_name', 'provider', 'duration_hours', 'cost',
            'start_date', 'end_date', 'location'
        ]
        widgets = {
            'course_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الدورة التدريبية',
                'required': True
            }),
            'provider': forms.Select(attrs={
                'class': 'form-select'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'عدد الساعات',
                'min': '1'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'التكلفة',
                'step': '0.01',
                'min': '0'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موقع التدريب'
            }),
        }
        labels = {
            'course_name': 'اسم الدورة',
            'provider': 'مزود التدريب',
            'duration_hours': 'عدد الساعات',
            'cost': 'التكلفة',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ الانتهاء',
            'location': 'الموقع',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ البداية')
            
            # Check if start date is not too far in the past
            if start_date < date.today() and (date.today() - start_date).days > 365:
                raise ValidationError('تاريخ البداية قديم جداً')
        
        duration_hours = cleaned_data.get('duration_hours')
        if duration_hours and duration_hours > 1000:
            raise ValidationError('عدد ساعات التدريب يبدو غير منطقي')
        
        return cleaned_data


class EmployeeTrainingForm(forms.ModelForm):
    """نموذج تسجيل موظف في دورة تدريبية"""
    
    STATUS_CHOICES = [
        ('Registered', 'مسجل'),
        ('In Progress', 'جاري'),
        ('Completed', 'مكتمل'),
        ('Cancelled', 'ملغي'),
        ('Failed', 'راسب'),
    ]
    
    GRADE_CHOICES = [
        ('', '-- اختر التقدير --'),
        ('A+', 'ممتاز جداً (A+)'),
        ('A', 'ممتاز (A)'),
        ('B+', 'جيد جداً (B+)'),
        ('B', 'جيد (B)'),
        ('C+', 'مقبول جداً (C+)'),
        ('C', 'مقبول (C)'),
        ('D', 'ضعيف (D)'),
        ('F', 'راسب (F)'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الحالة'
    )
    
    grade = forms.ChoiceField(
        choices=GRADE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='التقدير'
    )
    
    class Meta:
        model = EmployeeTraining
        fields = [
            'emp', 'course', 'enrollment_date', 'status',
            'grade', 'certificate_path', 'notes'
        ]
        widgets = {
            'emp': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'course': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'enrollment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'certificate_path': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مسار ملف الشهادة'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            }),
        }
        labels = {
            'emp': 'الموظف',
            'course': 'الدورة التدريبية',
            'enrollment_date': 'تاريخ التسجيل',
            'status': 'الحالة',
            'grade': 'التقدير',
            'certificate_path': 'مسار الشهادة',
            'notes': 'ملاحظات',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Improve employee dropdown display
        self.fields['emp'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('first_name', 'last_name')
        self.fields['emp'].label_from_instance = lambda obj: f"{obj.emp_code} - {obj.first_name} {obj.last_name}"
        
        # Improve course dropdown display
        self.fields['course'].queryset = TrainingCourse.objects.all().order_by('-start_date')
        self.fields['course'].label_from_instance = lambda obj: f"{obj.course_name} ({obj.start_date})"

    def clean(self):
        cleaned_data = super().clean()
        emp = cleaned_data.get('emp')
        course = cleaned_data.get('course')
        enrollment_date = cleaned_data.get('enrollment_date')
        status = cleaned_data.get('status')
        grade = cleaned_data.get('grade')
        
        # Check if employee is already enrolled in this course
        if emp and course:
            existing = EmployeeTraining.objects.filter(emp=emp, course=course)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError('هذا الموظف مسجل بالفعل في هذه الدورة')
        
        # Validate enrollment date against course dates
        if enrollment_date and course:
            if course.start_date and enrollment_date > course.start_date:
                raise ValidationError('تاريخ التسجيل يجب أن يكون قبل أو في تاريخ بداية الدورة')
        
        # Require grade for completed courses
        if status == 'Completed' and not grade:
            raise ValidationError('يجب إدخال التقدير للدورات المكتملة')
        
        # Don't allow grade for non-completed courses
        if status in ['Registered', 'In Progress', 'Cancelled'] and grade:
            self.add_error('grade', 'لا يمكن إدخال تقدير للدورات غير المكتملة')
        
        return cleaned_data


class EmployeeTrainingSearchForm(forms.Form):
    """نموذج البحث في سجلات التدريب"""
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(emp_status='Active').order_by('first_name'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الموظف'
    )
    
    course = forms.ModelChoiceField(
        queryset=TrainingCourse.objects.all().order_by('-start_date'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الدورة'
    )
    
    status = forms.ChoiceField(
        choices=[('', 'الكل')] + EmployeeTrainingForm.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الحالة'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='من تاريخ'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='إلى تاريخ'
    )

