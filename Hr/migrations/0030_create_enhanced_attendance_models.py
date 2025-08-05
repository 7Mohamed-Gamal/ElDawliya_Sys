# Generated migration for enhanced attendance models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Hr', '0029_create_enhanced_employee_extended_models'),
    ]

    operations = [
        # Create AttendanceRecordEnhanced
        migrations.CreateModel(
            name='AttendanceRecordEnhanced',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('date', models.DateField(verbose_name='التاريخ')),
                ('check_in_time', models.TimeField(blank=True, null=True, verbose_name='وقت الدخول')),
                ('check_in_method', models.CharField(blank=True, choices=[('fingerprint', 'بصمة الإصبع'), ('face', 'التعرف على الوجه'), ('card', 'البطاقة'), ('pin', 'رمز PIN'), ('manual', 'يدوي'), ('mobile', 'تطبيق الجوال'), ('web', 'الموقع الإلكتروني')], max_length=20, null=True, verbose_name='طريقة الدخول')),
                ('check_in_location', models.JSONField(blank=True, help_text='إحداثيات GPS للدخول', null=True, verbose_name='موقع الدخول')),
                ('check_out_time', models.TimeField(blank=True, null=True, verbose_name='وقت الخروج')),
                ('check_out_method', models.CharField(blank=True, choices=[('fingerprint', 'بصمة الإصبع'), ('face', 'التعرف على الوجه'), ('card', 'البطاقة'), ('pin', 'رمز PIN'), ('manual', 'يدوي'), ('mobile', 'تطبيق الجوال'), ('web', 'الموقع الإلكتروني')], max_length=20, null=True, verbose_name='طريقة الخروج')),
                ('check_out_location', models.JSONField(blank=True, help_text='إحداثيات GPS للخروج', null=True, verbose_name='موقع الخروج')),
                ('status', models.CharField(choices=[('present', 'حاضر'), ('absent', 'غائب'), ('late', 'متأخر'), ('early_departure', 'انصراف مبكر'), ('half_day', 'نصف يوم'), ('overtime', 'وقت إضافي'), ('holiday', 'عطلة'), ('leave', 'إجازة'), ('sick_leave', 'إجازة مرضية'), ('business_trip', 'مهمة عمل'), ('training', 'تدريب'), ('pending', 'في انتظار المراجعة')], default='present', max_length=20, verbose_name='الحالة')),
                ('total_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='إجمالي الساعات')),
                ('regular_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='الساعات العادية')),
                ('overtime_hours', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='ساعات الوقت الإضافي')),
                ('break_hours', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='ساعات الاستراحة')),
                ('late_minutes', models.PositiveIntegerField(default=0, verbose_name='دقائق التأخير')),
                ('early_departure_minutes', models.PositiveIntegerField(default=0, verbose_name='دقائق الانصراف المبكر')),
                ('break_start_time', models.TimeField(blank=True, null=True, verbose_name='بداية الاستراحة')),
                ('break_end_time', models.TimeField(blank=True, null=True, verbose_name='نهاية الاستراحة')),
                ('is_verified', models.BooleanField(default=False, verbose_name='تم التحقق')),
                ('verified_at', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ التحقق')),
                ('is_manual_entry', models.BooleanField(default=False, verbose_name='إدخال يدوي')),
                ('manual_entry_reason', models.TextField(blank=True, null=True, verbose_name='سبب الإدخال اليدوي')),
                ('has_exception', models.BooleanField(default=False, verbose_name='يحتوي على استثناء')),
                ('exception_type', models.CharField(blank=True, choices=[('late_arrival', 'تأخير في الوصول'), ('early_departure', 'انصراف مبكر'), ('missing_check_in', 'عدم تسجيل دخول'), ('missing_check_out', 'عدم تسجيل خروج'), ('long_break', 'استراحة طويلة'), ('overtime_unapproved', 'وقت إضافي غير معتمد'), ('location_mismatch', 'عدم تطابق الموقع'), ('duplicate_entry', 'إدخال مكرر'), ('system_error', 'خطأ في النظام')], max_length=50, null=True, verbose_name='نوع الاستثناء')),
                ('exception_notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات الاستثناء')),
                ('weather_condition', models.CharField(blank=True, max_length=50, null=True, verbose_name='حالة الطقس')),
                ('work_from_home', models.BooleanField(default=False, verbose_name='عمل من المنزل')),
                ('remote_work_approved', models.BooleanField(default=False, verbose_name='العمل عن بُعد معتمد')),
                ('productivity_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='نقاط الإنتاجية')),
                ('tasks_completed', models.PositiveIntegerField(default=0, verbose_name='المهام المكتملة')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('raw_data', models.JSONField(blank=True, help_text='البيانات الخام من جهاز الحضور', null=True, verbose_name='البيانات الخام')),
                ('assigned_shift', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendance_records', to='Hr.workshift', verbose_name='الوردية المعينة')),
                ('check_in_machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='check_in_records', to='Hr.attendancemachine', verbose_name='جهاز الدخول')),
                ('check_out_machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='check_out_records', to='Hr.attendancemachine', verbose_name='جهاز الخروج')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='Hr.employeeenhanced', verbose_name='الموظف')),
                ('entered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manual_attendance_entries', to=settings.AUTH_USER_MODEL, verbose_name='أدخل بواسطة')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_attendance_records', to=settings.AUTH_USER_MODEL, verbose_name='تم التحقق بواسطة')),
            ],
            options={
                'verbose_name': 'سجل حضور محسن',
                'verbose_name_plural': 'سجلات الحضور المحسنة',
                'db_table': 'hrms_attendance_record_enhanced',
                'ordering': ['-date', '-check_in_time'],
            },
        ),
        
        # Create EmployeeShiftAssignmentEnhanced
        migrations.CreateModel(
            name='EmployeeShiftAssignmentEnhanced',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('assignment_type', models.CharField(choices=[('permanent', 'دائم'), ('temporary', 'مؤقت'), ('rotating', 'متناوب'), ('seasonal', 'موسمي'), ('project_based', 'مشروع محدد'), ('emergency', 'طوارئ')], default='permanent', max_length=20, verbose_name='نوع التعيين')),
                ('start_date', models.DateField(verbose_name='تاريخ البداية')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='تاريخ النهاية')),
                ('days_of_week', models.JSONField(default=list, help_text='أيام الأسبوع المطبق عليها التعيين [0=الاثنين, 6=الأحد]', verbose_name='أيام الأسبوع')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('priority', models.PositiveIntegerField(default=1, help_text='أولوية التعيين (1 = أعلى أولوية)', verbose_name='الأولوية')),
                ('status', models.CharField(choices=[('draft', 'مسودة'), ('pending_approval', 'في انتظار الموافقة'), ('approved', 'معتمد'), ('rejected', 'مرفوض'), ('cancelled', 'ملغي'), ('expired', 'منتهي')], default='draft', max_length=20, verbose_name='الحالة')),
                ('approved_at', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الاعتماد')),
                ('rejection_reason', models.TextField(blank=True, null=True, verbose_name='سبب الرفض')),
                ('reason', models.TextField(blank=True, null=True, verbose_name='سبب التعيين')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('notify_employee', models.BooleanField(default=True, verbose_name='إشعار الموظف')),
                ('notification_sent', models.BooleanField(default=False, verbose_name='تم إرسال الإشعار')),
                ('notification_sent_at', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ إرسال الإشعار')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_shift_assignments', to=settings.AUTH_USER_MODEL, verbose_name='معتمد بواسطة')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_shift_assignments', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_assignments', to='Hr.employeeenhanced', verbose_name='الموظف')),
                ('requested_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requested_shift_assignments', to=settings.AUTH_USER_MODEL, verbose_name='طلب بواسطة')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_assignments', to='Hr.workshift', verbose_name='الوردية')),
            ],
            options={
                'verbose_name': 'تعيين وردية محسن',
                'verbose_name_plural': 'تعيينات الورديات المحسنة',
                'db_table': 'hrms_employee_shift_assignment_enhanced',
                'ordering': ['-start_date', 'priority'],
            },
        ),
        
        # Create AttendanceSummaryEnhanced
        migrations.CreateModel(
            name='AttendanceSummaryEnhanced',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('period_type', models.CharField(choices=[('daily', 'يومي'), ('weekly', 'أسبوعي'), ('monthly', 'شهري'), ('quarterly', 'ربع سنوي'), ('yearly', 'سنوي'), ('custom', 'مخصص')], default='monthly', max_length=20, verbose_name='نوع الفترة')),
                ('period_start', models.DateField(verbose_name='بداية الفترة')),
                ('period_end', models.DateField(verbose_name='نهاية الفترة')),
                ('year', models.PositiveIntegerField(verbose_name='السنة')),
                ('month', models.PositiveIntegerField(blank=True, null=True, verbose_name='الشهر')),
                ('week', models.PositiveIntegerField(blank=True, null=True, verbose_name='الأسبوع')),
                ('total_working_days', models.PositiveIntegerField(default=0, verbose_name='إجمالي أيام العمل')),
                ('present_days', models.PositiveIntegerField(default=0, verbose_name='أيام الحضور')),
                ('absent_days', models.PositiveIntegerField(default=0, verbose_name='أيام الغياب')),
                ('late_days', models.PositiveIntegerField(default=0, verbose_name='أيام التأخير')),
                ('early_departure_days', models.PositiveIntegerField(default=0, verbose_name='أيام الانصراف المبكر')),
                ('half_days', models.PositiveIntegerField(default=0, verbose_name='أنصاف الأيام')),
                ('overtime_days', models.PositiveIntegerField(default=0, verbose_name='أيام الوقت الإضافي')),
                ('total_hours_worked', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=8, verbose_name='إجمالي ساعات العمل')),
                ('total_regular_hours', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=8, verbose_name='إجمالي الساعات العادية')),
                ('total_overtime_hours', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=8, verbose_name='إجمالي ساعات الوقت الإضافي')),
                ('total_break_hours', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=8, verbose_name='إجمالي ساعات الاستراحة')),
                ('expected_hours', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=8, verbose_name='الساعات المتوقعة')),
                ('total_late_minutes', models.PositiveIntegerField(default=0, verbose_name='إجمالي دقائق التأخير')),
                ('total_early_departure_minutes', models.PositiveIntegerField(default=0, verbose_name='إجمالي دقائق الانصراف المبكر')),
                ('avg_late_minutes', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='متوسط دقائق التأخير')),
                ('vacation_days', models.PositiveIntegerField(default=0, verbose_name='أيام الإجازة')),
                ('sick_leave_days', models.PositiveIntegerField(default=0, verbose_name='أيام الإجازة المرضية')),
                ('business_trip_days', models.PositiveIntegerField(default=0, verbose_name='أيام المهام الرسمية')),
                ('training_days', models.PositiveIntegerField(default=0, verbose_name='أيام التدريب')),
                ('attendance_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='معدل الحضور (%)')),
                ('punctuality_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='معدل الالتزام بالمواعيد (%)')),
                ('productivity_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='نقاط الإنتاجية')),
                ('total_exceptions', models.PositiveIntegerField(default=0, verbose_name='إجمالي الاستثناءات')),
                ('unverified_records', models.PositiveIntegerField(default=0, verbose_name='السجلات غير المتحققة')),
                ('manual_entries', models.PositiveIntegerField(default=0, verbose_name='الإدخالات اليدوية')),
                ('most_common_check_in_time', models.TimeField(blank=True, null=True, verbose_name='أكثر أوقات الدخول شيوعاً')),
                ('most_common_check_out_time', models.TimeField(blank=True, null=True, verbose_name='أكثر أوقات الخروج شيوعاً')),
                ('avg_daily_hours', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='متوسط الساعات اليومية')),
                ('attendance_trend', models.CharField(choices=[('improving', 'تحسن'), ('declining', 'تراجع'), ('stable', 'مستقر'), ('no_data', 'لا توجد بيانات')], default='no_data', max_length=20, verbose_name='اتجاه الحضور')),
                ('trend_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='نسبة التغيير (%)')),
                ('weekend_work_days', models.PositiveIntegerField(default=0, verbose_name='أيام العمل في نهاية الأسبوع')),
                ('holiday_work_days', models.PositiveIntegerField(default=0, verbose_name='أيام العمل في العطل')),
                ('remote_work_days', models.PositiveIntegerField(default=0, verbose_name='أيام العمل عن بُعد')),
                ('is_processed', models.BooleanField(default=False, verbose_name='تم المعالجة')),
                ('processing_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ المعالجة')),
                ('needs_review', models.BooleanField(default=False, verbose_name='يحتاج مراجعة')),
                ('review_notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات المراجعة')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_attendance_summaries', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_summaries', to='Hr.employeeenhanced', verbose_name='الموظف')),
            ],
            options={
                'verbose_name': 'ملخص حضور محسن',
                'verbose_name_plural': 'ملخصات الحضور المحسنة',
                'db_table': 'hrms_attendance_summary_enhanced',
                'ordering': ['-period_start', 'employee'],
            },
        ),
        
        # Add unique constraints
        migrations.AddConstraint(
            model_name='attendancerecordenhanced',
            constraint=models.UniqueConstraint(fields=['employee', 'date'], name='unique_employee_date_attendance'),
        ),
        
        migrations.AddConstraint(
            model_name='employeeshiftassignmentenhanced',
            constraint=models.UniqueConstraint(fields=['employee', 'shift', 'start_date'], name='unique_employee_shift_start_date'),
        ),
        
        migrations.AddConstraint(
            model_name='attendancesummaryenhanced',
            constraint=models.UniqueConstraint(fields=['employee', 'period_type', 'period_start', 'period_end'], name='unique_employee_period_summary'),
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='attendancerecordenhanced',
            index=models.Index(fields=['employee', 'date'], name='hrms_attendance_record_enhanced_employee_date_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecordenhanced',
            index=models.Index(fields=['status'], name='hrms_attendance_record_enhanced_status_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecordenhanced',
            index=models.Index(fields=['is_verified'], name='hrms_attendance_record_enhanced_is_verified_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecordenhanced',
            index=models.Index(fields=['has_exception'], name='hrms_attendance_record_enhanced_has_exception_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecordenhanced',
            index=models.Index(fields=['assigned_shift'], name='hrms_attendance_record_enhanced_assigned_shift_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecordenhanced',
            index=models.Index(fields=['check_in_machine'], name='hrms_attendance_record_enhanced_check_in_machine_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecordenhanced',
            index=models.Index(fields=['check_out_machine'], name='hrms_attendance_record_enhanced_check_out_machine_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecordenhanced',
            index=models.Index(fields=['created_at'], name='hrms_attendance_record_enhanced_created_at_idx'),
        ),
        
        migrations.AddIndex(
            model_name='employeeshiftassignmentenhanced',
            index=models.Index(fields=['employee', 'is_active'], name='hrms_employee_shift_assignment_enhanced_employee_active_idx'),
        ),
        migrations.AddIndex(
            model_name='employeeshiftassignmentenhanced',
            index=models.Index(fields=['shift', 'is_active'], name='hrms_employee_shift_assignment_enhanced_shift_active_idx'),
        ),
        migrations.AddIndex(
            model_name='employeeshiftassignmentenhanced',
            index=models.Index(fields=['start_date', 'end_date'], name='hrms_employee_shift_assignment_enhanced_start_end_date_idx'),
        ),
        migrations.AddIndex(
            model_name='employeeshiftassignmentenhanced',
            index=models.Index(fields=['status'], name='hrms_employee_shift_assignment_enhanced_status_idx'),
        ),
        migrations.AddIndex(
            model_name='employeeshiftassignmentenhanced',
            index=models.Index(fields=['assignment_type'], name='hrms_employee_shift_assignment_enhanced_assignment_type_idx'),
        ),
        migrations.AddIndex(
            model_name='employeeshiftassignmentenhanced',
            index=models.Index(fields=['priority'], name='hrms_employee_shift_assignment_enhanced_priority_idx'),
        ),
        
        migrations.AddIndex(
            model_name='attendancesummaryenhanced',
            index=models.Index(fields=['employee', 'period_type'], name='hrms_attendance_summary_enhanced_employee_period_type_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancesummaryenhanced',
            index=models.Index(fields=['period_start', 'period_end'], name='hrms_attendance_summary_enhanced_period_start_end_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancesummaryenhanced',
            index=models.Index(fields=['year', 'month'], name='hrms_attendance_summary_enhanced_year_month_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancesummaryenhanced',
            index=models.Index(fields=['attendance_rate'], name='hrms_attendance_summary_enhanced_attendance_rate_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancesummaryenhanced',
            index=models.Index(fields=['is_processed'], name='hrms_attendance_summary_enhanced_is_processed_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancesummaryenhanced',
            index=models.Index(fields=['needs_review'], name='hrms_attendance_summary_enhanced_needs_review_idx'),
        ),
    ]