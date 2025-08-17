"""
Employee Family Models for HRMS
Handles employee family members and dependents
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from datetime import date


class EmployeeFamily(models.Model):
    """
    Employee Family model for storing family members and dependents
    Includes spouse, children, parents, and other dependents
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
        related_name='family_members',
        verbose_name=_("الموظف")
    )
    
    # Relationship Type
    RELATIONSHIP_CHOICES = [
        ('spouse', _('زوج/زوجة')),
        ('child', _('ابن/ابنة')),
        ('parent', _('أب/أم')),
        ('sibling', _('أخ/أخت')),
        ('grandparent', _('جد/جدة')),
        ('grandchild', _('حفيد/حفيدة')),
        ('other', _('أخرى')),
    ]
    
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        verbose_name=_("صلة القرابة")
    )
    
    other_relationship = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("صلة القرابة الأخرى"),
        help_text=_("يرجى تحديد صلة القرابة إذا اخترت 'أخرى'")
    )
    
    # Personal Information
    first_name = models.CharField(
        max_length=100,
        verbose_name=_("الاسم الأول")
    )
    
    middle_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الاسم الأوسط")
    )
    
    last_name = models.CharField(
        max_length=100,
        verbose_name=_("اسم العائلة")
    )
    
    full_name = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name=_("الاسم الكامل")
    )
    
    # Gender
    GENDER_CHOICES = [
        ('male', _('ذكر')),
        ('female', _('أنثى')),
    ]
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name=_("الجنس")
    )
    
    # Birth Information
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الميلاد")
    )
    
    birth_place = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("مكان الميلاد")
    )
    
    # Identification
    national_id = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("رقم الهوية الوطنية")
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
    
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني")
    )
    
    # Address
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("العنوان")
    )
    
    # Dependent Status
    is_dependent = models.BooleanField(
        default=False,
        verbose_name=_("معال"),
        help_text=_("هل هذا الشخص معال من قبل الموظف؟")
    )
    
    is_emergency_contact = models.BooleanField(
        default=False,
        verbose_name=_("جهة اتصال في حالات الطوارئ")
    )
    
    is_beneficiary = models.BooleanField(
        default=False,
        verbose_name=_("مستفيد"),
        help_text=_("هل هذا الشخص مستفيد من التأمين أو المعاشات؟")
    )
    
    # Insurance and Benefits
    is_covered_by_insurance = models.BooleanField(
        default=False,
        verbose_name=_("مشمول بالتأمين الصحي")
    )
    
    insurance_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("رقم التأمين")
    )
    
    # Education and Occupation (for spouse/adult dependents)
    education_level = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("المستوى التعليمي")
    )
    
    occupation = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("المهنة")
    )
    
    employer = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("جهة العمل")
    )
    
    # Documents
    document_file = models.FileField(
        upload_to='employee_family_documents/',
        null=True,
        blank=True,
        verbose_name=_("ملف الوثيقة"),
        help_text=_("شهادة ميلاد، عقد زواج، إلخ")
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
        related_name='created_employee_family',
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
        verbose_name = _("فرد من عائلة الموظف")
        verbose_name_plural = _("أفراد عائلة الموظف")
        db_table = 'hrms_employee_family'
        ordering = ['employee', 'relationship', 'first_name']
        indexes = [
            models.Index(fields=['employee', 'relationship']),
            models.Index(fields=['is_dependent']),
            models.Index(fields=['is_emergency_contact']),
            models.Index(fields=['is_beneficiary']),
        ]
    
    def __str__(self):
        relationship_display = dict(self.RELATIONSHIP_CHOICES).get(self.relationship, self.relationship)
        return f"{self.employee.full_name} - {self.full_name or self.first_name} ({relationship_display})"
    
    def clean(self):
        """Validate family member data"""
        super().clean()
        
        # Validate birth date
        if self.birth_date and self.birth_date > date.today():
            raise ValidationError(_("تاريخ الميلاد لا يمكن أن يكون في المستقبل"))
        
        # Validate relationship type 'other'
        if self.relationship == 'other' and not self.other_relationship:
            raise ValidationError(_("يرجى تحديد صلة القرابة الأخرى"))
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate fields"""
        # Auto-generate full name
        if not self.full_name:
            name_parts = [self.first_name]
            if self.middle_name:
                name_parts.append(self.middle_name)
            name_parts.append(self.last_name)
            self.full_name = ' '.join(name_parts)
        
        super().save(*args, **kwargs)
    
    @property
    def age(self):
        """Calculate age"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None
    
    @property
    def relationship_display(self):
        """Get formatted relationship"""
        if self.relationship == 'other' and self.other_relationship:
            return self.other_relationship
        return dict(self.RELATIONSHIP_CHOICES).get(self.relationship, self.relationship)