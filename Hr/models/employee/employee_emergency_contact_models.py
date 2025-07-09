"""
Employee Emergency Contact Models for HRMS
Handles emergency contact information for employees
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings


class EmployeeEmergencyContact(models.Model):
    """
    Employee Emergency Contact model
    Stores emergency contact information for employees
    """
    
    # Relationship to Employee
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
        verbose_name=_("الموظف")
    )
    
    # Contact Information
    full_name = models.CharField(
        max_length=200,
        verbose_name=_("الاسم الكامل")
    )
    
    # Relationship to Employee
    RELATIONSHIP_CHOICES = [
        ('spouse', _('زوج/زوجة')),
        ('father', _('والد')),
        ('mother', _('والدة')),
        ('son', _('ابن')),
        ('daughter', _('ابنة')),
        ('brother', _('أخ')),
        ('sister', _('أخت')),
        ('grandfather', _('جد')),
        ('grandmother', _('جدة')),
        ('uncle', _('عم/خال')),
        ('aunt', _('عمة/خالة')),
        ('cousin', _('ابن عم/خال')),
        ('friend', _('صديق')),
        ('colleague', _('زميل عمل')),
        ('neighbor', _('جار')),
        ('guardian', _('ولي أمر')),
        ('other', _('أخرى')),
    ]
    
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        verbose_name=_("صلة القرابة")
    )
    
    relationship_other = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("صلة القرابة (أخرى)"),
        help_text=_("حدد صلة القرابة إذا اخترت 'أخرى'")
    )
    
    # Contact Details
    primary_phone = models.CharField(
        max_length=20,
        verbose_name=_("رقم الهاتف الأساسي"),
        validators=[
            RegexValidator(
                regex=r'^\+?[\d\s\-\(\)]+$',
                message=_("رقم الهاتف غير صحيح")
            )
        ]
    )
    
    secondary_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم الهاتف الثانوي"),
        validators=[
            RegexValidator(
                regex=r'^\+?[\d\s\-\(\)]+$',
                message=_("رقم الهاتف غير صحيح")
            )
        ]
    )
    
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني")
    )
    
    # Address Information
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("العنوان")
    )
    
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المدينة")
    )
    
    country = models.CharField(
        max_length=100,
        default="مصر",
        verbose_name=_("الدولة")
    )
    
    # Additional Information
    occupation = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المهنة")
    )
    
    workplace = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("مكان العمل")
    )
    
    # Priority and Availability
    PRIORITY_CHOICES = [
        (1, _('الأولوية الأولى')),
        (2, _('الأولوية الثانية')),
        (3, _('الأولوية الثالثة')),
        (4, _('الأولوية الرابعة')),
        (5, _('الأولوية الخامسة')),
    ]
    
    priority = models.PositiveIntegerField(
        choices=PRIORITY_CHOICES,
        default=1,
        verbose_name=_("الأولوية"),
        help_text=_("أولوية الاتصال في حالات الطوارئ")
    )
    
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("جهة الاتصال الأساسية"),
        help_text=_("هل هذه جهة الاتصال الأساسية؟")
    )
    
    # Availability Information
    best_time_to_call = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("أفضل وقت للاتصال")
    )
    
    availability_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات التوفر"),
        help_text=_("معلومات إضافية حول أوقات التوفر")
    )
    
    # Authorization
    can_make_medical_decisions = models.BooleanField(
        default=False,
        verbose_name=_("يمكنه اتخاذ قرارات طبية"),
        help_text=_("هل يمكن لهذا الشخص اتخاذ قرارات طبية نيابة عن الموظف؟")
    )
    
    can_receive_salary = models.BooleanField(
        default=False,
        verbose_name=_("يمكنه استلام الراتب"),
        help_text=_("هل يمكن لهذا الشخص استلام راتب الموظف في حالات الطوارئ؟")
    )
    
    has_power_of_attorney = models.BooleanField(
        default=False,
        verbose_name=_("لديه توكيل قانوني"),
        help_text=_("هل لدى هذا الشخص توكيل قانوني من الموظف؟")
    )
    
    # Language Preferences
    preferred_language = models.CharField(
        max_length=50,
        choices=[
            ('ar', _('العربية')),
            ('en', _('الإنجليزية')),
            ('fr', _('الفرنسية')),
            ('other', _('أخرى')),
        ],
        default='ar',
        verbose_name=_("اللغة المفضلة")
    )
    
    # Status and Verification
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("تم التحقق"),
        help_text=_("هل تم التحقق من صحة معلومات الاتصال؟")
    )
    
    verified_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التحقق")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    # Additional Notes
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات إضافية")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_emergency_contacts',
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
        verbose_name = _("جهة اتصال طوارئ")
        verbose_name_plural = _("جهات اتصال الطوارئ")
        db_table = 'hrms_employee_emergency_contact'
        ordering = ['employee', 'priority']
        unique_together = [['employee', 'priority']]
        indexes = [
            models.Index(fields=['employee', 'priority']),
            models.Index(fields=['is_primary']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.full_name} ({self.get_relationship_display()})"
    
    def clean(self):
        """Validate emergency contact data"""
        super().clean()
        
        # Ensure only one primary contact per employee
        if self.is_primary:
            existing_primary = EmployeeEmergencyContact.objects.filter(
                employee=self.employee,
                is_primary=True
            ).exclude(pk=self.pk)
            
            if existing_primary.exists():
                from django.core.exceptions import ValidationError
                raise ValidationError(_("يمكن أن يكون هناك جهة اتصال أساسية واحدة فقط لكل موظف"))
        
        # Validate relationship_other field
        if self.relationship == 'other' and not self.relationship_other:
            from django.core.exceptions import ValidationError
            raise ValidationError(_("يجب تحديد صلة القرابة عند اختيار 'أخرى'"))
    
    @property
    def relationship_display(self):
        """Get relationship display with custom value if 'other'"""
        if self.relationship == 'other' and self.relationship_other:
            return self.relationship_other
        return self.get_relationship_display()
    
    @property
    def full_address(self):
        """Get formatted full address"""
        address_parts = []
        if self.address:
            address_parts.append(self.address)
        if self.city:
            address_parts.append(self.city)
        if self.country:
            address_parts.append(self.country)
        return ", ".join(address_parts)
    
    def get_contact_info(self):
        """Get formatted contact information"""
        contact_info = {
            'name': self.full_name,
            'relationship': self.relationship_display,
            'primary_phone': self.primary_phone,
            'secondary_phone': self.secondary_phone,
            'email': self.email,
            'address': self.full_address,
            'priority': self.priority,
            'is_primary': self.is_primary,
        }
        return contact_info
    
    def save(self, *args, **kwargs):
        """Override save to handle primary contact logic"""
        # If this is set as primary, unset other primary contacts for the same employee
        if self.is_primary:
            EmployeeEmergencyContact.objects.filter(
                employee=self.employee,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        # If no primary contact exists and this is the first contact, make it primary
        if not self.pk:  # New record
            existing_contacts = EmployeeEmergencyContact.objects.filter(employee=self.employee)
            if not existing_contacts.exists():
                self.is_primary = True
        
        super().save(*args, **kwargs)
