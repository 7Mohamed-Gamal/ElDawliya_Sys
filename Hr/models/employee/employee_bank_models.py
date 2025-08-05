"""
Employee Bank Models for HRMS
Handles employee banking information for payroll
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings
from cryptography.fernet import Fernet


class EncryptedField(models.CharField):
    """
    Custom field for encrypting sensitive data
    """
    def __init__(self, *args, **kwargs):
        # Get encryption key from settings or generate one
        try:
            from django.conf import settings
            if hasattr(settings, 'ENCRYPTION_KEY'):
                self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
            else:
                # Generate a key for development (should be in settings for production)
                key = Fernet.generate_key()
                self.cipher = Fernet(key)
        except Exception:
            # Fallback - no encryption in case of issues
            self.cipher = None
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None or not self.cipher:
            return value
        try:
            return self.cipher.decrypt(value.encode()).decode()
        except Exception:
            return value  # Return as-is if decryption fails
    
    def to_python(self, value):
        return value
    
    def get_prep_value(self, value):
        if value is None or not self.cipher:
            return value
        try:
            return self.cipher.encrypt(value.encode()).decode()
        except Exception:
            return value  # Return as-is if encryption fails


class EmployeeBank(models.Model):
    """
    Employee Bank model for storing banking information
    Includes account details for salary transfers and financial transactions
    """
    
    # Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    # Relationship to Employee
    employee = models.ForeignKey(
        'EmployeeEnhanced',
        on_delete=models.CASCADE,
        related_name='bank_accounts',
        verbose_name=_("الموظف")
    )
    
    # Account Type
    ACCOUNT_TYPE_CHOICES = [
        ('salary', _('حساب الراتب')),
        ('savings', _('حساب توفير')),
        ('current', _('حساب جاري')),
        ('credit_card', _('بطاقة ائتمان')),
        ('loan', _('قرض')),
        ('other', _('أخرى')),
    ]
    
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default='salary',
        verbose_name=_("نوع الحساب")
    )
    
    # Is Primary Account
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("حساب أساسي"),
        help_text=_("هل هذا هو الحساب الأساسي لتحويل الراتب؟")
    )
    
    # Bank Information
    bank_name = models.CharField(
        max_length=200,
        verbose_name=_("اسم البنك")
    )
    
    bank_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("كود البنك")
    )
    
    branch_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("اسم الفرع")
    )
    
    branch_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("كود الفرع")
    )
    
    # Account Information (Encrypted)
    account_number = EncryptedField(
        max_length=200,  # Increased for encrypted data
        verbose_name=_("رقم الحساب")
    )
    
    account_name = models.CharField(
        max_length=200,
        verbose_name=_("اسم الحساب")
    )
    
    iban = EncryptedField(
        max_length=200,  # Increased for encrypted data
        null=True,
        blank=True,
        verbose_name=_("رقم الآيبان (IBAN)")
    )
    
    swift_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رمز السويفت (SWIFT)")
    )
    
    # Currency
    currency = models.CharField(
        max_length=3,
        default="EGP",
        verbose_name=_("العملة")
    )
    
    # Card Information (if applicable)
    card_number = EncryptedField(
        max_length=200,  # Increased for encrypted data
        null=True,
        blank=True,
        verbose_name=_("رقم البطاقة")
    )
    
    card_expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ انتهاء البطاقة")
    )
    
    # Status
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('pending', _('معلق')),
        ('closed', _('مغلق')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_("الحالة")
    )
    
    # Verification Status
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("تم التحقق")
    )
    
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_bank_accounts',
        verbose_name=_("تم التحقق بواسطة")
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التحقق")
    )
    
    # Supporting Documents
    account_document = models.FileField(
        upload_to='employee_bank_documents/',
        null=True,
        blank=True,
        verbose_name=_("مستند الحساب"),
        help_text=_("كشف حساب، خطاب من البنك، إلخ")
    )
    
    # Additional Information
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_employee_bank_accounts',
        verbose_name=_("أنشئ بواسطة")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    class Meta:
        verbose_name = _("حساب بنكي للموظف")
        verbose_name_plural = _("حسابات بنكية للموظفين")
        db_table = 'hrms_employee_bank'
        ordering = ['employee', '-is_primary', 'bank_name']
        indexes = [
            models.Index(fields=['employee', 'account_type']),
            models.Index(fields=['is_primary']),
            models.Index(fields=['status']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.bank_name} ({self.get_account_type_display()})"
    
    def save(self, *args, **kwargs):
        """Override save to ensure only one primary account"""
        if self.is_primary:
            # Set all other accounts for this employee as non-primary
            EmployeeBank.objects.filter(
                employee=self.employee,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(*args, **kwargs)
    
    @property
    def masked_account_number(self):
        """Get masked account number for display"""
        if self.account_number:
            # Show only last 4 digits
            account_len = len(self.account_number)
            if account_len > 4:
                return '*' * (account_len - 4) + self.account_number[-4:]
            return self.account_number
        return None
    
    @property
    def masked_card_number(self):
        """Get masked card number for display"""
        if self.card_number:
            # Show only first 4 and last 4 digits
            card_len = len(self.card_number)
            if card_len > 8:
                return self.card_number[:4] + ' **** **** ' + self.card_number[-4:]
            return self.card_number
        return None