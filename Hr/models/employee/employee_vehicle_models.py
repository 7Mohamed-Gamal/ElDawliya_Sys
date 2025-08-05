"""
نماذج سيارات الموظفين - النسخة المحسنة
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from datetime import date, timedelta
from decimal import Decimal


class EmployeeVehicleEnhanced(models.Model):
    """نموذج سيارات الموظفين المحسن"""
    
    VEHICLE_TYPE_CHOICES = [
        ('company', _('سيارة الشركة')),
        ('personal', _('سيارة شخصية')),
        ('allowance', _('بدل سيارة')),
        ('rental', _('سيارة مستأجرة')),
        ('lease', _('سيارة مؤجرة')),
        ('pool', _('سيارة مشتركة')),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('gasoline', _('بنزين')),
        ('diesel', _('ديزل')),
        ('hybrid', _('هجين')),
        ('electric', _('كهربائي')),
        ('lpg', _('غاز')),
        ('cng', _('غاز طبيعي')),
    ]
    
    STATUS_CHOICES = [
        ('assigned', _('مخصصة')),
        ('available', _('متاحة')),
        ('maintenance', _('في الصيانة')),
        ('retired', _('خارج الخدمة')),
        ('sold', _('مباعة')),
        ('accident', _('في حادث')),
        ('repair', _('في الإصلاح')),
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', _('يدوي')),
        ('automatic', _('أوتوماتيك')),
        ('cvt', _('CVT')),
        ('semi_automatic', _('نصف أوتوماتيك')),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', _('ممتازة')),
        ('very_good', _('جيدة جداً')),
        ('good', _('جيدة')),
        ('fair', _('مقبولة')),
        ('poor', _('سيئة')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        'Hr.EmployeeEnhanced', 
        on_delete=models.CASCADE, 
        related_name='vehicle_records_enhanced', 
        verbose_name=_('الموظف')
    )
    
    # Vehicle Information
    vehicle_type = models.CharField(
        max_length=20, 
        choices=VEHICLE_TYPE_CHOICES, 
        verbose_name=_('نوع السيارة')
    )
    
    make = models.CharField(
        max_length=100, 
        verbose_name=_('الماركة')
    )
    
    model = models.CharField(
        max_length=100, 
        verbose_name=_('الموديل')
    )
    
    year = models.PositiveIntegerField(
        verbose_name=_('سنة الصنع'),
        validators=[
            MinValueValidator(1950),
            MaxValueValidator(date.today().year + 2)
        ]
    )
    
    license_plate = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name=_('رقم اللوحة')
    )
    
    vin_number = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        verbose_name=_('رقم الشاسيه'),
        help_text=_('رقم تعريف السيارة (VIN)')
    )
    
    color = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name=_('اللون')
    )
    
    fuel_type = models.CharField(
        max_length=20, 
        choices=FUEL_TYPE_CHOICES, 
        verbose_name=_('نوع الوقود')
    )
    
    engine_size = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name=_('حجم المحرك')
    )
    
    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES,
        blank=True,
        null=True,
        verbose_name=_('نوع ناقل الحركة')
    )
    
    doors_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('عدد الأبواب'),
        validators=[MinValueValidator(2), MaxValueValidator(6)]
    )
    
    seats_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('عدد المقاعد'),
        validators=[MinValueValidator(2), MaxValueValidator(50)]
    )
    
    # Assignment Information
    assigned_date = models.DateField(
        verbose_name=_('تاريخ التخصيص')
    )
    
    return_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('تاريخ الإرجاع')
    )
    
    assignment_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('سبب التخصيص')
    )
    
    # Financial Information
    monthly_allowance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name=_('البدل الشهري'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    purchase_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name=_('سعر الشراء'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    current_value = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name=_('القيمة الحالية'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    depreciation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('معدل الاستهلاك السنوي (%)'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    
    # Legal Information
    insurance_company = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name=_('شركة التأمين')
    )
    
    insurance_policy_number = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name=_('رقم بوليصة التأمين')
    )
    
    insurance_expiry = models.DateField(
        verbose_name=_('تاريخ انتهاء التأمين')
    )
    
    insurance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('مبلغ التأمين'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    registration_expiry = models.DateField(
        verbose_name=_('تاريخ انتهاء الاستمارة')
    )
    
    license_expiry = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('تاريخ انتهاء الرخصة')
    )
    
    # Maintenance Information
    last_maintenance_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('تاريخ آخر صيانة')
    )
    
    next_maintenance_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('تاريخ الصيانة القادمة')
    )
    
    maintenance_interval_km = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('فترة الصيانة (كم)'),
        validators=[MinValueValidator(1000), MaxValueValidator(50000)]
    )
    
    mileage = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        verbose_name=_('عدد الكيلومترات'),
        validators=[MaxValueValidator(2000000)]
    )
    
    last_mileage_update = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ آخر تحديث للكيلومترات')
    )
    
    fuel_consumption_per_100km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('استهلاك الوقود لكل 100 كم'),
        validators=[MinValueValidator(Decimal('1')), MaxValueValidator(Decimal('50'))]
    )
    
    # Condition and Status
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        blank=True,
        null=True,
        verbose_name=_('حالة السيارة')
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='assigned', 
        verbose_name=_('الحالة')
    )
    
    is_active = models.BooleanField(
        default=True, 
        verbose_name=_('نشط')
    )
    
    # GPS and Tracking
    has_gps = models.BooleanField(
        default=False,
        verbose_name=_('يحتوي على GPS')
    )
    
    gps_device_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('معرف جهاز GPS')
    )
    
    # Additional Features
    features = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('المميزات الإضافية'),
        help_text=_('مكيف، راديو، نظام ملاحة، إلخ')
    )
    
    # Additional Information
    notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_('ملاحظات')
    )
    
    # Files
    registration_document = models.FileField(
        upload_to='vehicles/registration/',
        blank=True,
        null=True,
        verbose_name=_('وثيقة التسجيل')
    )
    
    insurance_document = models.FileField(
        upload_to='vehicles/insurance/',
        blank=True,
        null=True,
        verbose_name=_('وثيقة التأمين')
    )
    
    vehicle_photos = models.FileField(
        upload_to='vehicles/photos/',
        blank=True,
        null=True,
        verbose_name=_('صور السيارة')
    )
    
    # Approval Information
    approved_by = models.ForeignKey(
        'accounts.Users_Login_New',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_vehicle_records',
        verbose_name=_('تم الاعتماد بواسطة')
    )
    
    approval_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ الاعتماد')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('تاريخ الإنشاء')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name=_('تاريخ التحديث')
    )
    
    created_by = models.ForeignKey(
        'accounts.Users_Login_New',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='created_vehicle_records',
        verbose_name=_('تم الإنشاء بواسطة')
    )

    class Meta:
        verbose_name = _('سيارة موظف محسنة')
        verbose_name_plural = _('سيارات الموظفين المحسنة')
        ordering = ['employee', '-assigned_date']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['license_plate']),
            models.Index(fields=['vehicle_type']),
            models.Index(fields=['status']),
            models.Index(fields=['insurance_expiry']),
            models.Index(fields=['registration_expiry']),
            models.Index(fields=['make', 'model']),
            models.Index(fields=['year']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(return_date__gte=models.F('assigned_date')),
                name='return_after_assignment'
            ),
            models.CheckConstraint(
                check=models.Q(current_value__lte=models.F('purchase_price')),
                name='current_value_realistic'
            ),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.make} {self.model} ({self.license_plate})"

    @property
    def insurance_days_remaining(self):
        """عدد الأيام المتبقية على انتهاء التأمين"""
        return (self.insurance_expiry - timezone.now().date()).days

    @property
    def registration_days_remaining(self):
        """عدد الأيام المتبقية على انتهاء الاستمارة"""
        return (self.registration_expiry - timezone.now().date()).days
    
    @property
    def license_days_remaining(self):
        """عدد الأيام المتبقية على انتهاء الرخصة"""
        if not self.license_expiry:
            return None
        return (self.license_expiry - timezone.now().date()).days

    @property
    def needs_maintenance(self):
        """هل تحتاج السيارة لصيانة"""
        if not self.next_maintenance_date:
            return False
        return timezone.now().date() >= self.next_maintenance_date
    
    @property
    def maintenance_overdue_days(self):
        """عدد أيام تأخير الصيانة"""
        if not self.next_maintenance_date:
            return 0
        overdue = (timezone.now().date() - self.next_maintenance_date).days
        return max(0, overdue)
    
    @property
    def vehicle_age_years(self):
        """عمر السيارة بالسنوات"""
        return date.today().year - self.year
    
    @property
    def assignment_duration_days(self):
        """مدة التخصيص بالأيام"""
        end_date = self.return_date or date.today()
        return (end_date - self.assigned_date).days
    
    @property
    def is_insurance_expiring_soon(self, warning_days=30):
        """هل ينتهي التأمين قريباً"""
        return 0 <= self.insurance_days_remaining <= warning_days
    
    @property
    def is_registration_expiring_soon(self, warning_days=30):
        """هل تنتهي الاستمارة قريباً"""
        return 0 <= self.registration_days_remaining <= warning_days
    
    @property
    def is_license_expiring_soon(self, warning_days=30):
        """هل تنتهي الرخصة قريباً"""
        if not self.license_expiry:
            return False
        days_left = self.license_days_remaining
        return days_left is not None and 0 <= days_left <= warning_days
    
    @property
    def estimated_current_value(self):
        """القيمة المقدرة الحالية بناءً على الاستهلاك"""
        if not self.purchase_price or not self.depreciation_rate:
            return self.current_value
        
        years_owned = self.vehicle_age_years
        depreciation_factor = (1 - (self.depreciation_rate / 100)) ** years_owned
        return self.purchase_price * depreciation_factor
    
    @property
    def monthly_cost(self):
        """التكلفة الشهرية الإجمالية"""
        cost = self.monthly_allowance
        
        # إضافة تكلفة الاستهلاك الشهري
        if self.purchase_price and self.depreciation_rate:
            monthly_depreciation = (self.purchase_price * self.depreciation_rate / 100) / 12
            cost += monthly_depreciation
        
        return cost
    
    @property
    def fuel_efficiency_rating(self):
        """تقييم كفاءة الوقود"""
        if not self.fuel_consumption_per_100km:
            return None
        
        consumption = float(self.fuel_consumption_per_100km)
        if consumption <= 6:
            return _('ممتاز')
        elif consumption <= 8:
            return _('جيد جداً')
        elif consumption <= 10:
            return _('جيد')
        elif consumption <= 12:
            return _('مقبول')
        else:
            return _('ضعيف')
    
    @property
    def needs_maintenance_by_mileage(self):
        """هل تحتاج صيانة بناءً على الكيلومترات"""
        if not self.mileage or not self.maintenance_interval_km or not self.last_maintenance_date:
            return False
        
        # حساب الكيلومترات منذ آخر صيانة (تقدير)
        days_since_maintenance = (date.today() - self.last_maintenance_date).days
        estimated_km_since = days_since_maintenance * 50  # تقدير 50 كم يومياً
        
        return estimated_km_since >= self.maintenance_interval_km

    def clean(self):
        """التحقق من صحة البيانات"""
        errors = {}
        
        if self.return_date and self.assigned_date > self.return_date:
            errors['return_date'] = _('تاريخ الإرجاع لا يمكن أن يكون قبل تاريخ التخصيص')
        
        if self.year > date.today().year + 1:
            errors['year'] = _('سنة الصنع لا يمكن أن تكون في المستقبل البعيد')
        
        if self.current_value and self.purchase_price and self.current_value > self.purchase_price:
            errors['current_value'] = _('القيمة الحالية لا يمكن أن تكون أكبر من سعر الشراء')
        
        if self.next_maintenance_date and self.last_maintenance_date:
            if self.next_maintenance_date <= self.last_maintenance_date:
                errors['next_maintenance_date'] = _('تاريخ الصيانة القادمة يجب أن يكون بعد آخر صيانة')
        
        if self.insurance_expiry < date.today():
            errors['insurance_expiry'] = _('تأمين السيارة منتهي الصلاحية')
        
        if self.registration_expiry < date.today():
            errors['registration_expiry'] = _('استمارة السيارة منتهية الصلاحية')
        
        if errors:
            raise ValidationError(errors)
    
    def calculate_next_maintenance_date(self):
        """حساب تاريخ الصيانة القادمة"""
        if not self.last_maintenance_date or not self.maintenance_interval_km:
            return None
        
        # تقدير بناءً على متوسط 50 كم يومياً
        days_to_next_maintenance = self.maintenance_interval_km / 50
        return self.last_maintenance_date + timedelta(days=int(days_to_next_maintenance))
    
    def update_mileage(self, new_mileage):
        """تحديث عدد الكيلومترات"""
        if new_mileage > (self.mileage or 0):
            self.mileage = new_mileage
            self.last_mileage_update = date.today()
            
            # تحديث تاريخ الصيانة القادمة إذا لزم الأمر
            if self.needs_maintenance_by_mileage:
                self.next_maintenance_date = self.calculate_next_maintenance_date()
            
            self.save()
    
    def perform_maintenance(self, maintenance_type, cost=None, notes=None):
        """تسجيل صيانة جديدة"""
        self.last_maintenance_date = date.today()
        self.next_maintenance_date = self.calculate_next_maintenance_date()
        
        if notes:
            self.notes = f"{self.notes or ''}\nصيانة {date.today()}: {maintenance_type} - {notes}"
        
        if self.status == 'maintenance':
            self.status = 'assigned'
        
        self.save()
    
    def return_vehicle(self, return_reason=None):
        """إرجاع السيارة"""
        self.return_date = date.today()
        self.status = 'available'
        
        if return_reason:
            self.notes = f"{self.notes or ''}\nتم الإرجاع {date.today()}: {return_reason}"
        
        self.save()
    
    def assign_to_employee(self, new_employee, assignment_reason=None):
        """تخصيص السيارة لموظف جديد"""
        # إرجاع السيارة من الموظف الحالي
        if self.employee and not self.return_date:
            self.return_vehicle("تخصيص لموظف آخر")
        
        # تخصيص للموظف الجديد
        self.employee = new_employee
        self.assigned_date = date.today()
        self.return_date = None
        self.status = 'assigned'
        
        if assignment_reason:
            self.assignment_reason = assignment_reason
            self.notes = f"{self.notes or ''}\nتم التخصيص {date.today()}: {assignment_reason}"
        
        self.save()
    
    def get_upcoming_expirations(self, warning_days=30):
        """الوثائق التي ستنتهي صلاحيتها قريباً"""
        upcoming = []
        today = date.today()
        
        documents = [
            ('insurance', self.insurance_expiry, 'تأمين السيارة'),
            ('registration', self.registration_expiry, 'استمارة السيارة'),
            ('license', self.license_expiry, 'رخصة السيارة'),
        ]
        
        for doc_type, expiry_date, doc_name in documents:
            if expiry_date:
                days_remaining = (expiry_date - today).days
                if 0 <= days_remaining <= warning_days:
                    upcoming.append({
                        'document_type': doc_type,
                        'document_name': doc_name,
                        'expiry_date': expiry_date,
                        'days_remaining': days_remaining
                    })
        
        return upcoming
    
    def calculate_total_cost_of_ownership(self):
        """حساب إجمالي تكلفة الملكية"""
        total_cost = 0
        
        # تكلفة الشراء
        if self.purchase_price:
            total_cost += self.purchase_price
        
        # البدل الشهري
        months_owned = self.assignment_duration_days / 30
        total_cost += self.monthly_allowance * months_owned
        
        # تكلفة التأمين (تقدير)
        if self.insurance_amount:
            years_owned = self.assignment_duration_days / 365
            total_cost += self.insurance_amount * years_owned
        
        return total_cost

    def save(self, *args, **kwargs):
        """تجاوز الحفظ للتحقق من البيانات وتحديث الحالة"""
        # تحديث تاريخ الصيانة القادمة تلقائياً
        if self.last_maintenance_date and self.maintenance_interval_km and not self.next_maintenance_date:
            self.next_maintenance_date = self.calculate_next_maintenance_date()
        
        # تحديث القيمة الحالية المقدرة
        if not self.current_value and self.purchase_price and self.depreciation_rate:
            self.current_value = self.estimated_current_value
        
        self.full_clean()
        super().save(*args, **kwargs)