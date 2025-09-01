from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Employee, EmployeeBankAccount, EmployeeDocument
from org.models import Department, Job, Branch
from datetime import date, timedelta


class EmployeeForm(forms.ModelForm):
    """نموذج إضافة وتعديل الموظفين"""
    
    class Meta:
        model = Employee
        fields = [
            'emp_code', 'first_name', 'second_name', 'third_name', 'last_name',
            'gender', 'birth_date', 'nationality', 'national_id', 'passport_no',
            'mobile', 'email', 'address', 'hire_date', 'join_date', 'probation_end',
            'job', 'dept', 'branch', 'manager', 'emp_status', 'termination_date', 'notes'
        ]
        
        widgets = {
            'emp_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: EMP001'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم الأول'
            }),
            'second_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم الثاني'
            }),
            'third_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم الثالث'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم العائلة'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('', 'اختر الجنس'),
                ('M', 'ذكر'),
                ('F', 'أنثى')
            ]),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: سعودي'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهوية الوطنية'
            }),
            'passport_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم جواز السفر'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف المحمول'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'العنوان الكامل'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'join_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'probation_end': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'job': forms.Select(attrs={
                'class': 'form-select'
            }),
            'dept': forms.Select(attrs={
                'class': 'form-select'
            }),
            'branch': forms.Select(attrs={
                'class': 'form-select'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select'
            }),
            'emp_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'termination_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تخصيص خيارات القوائم المنسدلة
        self.fields['job'].queryset = Job.objects.filter(is_active=True).order_by('job_title')
        self.fields['dept'].queryset = Department.objects.filter(is_active=True).order_by('dept_name')
        self.fields['branch'].queryset = Branch.objects.filter(is_active=True).order_by('branch_name')
        
        # تخصيص خيارات المدير المباشر (استبعاد الموظف نفسه)
        manager_queryset = Employee.objects.filter(emp_status='Active').order_by('first_name', 'last_name')
        if self.instance and self.instance.pk:
            manager_queryset = manager_queryset.exclude(pk=self.instance.pk)
        self.fields['manager'].queryset = manager_queryset
        
        # إضافة خيار فارغ للحقول الاختيارية
        self.fields['manager'].empty_label = "لا يوجد مدير مباشر"
        self.fields['job'].empty_label = "اختر الوظيفة"
        self.fields['dept'].empty_label = "اختر القسم"
        self.fields['branch'].empty_label = "اختر الفرع"

    def clean_emp_code(self):
        """التحقق من كود الموظف"""
        emp_code = self.cleaned_data.get('emp_code')
        if emp_code:
            # التحقق من عدم تكرار الكود
            existing = Employee.objects.filter(emp_code=emp_code)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('كود الموظف موجود مسبقاً. يرجى اختيار كود آخر.')
        
        return emp_code

    def clean_national_id(self):
        """التحقق من رقم الهوية الوطنية"""
        national_id = self.cleaned_data.get('national_id')
        if national_id:
            # التحقق من عدم تكرار رقم الهوية
            existing = Employee.objects.filter(national_id=national_id)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('رقم الهوية الوطنية موجود مسبقاً.')
        
        return national_id

    def clean_email(self):
        """التحقق من البريد الإلكتروني"""
        email = self.cleaned_data.get('email')
        if email:
            # التحقق من عدم تكرار البريد الإلكتروني
            existing = Employee.objects.filter(email=email)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('البريد الإلكتروني موجود مسبقاً.')
        
        return email

    def clean_birth_date(self):
        """التحقق من تاريخ الميلاد"""
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            # التحقق من أن العمر أكبر من 16 سنة
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 16:
                raise ValidationError('عمر الموظف يجب أن يكون 16 سنة على الأقل.')
            
            if age > 70:
                raise ValidationError('عمر الموظف لا يمكن أن يزيد عن 70 سنة.')
        
        return birth_date

    def clean(self):
        """التحقق الشامل من البيانات"""
        cleaned_data = super().clean()
        hire_date = cleaned_data.get('hire_date')
        join_date = cleaned_data.get('join_date')
        probation_end = cleaned_data.get('probation_end')
        birth_date = cleaned_data.get('birth_date')
        termination_date = cleaned_data.get('termination_date')
        emp_status = cleaned_data.get('emp_status')

        # التحقق من التواريخ
        if hire_date and birth_date:
            age_at_hire = hire_date.year - birth_date.year - ((hire_date.month, hire_date.day) < (birth_date.month, birth_date.day))
            if age_at_hire < 16:
                raise ValidationError('عمر الموظف عند التوظيف يجب أن يكون 16 سنة على الأقل.')

        if hire_date and join_date:
            if join_date < hire_date:
                raise ValidationError('تاريخ المباشرة لا يمكن أن يكون قبل تاريخ التوظيف.')

        if hire_date and probation_end:
            if probation_end <= hire_date:
                raise ValidationError('تاريخ انتهاء فترة التجربة يجب أن يكون بعد تاريخ التوظيف.')

        if termination_date and hire_date:
            if termination_date <= hire_date:
                raise ValidationError('تاريخ انتهاء الخدمة يجب أن يكون بعد تاريخ التوظيف.')

        # التحقق من حالة الموظف
        if emp_status in ['Terminated', 'Resigned'] and not termination_date:
            raise ValidationError('يجب تحديد تاريخ انتهاء الخدمة للموظفين المنتهية خدمتهم.')

        if emp_status not in ['Terminated', 'Resigned'] and termination_date:
            raise ValidationError('لا يمكن تحديد تاريخ انتهاء الخدمة للموظفين النشطين.')

        return cleaned_data


class EmployeeBankAccountForm(forms.ModelForm):
    """نموذج إضافة وتعديل الحسابات البنكية للموظفين"""
    
    class Meta:
        model = EmployeeBankAccount
        fields = ['bank', 'account_no', 'iban']
        
        widgets = {
            'bank': forms.Select(attrs={
                'class': 'form-select'
            }),
            'account_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الحساب البنكي'
            }),
            'iban': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الآيبان'
            })
        }

    def clean_iban(self):
        """التحقق من رقم الآيبان"""
        iban = self.cleaned_data.get('iban')
        if iban:
            # إزالة المسافات والتحقق من الطول
            iban = iban.replace(' ', '').upper()
            if len(iban) < 15 or len(iban) > 34:
                raise ValidationError('رقم الآيبان غير صحيح.')
        
        return iban


class EmployeeDocumentForm(forms.ModelForm):
    """نموذج إضافة وتعديل مستندات الموظفين"""
    
    file_upload = forms.FileField(
        label='الملف',
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif',
            'multiple': False
        }),
        help_text='الحد الأقصى لحجم الملف: 10 ميجابايت. الأنواع المدعومة: PDF, DOC, DOCX, JPG, PNG, GIF'
    )
    
    class Meta:
        model = EmployeeDocument
        fields = ['doc_type', 'doc_name', 'notes']  # file_upload is handled separately
        
        widgets = {
            'doc_type': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('', 'اختر نوع المستند'),
                ('identity', 'بطاقة الهوية'),
                ('passport', 'جواز السفر'),
                ('contract', 'عقد العمل'),
                ('certificate', 'شهادة علمية'),
                ('license', 'رخصة قيادة'),
                ('medical', 'تقرير طبي'),
                ('other', 'أخرى')
            ]),
            'doc_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المستند'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات حول المستند'
            })
        }

    def clean_file_upload(self):
        """التحقق من الملف المرفوع"""
        file = self.cleaned_data.get('file_upload')
        if file:
            # التحقق من حجم الملف (10 ميجابايت كحد أقصى)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('حجم الملف يجب أن يكون أقل من 10 ميجابايت.')

            # التحقق من نوع الملف
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
            file_extension = '.' + file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise ValidationError(f'نوع الملف غير مدعوم. الأنواع المدعومة: {", ".join(allowed_extensions)}')

            # التحقق من اسم الملف
            if len(file.name) > 255:
                raise ValidationError('اسم الملف طويل جداً.')

        return file

    def clean_doc_type(self):
        """التحقق من نوع المستند"""
        doc_type = self.cleaned_data.get('doc_type')
        if not doc_type:
            raise ValidationError('يرجى اختيار نوع المستند.')
        return doc_type


class EmployeeSearchForm(forms.Form):
    """نموذج البحث في الموظفين"""
    
    search = forms.CharField(
        label='البحث',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم الموظف أو الكود أو البريد الإلكتروني'
        })
    )
    
    department = forms.ModelChoiceField(
        label='القسم',
        queryset=Department.objects.filter(is_active=True).order_by('dept_name'),
        required=False,
        empty_label='جميع الأقسام',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    branch = forms.ModelChoiceField(
        label='الفرع',
        queryset=Branch.objects.filter(is_active=True).order_by('branch_name'),
        required=False,
        empty_label='جميع الأفرع',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    job = forms.ModelChoiceField(
        label='الوظيفة',
        queryset=Job.objects.filter(is_active=True).order_by('job_title'),
        required=False,
        empty_label='جميع الوظائف',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    status = forms.ChoiceField(
        label='الحالة',
        choices=[
            ('', 'جميع الحالات'),
            ('Active', 'نشط'),
            ('OnLeave', 'في إجازة'),
            ('Terminated', 'منتهي الخدمة'),
            ('Resigned', 'مستقيل')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class DepartmentForm(forms.ModelForm):
    """نموذج إضافة وتعديل الأقسام"""
    
    class Meta:
        model = Department
        fields = ['dept_name', 'parent_dept', 'branch', 'manager_id', 'is_active']
        
        widgets = {
            'dept_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم القسم'
            }),
            'parent_dept': forms.Select(attrs={
                'class': 'form-select'
            }),
            'branch': forms.Select(attrs={
                'class': 'form-select'
            }),
            'manager_id': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'معرف المدير'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تخصيص خيارات القوائم المنسدلة
        self.fields['parent_dept'].queryset = Department.objects.filter(is_active=True).order_by('dept_name')
        self.fields['branch'].queryset = Branch.objects.filter(is_active=True).order_by('branch_name')
        
        # إضافة خيارات فارغة
        self.fields['parent_dept'].empty_label = "لا يوجد قسم أب"
        self.fields['branch'].empty_label = "اختر الفرع"


class JobForm(forms.ModelForm):
    """نموذج إضافة وتعديل الوظائف"""
    
    class Meta:
        model = Job
        fields = ['job_title', 'job_level', 'basic_salary', 'description', 'is_active']
        
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مسمى الوظيفة'
            }),
            'job_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مستوى الوظيفة (1-10)'
            }),
            'basic_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'الراتب الأساسي',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الوظيفة'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_job_level(self):
        """التحقق من مستوى الوظيفة"""
        job_level = self.cleaned_data.get('job_level')
        if job_level is not None:
            if job_level < 1 or job_level > 10:
                raise ValidationError('مستوى الوظيفة يجب أن يكون بين 1 و 10.')
        
        return job_level

    def clean_basic_salary(self):
        """التحقق من الراتب الأساسي"""
        basic_salary = self.cleaned_data.get('basic_salary')
        if basic_salary is not None:
            if basic_salary < 0:
                raise ValidationError('الراتب الأساسي لا يمكن أن يكون سالباً.')
            
            if basic_salary > 999999.99:
                raise ValidationError('الراتب الأساسي كبير جداً.')
        
        return basic_salary