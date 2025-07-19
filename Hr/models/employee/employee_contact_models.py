"""
Employee Contact Models for HRMS
Handles employee contact information and emergency contacts
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, EmailValidator
from django.conf import settings


class EmployeeContact(models.Model):
    """
    Employee Contact model for storing detailed contact information
    Includes multiple addresses, phone numbers, and emergency contacts
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
        'Employee',
        on_delete=models.CASCADE,
        related_name='contact_details',
        verbose_name=_("الموظف")
    )
    
    # Contact Type
    CONTACT_TYPE_CHOICES = [
        ('home', _('منزل')),
        ('work', _('عمل')),
        ('permanent', _('دائم')),
        ('temporary', _('مؤقت')),
        ('emergency', _('طوارئ')),
        ('other', _('آخر')),
    ]
    
    contact_type = models.CharField(
        max_length=20,
        choices=CONTACT_TYPE_CHOICES,
        default='home',
        verbose_name=_("نوع جهة الاتصال")
    )
    
    # Is Primary
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("جهة اتصال أساسية")
    )
    
    # Address Information
    address_line1 = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("العنوان - السطر 1")
    )
    
    address_line2 = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("العنوان - السطر 2")
    )
    
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المدينة")
    )
    
    state = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المحافظة/الولاية")
    )
    
    postal_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("الرمز البريدي")
    )
    
    country = models.CharField(
        max_length=100,
        default="مصر",
        verbose_name=_("الدولة")
    )
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("رقم الهاتف يجب أن يكون بصيغة: '+999999999'. يسمح بـ 15 رقم.")
    )
    
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        null=True,
        blank=True,
        verbose_name=_("رقم الهاتف")
    )
    
    mobile = models.CharField(
        validators=[phone_regex],
        max_length=17,
        null=True,
        blank=True,
        verbose_name=_("رقم الجوال")
    )
    
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني"),
        validators=[EmailValidator()]
    )
    
    # Emergency Contact Information
    contact_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("اسم جهة الاتصال")
    )
    
    relationship = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("صلة القرابة")
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
        related_name='created_employee_contacts',
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
        verbose_name = _("معلومات اتصال الموظف")
        verbose_name_plural = _("معلومات اتصال الموظفين")
        db_table = 'hrms_employee_contact'
        ordering = ['employee', '-is_primary', 'contact_type']
        indexes = [
            models.Index(fields=['employee', 'contact_type']),
            models.Index(fields=['is_primary']),
        ]
    
    def __str__(self):
        contact_type_display = dict(self.CONTACT_TYPE_CHOICES).get(self.contact_type, self.contact_type)
        return f"{self.employee.full_name} - {contact_type_display}"
    
    def save(self, *args, **kwargs):
        """Override save to ensure only one primary contact per type"""
        if self.is_primary:
            # Set all other contacts of same type for this employee as non-primary
            EmployeeContact.objects.filter(
                employee=self.employee,
                contact_type=self.contact_type,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(*args, **kwargs)
    
    @property
    def full_address(self):
        """Get formatted full address"""
        address_parts = []
        if self.address_line1:
            address_parts.append(self.address_line1)
        if self.address_line2:
            address_parts.append(self.address_line2)
        if self.city:
            address_parts.append(self.city)
        if self.state:
            address_parts.append(self.state)
        if self.country:
            address_parts.append(self.country)
        if self.postal_code:
            address_parts.append(self.postal_code)
        return ", ".join(address_parts)