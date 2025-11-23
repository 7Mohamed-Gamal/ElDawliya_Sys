"""
نماذج الإجازات المحسنة
Enhanced Leave Models
"""
from decimal import Decimal
from datetime import date, timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .base import BaseModel, AuditableModel
from .hr import Employee


class LeaveType(BaseModel):
    """أنواع الإجازات المحسنة"""
    CALCULATION_METHODS = [
        ('days', _('بالأيام')),
        ('hours', _('بالساعات')),
        ('half_days', _('بأنصاف الأيام')),
    ]
    
    ACCRUAL_FREQUENCY = [
        ('monthly', _('شهري')),
        ('quarterly', _('ربع سنوي')),
        ('yearly', _('سنوي')),
        ('on_hire', _('عند التعيين')),
        ('manual', _('يدوي')),
    ]
    
    GENDER_RESTRICTION = [
        ('all', _('جميع الموظفين')),
        ('male', _('ذكور فقط')),
        ('female', _('إناث فقط')),
    ]
    
    name = models.CharField(max_length=100, verbose_name=_('اسم نوع الإجازة'))
    name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('رمز الإجازة'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    
    # Basic Settings
    is_paid = models.BooleanField(default=True, verbose_name=_('إجازة مدفوعة الأجر'))
    calculation_method = models.CharField(max_length=20, choices=CALCULATION_METHODS, default='days', verbose_name=_('طريقة الحساب'))
    max_days_per_year = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True, verbose_name=_('الحد الأقصى سنوياً'))
    max_consecutive_days = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('الحد الأقصى للأيام المتتالية'))
    
    # Accrual Settings
    accrual_frequency = models.CharField(max_length=20, choices=ACCRUAL_FREQUENCY, default='yearly', verbose_name=_('تكرار الاستحقاق'))
    accrual_rate = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('1.0'), verbose_name=_('معدل الاستحقاق'))
    
    # Carry Forward Settings
    can_carry_forward = models.BooleanField(default=False, verbose_name=_('يمكن ترحيلها'))
    max_carry_forward_days = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name=_('الحد الأقصى للترحيل'))
    carry_forward_expiry_months = models.PositiveIntegerField(default=12, verbose_name=_('انتهاء الترحيل (بالشهور)'))
    
    # Eligibility Requirements
    minimum_service_months = models.PositiveIntegerField(default=0, verbose_name=_('الحد الأدنى للخدمة (شهور)'))
    gender_restriction = models.CharField(max_length=10, choices=GENDER_RESTRICTION, default='all', verbose_name=_('قيود الجنس'))
    
    # Approval Settings
    requires_approval = models.BooleanField(default=True, verbose_name=_('تتطلب موافقة'))
    advance_notice_days = models.PositiveIntegerField(default=0, verbose_name=_('إشعار مسبق (أيام)'))
    requires_medical_certificate = models.BooleanField(default=False, verbose_name=_('تتطلب شهادة طبية'))
    requires_replacement = models.BooleanField(default=False, verbose_name=_('تتطلب بديل'))
    
    # System Settings
    affects_attendance = models.BooleanField(default=True, verbose_name=_('تؤثر على الحضور'))
    excludes_holidays = models.BooleanField(default=True, verbose_name=_('استثناء العطل الرسمية'))
    excludes_weekends = models.BooleanField(default=True, verbose_name=_('استثناء نهاية الأسبوع'))
    
    # Display Settings
    color_code = models.CharField(max_length=7, default='#007bff', verbose_name=_('لون العرض'))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('ترتيب العرض'))
    
    class Meta:
        verbose_name = _('نوع إجازة')
        verbose_name_plural = _('أنواع الإجازات')
        ordering = ['sort_order', 'name']
        
    def __str__(self):
        return self.name
    
    def is_eligible_for_employee(self, employee):
        """فحص أهلية الموظف لهذا النوع من الإجازات"""
        # فحص الجنس
        if self.gender_restriction != 'all':
            if self.gender_restriction == 'male' and employee.gender != 'M':
                return False, _('هذا النوع من الإجازات مخصص للذكور فقط')
            if self.gender_restriction == 'female' and employee.gender != 'F':
                return False, _('هذا النوع من الإجازات مخصص للإناث فقط')
        
        # فحص سنوات الخدمة
        if self.minimum_service_months > 0:
            if employee.months_of_service < self.minimum_service_months:
                return False, _('الحد الأدنى للخدمة المطلوب: {} شهر').format(self.minimum_service_months)
        
        return True, None
    
    def calculate_accrual_for_employee(self, employee, period_months=1):
        """حساب استحقاق الإجازة للموظف"""
        if not self.is_eligible_for_employee(employee)[0]:
            return 0
        
        if self.accrual_frequency == 'monthly':
            return float(self.accrual_rate) * period_months
        elif self.accrual_frequency == 'quarterly':
            return float(self.accrual_rate) * (period_months // 3)
        elif self.accrual_frequency == 'yearly':
            return float(self.accrual_rate) * (period_months // 12)
        elif self.accrual_frequency == 'on_hire':
            return float(self.accrual_rate) if employee.months_of_service == 0 else 0
        
        return 0


class LeaveBalance(BaseModel):
    """أرصدة الإجازات المحسنة"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances', verbose_name=_('الموظف'))
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='employee_balances', verbose_name=_('نوع الإجازة'))
    year = models.PositiveIntegerField(verbose_name=_('السنة'))
    
    # Balance Details
    allocated_days = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name=_('الأيام المخصصة'))
    used_days = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name=_('الأيام المستخدمة'))
    carried_forward = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name=_('المرحل من العام السابق'))
    pending_days = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name=_('الأيام المعلقة'))
    
    # Adjustment Fields
    manual_adjustment = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name=_('تعديل يدوي'))
    adjustment_reason = models.TextField(blank=True, null=True, verbose_name=_('سبب التعديل'))
    adjusted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='adjusted_balances', verbose_name=_('عُدل بواسطة'))
    
    # Expiry Information
    expires_at = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء الصلاحية'))
    
    class Meta:
        verbose_name = _('رصيد إجازة')
        verbose_name_plural = _('أرصدة الإجازات')
        unique_together = ['employee', 'leave_type', 'year']
        ordering = ['-year', 'leave_type__sort_order']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type.name} ({self.year})"
    
    @property
    def total_available(self):
        """إجمالي الأيام المتاحة"""
        return self.allocated_days + self.carried_forward + self.manual_adjustment
    
    @property
    def remaining_days(self):
        """الأيام المتبقية"""
        return max(Decimal('0'), self.total_available - self.used_days - self.pending_days)
    
    @property
    def utilization_rate(self):
        """معدل الاستخدام"""
        if self.total_available > 0:
            return (self.used_days / self.total_available) * 100
        return 0
    
    def can_take_leave(self, days_requested):
        """فحص إمكانية أخذ الإجازة المطلوبة"""
        return self.remaining_days >= Decimal(str(days_requested))
    
    def reserve_days(self, days_to_reserve):
        """حجز أيام للطلبات المعلقة"""
        if self.can_take_leave(days_to_reserve):
            self.pending_days += Decimal(str(days_to_reserve))
            self.save()
            return True
        return False
    
    def use_days(self, days_to_use):
        """استخدام أيام الإجازة"""
        days_decimal = Decimal(str(days_to_use))
        if self.pending_days >= days_decimal:
            self.pending_days -= days_decimal
            self.used_days += days_decimal
            self.save()
            return True
        return False
    
    def restore_days(self, days_to_restore):
        """استرداد أيام الإجازة (عند الإلغاء)"""
        days_decimal = Decimal(str(days_to_restore))
        self.used_days = max(Decimal('0'), self.used_days - days_decimal)
        self.save()
    
    def release_reserved_days(self, days_to_release):
        """إلغاء حجز الأيام"""
        days_decimal = Decimal(str(days_to_release))
        self.pending_days = max(Decimal('0'), self.pending_days - days_decimal)
        self.save()


class LeaveRequest(AuditableModel):
    """طلبات الإجازات المحسنة"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('submitted', _('مقدم')),
        ('under_review', _('قيد المراجعة')),
        ('approved', _('معتمد')),
        ('rejected', _('مرفوض')),
        ('cancelled', _('ملغى')),
        ('expired', _('منتهي الصلاحية')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('منخفض')),
        ('normal', _('عادي')),
        ('high', _('عالي')),
        ('urgent', _('عاجل')),
    ]
    
    # Basic Information
    request_number = models.CharField(max_length=20, unique=True, verbose_name=_('رقم الطلب'))
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests', verbose_name=_('الموظف'))
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, verbose_name=_('نوع الإجازة'))
    
    # Leave Details
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    duration_days = models.DecimalField(max_digits=6, decimal_places=1, verbose_name=_('عدد الأيام'))
    reason = models.TextField(verbose_name=_('سبب الإجازة'))
    
    # Additional Information
    emergency_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('جهة الاتصال للطوارئ'))
    replacement_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True,
                                           related_name='replacement_requests', verbose_name=_('الموظف البديل'))
    handover_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات تسليم العمل'))
    
    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('الحالة'))
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name=_('الأولوية'))
    
    # Attachments
    medical_certificate = models.FileField(upload_to='leave_requests/medical/', blank=True, null=True, verbose_name=_('الشهادة الطبية'))
    supporting_documents = models.FileField(upload_to='leave_requests/documents/', blank=True, null=True, verbose_name=_('مستندات داعمة'))
    
    # Workflow
    submitted_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ التقديم'))
    reviewed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='reviewed_leave_requests', verbose_name=_('راجعه'))
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ المراجعة'))
    review_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات المراجعة'))
    
    # System Fields
    balance_reserved = models.BooleanField(default=False, verbose_name=_('تم حجز الرصيد'))
    auto_calculated_duration = models.BooleanField(default=True, verbose_name=_('حساب المدة تلقائياً'))
    
    class Meta:
        verbose_name = _('طلب إجازة')
        verbose_name_plural = _('طلبات الإجازات')
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.request_number} - {self.employee.get_full_name()}'
    
    def save(self, *args, **kwargs):
        """حفظ محسن مع توليد رقم الطلب وحساب المدة"""
        if not self.request_number:
            self._generate_request_number()
        
        if self.auto_calculated_duration:
            self._calculate_duration()
        
        super().save(*args, **kwargs)
    
    def _generate_request_number(self):
        """توليد رقم طلب تلقائي"""
        year = date.today().year
        count = LeaveRequest.objects.filter(created_at__year=year).count() + 1
        self.request_number = f'LR{year}{count:04d}'
    
    def _calculate_duration(self):
        """حساب مدة الإجازة"""
        if self.start_date and self.end_date:
            total_days = (self.end_date - self.start_date).days + 1
            
            # خصم العطل الرسمية إذا كان مطلوباً
            if self.leave_type.excludes_holidays:
                holidays = PublicHoliday.get_holidays_in_range(self.start_date, self.end_date)
                total_days -= len(holidays)
            
            # خصم نهاية الأسبوع إذا كان مطلوباً
            if self.leave_type.excludes_weekends:
                weekend_days = self._count_weekend_days()
                total_days -= weekend_days
            
            self.duration_days = max(Decimal('0'), Decimal(str(total_days)))
    
    def _count_weekend_days(self):
        """حساب أيام نهاية الأسبوع في فترة الإجازة"""
        weekend_count = 0
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # افتراض أن الجمعة والسبت هما نهاية الأسبوع (4=الجمعة, 5=السبت)
            if current_date.weekday() in [4, 5]:
                weekend_count += 1
            current_date += timedelta(days=1)
        
        return weekend_count
    
    def submit(self):
        """تقديم الطلب"""
        if self.status == 'draft':
            # التحقق من الأهلية
            eligible, error_msg = self.leave_type.is_eligible_for_employee(self.employee)
            if not eligible:
                raise ValidationError(error_msg)
            
            # التحقق من الرصيد
            balance = self._get_or_create_balance()
            if not balance.can_take_leave(self.duration_days):
                raise ValidationError(_('رصيد الإجازة غير كافي'))
            
            # حجز الرصيد
            if balance.reserve_days(self.duration_days):
                self.balance_reserved = True
                self.status = 'submitted'
                self.submitted_at = timezone.now()
                self.save()
            else:
                raise ValidationError(_('فشل في حجز رصيد الإجازة'))
    
    def approve(self, reviewer, notes=None):
        """اعتماد الطلب"""
        if self.status in ['submitted', 'under_review']:
            # استخدام الأيام المحجوزة
            balance = self._get_or_create_balance()
            if balance.use_days(self.duration_days):
                self.status = 'approved'
                self.reviewed_by = reviewer
                self.reviewed_at = timezone.now()
                if notes:
                    self.review_notes = notes
                self.save()
                
                # إنشاء سجل الإجازة
                self._create_leave_record()
            else:
                raise ValidationError(_('فشل في استخدام رصيد الإجازة'))
    
    def reject(self, reviewer, reason):
        """رفض الطلب"""
        if self.status in ['submitted', 'under_review']:
            # إلغاء حجز الرصيد
            if self.balance_reserved:
                balance = self._get_or_create_balance()
                balance.release_reserved_days(self.duration_days)
                self.balance_reserved = False
            
            self.status = 'rejected'
            self.reviewed_by = reviewer
            self.reviewed_at = timezone.now()
            self.review_notes = reason
            self.save()
    
    def cancel(self):
        """إلغاء الطلب"""
        if self.status in ['draft', 'submitted', 'under_review']:
            # إلغاء حجز الرصيد
            if self.balance_reserved:
                balance = self._get_or_create_balance()
                balance.release_reserved_days(self.duration_days)
                self.balance_reserved = False
            
            self.status = 'cancelled'
            self.save()
        elif self.status == 'approved' and self.start_date > date.today():
            # يمكن إلغاء الإجازة المعتمدة إذا لم تبدأ بعد
            balance = self._get_or_create_balance()
            balance.restore_days(self.duration_days)
            self.status = 'cancelled'
            self.save()
            
            # حذف سجل الإجازة إذا وُجد
            LeaveRecord.objects.filter(leave_request=self).delete()
    
    def _get_or_create_balance(self):
        """الحصول على أو إنشاء رصيد الإجازة"""
        balance, created = LeaveBalance.objects.get_or_create(
            employee=self.employee,
            leave_type=self.leave_type,
            year=self.start_date.year,
            defaults={
                'allocated_days': self.leave_type.max_days_per_year or 0,
                'created_by': self.employee.user_account
            }
        )
        return balance
    
    def _create_leave_record(self):
        """إنشاء سجل الإجازة"""
        LeaveRecord.objects.create(
            employee=self.employee,
            leave_type=self.leave_type,
            leave_request=self,
            start_date=self.start_date,
            end_date=self.end_date,
            duration_days=self.duration_days,
            reason=self.reason,
            approved_by=self.reviewed_by,
            created_by=self.employee.user_account
        )
    
    def clean(self):
        """التحقق من صحة البيانات"""
        errors = {}
        
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                errors['end_date'] = _('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')
            
            # التحقق من الحد الأقصى للأيام المتتالية
            if self.leave_type.max_consecutive_days:
                if self.duration_days > self.leave_type.max_consecutive_days:
                    errors['duration_days'] = _('تجاوز الحد الأقصى للأيام المتتالية: {}').format(self.leave_type.max_consecutive_days)
            
            # التحقق من الإشعار المسبق
            if self.leave_type.advance_notice_days > 0:
                notice_date = date.today() + timedelta(days=self.leave_type.advance_notice_days)
                if self.start_date < notice_date:
                    errors['start_date'] = _('يجب تقديم إشعار مسبق {} يوم على الأقل').format(self.leave_type.advance_notice_days)
        
        # التحقق من الشهادة الطبية
        if self.leave_type.requires_medical_certificate and not self.medical_certificate:
            errors['medical_certificate'] = _('هذا النوع من الإجازات يتطلب شهادة طبية')
        
        # التحقق من البديل
        if self.leave_type.requires_replacement and not self.replacement_employee:
            errors['replacement_employee'] = _('هذا النوع من الإجازات يتطلب تحديد بديل')
        
        if errors:
            raise ValidationError(errors)


class LeaveRecord(BaseModel):
    """سجل الإجازات الفعلية"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_records', verbose_name=_('الموظف'))
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, verbose_name=_('نوع الإجازة'))
    leave_request = models.OneToOneField(LeaveRequest, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('طلب الإجازة'))
    
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    duration_days = models.DecimalField(max_digits=6, decimal_places=1, verbose_name=_('عدد الأيام'))
    reason = models.TextField(verbose_name=_('السبب'))
    
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_leave_records', verbose_name=_('معتمد بواسطة'))
    
    class Meta:
        verbose_name = _('سجل إجازة')
        verbose_name_plural = _('سجلات الإجازات')
        ordering = ['-start_date']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type.name} ({self.start_date})"
    
    @property
    def is_current(self):
        """فحص إذا كانت الإجازة حالية"""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def is_future(self):
        """فحص إذا كانت الإجازة مستقبلية"""
        return self.start_date > date.today()
    
    @property
    def is_past(self):
        """فحص إذا كانت الإجازة منتهية"""
        return self.end_date < date.today()


class PublicHoliday(BaseModel):
    """العطلات الرسمية المحسنة"""
    name = models.CharField(max_length=200, verbose_name=_('اسم العطلة'))
    name_en = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('الاسم بالإنجليزية'))
    holiday_date = models.DateField(verbose_name=_('تاريخ العطلة'))
    is_recurring = models.BooleanField(default=False, verbose_name=_('عطلة متكررة سنوياً'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    
    class Meta:
        verbose_name = _('عطلة رسمية')
        verbose_name_plural = _('العطلات الرسمية')
        unique_together = ['holiday_date']
        ordering = ['holiday_date']
        
    def __str__(self):
        return f"{self.name} - {self.holiday_date}"
    
    @classmethod
    def is_holiday(cls, check_date):
        """فحص إذا كان التاريخ عطلة رسمية"""
        return cls.objects.filter(
            holiday_date=check_date,
            is_active=True
        ).exists()
    
    @classmethod
    def get_holidays_in_range(cls, start_date, end_date):
        """الحصول على العطلات في فترة محددة"""
        return cls.objects.filter(
            holiday_date__range=[start_date, end_date],
            is_active=True
        ).values_list('holiday_date', flat=True)