# -*- coding: utf-8 -*-
"""
نماذج الحضور والوقت المتقدمة لنظام إدارة الموارد البشرية (HRMS)
Enhanced Attendance Models with Advanced Features
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from django.conf import settings
from decimal import Decimal
import json

User = get_user_model()


class AttendanceRecordEnhanced(models.Model):
    """نموذج سجل الحضور المفصل والمتقدم"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    employee = models.ForeignKey(
        'Hr.EmployeeEnhanced',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_("الموظف")
    )
    
    # Date and Time Information
    date = models.DateField(verbose_name=_("التاريخ"))
    
    # Check-in Information
    check_in_time = models.TimeField(
        null=True, 
        blank=True, 
        verbose_name=_("وقت الدخول")
    )
    
    check_in_machine = models.ForeignKey(
        'Hr.AttendanceMachine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='check_in_records',
        verbose_name=_("جهاز الدخول")
    )
    
    check_in_method = models.CharField(
        max_length=20,
        choices=[
            ('fingerprint', _('بصمة الإصبع')),
            ('face', _('التعرف على الوجه')),
            ('card', _('البطاقة')),
            ('pin', _('رمز PIN')),
            ('manual', _('يدوي')),
            ('mobile', _('تطبيق الجوال')),
            ('web', _('الموقع الإلكتروني')),
        ],
        null=True,
        blank=True,
        verbose_name=_("طريقة الدخول")
    )
    
    check_in_location = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("موقع الدخول"),
        help_text=_("إحداثيات GPS للدخول")
    )
    
    # Check-out Information
    check_out_time = models.TimeField(
        null=True, 
        blank=True, 
        verbose_name=_("وقت الخروج")
    )
    
    check_out_machine = models.ForeignKey(
        'Hr.AttendanceMachine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='check_out_records',
        verbose_name=_("جهاز الخروج")
    )
    
    check_out_method = models.CharField(
        max_length=20,
        choices=[
            ('fingerprint', _('بصمة الإصبع')),
            ('face', _('التعرف على الوجه')),
            ('card', _('البطاقة')),
            ('pin', _('رمز PIN')),
            ('manual', _('يدوي')),
            ('mobile', _('تطبيق الجوال')),
            ('web', _('الموقع الإلكتروني')),
        ],
        null=True,
        blank=True,
        verbose_name=_("طريقة الخروج")
    )
    
    check_out_location = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("موقع الخروج"),
        help_text=_("إحداثيات GPS للخروج")
    )
    
    # Shift Information
    assigned_shift = models.ForeignKey(
        'Hr.WorkShift',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records',
        verbose_name=_("الوردية المعينة")
    )
    
    # Status and Calculations
    STATUS_CHOICES = [
        ('present', _('حاضر')),
        ('absent', _('غائب')),
        ('late', _('متأخر')),
        ('early_departure', _('انصراف مبكر')),
        ('half_day', _('نصف يوم')),
        ('overtime', _('وقت إضافي')),
        ('holiday', _('عطلة')),
        ('leave', _('إجازة')),
        ('sick_leave', _('إجازة مرضية')),
        ('business_trip', _('مهمة عمل')),
        ('training', _('تدريب')),
        ('pending', _('في انتظار المراجعة')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present',
        verbose_name=_("الحالة")
    )
    
    # Time Calculations
    total_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("إجمالي الساعات")
    )
    
    regular_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("الساعات العادية")
    )
    
    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("ساعات الوقت الإضافي")
    )
    
    break_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("ساعات الاستراحة")
    )
    
    late_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("دقائق التأخير")
    )
    
    early_departure_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("دقائق الانصراف المبكر")
    )
    
    # Break Information
    break_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("بداية الاستراحة")
    )
    
    break_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("نهاية الاستراحة")
    )
    
    # Approval and Verification
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("تم التحقق")
    )
    
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_attendance_records',
        verbose_name=_("تم التحقق بواسطة")
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ التحقق")
    )
    
    # Manual Entry Information
    is_manual_entry = models.BooleanField(
        default=False,
        verbose_name=_("إدخال يدوي")
    )
    
    manual_entry_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("سبب الإدخال اليدوي")
    )
    
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manual_attendance_entries',
        verbose_name=_("أدخل بواسطة")
    )
    
    # Exception and Notes
    has_exception = models.BooleanField(
        default=False,
        verbose_name=_("يحتوي على استثناء")
    )
    
    exception_type = models.CharField(
        max_length=50,
        choices=[
            ('late_arrival', _('تأخير في الوصول')),
            ('early_departure', _('انصراف مبكر')),
            ('missing_check_in', _('عدم تسجيل دخول')),
            ('missing_check_out', _('عدم تسجيل خروج')),
            ('long_break', _('استراحة طويلة')),
            ('overtime_unapproved', _('وقت إضافي غير معتمد')),
            ('location_mismatch', _('عدم تطابق الموقع')),
            ('duplicate_entry', _('إدخال مكرر')),
            ('system_error', _('خطأ في النظام')),
        ],
        null=True,
        blank=True,
        verbose_name=_("نوع الاستثناء")
    )
    
    exception_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات الاستثناء")
    )
    
    # Additional Information
    weather_condition = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("حالة الطقس")
    )
    
    work_from_home = models.BooleanField(
        default=False,
        verbose_name=_("عمل من المنزل")
    )
    
    remote_work_approved = models.BooleanField(
        default=False,
        verbose_name=_("العمل عن بُعد معتمد")
    )
    
    # Productivity Metrics
    productivity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("نقاط الإنتاجية")
    )
    
    tasks_completed = models.PositiveIntegerField(
        default=0,
        verbose_name=_("المهام المكتملة")
    )
    
    # System Fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    # Metadata
    raw_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("البيانات الخام"),
        help_text=_("البيانات الخام من جهاز الحضور")
    )
    
    class Meta:
        verbose_name = _("سجل حضور محسن")
        verbose_name_plural = _("سجلات الحضور المحسنة")
        db_table = 'hrms_attendance_record_enhanced'
        ordering = ['-date', '-check_in_time']
        unique_together = [['employee', 'date']]
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['has_exception']),
            models.Index(fields=['assigned_shift']),
            models.Index(fields=['check_in_machine']),
            models.Index(fields=['check_out_machine']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.get_status_display()})"
    
    def clean(self):
        """التحقق من صحة البيانات"""
        super().clean()
        
        # التحقق من أن وقت الخروج بعد وقت الدخول
        if self.check_in_time and self.check_out_time:
            # للورديات العادية
            if not (self.assigned_shift and self.assigned_shift.is_overnight):
                if self.check_out_time <= self.check_in_time:
                    raise ValidationError(_("وقت الخروج يجب أن يكون بعد وقت الدخول"))
        
        # التحقق من وقت الاستراحة
        if self.break_start_time and self.break_end_time:
            if self.break_end_time <= self.break_start_time:
                raise ValidationError(_("وقت نهاية الاستراحة يجب أن يكون بعد وقت البداية"))
    
    def save(self, *args, **kwargs):
        """حفظ السجل مع حساب القيم التلقائية"""
        # حساب إجمالي الساعات والقيم الأخرى
        self.calculate_attendance_metrics()
        
        # تحديد الحالة تلقائياً
        self.auto_determine_status()
        
        # التحقق من الاستثناءات
        self.check_for_exceptions()
        
        super().save(*args, **kwargs)
    
    def calculate_attendance_metrics(self):
        """حساب مقاييس الحضور"""
        if not self.check_in_time or not self.check_out_time:
            return
        
        # حساب إجمالي الساعات
        check_in_dt = datetime.combine(self.date, self.check_in_time)
        check_out_dt = datetime.combine(self.date, self.check_out_time)
        
        # للورديات الليلية
        if self.assigned_shift and self.assigned_shift.is_overnight:
            if self.check_out_time < self.check_in_time:
                check_out_dt += timedelta(days=1)
        
        total_time = check_out_dt - check_in_dt
        total_hours = Decimal(str(total_time.total_seconds() / 3600))
        
        # خصم وقت الاستراحة
        if self.break_start_time and self.break_end_time:
            break_start_dt = datetime.combine(self.date, self.break_start_time)
            break_end_dt = datetime.combine(self.date, self.break_end_time)
            break_time = break_end_dt - break_start_dt
            self.break_hours = Decimal(str(break_time.total_seconds() / 3600))
            total_hours -= self.break_hours
        
        self.total_hours = round(total_hours, 2)
        
        # حساب الساعات العادية والإضافية
        if self.assigned_shift:
            shift_hours = self.assigned_shift.total_hours
            if self.total_hours > shift_hours:
                self.regular_hours = shift_hours
                self.overtime_hours = self.total_hours - shift_hours
            else:
                self.regular_hours = self.total_hours
                self.overtime_hours = Decimal('0.00')
        else:
            self.regular_hours = self.total_hours
            self.overtime_hours = Decimal('0.00')
        
        # حساب دقائق التأخير
        if self.assigned_shift and self.check_in_time:
            self.late_minutes = self.assigned_shift.calculate_late_minutes(self.check_in_time)
        
        # حساب دقائق الانصراف المبكر
        if self.assigned_shift and self.check_out_time:
            expected_end = self.assigned_shift.end_time
            if self.check_out_time < expected_end:
                early_time = datetime.combine(self.date, expected_end) - datetime.combine(self.date, self.check_out_time)
                self.early_departure_minutes = int(early_time.total_seconds() / 60)
    
    def auto_determine_status(self):
        """تحديد الحالة تلقائياً"""
        if not self.check_in_time and not self.check_out_time:
            self.status = 'absent'
        elif self.late_minutes > 0:
            self.status = 'late'
        elif self.early_departure_minutes > 0:
            self.status = 'early_departure'
        elif self.overtime_hours > 0:
            self.status = 'overtime'
        elif self.total_hours and self.total_hours < 4:  # أقل من 4 ساعات
            self.status = 'half_day'
        else:
            self.status = 'present'
    
    def check_for_exceptions(self):
        """فحص الاستثناءات"""
        exceptions = []
        
        if self.late_minutes > 0:
            exceptions.append('late_arrival')
        
        if self.early_departure_minutes > 0:
            exceptions.append('early_departure')
        
        if self.check_in_time and not self.check_out_time:
            exceptions.append('missing_check_out')
        
        if not self.check_in_time and self.check_out_time:
            exceptions.append('missing_check_in')
        
        if self.overtime_hours > 0 and not self.remote_work_approved:
            exceptions.append('overtime_unapproved')
        
        if exceptions:
            self.has_exception = True
            self.exception_type = exceptions[0]  # أول استثناء
        else:
            self.has_exception = False
            self.exception_type = None
    
    # Properties
    @property
    def is_present(self):
        """هل الموظف حاضر؟"""
        return self.status in ['present', 'late', 'overtime']
    
    @property
    def is_complete_day(self):
        """هل هو يوم كامل؟"""
        return self.check_in_time is not None and self.check_out_time is not None
    
    @property
    def attendance_percentage(self):
        """نسبة الحضور"""
        if not self.assigned_shift or not self.total_hours:
            return 0
        
        expected_hours = self.assigned_shift.total_hours
        return min(100, (float(self.total_hours) / float(expected_hours)) * 100)
    
    @property
    def location_info(self):
        """معلومات الموقع"""
        info = {}
        if self.check_in_location:
            info['check_in'] = self.check_in_location
        if self.check_out_location:
            info['check_out'] = self.check_out_location
        return info
    
    # Methods
    def get_status_display_with_icon(self):
        """عرض الحالة مع الأيقونة"""
        status_icons = {
            'present': '✅ حاضر',
            'absent': '❌ غائب',
            'late': '⏰ متأخر',
            'early_departure': '🏃 انصراف مبكر',
            'half_day': '🕐 نصف يوم',
            'overtime': '⏱️ وقت إضافي',
            'holiday': '🎉 عطلة',
            'leave': '🏖️ إجازة',
            'sick_leave': '🤒 إجازة مرضية',
            'business_trip': '✈️ مهمة عمل',
            'training': '📚 تدريب',
            'pending': '⏳ في انتظار المراجعة',
        }
        return status_icons.get(self.status, self.get_status_display())
    
    def get_time_summary(self):
        """ملخص الأوقات"""
        return {
            'check_in': self.check_in_time.strftime('%H:%M') if self.check_in_time else None,
            'check_out': self.check_out_time.strftime('%H:%M') if self.check_out_time else None,
            'total_hours': float(self.total_hours) if self.total_hours else 0,
            'regular_hours': float(self.regular_hours) if self.regular_hours else 0,
            'overtime_hours': float(self.overtime_hours) if self.overtime_hours else 0,
            'break_hours': float(self.break_hours) if self.break_hours else 0,
            'late_minutes': self.late_minutes,
            'early_departure_minutes': self.early_departure_minutes,
        }
    
    def verify_attendance(self, verified_by_user, notes=None):
        """التحقق من سجل الحضور"""
        self.is_verified = True
        self.verified_by = verified_by_user
        self.verified_at = timezone.now()
        if notes:
            self.exception_notes = f"{self.exception_notes or ''}\nملاحظات التحقق: {notes}"
        self.save()
    
    def add_manual_entry(self, entered_by_user, reason, check_in=None, check_out=None):
        """إضافة إدخال يدوي"""
        self.is_manual_entry = True
        self.manual_entry_reason = reason
        self.entered_by = entered_by_user
        
        if check_in:
            self.check_in_time = check_in
            self.check_in_method = 'manual'
        
        if check_out:
            self.check_out_time = check_out
            self.check_out_method = 'manual'
        
        self.save()
    
    def calculate_distance_from_office(self, office_location):
        """حساب المسافة من المكتب"""
        if not self.check_in_location or not office_location:
            return None
        
        # حساب المسافة باستخدام إحداثيات GPS
        # يمكن استخدام مكتبة geopy للحساب الدقيق
        try:
            from geopy.distance import geodesic
            
            employee_location = (
                self.check_in_location.get('latitude'),
                self.check_in_location.get('longitude')
            )
            
            office_coords = (
                office_location.get('latitude'),
                office_location.get('longitude')
            )
            
            distance = geodesic(employee_location, office_coords).meters
            return round(distance, 2)
        except:
            return None
    
    @classmethod
    def get_daily_summary(cls, date_filter=None, employee=None):
        """ملخص يومي للحضور"""
        queryset = cls.objects.all()
        
        if date_filter:
            queryset = queryset.filter(date=date_filter)
        else:
            queryset = queryset.filter(date=timezone.now().date())
        
        if employee:
            queryset = queryset.filter(employee=employee)
        
        summary = {
            'total_employees': queryset.count(),
            'present': queryset.filter(status__in=['present', 'late', 'overtime']).count(),
            'absent': queryset.filter(status='absent').count(),
            'late': queryset.filter(status='late').count(),
            'early_departure': queryset.filter(status='early_departure').count(),
            'overtime': queryset.filter(status='overtime').count(),
            'half_day': queryset.filter(status='half_day').count(),
            'on_leave': queryset.filter(status__in=['leave', 'sick_leave']).count(),
            'exceptions': queryset.filter(has_exception=True).count(),
            'unverified': queryset.filter(is_verified=False).count(),
        }
        
        # حساب النسب المئوية
        if summary['total_employees'] > 0:
            summary['attendance_rate'] = (summary['present'] / summary['total_employees']) * 100
            summary['punctuality_rate'] = ((summary['present'] - summary['late']) / summary['total_employees']) * 100
        else:
            summary['attendance_rate'] = 0
            summary['punctuality_rate'] = 0
        
        return summary
    
    @classmethod
    def get_employee_monthly_stats(cls, employee, year, month):
        """إحصائيات شهرية للموظف"""
        records = cls.objects.filter(
            employee=employee,
            date__year=year,
            date__month=month
        )
        
        stats = {
            'total_days': records.count(),
            'present_days': records.filter(status__in=['present', 'late', 'overtime']).count(),
            'absent_days': records.filter(status='absent').count(),
            'late_days': records.filter(status='late').count(),
            'overtime_days': records.filter(status='overtime').count(),
            'total_hours': sum(r.total_hours for r in records if r.total_hours),
            'total_overtime_hours': sum(r.overtime_hours for r in records if r.overtime_hours),
            'total_late_minutes': sum(r.late_minutes for r in records),
            'exceptions_count': records.filter(has_exception=True).count(),
        }
        
        # حساب المتوسطات
        if stats['present_days'] > 0:
            stats['avg_daily_hours'] = stats['total_hours'] / stats['present_days']
            stats['avg_late_minutes'] = stats['total_late_minutes'] / stats['present_days']
        else:
            stats['avg_daily_hours'] = 0
            stats['avg_late_minutes'] = 0
        
        return stats


class EmployeeShiftAssignmentEnhanced(models.Model):
    """نموذج تعيين الورديات المحسن للموظفين"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    employee = models.ForeignKey(
        'Hr.EmployeeEnhanced',
        on_delete=models.CASCADE,
        related_name='shift_assignments',
        verbose_name=_("الموظف")
    )
    
    shift = models.ForeignKey(
        'Hr.WorkShift',
        on_delete=models.CASCADE,
        related_name='employee_assignments',
        verbose_name=_("الوردية")
    )
    
    # Assignment Details
    ASSIGNMENT_TYPES = [
        ('permanent', _('دائم')),
        ('temporary', _('مؤقت')),
        ('rotating', _('متناوب')),
        ('seasonal', _('موسمي')),
        ('project_based', _('مشروع محدد')),
        ('emergency', _('طوارئ')),
    ]
    
    assignment_type = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_TYPES,
        default='permanent',
        verbose_name=_("نوع التعيين")
    )
    
    # Date Range
    start_date = models.DateField(verbose_name=_("تاريخ البداية"))
    end_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("تاريخ النهاية")
    )
    
    # Days of Week (for rotating shifts)
    days_of_week = models.JSONField(
        default=list,
        verbose_name=_("أيام الأسبوع"),
        help_text=_("أيام الأسبوع المطبق عليها التعيين [0=الاثنين, 6=الأحد]")
    )
    
    # Status and Priority
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )
    
    priority = models.PositiveIntegerField(
        default=1,
        verbose_name=_("الأولوية"),
        help_text=_("أولوية التعيين (1 = أعلى أولوية)")
    )
    
    # Approval Workflow
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('pending_approval', _('في انتظار الموافقة')),
        ('approved', _('معتمد')),
        ('rejected', _('مرفوض')),
        ('cancelled', _('ملغي')),
        ('expired', _('منتهي')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_("الحالة")
    )
    
    # Approval Information
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requested_shift_assignments',
        verbose_name=_("طلب بواسطة")
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_shift_assignments',
        verbose_name=_("معتمد بواسطة")
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الاعتماد")
    )
    
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("سبب الرفض")
    )
    
    # Additional Information
    reason = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("سبب التعيين")
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    # Notification Settings
    notify_employee = models.BooleanField(
        default=True,
        verbose_name=_("إشعار الموظف")
    )
    
    notification_sent = models.BooleanField(
        default=False,
        verbose_name=_("تم إرسال الإشعار")
    )
    
    notification_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ إرسال الإشعار")
    )
    
    # System Fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_shift_assignments',
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
        verbose_name = _("تعيين وردية محسن")
        verbose_name_plural = _("تعيينات الورديات المحسنة")
        db_table = 'hrms_employee_shift_assignment_enhanced'
        ordering = ['-start_date', 'priority']
        unique_together = [['employee', 'shift', 'start_date']]
        indexes = [
            models.Index(fields=['employee', 'is_active']),
            models.Index(fields=['shift', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status']),
            models.Index(fields=['assignment_type']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.shift.name} ({self.start_date})"
    
    def clean(self):
        """التحقق من صحة البيانات"""
        super().clean()
        
        # التحقق من التواريخ
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(_("تاريخ البداية يجب أن يكون قبل تاريخ النهاية"))
        
        # التحقق من عدم تداخل التعيينات النشطة
        if self.is_active and self.status == 'approved':
            overlapping = EmployeeShiftAssignmentEnhanced.objects.filter(
                employee=self.employee,
                is_active=True,
                status='approved'
            ).exclude(id=self.id)
            
            for assignment in overlapping:
                if self._check_date_overlap(assignment):
                    raise ValidationError(
                        _('يوجد تعيين وردية نشط متداخل لهذا الموظف في نفس الفترة')
                    )
    
    def _check_date_overlap(self, other_assignment):
        """فحص تداخل التواريخ"""
        # تحديد نهاية الفترة لكل تعيين
        self_end = self.end_date or date(2099, 12, 31)
        other_end = other_assignment.end_date or date(2099, 12, 31)
        
        # فحص التداخل
        return (self.start_date <= other_end and self_end >= other_assignment.start_date)
    
    def save(self, *args, **kwargs):
        """حفظ التعيين مع التحقق من الصحة"""
        # تحديث الحالة تلقائياً
        self._auto_update_status()
        
        super().save(*args, **kwargs)
        
        # إرسال الإشعارات إذا لزم الأمر
        if self.notify_employee and not self.notification_sent and self.status == 'approved':
            self._send_notification()
    
    def _auto_update_status(self):
        """تحديث الحالة تلقائياً"""
        today = timezone.now().date()
        
        # إذا انتهت الفترة، تحديث الحالة إلى منتهي
        if self.end_date and self.end_date < today and self.status == 'approved':
            self.status = 'expired'
            self.is_active = False
    
    def _send_notification(self):
        """إرسال إشعار للموظف"""
        # هنا يمكن تنفيذ منطق إرسال الإشعارات
        # مثل إرسال بريد إلكتروني أو إشعار في التطبيق
        self.notification_sent = True
        self.notification_sent_at = timezone.now()
    
    # Properties
    @property
    def is_current(self):
        """هل هذا التعيين حالي؟"""
        today = timezone.now().date()
        if not self.is_active or self.status != 'approved':
            return False
        
        if self.start_date > today:
            return False
        
        if self.end_date and self.end_date < today:
            return False
        
        return True
    
    @property
    def duration_days(self):
        """مدة التعيين بالأيام"""
        if not self.end_date:
            return None
        
        return (self.end_date - self.start_date).days + 1
    
    @property
    def days_remaining(self):
        """الأيام المتبقية"""
        if not self.end_date:
            return None
        
        today = timezone.now().date()
        if self.end_date < today:
            return 0
        
        return (self.end_date - today).days
    
    @property
    def applicable_days_display(self):
        """عرض الأيام المطبقة"""
        if not self.days_of_week:
            return _("جميع الأيام")
        
        day_names = [
            _("الاثنين"), _("الثلاثاء"), _("الأربعاء"), _("الخميس"),
            _("الجمعة"), _("السبت"), _("الأحد")
        ]
        
        selected_days = [day_names[day] for day in self.days_of_week if 0 <= day <= 6]
        return ", ".join(selected_days)
    
    # Methods
    def approve(self, approved_by_user, notes=None):
        """اعتماد التعيين"""
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        if notes:
            self.notes = f"{self.notes or ''}\nملاحظات الاعتماد: {notes}"
        self.save()
    
    def reject(self, reason):
        """رفض التعيين"""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.is_active = False
        self.save()
    
    def cancel(self, reason=None):
        """إلغاء التعيين"""
        self.status = 'cancelled'
        self.is_active = False
        if reason:
            self.notes = f"{self.notes or ''}\nسبب الإلغاء: {reason}"
        self.save()
    
    def extend(self, new_end_date, reason=None):
        """تمديد التعيين"""
        if new_end_date <= self.end_date:
            raise ValidationError(_("تاريخ النهاية الجديد يجب أن يكون بعد التاريخ الحالي"))
        
        old_end_date = self.end_date
        self.end_date = new_end_date
        
        if reason:
            self.notes = f"{self.notes or ''}\nتم التمديد من {old_end_date} إلى {new_end_date}: {reason}"
        
        self.save()
    
    def is_applicable_for_date(self, check_date):
        """هل التعيين مطبق في تاريخ معين؟"""
        # فحص النطاق الزمني
        if check_date < self.start_date:
            return False
        
        if self.end_date and check_date > self.end_date:
            return False
        
        # فحص أيام الأسبوع
        if self.days_of_week:
            weekday = check_date.weekday()  # 0=Monday, 6=Sunday
            if weekday not in self.days_of_week:
                return False
        
        return self.is_active and self.status == 'approved'
    
    def get_status_display_with_icon(self):
        """عرض الحالة مع الأيقونة"""
        status_icons = {
            'draft': '📝 مسودة',
            'pending_approval': '⏳ في انتظار الموافقة',
            'approved': '✅ معتمد',
            'rejected': '❌ مرفوض',
            'cancelled': '🚫 ملغي',
            'expired': '⏰ منتهي',
        }
        return status_icons.get(self.status, self.get_status_display())
    
    def get_assignment_summary(self):
        """ملخص التعيين"""
        return {
            'employee': self.employee.full_name,
            'shift': self.shift.name,
            'type': self.get_assignment_type_display(),
            'status': self.get_status_display_with_icon(),
            'period': {
                'start': self.start_date,
                'end': self.end_date,
                'duration_days': self.duration_days,
                'days_remaining': self.days_remaining
            },
            'applicable_days': self.applicable_days_display,
            'is_current': self.is_current,
            'priority': self.priority,
            'approval': {
                'approved_by': self.approved_by.get_full_name() if self.approved_by else None,
                'approved_at': self.approved_at,
                'rejection_reason': self.rejection_reason
            }
        }
    
    @classmethod
    def get_employee_current_assignment(cls, employee, date=None):
        """الحصول على التعيين الحالي للموظف"""
        if date is None:
            date = timezone.now().date()
        
        assignments = cls.objects.filter(
            employee=employee,
            is_active=True,
            status='approved',
            start_date__lte=date
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=date)
        ).order_by('priority', '-start_date')
        
        for assignment in assignments:
            if assignment.is_applicable_for_date(date):
                return assignment
        
        return None
    
    @classmethod
    def get_shift_assignments_for_date(cls, shift, date):
        """الحصول على تعيينات الوردية في تاريخ معين"""
        return cls.objects.filter(
            shift=shift,
            is_active=True,
            status='approved',
            start_date__lte=date
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=date)
        ).select_related('employee')
    
    @classmethod
    def get_pending_approvals(cls):
        """الحصول على التعيينات في انتظار الموافقة"""
        return cls.objects.filter(
            status='pending_approval'
        ).select_related('employee', 'shift', 'requested_by').order_by('-created_at')
    
    @classmethod
    def get_expiring_assignments(cls, days_ahead=7):
        """الحصول على التعيينات التي ستنتهي قريباً"""
        end_date = timezone.now().date() + timedelta(days=days_ahead)
        
        return cls.objects.filter(
            is_active=True,
            status='approved',
            end_date__lte=end_date,
            end_date__gte=timezone.now().date()
        ).select_related('employee', 'shift').order_by('end_date')


class AttendanceSummaryEnhanced(models.Model):
    """نموذج ملخص الحضور المتقدم"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    employee = models.ForeignKey(
        'Hr.EmployeeEnhanced',
        on_delete=models.CASCADE,
        related_name='attendance_summaries',
        verbose_name=_("الموظف")
    )
    
    # Period Information
    PERIOD_TYPES = [
        ('daily', _('يومي')),
        ('weekly', _('أسبوعي')),
        ('monthly', _('شهري')),
        ('quarterly', _('ربع سنوي')),
        ('yearly', _('سنوي')),
        ('custom', _('مخصص')),
    ]
    
    period_type = models.CharField(
        max_length=20,
        choices=PERIOD_TYPES,
        default='monthly',
        verbose_name=_("نوع الفترة")
    )
    
    period_start = models.DateField(verbose_name=_("بداية الفترة"))
    period_end = models.DateField(verbose_name=_("نهاية الفترة"))
    
    year = models.PositiveIntegerField(verbose_name=_("السنة"))
    month = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الشهر")
    )
    week = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الأسبوع")
    )
    
    # Basic Attendance Metrics
    total_working_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("إجمالي أيام العمل")
    )
    
    present_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام الحضور")
    )
    
    absent_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام الغياب")
    )
    
    late_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام التأخير")
    )
    
    early_departure_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام الانصراف المبكر")
    )
    
    half_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أنصاف الأيام")
    )
    
    overtime_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام الوقت الإضافي")
    )
    
    # Time Metrics
    total_hours_worked = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي ساعات العمل")
    )
    
    total_regular_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي الساعات العادية")
    )
    
    total_overtime_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي ساعات الوقت الإضافي")
    )
    
    total_break_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي ساعات الاستراحة")
    )
    
    expected_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("الساعات المتوقعة")
    )
    
    # Lateness and Early Departure
    total_late_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("إجمالي دقائق التأخير")
    )
    
    total_early_departure_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("إجمالي دقائق الانصراف المبكر")
    )
    
    avg_late_minutes = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("متوسط دقائق التأخير")
    )
    
    # Leave and Absence
    vacation_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام الإجازة")
    )
    
    sick_leave_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام الإجازة المرضية")
    )
    
    business_trip_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام المهام الرسمية")
    )
    
    training_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام التدريب")
    )
    
    # Performance Metrics
    attendance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("معدل الحضور (%)")
    )
    
    punctuality_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("معدل الالتزام بالمواعيد (%)")
    )
    
    productivity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("نقاط الإنتاجية")
    )
    
    # Exception Tracking
    total_exceptions = models.PositiveIntegerField(
        default=0,
        verbose_name=_("إجمالي الاستثناءات")
    )
    
    unverified_records = models.PositiveIntegerField(
        default=0,
        verbose_name=_("السجلات غير المتحققة")
    )
    
    manual_entries = models.PositiveIntegerField(
        default=0,
        verbose_name=_("الإدخالات اليدوية")
    )
    
    # Work Pattern Analysis
    most_common_check_in_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("أكثر أوقات الدخول شيوعاً")
    )
    
    most_common_check_out_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("أكثر أوقات الخروج شيوعاً")
    )
    
    avg_daily_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("متوسط الساعات اليومية")
    )
    
    # Comparison with Previous Period
    attendance_trend = models.CharField(
        max_length=20,
        choices=[
            ('improving', _('تحسن')),
            ('declining', _('تراجع')),
            ('stable', _('مستقر')),
            ('no_data', _('لا توجد بيانات')),
        ],
        default='no_data',
        verbose_name=_("اتجاه الحضور")
    )
    
    trend_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("نسبة التغيير (%)")
    )
    
    # Additional Metrics
    weekend_work_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام العمل في نهاية الأسبوع")
    )
    
    holiday_work_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام العمل في العطل")
    )
    
    remote_work_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام العمل عن بُعد")
    )
    
    # Status and Processing
    is_processed = models.BooleanField(
        default=False,
        verbose_name=_("تم المعالجة")
    )
    
    processing_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ المعالجة")
    )
    
    needs_review = models.BooleanField(
        default=False,
        verbose_name=_("يحتاج مراجعة")
    )
    
    review_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات المراجعة")
    )
    
    # System Fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_attendance_summaries',
        verbose_name=_("أنشئ بواسطة")
    )
    
    class Meta:
        verbose_name = _("ملخص حضور محسن")
        verbose_name_plural = _("ملخصات الحضور المحسنة")
        db_table = 'hrms_attendance_summary_enhanced'
        ordering = ['-period_start', 'employee']
        unique_together = [['employee', 'period_type', 'period_start', 'period_end']]
        indexes = [
            models.Index(fields=['employee', 'period_type']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['year', 'month']),
            models.Index(fields=['attendance_rate']),
            models.Index(fields=['is_processed']),
            models.Index(fields=['needs_review']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_period_type_display()} ({self.period_start})"
    
    def clean(self):
        """التحقق من صحة البيانات"""
        super().clean()
        
        if self.period_start and self.period_end:
            if self.period_start > self.period_end:
                raise ValidationError(_("تاريخ البداية يجب أن يكون قبل تاريخ النهاية"))
    
    def save(self, *args, **kwargs):
        """حفظ الملخص مع حساب القيم التلقائية"""
        # تحديد السنة والشهر تلقائياً
        if not self.year:
            self.year = self.period_start.year
        
        if not self.month and self.period_type == 'monthly':
            self.month = self.period_start.month
        
        # حساب المعدلات
        self.calculate_rates()
        
        # تحديد الاتجاه
        self.determine_trend()
        
        super().save(*args, **kwargs)
    
    def calculate_rates(self):
        """حساب المعدلات والنسب"""
        # معدل الحضور
        if self.total_working_days > 0:
            self.attendance_rate = round(
                (Decimal(self.present_days) / Decimal(self.total_working_days)) * 100, 2
            )
        else:
            self.attendance_rate = Decimal('0.00')
        
        # معدل الالتزام بالمواعيد
        if self.present_days > 0:
            punctual_days = self.present_days - self.late_days
            self.punctuality_rate = round(
                (Decimal(punctual_days) / Decimal(self.present_days)) * 100, 2
            )
        else:
            self.punctuality_rate = Decimal('0.00')
        
        # متوسط الساعات اليومية
        if self.present_days > 0:
            self.avg_daily_hours = round(
                self.total_hours_worked / Decimal(self.present_days), 2
            )
        else:
            self.avg_daily_hours = Decimal('0.00')
        
        # متوسط دقائق التأخير
        if self.late_days > 0:
            self.avg_late_minutes = round(
                Decimal(self.total_late_minutes) / Decimal(self.late_days), 2
            )
        else:
            self.avg_late_minutes = Decimal('0.00')
    
    def determine_trend(self):
        """تحديد اتجاه الحضور مقارنة بالفترة السابقة"""
        try:
            # البحث عن الملخص السابق
            previous_summary = AttendanceSummaryEnhanced.objects.filter(
                employee=self.employee,
                period_type=self.period_type,
                period_start__lt=self.period_start
            ).order_by('-period_start').first()
            
            if previous_summary:
                current_rate = float(self.attendance_rate)
                previous_rate = float(previous_summary.attendance_rate)
                
                if current_rate > previous_rate:
                    self.attendance_trend = 'improving'
                    self.trend_percentage = round(
                        ((current_rate - previous_rate) / previous_rate) * 100, 2
                    )
                elif current_rate < previous_rate:
                    self.attendance_trend = 'declining'
                    self.trend_percentage = round(
                        ((previous_rate - current_rate) / previous_rate) * 100, 2
                    )
                else:
                    self.attendance_trend = 'stable'
                    self.trend_percentage = Decimal('0.00')
            else:
                self.attendance_trend = 'no_data'
                self.trend_percentage = None
        
        except Exception:
            self.attendance_trend = 'no_data'
            self.trend_percentage = None
    
    # Properties
    @property
    def period_display(self):
        """عرض الفترة"""
        if self.period_type == 'monthly':
            return f"{self.year}/{self.month:02d}"
        elif self.period_type == 'yearly':
            return str(self.year)
        else:
            return f"{self.period_start} - {self.period_end}"
    
    @property
    def efficiency_score(self):
        """نقاط الكفاءة"""
        # حساب نقاط الكفاءة بناءً على عدة عوامل
        score = 0
        
        # نقاط الحضور (40%)
        score += float(self.attendance_rate) * 0.4
        
        # نقاط الالتزام بالمواعيد (30%)
        score += float(self.punctuality_rate) * 0.3
        
        # نقاط الوقت الإضافي (20%)
        if self.present_days > 0:
            overtime_ratio = float(self.overtime_days) / self.present_days
            overtime_score = min(100, overtime_ratio * 200)  # مكافأة للوقت الإضافي
            score += overtime_score * 0.2
        
        # نقاط قلة الاستثناءات (10%)
        if self.present_days > 0:
            exception_ratio = self.total_exceptions / self.present_days
            exception_score = max(0, 100 - (exception_ratio * 100))
            score += exception_score * 0.1
        
        return round(score, 2)
    
    @property
    def hours_deficit(self):
        """عجز الساعات"""
        return max(Decimal('0.00'), self.expected_hours - self.total_hours_worked)
    
    @property
    def hours_surplus(self):
        """فائض الساعات"""
        return max(Decimal('0.00'), self.total_hours_worked - self.expected_hours)
    
    # Methods
    def get_trend_display_with_icon(self):
        """عرض الاتجاه مع الأيقونة"""
        trend_icons = {
            'improving': '📈 تحسن',
            'declining': '📉 تراجع',
            'stable': '➡️ مستقر',
            'no_data': '❓ لا توجد بيانات',
        }
        return trend_icons.get(self.attendance_trend, self.get_attendance_trend_display())
    
    def get_performance_grade(self):
        """تقدير الأداء"""
        efficiency = self.efficiency_score
        
        if efficiency >= 90:
            return {'grade': 'A+', 'description': 'ممتاز', 'color': 'success'}
        elif efficiency >= 80:
            return {'grade': 'A', 'description': 'جيد جداً', 'color': 'success'}
        elif efficiency >= 70:
            return {'grade': 'B', 'description': 'جيد', 'color': 'info'}
        elif efficiency >= 60:
            return {'grade': 'C', 'description': 'مقبول', 'color': 'warning'}
        else:
            return {'grade': 'D', 'description': 'ضعيف', 'color': 'danger'}
    
    def get_detailed_breakdown(self):
        """تفصيل شامل للملخص"""
        return {
            'period': {
                'type': self.get_period_type_display(),
                'start': self.period_start,
                'end': self.period_end,
                'display': self.period_display
            },
            'attendance': {
                'total_working_days': self.total_working_days,
                'present_days': self.present_days,
                'absent_days': self.absent_days,
                'attendance_rate': float(self.attendance_rate)
            },
            'punctuality': {
                'late_days': self.late_days,
                'total_late_minutes': self.total_late_minutes,
                'avg_late_minutes': float(self.avg_late_minutes),
                'punctuality_rate': float(self.punctuality_rate)
            },
            'hours': {
                'total_worked': float(self.total_hours_worked),
                'regular': float(self.total_regular_hours),
                'overtime': float(self.total_overtime_hours),
                'expected': float(self.expected_hours),
                'avg_daily': float(self.avg_daily_hours),
                'deficit': float(self.hours_deficit),
                'surplus': float(self.hours_surplus)
            },
            'leave': {
                'vacation_days': self.vacation_days,
                'sick_leave_days': self.sick_leave_days,
                'business_trip_days': self.business_trip_days,
                'training_days': self.training_days
            },
            'performance': {
                'efficiency_score': self.efficiency_score,
                'grade': self.get_performance_grade(),
                'productivity_score': float(self.productivity_score) if self.productivity_score else None
            },
            'trend': {
                'direction': self.get_trend_display_with_icon(),
                'percentage': float(self.trend_percentage) if self.trend_percentage else None
            },
            'exceptions': {
                'total': self.total_exceptions,
                'unverified': self.unverified_records,
                'manual_entries': self.manual_entries
            }
        }
    
    @classmethod
    def generate_summary(cls, employee, period_start, period_end, period_type='custom'):
        """إنشاء ملخص حضور للفترة المحددة"""
        # الحصول على سجلات الحضور للفترة
        attendance_records = AttendanceRecordEnhanced.objects.filter(
            employee=employee,
            date__range=[period_start, period_end]
        )
        
        # إنشاء أو تحديث الملخص
        summary, created = cls.objects.get_or_create(
            employee=employee,
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
            defaults={
                'year': period_start.year,
                'month': period_start.month if period_type == 'monthly' else None,
            }
        )
        
        # حساب الإحصائيات
        summary._calculate_from_records(attendance_records)
        summary.is_processed = True
        summary.processing_date = timezone.now()
        summary.save()
        
        return summary
    
    def _calculate_from_records(self, records):
        """حساب الإحصائيات من السجلات"""
        # إعادة تعيين القيم
        self.total_working_days = records.count()
        self.present_days = records.filter(status__in=['present', 'late', 'overtime']).count()
        self.absent_days = records.filter(status='absent').count()
        self.late_days = records.filter(status='late').count()
        self.early_departure_days = records.filter(status='early_departure').count()
        self.half_days = records.filter(status='half_day').count()
        self.overtime_days = records.filter(status='overtime').count()
        
        # حساب الساعات
        self.total_hours_worked = sum(
            r.total_hours for r in records if r.total_hours
        ) or Decimal('0.00')
        
        self.total_regular_hours = sum(
            r.regular_hours for r in records if r.regular_hours
        ) or Decimal('0.00')
        
        self.total_overtime_hours = sum(
            r.overtime_hours for r in records if r.overtime_hours
        ) or Decimal('0.00')
        
        self.total_break_hours = sum(
            r.break_hours for r in records if r.break_hours
        ) or Decimal('0.00')
        
        # حساب التأخير
        self.total_late_minutes = sum(r.late_minutes for r in records)
        self.total_early_departure_minutes = sum(r.early_departure_minutes for r in records)
        
        # حساب الإجازات
        self.vacation_days = records.filter(status='leave').count()
        self.sick_leave_days = records.filter(status='sick_leave').count()
        self.business_trip_days = records.filter(status='business_trip').count()
        self.training_days = records.filter(status='training').count()
        
        # حساب الاستثناءات
        self.total_exceptions = records.filter(has_exception=True).count()
        self.unverified_records = records.filter(is_verified=False).count()
        self.manual_entries = records.filter(is_manual_entry=True).count()
        
        # العمل عن بُعد ونهاية الأسبوع
        self.remote_work_days = records.filter(work_from_home=True).count()
        
        # حساب الساعات المتوقعة (بناءً على الورديات المعينة)
        self.expected_hours = self._calculate_expected_hours(records)
    
    def _calculate_expected_hours(self, records):
        """حساب الساعات المتوقعة"""
        expected = Decimal('0.00')
        
        for record in records:
            if record.assigned_shift:
                expected += record.assigned_shift.total_hours
            else:
                # افتراض 8 ساعات يومياً إذا لم تكن هناك وردية محددة
                expected += Decimal('8.00')
        
        return expected
    
    @classmethod
    def get_department_summary(cls, department, period_start, period_end):
        """ملخص الحضور للقسم"""
        employees = department.employees.filter(is_active=True)
        summaries = cls.objects.filter(
            employee__in=employees,
            period_start=period_start,
            period_end=period_end
        )
        
        if not summaries.exists():
            return None
        
        total_employees = summaries.count()
        
        return {
            'department': department.name,
            'period': f"{period_start} - {period_end}",
            'total_employees': total_employees,
            'avg_attendance_rate': summaries.aggregate(
                avg_rate=models.Avg('attendance_rate')
            )['avg_rate'] or 0,
            'avg_punctuality_rate': summaries.aggregate(
                avg_rate=models.Avg('punctuality_rate')
            )['avg_rate'] or 0,
            'total_hours_worked': summaries.aggregate(
                total=models.Sum('total_hours_worked')
            )['total'] or 0,
            'total_overtime_hours': summaries.aggregate(
                total=models.Sum('total_overtime_hours')
            )['total'] or 0,
            'total_exceptions': summaries.aggregate(
                total=models.Sum('total_exceptions')
            )['total'] or 0,
        }