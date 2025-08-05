"""
Employee Emergency Contact Models for HRMS
Handles emergency contact information for employees
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings


class EmployeeEmergencyContactEnhanced(models.Model):
    """
    Employee Emergency Contact model
    Stores emergency contact information for employees
    """
    
    # Relationship to Employee
    employee = models.ForeignKey(
        'EmployeeEnhanced',
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
            existing_primary = EmployeeEmergencyContactEnhanced.objects.filter(
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
            EmployeeEmergencyContactEnhanced.objects.filter(
                employee=self.employee,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        # If no primary contact exists and this is the first contact, make it primary
        if not self.pk:  # New record
            existing_contacts = EmployeeEmergencyContactEnhanced.objects.filter(employee=self.employee)
            if not existing_contacts.exists():
                self.is_primary = True
        
        super().save(*args, **kwargs)
    
    # Advanced Methods
    def get_priority_display_with_icon(self):
        """Get priority with visual indicator"""
        priority_icons = {
            1: "🔴 الأولوية الأولى",
            2: "🟠 الأولوية الثانية", 
            3: "🟡 الأولوية الثالثة",
            4: "🟢 الأولوية الرابعة",
            5: "⚪ الأولوية الخامسة"
        }
        return priority_icons.get(self.priority, "غير محدد")
    
    def get_authorization_summary(self):
        """Get summary of authorizations"""
        authorizations = []
        if self.can_make_medical_decisions:
            authorizations.append("قرارات طبية")
        if self.can_receive_salary:
            authorizations.append("استلام راتب")
        if self.has_power_of_attorney:
            authorizations.append("توكيل قانوني")
        
        return ", ".join(authorizations) if authorizations else "لا توجد تفويضات"
    
    def get_contact_methods(self):
        """Get available contact methods"""
        methods = []
        if self.primary_phone:
            methods.append(f"📞 {self.primary_phone}")
        if self.secondary_phone:
            methods.append(f"📱 {self.secondary_phone}")
        if self.email:
            methods.append(f"📧 {self.email}")
        
        return methods
    
    def get_availability_info(self):
        """Get formatted availability information"""
        info = {}
        if self.best_time_to_call:
            info['best_time'] = self.best_time_to_call
        if self.availability_notes:
            info['notes'] = self.availability_notes
        if self.preferred_language:
            info['language'] = self.get_preferred_language_display()
        
        return info
    
    def is_reachable_now(self):
        """Check if contact is likely reachable now (basic implementation)"""
        from datetime import datetime
        current_hour = datetime.now().hour
        
        # Basic logic - can be enhanced with more sophisticated rules
        if self.best_time_to_call:
            if "صباح" in self.best_time_to_call and 6 <= current_hour <= 12:
                return True
            elif "مساء" in self.best_time_to_call and 18 <= current_hour <= 22:
                return True
            elif "ليل" in self.best_time_to_call and (22 <= current_hour or current_hour <= 6):
                return True
        
        # Default: assume reachable during normal hours
        return 8 <= current_hour <= 20
    
    def get_contact_score(self):
        """Calculate contact reliability score"""
        score = 100
        
        # Deduct points based on priority (lower priority = lower score)
        score -= (self.priority - 1) * 10
        
        # Add points for verification
        if self.is_verified:
            score += 20
        
        # Add points for multiple contact methods
        contact_methods = len([x for x in [self.primary_phone, self.secondary_phone, self.email] if x])
        score += contact_methods * 5
        
        # Add points for authorizations
        authorizations = sum([
            self.can_make_medical_decisions,
            self.can_receive_salary,
            self.has_power_of_attorney
        ])
        score += authorizations * 10
        
        # Deduct points if not active
        if not self.is_active:
            score -= 50
        
        return max(0, min(100, score))
    
    def needs_verification(self):
        """Check if contact needs verification"""
        if not self.is_verified:
            return True
        
        # Check if verification is old (more than 1 year)
        if self.verified_date:
            from datetime import datetime, timedelta
            one_year_ago = datetime.now() - timedelta(days=365)
            return self.verified_date < one_year_ago
        
        return True
    
    def get_relationship_category(self):
        """Get relationship category for grouping"""
        family_relationships = ['spouse', 'father', 'mother', 'son', 'daughter', 
                               'brother', 'sister', 'grandfather', 'grandmother']
        extended_family = ['uncle', 'aunt', 'cousin']
        
        if self.relationship in family_relationships:
            return "أسرة مباشرة"
        elif self.relationship in extended_family:
            return "أسرة ممتدة"
        elif self.relationship in ['friend', 'colleague', 'neighbor']:
            return "معارف"
        else:
            return "أخرى"
    
    @classmethod
    def get_emergency_contacts_by_priority(cls, employee):
        """Get emergency contacts ordered by priority"""
        return cls.objects.filter(
            employee=employee,
            is_active=True
        ).order_by('priority')
    
    @classmethod
    def get_primary_contact(cls, employee):
        """Get primary emergency contact for employee"""
        try:
            return cls.objects.get(employee=employee, is_primary=True, is_active=True)
        except cls.DoesNotExist:
            # Return highest priority contact if no primary is set
            return cls.objects.filter(
                employee=employee,
                is_active=True
            ).order_by('priority').first()
    
    @classmethod
    def get_authorized_contacts(cls, employee, authorization_type):
        """Get contacts with specific authorization"""
        filters = {'employee': employee, 'is_active': True}
        
        if authorization_type == 'medical':
            filters['can_make_medical_decisions'] = True
        elif authorization_type == 'salary':
            filters['can_receive_salary'] = True
        elif authorization_type == 'legal':
            filters['has_power_of_attorney'] = True
        
        return cls.objects.filter(**filters).order_by('priority')
    
    def send_test_notification(self):
        """Send test notification to verify contact information"""
        # This would integrate with notification system
        # For now, just return the contact methods that would be used
        methods = self.get_contact_methods()
        return {
            'contact': self.full_name,
            'methods': methods,
            'language': self.get_preferred_language_display(),
            'message': f"اختبار إشعار طوارئ للموظف {self.employee.full_name}"
        }
    
    def get_emergency_notification_template(self):
        """Get emergency notification template for this contact"""
        template = {
            'recipient_name': self.full_name,
            'employee_name': self.employee.full_name,
            'relationship': self.relationship_display,
            'language': self.preferred_language,
            'contact_methods': self.get_contact_methods(),
            'authorizations': self.get_authorization_summary(),
        }
        return template
