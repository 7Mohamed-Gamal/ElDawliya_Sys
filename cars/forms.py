from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from .models import Car, Supplier, Trip, Settings, RoutePoint


class CarForm(forms.ModelForm):
    """نموذج إضافة وتعديل السيارات"""
    
    class Meta:
        model = Car
        fields = [
            'car_code', 'car_name', 'car_type', 'supplier', 'fuel_type',
            'passengers_count', 'fuel_consumption_rate', 'car_status'
        ]
        
        widgets = {
            'car_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود السيارة'
            }),
            'car_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم السيارة'
            }),
            'car_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fuel_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'passengers_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '50'
            }),
            'fuel_consumption_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'لتر/كيلومتر'
            }),
            'car_status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        
        labels = {
            'car_code': 'كود السيارة',
            'car_name': 'اسم السيارة',
            'car_type': 'نوع السيارة',
            'supplier': 'المورد',
            'fuel_type': 'نوع الوقود',
            'passengers_count': 'عدد الركاب',
            'fuel_consumption_rate': 'معدل استهلاك الوقود',
            'car_status': 'حالة السيارة'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تخصيص خيارات الموردين
        self.fields['supplier'].queryset = Supplier.objects.all().order_by('name')
        self.fields['supplier'].empty_label = "اختر المورد"

    def clean_car_code(self):
        """التحقق من كود السيارة"""
        car_code = self.cleaned_data.get('car_code')
        if car_code:
            # التحقق من عدم تكرار الكود
            existing = Car.objects.filter(car_code=car_code)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('كود السيارة موجود مسبقاً.')
        
        return car_code

    def clean_passengers_count(self):
        """التحقق من عدد الركاب"""
        passengers_count = self.cleaned_data.get('passengers_count')
        if passengers_count is not None:
            if passengers_count < 1:
                raise ValidationError('عدد الركاب يجب أن يكون أكبر من صفر.')
            if passengers_count > 50:
                raise ValidationError('عدد الركاب كبير جداً.')
        return passengers_count

    def clean_fuel_consumption_rate(self):
        """التحقق من معدل استهلاك الوقود"""
        fuel_consumption_rate = self.cleaned_data.get('fuel_consumption_rate')
        if fuel_consumption_rate is not None:
            if fuel_consumption_rate <= 0:
                raise ValidationError('معدل استهلاك الوقود يجب أن يكون أكبر من صفر.')
            if fuel_consumption_rate > 10:
                raise ValidationError('معدل استهلاك الوقود عالي جداً.')
        return fuel_consumption_rate


class SupplierForm(forms.ModelForm):
    """نموذج إضافة وتعديل الموردين"""
    
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المورد'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الشخص المسؤول'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'العنوان'
            })
        }
        
        labels = {
            'name': 'اسم المورد',
            'contact_person': 'الشخص المسؤول',
            'phone': 'رقم الهاتف',
            'email': 'البريد الإلكتروني',
            'address': 'العنوان'
        }

    def clean_name(self):
        """التحقق من اسم المورد"""
        name = self.cleaned_data.get('name')
        if name:
            # التحقق من عدم تكرار الاسم
            existing = Supplier.objects.filter(name=name)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('اسم المورد موجود مسبقاً.')
        
        return name


class TripForm(forms.ModelForm):
    """نموذج إضافة وتعديل الرحلات"""
    
    class Meta:
        model = Trip
        fields = ['date', 'car', 'distance']
        
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'car': forms.Select(attrs={
                'class': 'form-select'
            }),
            'distance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.1',
                'placeholder': 'المسافة بالكيلومتر'
            })
        }
        
        labels = {
            'date': 'تاريخ الرحلة',
            'car': 'السيارة',
            'distance': 'المسافة (كم)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تخصيص خيارات السيارات (السيارات النشطة فقط)
        self.fields['car'].queryset = Car.objects.filter(
            car_status='active'
        ).order_by('car_code')
        self.fields['car'].empty_label = "اختر السيارة"
        
        # تعيين التاريخ الافتراضي
        if not self.instance.pk:
            self.fields['date'].initial = date.today()

    def clean_date(self):
        """التحقق من تاريخ الرحلة"""
        trip_date = self.cleaned_data.get('date')
        if trip_date:
            # التحقق من أن التاريخ ليس في المستقبل
            if trip_date > date.today():
                raise ValidationError('لا يمكن إضافة رحلة في المستقبل.')
            
            # التحقق من أن التاريخ ليس قديماً جداً
            if trip_date < date.today() - timedelta(days=365):
                raise ValidationError('تاريخ الرحلة قديم جداً.')
        
        return trip_date

    def clean_distance(self):
        """التحقق من المسافة"""
        distance = self.cleaned_data.get('distance')
        if distance is not None:
            if distance <= 0:
                raise ValidationError('المسافة يجب أن تكون أكبر من صفر.')
            if distance > 10000:
                raise ValidationError('المسافة كبيرة جداً.')
        return distance


class SettingsForm(forms.ModelForm):
    """نموذج إعدادات النظام"""
    
    class Meta:
        model = Settings
        fields = [
            'diesel_price', 'gasoline_price', 'gas_price', 'maintenance_rate',
            'depreciation_rate', 'license_rate', 'driver_profit_rate', 'tax_rate'
        ]
        
        widgets = {
            'diesel_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'gasoline_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'gas_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'maintenance_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'depreciation_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'license_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'driver_profit_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            })
        }
        
        labels = {
            'diesel_price': 'سعر الديزل (لتر)',
            'gasoline_price': 'سعر البنزين (لتر)',
            'gas_price': 'سعر الغاز (لتر)',
            'maintenance_rate': 'معدل الصيانة (كم)',
            'depreciation_rate': 'معدل الإهلاك (كم)',
            'license_rate': 'معدل الرخصة (كم)',
            'driver_profit_rate': 'معدل ربح السائق (كم)',
            'tax_rate': 'معدل الضريبة (%)'
        }

    def clean_tax_rate(self):
        """التحقق من معدل الضريبة"""
        tax_rate = self.cleaned_data.get('tax_rate')
        if tax_rate is not None:
            if tax_rate < 0 or tax_rate > 100:
                raise ValidationError('معدل الضريبة يجب أن يكون بين 0 و 100.')
        return tax_rate


class RoutePointForm(forms.ModelForm):
    """نموذج نقاط خط السير"""
    
    class Meta:
        model = RoutePoint
        fields = ['car', 'point_name', 'departure_time', 'order', 'employees']
        
        widgets = {
            'car': forms.Select(attrs={
                'class': 'form-select'
            }),
            'point_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم النقطة'
            }),
            'departure_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'employees': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            })
        }
        
        labels = {
            'car': 'السيارة',
            'point_name': 'اسم النقطة',
            'departure_time': 'وقت المغادرة',
            'order': 'الترتيب',
            'employees': 'الموظفون'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تخصيص خيارات السيارات
        self.fields['car'].queryset = Car.objects.filter(
            car_status='active'
        ).order_by('car_code')
        self.fields['car'].empty_label = "اختر السيارة"
        
        # تخصيص خيارات الموظفين
        from employees.models import Employee
        self.fields['employees'].queryset = Employee.objects.filter(
            emp_status='Active'
        ).order_by('first_name', 'last_name')


class CarSearchForm(forms.Form):
    """نموذج البحث في السيارات"""
    
    search = forms.CharField(
        label='البحث',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'كود السيارة أو اسم السيارة'
        })
    )
    
    car_type = forms.ChoiceField(
        label='نوع السيارة',
        choices=[('', 'جميع الأنواع')] + Car._meta.get_field('car_type').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    supplier = forms.ModelChoiceField(
        label='المورد',
        queryset=Supplier.objects.all().order_by('name'),
        required=False,
        empty_label='جميع الموردين',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    status = forms.ChoiceField(
        label='الحالة',
        choices=[('', 'جميع الحالات')] + Car._meta.get_field('car_status').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class TripSearchForm(forms.Form):
    """نموذج البحث في الرحلات"""
    
    search = forms.CharField(
        label='البحث',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'كود السيارة أو اسم السيارة'
        })
    )
    
    car = forms.ModelChoiceField(
        label='السيارة',
        queryset=Car.objects.all().order_by('car_code'),
        required=False,
        empty_label='جميع السيارات',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    date_from = forms.DateField(
        label='من تاريخ',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        label='إلى تاريخ',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean(self):
        """التحقق من صحة فترة البحث"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

        return cleaned_data


class CarReportForm(forms.Form):
    """نموذج تقارير السيارات"""
    
    REPORT_TYPES = [
        ('summary', 'تقرير ملخص'),
        ('detailed', 'تقرير مفصل'),
        ('cost_analysis', 'تحليل التكلفة'),
        ('usage_analysis', 'تحليل الاستخدام')
    ]
    
    report_type = forms.ChoiceField(
        label='نوع التقرير',
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    car = forms.ModelChoiceField(
        label='السيارة',
        queryset=Car.objects.all().order_by('car_code'),
        required=False,
        empty_label='جميع السيارات',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    car_type = forms.ChoiceField(
        label='نوع السيارة',
        choices=[('', 'جميع الأنواع')] + Car._meta.get_field('car_type').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    date_from = forms.DateField(
        label='من تاريخ',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        label='إلى تاريخ',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تعيين التواريخ الافتراضية
        today = date.today()
        self.fields['date_from'].initial = today.replace(month=1, day=1)  # بداية السنة
        self.fields['date_to'].initial = today

    def clean(self):
        """التحقق من صحة فترة التقرير"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

        return cleaned_data