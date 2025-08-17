# Generated migration for enhanced employee extended models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Hr', '0028_create_enhanced_employee_models'),
    ]

    operations = [
        # Create EmployeeFileCategory
        migrations.CreateModel(
            name='EmployeeFileCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='اسم الفئة')),
                ('name_en', models.CharField(blank=True, max_length=100, null=True, verbose_name='الاسم بالإنجليزية')),
                ('description', models.TextField(blank=True, null=True, verbose_name='الوصف')),
                ('icon', models.CharField(default='📁', max_length=50, verbose_name='الأيقونة')),
                ('color', models.CharField(default='#007bff', help_text='كود اللون بصيغة hex', max_length=7, verbose_name='اللون')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='ترتيب العرض')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
            ],
            options={
                'verbose_name': 'فئة الملفات',
                'verbose_name_plural': 'فئات الملفات',
                'db_table': 'hrms_employee_file_category',
                'ordering': ['sort_order', 'name'],
            },
        ),
        
        # Create EmployeeFileEnhanced
        migrations.CreateModel(
            name='EmployeeFileEnhanced',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200, verbose_name='عنوان الملف')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف الملف')),
                ('file', models.FileField(upload_to='employee_files/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'rtf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'xls', 'xlsx', 'csv', 'ppt', 'pptx', 'zip', 'rar', '7z'])], verbose_name='الملف')),
                ('original_filename', models.CharField(max_length=255, verbose_name='اسم الملف الأصلي')),
                ('file_size', models.PositiveIntegerField(verbose_name='حجم الملف (بايت)')),
                ('mime_type', models.CharField(max_length=100, verbose_name='نوع الملف')),
                ('file_hash', models.CharField(help_text='SHA-256 hash للتحقق من سلامة الملف', max_length=64, unique=True, verbose_name='هاش الملف')),
                ('tags', models.JSONField(default=list, help_text='علامات للبحث والتصنيف', verbose_name='العلامات')),
                ('access_level', models.CharField(choices=[('public', 'عام - يمكن للجميع الوصول'), ('internal', 'داخلي - الموظفون والإدارة'), ('confidential', 'سري - الإدارة العليا فقط'), ('restricted', 'مقيد - أشخاص محددون فقط'), ('personal', 'شخصي - الموظف فقط')], default='internal', max_length=20, verbose_name='مستوى الوصول')),
                ('is_confidential', models.BooleanField(default=False, verbose_name='ملف سري')),
                ('version', models.CharField(default='1.0', max_length=20, verbose_name='الإصدار')),
                ('status', models.CharField(choices=[('draft', 'مسودة'), ('pending_review', 'في انتظار المراجعة'), ('approved', 'معتمد'), ('rejected', 'مرفوض'), ('archived', 'مؤرشف'), ('deleted', 'محذوف')], default='pending_review', max_length=20, verbose_name='الحالة')),
                ('expiry_date', models.DateField(blank=True, null=True, verbose_name='تاريخ انتهاء الصلاحية')),
                ('renewal_required', models.BooleanField(default=False, verbose_name='يتطلب تجديد')),
                ('reminder_days', models.PositiveIntegerField(default=30, verbose_name='تذكير قبل (أيام)')),
                ('is_encrypted', models.BooleanField(default=False, verbose_name='مشفر')),
                ('encryption_key_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='معرف مفتاح التشفير')),
                ('download_count', models.PositiveIntegerField(default=0, verbose_name='عدد مرات التحميل')),
                ('last_accessed', models.DateTimeField(blank=True, null=True, verbose_name='آخر وصول')),
                ('approved_at', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الاعتماد')),
                ('rejection_reason', models.TextField(blank=True, null=True, verbose_name='سبب الرفض')),
                ('keywords', models.TextField(blank=True, help_text='كلمات مفتاحية للبحث', null=True, verbose_name='كلمات مفتاحية')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_files', to=settings.AUTH_USER_MODEL, verbose_name='معتمد بواسطة')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='Hr.employeefilecategory', verbose_name='الفئة')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='Hr.employeeenhanced', verbose_name='الموظف')),
                ('parent_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='Hr.employeefileenhanced', verbose_name='الملف الأصلي')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_files', to=settings.AUTH_USER_MODEL, verbose_name='رفع بواسطة')),
            ],
            options={
                'verbose_name': 'ملف موظف',
                'verbose_name_plural': 'ملفات الموظفين',
                'db_table': 'hrms_employee_file_enhanced',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create EmployeeFileAccessLog
        migrations.CreateModel(
            name='EmployeeFileAccessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('view', 'عرض'), ('download', 'تحميل'), ('edit', 'تعديل'), ('delete', 'حذف'), ('approve', 'اعتماد'), ('reject', 'رفض')], max_length=20, verbose_name='الإجراء')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='عنوان IP')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='معلومات المتصفح')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='وقت الإجراء')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_logs', to='Hr.employeefileenhanced', verbose_name='الملف')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'سجل وصول الملف',
                'verbose_name_plural': 'سجلات وصول الملفات',
                'db_table': 'hrms_employee_file_access_log',
                'ordering': ['-timestamp'],
            },
        ),
        
        # Create TrainingCategory
        migrations.CreateModel(
            name='TrainingCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='اسم الفئة')),
                ('name_en', models.CharField(blank=True, max_length=100, null=True, verbose_name='الاسم بالإنجليزية')),
                ('description', models.TextField(blank=True, null=True, verbose_name='الوصف')),
                ('icon', models.CharField(default='🎓', max_length=50, verbose_name='الأيقونة')),
                ('color', models.CharField(default='#28a745', max_length=7, verbose_name='اللون')),
                ('is_mandatory', models.BooleanField(default=False, help_text='هل هذا النوع من التدريب إجباري؟', verbose_name='إجباري')),
                ('renewal_period_months', models.PositiveIntegerField(blank=True, help_text='كم شهر قبل انتهاء صلاحية الشهادة؟', null=True, verbose_name='فترة التجديد (شهور)')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='ترتيب العرض')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
            ],
            options={
                'verbose_name': 'فئة التدريب',
                'verbose_name_plural': 'فئات التدريب',
                'db_table': 'hrms_training_category',
                'ordering': ['sort_order', 'name'],
            },
        ),
        
        # Create TrainingProvider
        migrations.CreateModel(
            name='TrainingProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='اسم مقدم التدريب')),
                ('name_en', models.CharField(blank=True, max_length=200, null=True, verbose_name='الاسم بالإنجليزية')),
                ('provider_type', models.CharField(choices=[('internal', 'داخلي'), ('external', 'خارجي'), ('university', 'جامعة'), ('institute', 'معهد'), ('online', 'منصة إلكترونية'), ('consultant', 'استشاري'), ('government', 'حكومي')], max_length=20, verbose_name='نوع مقدم التدريب')),
                ('description', models.TextField(blank=True, null=True, verbose_name='الوصف')),
                ('contact_person', models.CharField(blank=True, max_length=100, null=True, verbose_name='الشخص المسؤول')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='رقم الهاتف')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='البريد الإلكتروني')),
                ('website', models.URLField(blank=True, null=True, verbose_name='الموقع الإلكتروني')),
                ('address', models.TextField(blank=True, null=True, verbose_name='العنوان')),
                ('accreditation_body', models.CharField(blank=True, max_length=200, null=True, verbose_name='جهة الاعتماد')),
                ('accreditation_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='رقم الاعتماد')),
                ('rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='التقييم (من 5)')),
                ('is_preferred', models.BooleanField(default=False, verbose_name='مقدم مفضل')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
            ],
            options={
                'verbose_name': 'مقدم التدريب',
                'verbose_name_plural': 'مقدمو التدريب',
                'db_table': 'hrms_training_provider',
                'ordering': ['-is_preferred', 'name'],
            },
        ),
        
        # Create EmployeeTrainingEnhanced
        migrations.CreateModel(
            name='EmployeeTrainingEnhanced',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200, verbose_name='عنوان التدريب')),
                ('title_en', models.CharField(blank=True, max_length=200, null=True, verbose_name='العنوان بالإنجليزية')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف التدريب')),
                ('training_type', models.CharField(choices=[('course', 'دورة تدريبية'), ('workshop', 'ورشة عمل'), ('seminar', 'ندوة'), ('conference', 'مؤتمر'), ('certification', 'شهادة مهنية'), ('degree', 'درجة علمية'), ('online', 'تدريب إلكتروني'), ('on_job', 'تدريب على رأس العمل'), ('mentoring', 'إرشاد مهني')], max_length=20, verbose_name='نوع التدريب')),
                ('delivery_method', models.CharField(choices=[('in_person', 'حضوري'), ('online', 'إلكتروني'), ('hybrid', 'مختلط'), ('self_paced', 'ذاتي السرعة')], default='in_person', max_length=20, verbose_name='طريقة التقديم')),
                ('start_date', models.DateField(verbose_name='تاريخ البداية')),
                ('end_date', models.DateField(verbose_name='تاريخ النهاية')),
                ('duration_hours', models.PositiveIntegerField(verbose_name='مدة التدريب (ساعات)')),
                ('location', models.CharField(blank=True, max_length=200, null=True, verbose_name='مكان التدريب')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='المدينة')),
                ('country', models.CharField(default='مصر', max_length=100, verbose_name='الدولة')),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='التكلفة')),
                ('currency', models.CharField(default='EGP', max_length=3, verbose_name='العملة')),
                ('budget_code', models.CharField(blank=True, max_length=50, null=True, verbose_name='رمز الميزانية')),
                ('status', models.CharField(choices=[('planned', 'مخطط'), ('approved', 'معتمد'), ('registered', 'مسجل'), ('in_progress', 'قيد التنفيذ'), ('completed', 'مكتمل'), ('cancelled', 'ملغي'), ('postponed', 'مؤجل'), ('failed', 'فاشل')], default='planned', max_length=20, verbose_name='الحالة')),
                ('progress_percentage', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='نسبة الإنجاز (%)')),
                ('has_assessment', models.BooleanField(default=False, verbose_name='يتضمن تقييم')),
                ('assessment_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='درجة التقييم')),
                ('max_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='الدرجة العظمى')),
                ('pass_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='درجة النجاح')),
                ('is_passed', models.BooleanField(default=False, verbose_name='نجح في التقييم')),
                ('has_certificate', models.BooleanField(default=False, verbose_name='يحصل على شهادة')),
                ('certificate_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='رقم الشهادة')),
                ('certificate_date', models.DateField(blank=True, null=True, verbose_name='تاريخ الشهادة')),
                ('certificate_expiry_date', models.DateField(blank=True, null=True, verbose_name='تاريخ انتهاء الشهادة')),
                ('certificate_file', models.FileField(blank=True, null=True, upload_to='training_certificates/', verbose_name='ملف الشهادة')),
                ('approved_at', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الاعتماد')),
                ('rejection_reason', models.TextField(blank=True, null=True, verbose_name='سبب الرفض')),
                ('priority', models.CharField(choices=[('low', 'منخفضة'), ('medium', 'متوسطة'), ('high', 'عالية'), ('critical', 'حرجة')], default='medium', max_length=10, verbose_name='الأولوية')),
                ('is_mandatory', models.BooleanField(default=False, verbose_name='إجباري')),
                ('skills_gained', models.JSONField(default=list, help_text='قائمة بالمهارات التي تم اكتسابها', verbose_name='المهارات المكتسبة')),
                ('competencies_improved', models.JSONField(default=list, help_text='قائمة بالكفاءات التي تم تحسينها', verbose_name='الكفاءات المحسنة')),
                ('employee_feedback', models.TextField(blank=True, null=True, verbose_name='تقييم الموظف للتدريب')),
                ('employee_rating', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='تقييم الموظف (من 5)')),
                ('trainer_feedback', models.TextField(blank=True, null=True, verbose_name='تقييم المدرب للموظف')),
                ('trainer_rating', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='تقييم المدرب (من 5)')),
                ('follow_up_required', models.BooleanField(default=False, verbose_name='يتطلب متابعة')),
                ('follow_up_date', models.DateField(blank=True, null=True, verbose_name='تاريخ المتابعة')),
                ('application_plan', models.TextField(blank=True, null=True, verbose_name='خطة تطبيق المعرفة المكتسبة')),
                ('prerequisites', models.TextField(blank=True, null=True, verbose_name='المتطلبات المسبقة')),
                ('learning_objectives', models.TextField(blank=True, null=True, verbose_name='أهداف التعلم')),
                ('materials_provided', models.TextField(blank=True, null=True, verbose_name='المواد المقدمة')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_trainings', to=settings.AUTH_USER_MODEL, verbose_name='معتمد بواسطة')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trainings', to='Hr.trainingcategory', verbose_name='فئة التدريب')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_trainings', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trainings', to='Hr.employeeenhanced', verbose_name='الموظف')),
                ('provider', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trainings', to='Hr.trainingprovider', verbose_name='مقدم التدريب')),
                ('requested_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requested_trainings', to=settings.AUTH_USER_MODEL, verbose_name='طلب بواسطة')),
            ],
            options={
                'verbose_name': 'تدريب موظف',
                'verbose_name_plural': 'تدريبات الموظفين',
                'db_table': 'hrms_employee_training_enhanced',
                'ordering': ['-start_date'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='employeefileenhanced',
            index=models.Index(fields=['employee', 'category'], name='hrms_employee_file_enhanced_employee_category_idx'),
        ),
        migrations.AddIndex(
            model_name='employeefileenhanced',
            index=models.Index(fields=['status'], name='hrms_employee_file_enhanced_status_idx'),
        ),
        migrations.AddIndex(
            model_name='employeefileenhanced',
            index=models.Index(fields=['access_level'], name='hrms_employee_file_enhanced_access_level_idx'),
        ),
        migrations.AddIndex(
            model_name='employeefileenhanced',
            index=models.Index(fields=['expiry_date'], name='hrms_employee_file_enhanced_expiry_date_idx'),
        ),
        migrations.AddIndex(
            model_name='employeefileenhanced',
            index=models.Index(fields=['file_hash'], name='hrms_employee_file_enhanced_file_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='employeefileenhanced',
            index=models.Index(fields=['created_at'], name='hrms_employee_file_enhanced_created_at_idx'),
        ),
        
        migrations.AddIndex(
            model_name='employeefileaccesslog',
            index=models.Index(fields=['file', 'timestamp'], name='hrms_employee_file_access_log_file_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='employeefileaccesslog',
            index=models.Index(fields=['user', 'timestamp'], name='hrms_employee_file_access_log_user_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='employeefileaccesslog',
            index=models.Index(fields=['action'], name='hrms_employee_file_access_log_action_idx'),
        ),
        
        migrations.AddIndex(
            model_name='employeetrainingenhanced',
            index=models.Index(fields=['employee', 'status'], name='hrms_employee_training_enhanced_employee_status_idx'),
        ),
        migrations.AddIndex(
            model_name='employeetrainingenhanced',
            index=models.Index(fields=['start_date', 'end_date'], name='hrms_employee_training_enhanced_start_end_date_idx'),
        ),
        migrations.AddIndex(
            model_name='employeetrainingenhanced',
            index=models.Index(fields=['category'], name='hrms_employee_training_enhanced_category_idx'),
        ),
        migrations.AddIndex(
            model_name='employeetrainingenhanced',
            index=models.Index(fields=['provider'], name='hrms_employee_training_enhanced_provider_idx'),
        ),
        migrations.AddIndex(
            model_name='employeetrainingenhanced',
            index=models.Index(fields=['priority'], name='hrms_employee_training_enhanced_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='employeetrainingenhanced',
            index=models.Index(fields=['certificate_expiry_date'], name='hrms_employee_training_enhanced_cert_expiry_idx'),
        ),
    ]