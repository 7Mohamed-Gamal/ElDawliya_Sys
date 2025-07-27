# =============================================================================
# ElDawliya HR Management System - New Enhanced Models
# =============================================================================
# Additional models for comprehensive HR management
# =============================================================================

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid
from django.core.exceptions import ValidationError
from django.db.models import Q
from cryptography.fernet import Fernet
from django.conf import settings


# =============================================================================
# ENCRYPTED FIELD FOR SENSITIVE DATA
# =============================================================================

class EncryptedField(models.CharField):
    """حقل مشفر للبيانات الحساسة"""
    
    def __init__(self, *args, **kwargs):
        if hasattr(settings, 'FIELD_ENCRYPTION_KEY') and settings.FIELD_ENCRYPTION_KEY:
            self.cipher = Fernet(settings.FIELD_ENCRYPTION_KEY.encode())
        else:
            self.cipher = None
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None or not self.cipher:
            return value
        try:
            return self.cipher.decrypt(value.encode()).decode()
        except:
            return value  # Return as-is if decryption fails
    
    def get_prep_value(self, value):
        if value is None or not self.cipher:
            return value
        try:
            return self.cipher.encrypt(value.encode()).decode()
        except:
            return value


# =============================================================================
# NEW EXTENDED EMPLOYEE MODELS
# =============================================================================

class EmployeeEducation(models.Model):
    """نموذج المؤهلات الدراسية للموظف"""
    
    DEGREE_CHOICES = [
        ('elementary', _('ابتدائية')),
        ('intermediate', _('متوسطة')),
        ('high_school', _('ثانوية عامة')),
        ('diploma', _('دبلوم')),
        ('bachelor', _('بكالوريوس')),
        ('master', _('ماجستير')),
        ('phd', _('دكتوراه')),
        ('certificate', _('شهادة مهنية')),
        ('training', _('دورة تدريبية')),
    ]
    
    GRADE_SYSTEM_CHOICES = [
        ('percentage', _('نسبة مئوية')),
        ('gpa_4', _('GPA من 4')),
        ('gpa_5', _('GPA من 5')),
        ('letter', _('حروف')),
        ('pass_fail', _('نجح/راسب')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='education_records', verbose_name=_('الموظف'))
    
    # Education Details
    degree_type = models.CharField(max_length=20, choices=DEGREE_CHOICES, verbose_name=_('نوع الشهادة'))
    major = models.CharField(max_length=200, verbose_name=_('التخصص'))
    minor = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('التخصص الفرعي'))
    institution = models.CharField(max_length=200, verbose_name=_('الجامعة/المؤسسة'))
    institution_english = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('اسم المؤسسة بالإنجليزية'))
    
    # Academic Information
    graduation_year = models.PositiveIntegerField(verbose_name=_('سنة التخرج'))
    start_year = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('سنة البداية'))
    grade_system = models.CharField(max_length=20, choices=GRADE_SYSTEM_CHOICES, default='percentage', verbose_name=_('نظام الدرجات'))
    grade = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('المعدل/الدرجة'))
    
    # Location
    country = models.CharField(max_length=100, verbose_name=_('الدولة'))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('المدينة'))
    
    # Verification
    is_verified = models.BooleanField(default=False, verbose_name=_('تم التحقق'))
    verification_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ التحقق'))
    verification_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات التحقق'))
    
    # Files
    certificate_file = models.FileField(upload_to='education/certificates/', blank=True, null=True, verbose_name=_('ملف الشهادة'))
    transcript_file = models.FileField(upload_to='education/transcripts/', blank=True, null=True, verbose_name=_('كشف الدرجات'))
    
    # Additional Information
    honors = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('مرتبة الشرف'))
    thesis_title = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('عنوان الرسالة'))
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('مؤهل دراسي')
        verbose_name_plural = _('المؤهلات الدراسية')
        ordering = ['-graduation_year', 'degree_type']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['degree_type']),
            models.Index(fields=['graduation_year']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_degree_type_display()} - {self.major}"

    def clean(self):
        if self.start_year and self.graduation_year and self.start_year > self.graduation_year:
            raise ValidationError(_('سنة البداية لا يمكن أن تكون أكبر من سنة التخرج'))


class EmployeeInsurance(models.Model):
    """نموذج تأمينات الموظف"""
    
    INSURANCE_TYPE_CHOICES = [
        ('social', _('تأمين اجتماعي')),
        ('medical', _('تأمين صحي')),
        ('life', _('تأمين على الحياة')),
        ('disability', _('تأمين ضد العجز')),
        ('unemployment', _('تأمين ضد البطالة')),
        ('professional', _('تأمين مهني')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('suspended', _('موقوف')),
        ('expired', _('منتهي')),
        ('cancelled', _('ملغى')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='insurance_records', verbose_name=_('الموظف'))
    
    # Insurance Details
    insurance_type = models.CharField(max_length=20, choices=INSURANCE_TYPE_CHOICES, verbose_name=_('نوع التأمين'))
    policy_number = models.CharField(max_length=100, verbose_name=_('رقم البوليصة'))
    provider = models.CharField(max_length=200, verbose_name=_('مقدم التأمين'))
    provider_contact = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('جهة الاتصال'))
    
    # Dates
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ النهاية'))
    renewal_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ التجديد'))
    
    # Financial Information
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('قسط التأمين'))
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('مبلغ التغطية'))
    employee_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('مساهمة الموظف'))
    employer_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('مساهمة صاحب العمل'))
    deductible = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('المبلغ المقتطع'))
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_('الحالة'))
    
    # Beneficiaries
    beneficiaries = models.TextField(blank=True, null=True, verbose_name=_('المستفيدون'))
    
    # Files
    policy_document = models.FileField(upload_to='insurance/policies/', blank=True, null=True, verbose_name=_('وثيقة التأمين'))
    
    # Additional Information
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('تأمين موظف')
        verbose_name_plural = _('تأمينات الموظفين')
        ordering = ['employee', 'insurance_type', '-start_date']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['insurance_type']),
            models.Index(fields=['policy_number']),
            models.Index(fields=['status']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_insurance_type_display()}"

    @property
    def is_active_insurance(self):
        """هل التأمين نشط"""
        if self.status != 'active':
            return False
        if self.end_date and self.end_date < timezone.now().date():
            return False
        return True

    @property
    def days_until_expiry(self):
        """عدد الأيام حتى انتهاء التأمين"""
        if not self.end_date:
            return None
        return (self.end_date - timezone.now().date()).days

    def clean(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError(_('تاريخ البداية لا يمكن أن يكون أكبر من تاريخ النهاية'))
        if self.employee_contribution + self.employer_contribution != self.premium_amount:
            raise ValidationError(_('مجموع مساهمة الموظف وصاحب العمل يجب أن يساوي قسط التأمين'))


class EmployeeVehicle(models.Model):
    """نموذج سيارات الموظفين"""
    
    VEHICLE_TYPE_CHOICES = [
        ('company', _('سيارة الشركة')),
        ('personal', _('سيارة شخصية')),
        ('allowance', _('بدل سيارة')),
        ('rental', _('سيارة مستأجرة')),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('gasoline', _('بنزين')),
        ('diesel', _('ديزل')),
        ('hybrid', _('هجين')),
        ('electric', _('كهربائي')),
        ('lpg', _('غاز')),
    ]
    
    STATUS_CHOICES = [
        ('assigned', _('مخصصة')),
        ('available', _('متاحة')),
        ('maintenance', _('في الصيانة')),
        ('retired', _('خارج الخدمة')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='vehicle_records', verbose_name=_('الموظف'))
    
    # Vehicle Information
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, verbose_name=_('نوع السيارة'))
    make = models.CharField(max_length=100, verbose_name=_('الماركة'))
    model = models.CharField(max_length=100, verbose_name=_('الموديل'))
    year = models.PositiveIntegerField(verbose_name=_('سنة الصنع'))
    license_plate = models.CharField(max_length=20, unique=True, verbose_name=_('رقم اللوحة'))
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('اللون'))
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, verbose_name=_('نوع الوقود'))
    engine_size = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('حجم المحرك'))
    
    # Assignment Information
    assigned_date = models.DateField(verbose_name=_('تاريخ التخصيص'))
    return_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الإرجاع'))
    
    # Financial Information
    monthly_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('البدل الشهري'))
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name=_('سعر الشراء'))
    current_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name=_('القيمة الحالية'))
    
    # Legal Information
    insurance_company = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('شركة التأمين'))
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('رقم بوليصة التأمين'))
    insurance_expiry = models.DateField(verbose_name=_('تاريخ انتهاء التأمين'))
    registration_expiry = models.DateField(verbose_name=_('تاريخ انتهاء الاستمارة'))
    license_expiry = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء الرخصة'))
    
    # Maintenance Information
    last_maintenance_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ آخر صيانة'))
    next_maintenance_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الصيانة القادمة'))
    mileage = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('عدد الكيلومترات'))
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned', verbose_name=_('الحالة'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    
    # Additional Information
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('سيارة موظف')
        verbose_name_plural = _('سيارات الموظفين')
        ordering = ['employee', '-assigned_date']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['license_plate']),
            models.Index(fields=['vehicle_type']),
            models.Index(fields=['status']),
            models.Index(fields=['insurance_expiry']),
            models.Index(fields=['registration_expiry']),
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
    def needs_maintenance(self):
        """هل تحتاج السيارة لصيانة"""
        if not self.next_maintenance_date:
            return False
        return timezone.now().date() >= self.next_maintenance_date

    def clean(self):
        if self.return_date and self.assigned_date > self.return_date:
            raise ValidationError(_('تاريخ التخصيص لا يمكن أن يكون أكبر من تاريخ الإرجاع'))


class EmployeeFileNew(models.Model):
    """نموذج ملفات ووثائق الموظف المحسن"""
    
    FILE_TYPE_CHOICES = [
        ('id_copy', _('صورة الهوية')),
        ('passport', _('جواز السفر')),
        ('contract', _('عقد العمل')),
        ('job_offer', _('عرض العمل')),
        ('certificate', _('شهادة دراسية')),
        ('transcript', _('كشف درجات')),
        ('medical', _('تقرير طبي')),
        ('photo', _('صورة شخصية')),
        ('cv', _('السيرة الذاتية')),
        ('reference', _('خطاب توصية')),
        ('bank_letter', _('خطاب بنكي')),
        ('insurance', _('وثيقة تأمين')),
        ('training', _('شهادة تدريب')),
        ('performance', _('تقييم أداء')),
        ('disciplinary', _('إجراء تأديبي')),
        ('resignation', _('استقالة')),
        ('termination', _('إنهاء خدمة')),
        ('other', _('أخرى')),
    ]
    
    CONFIDENTIALITY_LEVEL_CHOICES = [
        ('public', _('عام')),
        ('internal', _('داخلي')),
        ('confidential', _('سري')),
        ('highly_confidential', _('سري للغاية')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='files_new', verbose_name=_('الموظف'))
    
    # File Information
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, verbose_name=_('نوع الملف'))
    title = models.CharField(max_length=200, verbose_name=_('العنوان'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    
    # File Storage
    file = models.FileField(upload_to='employee_files_new/', verbose_name=_('الملف'))
    file_size = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('حجم الملف'))
    mime_type = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('نوع الملف'))
    
    # Dates
    document_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الوثيقة'))
    expiry_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الانتهاء'))
    
    # Security
    confidentiality_level = models.CharField(max_length=20, choices=CONFIDENTIALITY_LEVEL_CHOICES, 
                                           default='internal', verbose_name=_('مستوى السرية'))
    is_verified = models.BooleanField(default=False, verbose_name=_('تم التحقق'))
    verification_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ التحقق'))
    verified_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='verified_files_new', verbose_name=_('تم التحقق بواسطة'))
    
    # Access Control
    can_be_downloaded = models.BooleanField(default=True, verbose_name=_('قابل للتحميل'))
    download_count = models.PositiveIntegerField(default=0, verbose_name=_('عدد مرات التحميل'))
    
    # System Information
    uploaded_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.PROTECT, verbose_name=_('تم الرفع بواسطة'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الرفع'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('ملف موظف محسن')
        verbose_name_plural = _('ملفات الموظفين المحسنة')
        ordering = ['employee', '-uploaded_at']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['file_type']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['confidentiality_level']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"

    @property
    def days_until_expiry(self):
        """عدد الأيام حتى انتهاء الوثيقة"""
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.now().date()).days

    @property
    def is_expired(self):
        """هل انتهت صلاحية الوثيقة"""
        if not self.expiry_date:
            return False
        return timezone.now().date() > self.expiry_date

    @property
    def is_expiring_soon(self):
        """هل ستنتهي صلاحية الوثيقة قريباً"""
        if not self.expiry_date:
            return False
        warning_days = getattr(settings, 'HR_SETTINGS', {}).get('DOCUMENT_EXPIRY_WARNING_DAYS', 30)
        return 0 <= self.days_until_expiry <= warning_days

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            # You can add mime type detection here
        super().save(*args, **kwargs)

    def increment_download_count(self):
        """زيادة عداد التحميل"""
        self.download_count += 1
        self.save(update_fields=['download_count'])