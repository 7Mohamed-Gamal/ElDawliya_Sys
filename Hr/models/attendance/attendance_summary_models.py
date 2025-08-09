# -*- coding: utf-8 -*-
"""
نماذج ملخص الحضور المتقدمة لنظام إدارة الموارد البشرية (HRMS)
Enhanced Attendance Summary Models with Advanced Features
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


class AttendanceSummaryEnhanced(models.Model):
    """نموذج ملخص الحضور اليومي المحسن"""
    
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
    
    date = models.DateField(verbose_name=_("التاريخ"))
    
    # Shift Information
    assigned_shift = models.ForeignKey(
        'Hr.WorkShiftEnhanced',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("الوردية المعينة")
    )
    
    # Time Summary
    scheduled_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت البداية المجدول")
    )
    
    scheduled_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت النهاية المجدول")
    )
    
    actual_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت البداية الفعلي")
    )
    
    actual_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("وقت النهاية الفعلي")
    )
    
    # Hours Calculation
    scheduled_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("الساعات المجدولة")
    )
    
    actual_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("الساعات الفعلية")
    )
    
    regular_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
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
    
    # Attendance Metrics
    late_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("دقائق التأخير")
    )
    
    early_departure_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("دقائق الانصراف المبكر")
    )
    
    # Status Information
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
        ('work_from_home', _('عمل من المنزل')),
        ('pending', _('في انتظار المراجعة')),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present',
        verbose_name=_("الحالة")
    )
    
    # Leave Information
    leave_type = models.ForeignKey(
        'Hr.LeaveType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("نوع الإجازة")
    )
    
    leave_request = models.ForeignKey(
        'Hr.LeaveRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("طلب الإجازة")
    )
    
    # Holiday Information
    # holiday = models.ForeignKey(
    #     'Hr.Holiday',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name=_("العطلة")
    # )
    
    # Performance Metrics
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
    
    tasks_assigned = models.PositiveIntegerField(
        default=0,
        verbose_name=_("المهام المعينة")
    )
    
    # Location and Method
    work_location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("موقع العمل")
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
        verbose_name=_("طريقة تسجيل الدخول")
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
        verbose_name=_("طريقة تسجيل الخروج")
    )
    
    # Exceptions and Flags
    has_exception = models.BooleanField(
        default=False,
        verbose_name=_("يحتوي على استثناء")
    )
    
    exception_types = models.JSONField(
        default=list,
        verbose_name=_("أنواع الاستثناءات")
    )
    
    is_manual_entry = models.BooleanField(
        default=False,
        verbose_name=_("إدخال يدوي")
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("تم التحقق")
    )
    
    requires_approval = models.BooleanField(
        default=False,
        verbose_name=_("يتطلب موافقة")
    )
    
    # Weather and Environmental
    weather_condition = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("حالة الطقس")
    )
    
    temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("درجة الحرارة")
    )
    
    # Cost Calculation
    regular_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("الأجر العادي")
    )
    
    overtime_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("أجر الوقت الإضافي")
    )
    
    total_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي الأجر")
    )
    
    # Deductions
    late_deduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("خصم التأخير")
    )
    
    absence_deduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("خصم الغياب")
    )
    
    total_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي الخصومات")
    )
    
    # Net Pay
    net_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("صافي الأجر")
    )
    
    # Approval Information
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_attendance_summaries',
        verbose_name=_("معتمد بواسطة")
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الاعتماد")
    )
    
    # Notes and Comments
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("ملاحظات")
    )
    
    supervisor_comments = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("تعليقات المشرف")
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
    metadata = models.JSONField(
        default=dict,
        verbose_name=_("بيانات إضافية")
    )
    
    class Meta:
        verbose_name = _("ملخص حضور محسن")
        verbose_name_plural = _("ملخصات الحضور المحسنة")
        db_table = 'hrms_attendance_summary_enhanced'
        ordering = ['-date', 'employee']
        unique_together = [['employee', 'date']]
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['has_exception']),
            models.Index(fields=['requires_approval']),
            models.Index(fields=['assigned_shift']),
            models.Index(fields=['leave_type']),
            # models.Index(fields=['holiday']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.get_status_display()})"
    
    def clean(self):
        """التحقق من صحة البيانات"""
        super().clean()
        
        # التحقق من الأوقات
        if self.actual_start_time and self.actual_end_time:
            if not (self.assigned_shift and self.assigned_shift.is_overnight):
                if self.actual_end_time <= self.actual_start_time:
                    raise ValidationError(_("وقت النهاية الفعلي يجب أن يكون بعد وقت البداية"))
    
    def save(self, *args, **kwargs):
        """حفظ الملخص مع حساب القيم التلقائية"""
        # حساب الساعات والمقاييس
        self.calculate_hours()
        self.calculate_pay()
        self.calculate_deductions()
        self.calculate_net_pay()
        
        # تحديد الحالة والاستثناءات
        self.determine_status()
        self.check_exceptions()
        
        super().save(*args, **kwargs)
    
    def calculate_hours(self):
        """حساب الساعات المختلفة"""
        # الساعات المجدولة
        if self.assigned_shift:
            self.scheduled_hours = self.assigned_shift.total_hours
            self.scheduled_start_time = self.assigned_shift.start_time
            self.scheduled_end_time = self.assigned_shift.end_time
        
        # الساعات الفعلية
        if self.actual_start_time and self.actual_end_time:
            start_dt = datetime.combine(self.date, self.actual_start_time)
            end_dt = datetime.combine(self.date, self.actual_end_time)
            
            # للورديات الليلية
            if self.assigned_shift and self.assigned_shift.is_overnight:
                if self.actual_end_time < self.actual_start_time:
                    end_dt += timedelta(days=1)
            
            total_time = end_dt - start_dt
            self.actual_hours = Decimal(str(total_time.total_seconds() / 3600))
            
            # خصم وقت الاستراحة
            if self.assigned_shift and self.assigned_shift.break_duration_hours:
                self.actual_hours -= self.assigned_shift.break_duration_hours
                self.break_hours = self.assigned_shift.break_duration_hours
            
            # حساب الساعات العادية والإضافية
            if self.scheduled_hours:
                if self.actual_hours > self.scheduled_hours:
                    self.regular_hours = self.scheduled_hours
                    self.overtime_hours = self.actual_hours - self.scheduled_hours
                else:
                    self.regular_hours = self.actual_hours
                    self.overtime_hours = Decimal('0.00')
            else:
                self.regular_hours = self.actual_hours
                self.overtime_hours = Decimal('0.00')
        
        # حساب دقائق التأخير والانصراف المبكر
        if self.assigned_shift:
            if self.actual_start_time:
                self.late_minutes = self.assigned_shift.calculate_late_minutes(self.actual_start_time)
            
            if self.actual_end_time:
                self.early_departure_minutes = self.assigned_shift.calculate_early_departure_minutes(self.actual_end_time)
    
    def calculate_pay(self):
        """حساب الأجور"""
        if not self.employee.salary_per_hour:
            return
        
        hourly_rate = self.employee.salary_per_hour
        
        # الأجر العادي
        self.regular_pay = self.regular_hours * hourly_rate
        
        # أجر الوقت الإضافي
        if self.overtime_hours > 0:
            overtime_multiplier = Decimal('1.5')  # يمكن أخذها من إعدادات الوردية
            if self.assigned_shift:
                overtime_multiplier = self.assigned_shift.overtime_multiplier
            
            self.overtime_pay = self.overtime_hours * hourly_rate * overtime_multiplier
        
        # إجمالي الأجر
        self.total_pay = self.regular_pay + self.overtime_pay
    
    def calculate_deductions(self):
        """حساب الخصومات"""
        self.late_deduction = Decimal('0.00')
        self.absence_deduction = Decimal('0.00')
        
        # خصم التأخير
        if self.late_minutes > 0 and self.employee.salary_per_hour:
            # خصم حسب الدقائق
            late_hours = Decimal(str(self.late_minutes / 60))
            self.late_deduction = late_hours * self.employee.salary_per_hour
        
        # خصم الغياب
        if self.status == 'absent' and self.employee.salary_per_hour:
            if self.scheduled_hours:
                self.absence_deduction = self.scheduled_hours * self.employee.salary_per_hour
        
        # إجمالي الخصومات
        self.total_deductions = self.late_deduction + self.absence_deduction
    
    def calculate_net_pay(self):
        """حساب صافي الأجر"""
        self.net_pay = self.total_pay - self.total_deductions
    
    def determine_status(self):
        """تحديد الحالة"""
        # إذا كان في إجازة
        if self.leave_request and self.leave_request.status == 'approved':
            if self.leave_type and self.leave_type.code == 'sick':
                self.status = 'sick_leave'
            else:
                self.status = 'leave'
            return
        
        # إذا كان يوم عطلة
        # if self.holiday:
        #     self.status = 'holiday'
        #     return
        
        # إذا لم يحضر
        if not self.actual_start_time and not self.actual_end_time:
            self.status = 'absent'
            return
        
        # تحديد الحالة حسب الأداء
        if self.late_minutes > 0:
            self.status = 'late'
        elif self.early_departure_minutes > 0:
            self.status = 'early_departure'
        elif self.overtime_hours > 0:
            self.status = 'overtime'
        elif self.actual_hours and self.actual_hours < 4:  # أقل من 4 ساعات
            self.status = 'half_day'
        else:
            self.status = 'present'
    
    def check_exceptions(self):
        """فحص الاستثناءات"""
        exceptions = []
        
        if self.late_minutes > 0:
            exceptions.append('late_arrival')
        
        if self.early_departure_minutes > 0:
            exceptions.append('early_departure')
        
        if self.actual_start_time and not self.actual_end_time:
            exceptions.append('missing_check_out')
        
        if not self.actual_start_time and self.actual_end_time:
            exceptions.append('missing_check_in')
        
        if self.overtime_hours > 0:
            exceptions.append('overtime_worked')
        
        if self.is_manual_entry:
            exceptions.append('manual_entry')
        
        self.exception_types = exceptions
        self.has_exception = len(exceptions) > 0
        
        # تحديد ما إذا كان يتطلب موافقة
        self.requires_approval = (
            self.has_exception or 
            self.is_manual_entry or 
            self.overtime_hours > 0
        )
    
    # Properties
    @property
    def is_present(self):
        """هل الموظف حاضر؟"""
        return self.status in ['present', 'late', 'overtime', 'work_from_home']
    
    @property
    def attendance_percentage(self):
        """نسبة الحضور"""
        if not self.scheduled_hours or self.scheduled_hours == 0:
            return 0
        
        if not self.actual_hours:
            return 0
        
        return min(100, (float(self.actual_hours) / float(self.scheduled_hours)) * 100)
    
    @property
    def efficiency_score(self):
        """نقاط الكفاءة"""
        score = 100
        
        # خصم نقاط للتأخير
        if self.late_minutes > 0:
            score -= min(20, self.late_minutes / 5)  # خصم نقطة لكل 5 دقائق تأخير
        
        # خصم نقاط للانصراف المبكر
        if self.early_departure_minutes > 0:
            score -= min(20, self.early_departure_minutes / 5)
        
        # إضافة نقاط للوقت الإضافي
        if self.overtime_hours > 0:
            score += min(10, float(self.overtime_hours) * 2)
        
        # إضافة نقاط للإنتاجية
        if self.productivity_score:
            score = (score + float(self.productivity_score)) / 2
        
        return max(0, min(100, round(score, 2)))
    
    @property
    def status_display_with_icon(self):
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
            'work_from_home': '🏠 عمل من المنزل',
            'pending': '⏳ في انتظار المراجعة',
        }
        return status_icons.get(self.status, self.get_status_display())
    
    @property
    def time_summary(self):
        """ملخص الأوقات"""
        return {
            'scheduled_start': self.scheduled_start_time.strftime('%H:%M') if self.scheduled_start_time else None,
            'scheduled_end': self.scheduled_end_time.strftime('%H:%M') if self.scheduled_end_time else None,
            'actual_start': self.actual_start_time.strftime('%H:%M') if self.actual_start_time else None,
            'actual_end': self.actual_end_time.strftime('%H:%M') if self.actual_end_time else None,
            'scheduled_hours': float(self.scheduled_hours),
            'actual_hours': float(self.actual_hours),
            'regular_hours': float(self.regular_hours),
            'overtime_hours': float(self.overtime_hours),
            'break_hours': float(self.break_hours),
            'late_minutes': self.late_minutes,
            'early_departure_minutes': self.early_departure_minutes,
        }
    
    @property
    def pay_summary(self):
        """ملخص الأجور"""
        return {
            'regular_pay': float(self.regular_pay),
            'overtime_pay': float(self.overtime_pay),
            'total_pay': float(self.total_pay),
            'late_deduction': float(self.late_deduction),
            'absence_deduction': float(self.absence_deduction),
            'total_deductions': float(self.total_deductions),
            'net_pay': float(self.net_pay),
        }
    
    # Methods
    def approve(self, approved_by_user, comments=None):
        """اعتماد الملخص"""
        self.is_verified = True
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.requires_approval = False
        
        if comments:
            self.supervisor_comments = comments
        
        self.save()
    
    def reject(self, rejected_by_user, reason):
        """رفض الملخص"""
        self.is_verified = False
        self.requires_approval = True
        self.supervisor_comments = f"مرفوض: {reason}"
        
        self.save()
    
    def add_note(self, note, user=None):
        """إضافة ملاحظة"""
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
        user_name = user.get_full_name() if user else 'النظام'
        
        new_note = f"[{timestamp}] {user_name}: {note}"
        
        if self.notes:
            self.notes += f"\n{new_note}"
        else:
            self.notes = new_note
        
        self.save(update_fields=['notes'])
    
    def calculate_task_completion_rate(self):
        """حساب معدل إنجاز المهام"""
        if self.tasks_assigned == 0:
            return 0
        
        return round((self.tasks_completed / self.tasks_assigned) * 100, 2)
    
    @classmethod
    def create_from_attendance_record(cls, attendance_record):
        """إنشاء ملخص من سجل الحضور"""
        summary, created = cls.objects.get_or_create(
            employee=attendance_record.employee,
            date=attendance_record.date,
            defaults={
                'assigned_shift': attendance_record.assigned_shift,
                'actual_start_time': attendance_record.check_in_time,
                'actual_end_time': attendance_record.check_out_time,
                'status': attendance_record.status,
                'check_in_method': attendance_record.check_in_method,
                'check_out_method': attendance_record.check_out_method,
                'is_manual_entry': attendance_record.is_manual_entry,
                'has_exception': attendance_record.has_exception,
                'work_location': attendance_record.check_in_location.get('address') if attendance_record.check_in_location else None,
                'productivity_score': attendance_record.productivity_score,
                'tasks_completed': attendance_record.tasks_completed,
            }
        )
        
        if not created:
            # تحديث البيانات الموجودة
            summary.actual_start_time = attendance_record.check_in_time
            summary.actual_end_time = attendance_record.check_out_time
            summary.status = attendance_record.status
            summary.check_in_method = attendance_record.check_in_method
            summary.check_out_method = attendance_record.check_out_method
            summary.is_manual_entry = attendance_record.is_manual_entry
            summary.has_exception = attendance_record.has_exception
            summary.productivity_score = attendance_record.productivity_score
            summary.tasks_completed = attendance_record.tasks_completed
            summary.save()
        
        return summary
    
    @classmethod
    def get_monthly_summary(cls, employee, year, month):
        """ملخص شهري للموظف"""
        summaries = cls.objects.filter(
            employee=employee,
            date__year=year,
            date__month=month
        )
        
        stats = {
            'total_days': summaries.count(),
            'present_days': summaries.filter(status__in=['present', 'late', 'overtime', 'work_from_home']).count(),
            'absent_days': summaries.filter(status='absent').count(),
            'late_days': summaries.filter(status='late').count(),
            'overtime_days': summaries.filter(status='overtime').count(),
            'leave_days': summaries.filter(status__in=['leave', 'sick_leave']).count(),
            'holiday_days': summaries.filter(status='holiday').count(),
            'total_scheduled_hours': sum(s.scheduled_hours for s in summaries if s.scheduled_hours),
            'total_actual_hours': sum(s.actual_hours for s in summaries if s.actual_hours),
            'total_overtime_hours': sum(s.overtime_hours for s in summaries if s.overtime_hours),
            'total_late_minutes': sum(s.late_minutes for s in summaries),
            'total_regular_pay': sum(s.regular_pay for s in summaries if s.regular_pay),
            'total_overtime_pay': sum(s.overtime_pay for s in summaries if s.overtime_pay),
            'total_deductions': sum(s.total_deductions for s in summaries if s.total_deductions),
            'total_net_pay': sum(s.net_pay for s in summaries if s.net_pay),
            'exceptions_count': summaries.filter(has_exception=True).count(),
            'pending_approval_count': summaries.filter(requires_approval=True).count(),
        }
        
        # حساب المتوسطات والنسب
        if stats['total_days'] > 0:
            stats['attendance_rate'] = round((stats['present_days'] / stats['total_days']) * 100, 2)
            stats['punctuality_rate'] = round(((stats['present_days'] - stats['late_days']) / stats['total_days']) * 100, 2)
            stats['avg_daily_hours'] = round(stats['total_actual_hours'] / stats['present_days'], 2) if stats['present_days'] > 0 else 0
            stats['avg_efficiency_score'] = round(sum(s.efficiency_score for s in summaries) / stats['total_days'], 2)
        else:
            stats['attendance_rate'] = 0
            stats['punctuality_rate'] = 0
            stats['avg_daily_hours'] = 0
            stats['avg_efficiency_score'] = 0
        
        return stats
    
    @classmethod
    def get_department_daily_summary(cls, department, date_obj=None):
        """ملخص يومي للقسم"""
        if not date_obj:
            date_obj = timezone.now().date()
        
        summaries = cls.objects.filter(
            employee__department=department,
            date=date_obj
        )
        
        return {
            'total_employees': summaries.count(),
            'present': summaries.filter(status__in=['present', 'late', 'overtime', 'work_from_home']).count(),
            'absent': summaries.filter(status='absent').count(),
            'late': summaries.filter(status='late').count(),
            'on_leave': summaries.filter(status__in=['leave', 'sick_leave']).count(),
            'overtime': summaries.filter(status='overtime').count(),
            'exceptions': summaries.filter(has_exception=True).count(),
            'pending_approval': summaries.filter(requires_approval=True).count(),
            'total_hours_worked': sum(s.actual_hours for s in summaries if s.actual_hours),
            'total_overtime_hours': sum(s.overtime_hours for s in summaries if s.overtime_hours),
            'avg_efficiency_score': round(sum(s.efficiency_score for s in summaries) / summaries.count(), 2) if summaries.count() > 0 else 0,
        }


class MonthlyAttendanceSummary(models.Model):
    """ملخص الحضور الشهري"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    
    employee = models.ForeignKey(
        'Hr.EmployeeEnhanced',
        on_delete=models.CASCADE,
        related_name='monthly_attendance_summaries',
        verbose_name=_("الموظف")
    )
    
    year = models.PositiveIntegerField(verbose_name=_("السنة"))
    month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name=_("الشهر")
    )
    
    # Days Count
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
    
    overtime_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام الوقت الإضافي")
    )
    
    leave_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام الإجازة")
    )
    
    holiday_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("أيام العطل")
    )
    
    # Hours Summary
    total_scheduled_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي الساعات المجدولة")
    )
    
    total_actual_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي الساعات الفعلية")
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
    
    # Time Metrics
    total_late_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("إجمالي دقائق التأخير")
    )
    
    total_early_departure_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("إجمالي دقائق الانصراف المبكر")
    )
    
    # Performance Metrics
    attendance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("معدل الحضور")
    )
    
    punctuality_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("معدل الالتزام بالوقت")
    )
    
    avg_daily_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("متوسط الساعات اليومية")
    )
    
    avg_efficiency_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("متوسط نقاط الكفاءة")
    )
    
    # Financial Summary
    total_regular_pay = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي الأجر العادي")
    )
    
    total_overtime_pay = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي أجر الوقت الإضافي")
    )
    
    total_deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي الخصومات")
    )
    
    total_net_pay = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("إجمالي صافي الأجر")
    )
    
    # Exception Counts
    total_exceptions = models.PositiveIntegerField(
        default=0,
        verbose_name=_("إجمالي الاستثناءات")
    )
    
    manual_entries = models.PositiveIntegerField(
        default=0,
        verbose_name=_("الإدخالات اليدوية")
    )
    
    # Status
    is_finalized = models.BooleanField(
        default=False,
        verbose_name=_("مكتمل")
    )
    
    finalized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("اكتمل بواسطة")
    )
    
    finalized_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الاكتمال")
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
    
    class Meta:
        verbose_name = _("ملخص حضور شهري")
        verbose_name_plural = _("ملخصات الحضور الشهرية")
        db_table = 'hrms_monthly_attendance_summary'
        ordering = ['-year', '-month', 'employee']
        unique_together = [['employee', 'year', 'month']]
        indexes = [
            models.Index(fields=['employee', 'year', 'month']),
            models.Index(fields=['year', 'month']),
            models.Index(fields=['is_finalized']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.year}/{self.month:02d}"
    
    def calculate_summary(self):
        """حساب الملخص من البيانات اليومية"""
        daily_summaries = AttendanceSummaryEnhanced.objects.filter(
            employee=self.employee,
            date__year=self.year,
            date__month=self.month
        )
        
        # حساب الأيام
        self.total_working_days = daily_summaries.count()
        self.present_days = daily_summaries.filter(
            status__in=['present', 'late', 'overtime', 'work_from_home']
        ).count()
        self.absent_days = daily_summaries.filter(status='absent').count()
        self.late_days = daily_summaries.filter(status='late').count()
        self.overtime_days = daily_summaries.filter(status='overtime').count()
        self.leave_days = daily_summaries.filter(
            status__in=['leave', 'sick_leave']
        ).count()
        self.holiday_days = daily_summaries.filter(status='holiday').count()
        
        # حساب الساعات
        self.total_scheduled_hours = sum(
            s.scheduled_hours for s in daily_summaries if s.scheduled_hours
        )
        self.total_actual_hours = sum(
            s.actual_hours for s in daily_summaries if s.actual_hours
        )
        self.total_regular_hours = sum(
            s.regular_hours for s in daily_summaries if s.regular_hours
        )
        self.total_overtime_hours = sum(
            s.overtime_hours for s in daily_summaries if s.overtime_hours
        )
        
        # حساب الدقائق
        self.total_late_minutes = sum(s.late_minutes for s in daily_summaries)
        self.total_early_departure_minutes = sum(
            s.early_departure_minutes for s in daily_summaries
        )
        
        # حساب المعدلات
        if self.total_working_days > 0:
            self.attendance_rate = Decimal(
                str((self.present_days / self.total_working_days) * 100)
            )
            self.punctuality_rate = Decimal(
                str(((self.present_days - self.late_days) / self.total_working_days) * 100)
            )
            
            if self.present_days > 0:
                self.avg_daily_hours = self.total_actual_hours / self.present_days
            
            self.avg_efficiency_score = Decimal(
                str(sum(s.efficiency_score for s in daily_summaries) / self.total_working_days)
            )
        
        # حساب الأجور
        self.total_regular_pay = sum(
            s.regular_pay for s in daily_summaries if s.regular_pay
        )
        self.total_overtime_pay = sum(
            s.overtime_pay for s in daily_summaries if s.overtime_pay
        )
        self.total_deductions = sum(
            s.total_deductions for s in daily_summaries if s.total_deductions
        )
        self.total_net_pay = sum(
            s.net_pay for s in daily_summaries if s.net_pay
        )
        
        # حساب الاستثناءات
        self.total_exceptions = daily_summaries.filter(has_exception=True).count()
        self.manual_entries = daily_summaries.filter(is_manual_entry=True).count()
        
        self.save()
    
    def finalize(self, user):
        """اكتمال الملخص الشهري"""
        self.is_finalized = True
        self.finalized_by = user
        self.finalized_at = timezone.now()
        self.save()
    
    @classmethod
    def generate_for_employee(cls, employee, year, month):
        """إنشاء ملخص شهري للموظف"""
        summary, created = cls.objects.get_or_create(
            employee=employee,
            year=year,
            month=month
        )
        
        summary.calculate_summary()
        return summary
    
    @classmethod
    def generate_for_department(cls, department, year, month):
        """إنشاء ملخصات شهرية لجميع موظفي القسم"""
        employees = department.employees.filter(is_active=True)
        summaries = []
        
        for employee in employees:
            summary = cls.generate_for_employee(employee, year, month)
            summaries.append(summary)
        
        return summaries