# Generated migration for Employee Extended Models

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import uuid
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0030_create_enhanced_attendance_models'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Create EmployeeFileCategory
        migrations.CreateModel(
            name='EmployeeFileCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
        
        # Create EmployeeEducationEnhanced
        migrations.CreateModel(
            name='EmployeeEducationEnhanced',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('degree_type', models.CharField(choices=[('elementary', 'ابتدائية'), ('intermediate', 'متوسطة'), ('high_school', 'ثانوية عامة'), ('vocational', 'مهني'), ('diploma', 'دبلوم'), ('associate', 'دبلوم عالي'), ('bachelor', 'بكالوريوس'), ('master', 'ماجستير'), ('phd', 'دكتوراه'), ('certificate', 'شهادة مهنية'), ('training', 'دورة تدريبية'), ('professional', 'شهادة احترافية')], max_length=20, verbose_name='نوع الشهادة')),
                ('major', models.CharField(max_length=200, verbose_name='التخصص الرئيسي')),
                ('minor', models.CharField(blank=True, max_length=200, null=True, verbose_name='التخصص الفرعي')),
                ('institution', models.CharField(max_length=200, verbose_name='الجامعة/المؤسسة')),
                ('institution_english', models.CharField(blank=True, max_length=200, null=True, verbose_name='اسم المؤسسة بالإنجليزية')),
                ('graduation_year', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1950), django.core.validators.MaxValueValidator(2035)], verbose_name='سنة التخرج')),
                ('start_year', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1950), django.core.validators.MaxValueValidator(2035)], verbose_name='سنة البداية')),
                ('study_duration_years', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(15)], verbose_name='مدة الدراسة بالسنوات')),
                ('study_mode', models.CharField(choices=[('full_time', 'دوام كامل'), ('part_time', 'دوام جزئي'), ('distance', 'تعليم عن بُعد'), ('evening', 'مسائي'), ('weekend', 'نهاية الأسبوع')], default='full_time', max_length=20, verbose_name='نظام الدراسة')),
                ('grade_system', models.CharField(choices=[('percentage', 'نسبة مئوية'), ('gpa_4', 'GPA من 4'), ('gpa_5', 'GPA من 5'), ('letter', 'حروف (A, B, C)'), ('pass_fail', 'نجح/راسب'), ('honors', 'مرتبة الشرف')], default='percentage', max_length=20, verbose_name='نظام الدرجات')),
                ('grade', models.CharField(blank=True, max_length=10, null=True, verbose_name='المعدل/الدرجة')),
                ('country', models.CharField(max_length=100, verbose_name='الدولة')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='المدينة')),
                ('is_verified', models.BooleanField(default=False, verbose_name='تم التحقق')),
                ('verification_date', models.DateField(blank=True, null=True, verbose_name='تاريخ التحقق')),
                ('verification_notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات التحقق')),
                ('certificate_file', models.FileField(blank=True, null=True, upload_to='education/certificates/', verbose_name='ملف الشهادة')),
                ('transcript_file', models.FileField(blank=True, null=True, upload_to='education/transcripts/', verbose_name='كشف الدرجات')),
                ('honors', models.CharField(blank=True, max_length=200, null=True, verbose_name='مرتبة الشرف')),
                ('thesis_title', models.CharField(blank=True, max_length=500, null=True, verbose_name='عنوان الرسالة/المشروع')),
                ('thesis_title_en', models.CharField(blank=True, max_length=500, null=True, verbose_name='عنوان الرسالة بالإنجليزية')),
                ('supervisor_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='اسم المشرف')),
                ('class_rank', models.PositiveIntegerField(blank=True, null=True, verbose_name='الترتيب على الدفعة')),
                ('class_size', models.PositiveIntegerField(blank=True, null=True, verbose_name='عدد طلاب الدفعة')),
                ('awards', models.TextField(blank=True, null=True, verbose_name='الجوائز والتكريمات')),
                ('is_relevant_to_job', models.BooleanField(default=True, verbose_name='مرتبط بالوظيفة')),
                ('relevance_notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات الصلة بالوظيفة')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education_records_enhanced', to='Hr.EmployeeEnhanced', verbose_name='الموظف')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_education_records', to='accounts.Users_Login_New', verbose_name='تم التحقق بواسطة')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='created_education_records', to='accounts.Users_Login_New', verbose_name='تم الإنشاء بواسطة')),
            ],
            options={
                'verbose_name': 'مؤهل دراسي محسن',
                'verbose_name_plural': 'المؤهلات الدراسية المحسنة',
                'ordering': ['-graduation_year', 'degree_type'],
            },
        ),
        
        # Create EmployeeInsuranceEnhanced
        migrations.CreateModel(
            name='EmployeeInsuranceEnhanced',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('insurance_type', models.CharField(choices=[('social', 'تأمين اجتماعي'), ('medical', 'تأمين صحي'), ('life', 'تأمين على الحياة'), ('disability', 'تأمين ضد العجز'), ('unemployment', 'تأمين ضد البطالة'), ('professional', 'تأمين مهني'), ('travel', 'تأمين سفر'), ('dental', 'تأمين أسنان'), ('vision', 'تأمين نظر'), ('maternity', 'تأمين أمومة')], max_length=20, verbose_name='نوع التأمين')),
                ('policy_number', models.CharField(max_length=100, unique=True, verbose_name='رقم البوليصة')),
                ('provider', models.CharField(max_length=200, verbose_name='مقدم التأمين')),
                ('provider_contact', models.CharField(blank=True, max_length=200, null=True, verbose_name='جهة الاتصال')),
                ('provider_phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='هاتف مقدم التأمين')),
                ('provider_email', models.EmailField(blank=True, null=True, verbose_name='بريد مقدم التأمين')),
                ('coverage_type', models.CharField(choices=[('individual', 'فردي'), ('family', 'عائلي'), ('spouse', 'الزوج/الزوجة'), ('children', 'الأطفال'), ('parents', 'الوالدين')], default='individual', max_length=20, verbose_name='نوع التغطية')),
                ('coverage_description', models.TextField(blank=True, null=True, verbose_name='وصف التغطية')),
                ('start_date', models.DateField(verbose_name='تاريخ البداية')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='تاريخ النهاية')),
                ('renewal_date', models.DateField(blank=True, null=True, verbose_name='تاريخ التجديد')),
                ('last_renewal_date', models.DateField(blank=True, null=True, verbose_name='تاريخ آخر تجديد')),
                ('premium_amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='قسط التأمين')),
                ('coverage_amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='مبلغ التغطية')),
                ('employee_contribution', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='مساهمة الموظف')),
                ('employer_contribution', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='مساهمة صاحب العمل')),
                ('deductible', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='المبلغ المقتطع')),
                ('payment_frequency', models.CharField(choices=[('monthly', 'شهري'), ('quarterly', 'ربع سنوي'), ('semi_annual', 'نصف سنوي'), ('annual', 'سنوي')], default='monthly', max_length=20, verbose_name='تكرار الدفع')),
                ('currency', models.CharField(default='SAR', max_length=10, verbose_name='العملة')),
                ('status', models.CharField(choices=[('active', 'نشط'), ('inactive', 'غير نشط'), ('suspended', 'موقوف'), ('expired', 'منتهي'), ('cancelled', 'ملغى'), ('pending', 'في الانتظار')], default='active', max_length=20, verbose_name='الحالة')),
                ('beneficiaries', models.TextField(blank=True, null=True, verbose_name='المستفيدون')),
                ('spouse_covered', models.BooleanField(default=False, verbose_name='يشمل الزوج/الزوجة')),
                ('children_covered', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(20)], verbose_name='عدد الأطفال المشمولين')),
                ('parents_covered', models.BooleanField(default=False, verbose_name='يشمل الوالدين')),
                ('total_claims_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='إجمالي المطالبات')),
                ('claims_count', models.PositiveIntegerField(default=0, verbose_name='عدد المطالبات')),
                ('last_claim_date', models.DateField(blank=True, null=True, verbose_name='تاريخ آخر مطالبة')),
                ('policy_document', models.FileField(blank=True, null=True, upload_to='insurance/policies/', verbose_name='وثيقة التأمين')),
                ('terms_document', models.FileField(blank=True, null=True, upload_to='insurance/terms/', verbose_name='شروط وأحكام التأمين')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('special_conditions', models.TextField(blank=True, null=True, verbose_name='شروط خاصة')),
                ('approval_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الاعتماد')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='insurance_records_enhanced', to='Hr.EmployeeEnhanced', verbose_name='الموظف')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_insurance_records', to='accounts.Users_Login_New', verbose_name='تم الاعتماد بواسطة')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='created_insurance_records', to='accounts.Users_Login_New', verbose_name='تم الإنشاء بواسطة')),
            ],
            options={
                'verbose_name': 'تأمين موظف محسن',
                'verbose_name_plural': 'تأمينات الموظفين المحسنة',
                'ordering': ['employee', 'insurance_type', '-start_date'],
            },
        ),
        
        # Create EmployeeVehicleEnhanced
        migrations.CreateModel(
            name='EmployeeVehicleEnhanced',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('vehicle_type', models.CharField(choices=[('company', 'سيارة الشركة'), ('personal', 'سيارة شخصية'), ('allowance', 'بدل سيارة'), ('rental', 'سيارة مستأجرة'), ('lease', 'سيارة مؤجرة'), ('pool', 'سيارة مشتركة')], max_length=20, verbose_name='نوع السيارة')),
                ('make', models.CharField(max_length=100, verbose_name='الماركة')),
                ('model', models.CharField(max_length=100, verbose_name='الموديل')),
                ('year', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1950), django.core.validators.MaxValueValidator(2027)], verbose_name='سنة الصنع')),
                ('license_plate', models.CharField(max_length=20, unique=True, verbose_name='رقم اللوحة')),
                ('vin_number', models.CharField(blank=True, help_text='رقم تعريف السيارة (VIN)', max_length=17, null=True, verbose_name='رقم الشاسيه')),
                ('color', models.CharField(blank=True, max_length=50, null=True, verbose_name='اللون')),
                ('fuel_type', models.CharField(choices=[('gasoline', 'بنزين'), ('diesel', 'ديزل'), ('hybrid', 'هجين'), ('electric', 'كهربائي'), ('lpg', 'غاز'), ('cng', 'غاز طبيعي')], max_length=20, verbose_name='نوع الوقود')),
                ('engine_size', models.CharField(blank=True, max_length=20, null=True, verbose_name='حجم المحرك')),
                ('transmission', models.CharField(blank=True, choices=[('manual', 'يدوي'), ('automatic', 'أوتوماتيك'), ('cvt', 'CVT'), ('semi_automatic', 'نصف أوتوماتيك')], max_length=20, null=True, verbose_name='نوع ناقل الحركة')),
                ('doors_count', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(6)], verbose_name='عدد الأبواب')),
                ('seats_count', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(50)], verbose_name='عدد المقاعد')),
                ('assigned_date', models.DateField(verbose_name='تاريخ التخصيص')),
                ('return_date', models.DateField(blank=True, null=True, verbose_name='تاريخ الإرجاع')),
                ('assignment_reason', models.TextField(blank=True, null=True, verbose_name='سبب التخصيص')),
                ('monthly_allowance', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='البدل الشهري')),
                ('purchase_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='سعر الشراء')),
                ('current_value', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='القيمة الحالية')),
                ('depreciation_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('100'))], verbose_name='معدل الاستهلاك السنوي (%)')),
                ('insurance_company', models.CharField(blank=True, max_length=200, null=True, verbose_name='شركة التأمين')),
                ('insurance_policy_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='رقم بوليصة التأمين')),
                ('insurance_expiry', models.DateField(verbose_name='تاريخ انتهاء التأمين')),
                ('insurance_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='مبلغ التأمين')),
                ('registration_expiry', models.DateField(verbose_name='تاريخ انتهاء الاستمارة')),
                ('license_expiry', models.DateField(blank=True, null=True, verbose_name='تاريخ انتهاء الرخصة')),
                ('last_maintenance_date', models.DateField(blank=True, null=True, verbose_name='تاريخ آخر صيانة')),
                ('next_maintenance_date', models.DateField(blank=True, null=True, verbose_name='تاريخ الصيانة القادمة')),
                ('maintenance_interval_km', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1000), django.core.validators.MaxValueValidator(50000)], verbose_name='فترة الصيانة (كم)')),
                ('mileage', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(2000000)], verbose_name='عدد الكيلومترات')),
                ('last_mileage_update', models.DateField(blank=True, null=True, verbose_name='تاريخ آخر تحديث للكيلومترات')),
                ('fuel_consumption_per_100km', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(Decimal('1')), django.core.validators.MaxValueValidator(Decimal('50'))], verbose_name='استهلاك الوقود لكل 100 كم')),
                ('condition', models.CharField(blank=True, choices=[('excellent', 'ممتازة'), ('very_good', 'جيدة جداً'), ('good', 'جيدة'), ('fair', 'مقبولة'), ('poor', 'سيئة')], max_length=20, null=True, verbose_name='حالة السيارة')),
                ('status', models.CharField(choices=[('assigned', 'مخصصة'), ('available', 'متاحة'), ('maintenance', 'في الصيانة'), ('retired', 'خارج الخدمة'), ('sold', 'مباعة'), ('accident', 'في حادث'), ('repair', 'في الإصلاح')], default='assigned', max_length=20, verbose_name='الحالة')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('has_gps', models.BooleanField(default=False, verbose_name='يحتوي على GPS')),
                ('gps_device_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='معرف جهاز GPS')),
                ('features', models.TextField(blank=True, help_text='مكيف، راديو، نظام ملاحة، إلخ', null=True, verbose_name='المميزات الإضافية')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('registration_document', models.FileField(blank=True, null=True, upload_to='vehicles/registration/', verbose_name='وثيقة التسجيل')),
                ('insurance_document', models.FileField(blank=True, null=True, upload_to='vehicles/insurance/', verbose_name='وثيقة التأمين')),
                ('vehicle_photos', models.FileField(blank=True, null=True, upload_to='vehicles/photos/', verbose_name='صور السيارة')),
                ('approval_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الاعتماد')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicle_records_enhanced', to='Hr.EmployeeEnhanced', verbose_name='الموظف')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_vehicle_records', to='accounts.Users_Login_New', verbose_name='تم الاعتماد بواسطة')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='created_vehicle_records', to='accounts.Users_Login_New', verbose_name='تم الإنشاء بواسطة')),
            ],
            options={
                'verbose_name': 'سيارة موظف محسنة',
                'verbose_name_plural': 'سيارات الموظفين المحسنة',
                'ordering': ['employee', '-assigned_date'],
            },
        ),
        
        # Create EmployeeFileEnhanced
        migrations.CreateModel(
            name='EmployeeFileEnhanced',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='عنوان الملف')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف الملف')),
                ('file', models.FileField(upload_to='employee_files/', verbose_name='الملف')),
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
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='Hr.EmployeeEnhanced', verbose_name='الموظف')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='Hr.EmployeeFileCategory', verbose_name='الفئة')),
                ('parent_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='Hr.EmployeeFileEnhanced', verbose_name='الملف الأصلي')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_files', to='accounts.Users_Login_New', verbose_name='معتمد بواسطة')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_files', to='accounts.Users_Login_New', verbose_name='رفع بواسطة')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('view', 'عرض'), ('download', 'تحميل'), ('edit', 'تعديل'), ('delete', 'حذف'), ('approve', 'اعتماد'), ('reject', 'رفض')], max_length=20, verbose_name='الإجراء')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='عنوان IP')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='معلومات المتصفح')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='وقت الإجراء')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_logs', to='Hr.EmployeeFileEnhanced', verbose_name='الملف')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Users_Login_New', verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'سجل وصول الملف',
                'verbose_name_plural': 'سجلات وصول الملفات',
                'db_table': 'hrms_employee_file_access_log',
                'ordering': ['-timestamp'],
            },
        ),
        
        # Create EmployeeEmergencyContactEnhanced
        migrations.CreateModel(
            name='EmployeeEmergencyContactEnhanced',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200, verbose_name='الاسم الكامل')),
                ('relationship', models.CharField(choices=[('spouse', 'زوج/زوجة'), ('father', 'والد'), ('mother', 'والدة'), ('son', 'ابن'), ('daughter', 'ابنة'), ('brother', 'أخ'), ('sister', 'أخت'), ('grandfather', 'جد'), ('grandmother', 'جدة'), ('uncle', 'عم/خال'), ('aunt', 'عمة/خالة'), ('cousin', 'ابن عم/خال'), ('friend', 'صديق'), ('colleague', 'زميل عمل'), ('neighbor', 'جار'), ('guardian', 'ولي أمر'), ('other', 'أخرى')], max_length=20, verbose_name='صلة القرابة')),
                ('relationship_other', models.CharField(blank=True, help_text="حدد صلة القرابة إذا اخترت 'أخرى'", max_length=100, null=True, verbose_name='صلة القرابة (أخرى)')),
                ('primary_phone', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='رقم الهاتف غير صحيح', regex='^\\+?[\\d\\s\\-\\(\\)]+$')], verbose_name='رقم الهاتف الأساسي')),
                ('secondary_phone', models.CharField(blank=True, max_length=20, null=True, validators=[django.core.validators.RegexValidator(message='رقم الهاتف غير صحيح', regex='^\\+?[\\d\\s\\-\\(\\)]+$')], verbose_name='رقم الهاتف الثانوي')),
                ('email', models.EmailField(blank=True, null=True, verbose_name='البريد الإلكتروني')),
                ('address', models.TextField(blank=True, null=True, verbose_name='العنوان')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='المدينة')),
                ('country', models.CharField(default='مصر', max_length=100, verbose_name='الدولة')),
                ('occupation', models.CharField(blank=True, max_length=100, null=True, verbose_name='المهنة')),
                ('workplace', models.CharField(blank=True, max_length=200, null=True, verbose_name='مكان العمل')),
                ('priority', models.PositiveIntegerField(choices=[(1, 'الأولوية الأولى'), (2, 'الأولوية الثانية'), (3, 'الأولوية الثالثة'), (4, 'الأولوية الرابعة'), (5, 'الأولوية الخامسة')], default=1, help_text='أولوية الاتصال في حالات الطوارئ', verbose_name='الأولوية')),
                ('is_primary', models.BooleanField(default=False, help_text='هل هذه جهة الاتصال الأساسية؟', verbose_name='جهة الاتصال الأساسية')),
                ('best_time_to_call', models.CharField(blank=True, max_length=100, null=True, verbose_name='أفضل وقت للاتصال')),
                ('availability_notes', models.TextField(blank=True, help_text='معلومات إضافية حول أوقات التوفر', null=True, verbose_name='ملاحظات التوفر')),
                ('can_make_medical_decisions', models.BooleanField(default=False, help_text='هل يمكن لهذا الشخص اتخاذ قرارات طبية نيابة عن الموظف؟', verbose_name='يمكنه اتخاذ قرارات طبية')),
                ('can_receive_salary', models.BooleanField(default=False, help_text='هل يمكن لهذا الشخص استلام راتب الموظف في حالات الطوارئ؟', verbose_name='يمكنه استلام الراتب')),
                ('has_power_of_attorney', models.BooleanField(default=False, help_text='هل لدى هذا الشخص توكيل قانوني من الموظف؟', verbose_name='لديه توكيل قانوني')),
                ('preferred_language', models.CharField(choices=[('ar', 'العربية'), ('en', 'الإنجليزية'), ('fr', 'الفرنسية'), ('other', 'أخرى')], default='ar', max_length=50, verbose_name='اللغة المفضلة')),
                ('is_verified', models.BooleanField(default=False, help_text='هل تم التحقق من صحة معلومات الاتصال؟', verbose_name='تم التحقق')),
                ('verified_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ التحقق')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات إضافية')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emergency_contacts', to='Hr.EmployeeEnhanced', verbose_name='الموظف')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_emergency_contacts', to='accounts.Users_Login_New', verbose_name='أنشئ بواسطة')),
            ],
            options={
                'verbose_name': 'جهة اتصال طوارئ',
                'verbose_name_plural': 'جهات اتصال الطوارئ',
                'db_table': 'hrms_employee_emergency_contact',
                'ordering': ['employee', 'priority'],
            },
        ),
        
        # Add indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_employee_education_employee ON hrms_employee_education_enhanced(employee_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_employee_education_employee;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_employee_education_degree ON hrms_employee_education_enhanced(degree_type);",
            reverse_sql="DROP INDEX IF EXISTS idx_employee_education_degree;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_employee_education_graduation ON hrms_employee_education_enhanced(graduation_year);",
            reverse_sql="DROP INDEX IF EXISTS idx_employee_education_graduation;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_employee_insurance_employee ON hrms_employee_insurance_enhanced(employee_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_employee_insurance_employee;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_employee_insurance_type ON hrms_employee_insurance_enhanced(insurance_type);",
            reverse_sql="DROP INDEX IF EXISTS idx_employee_insurance_type;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_employee_vehicle_employee ON hrms_employee_vehicle_enhanced(employee_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_employee_vehicle_employee;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_employee_vehicle_plate ON hrms_employee_vehicle_enhanced(license_plate);",
            reverse_sql="DROP INDEX IF EXISTS idx_employee_vehicle_plate;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_employee_file_employee ON hrms_employee_file_enhanced(employee_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_employee_file_employee;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_employee_file_status ON hrms_employee_file_enhanced(status);",
            reverse_sql="DROP INDEX IF EXISTS idx_employee_file_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_employee_emergency_employee ON hrms_employee_emergency_contact(employee_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_employee_emergency_employee;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_employee_emergency_priority ON hrms_employee_emergency_contact(priority);",
            reverse_sql="DROP INDEX IF EXISTS idx_employee_emergency_priority;"
        ),
        
        # Add constraints
        migrations.RunSQL(
            "ALTER TABLE hrms_employee_education_enhanced ADD CONSTRAINT chk_start_before_graduation CHECK (start_year <= graduation_year);",
            reverse_sql="ALTER TABLE hrms_employee_education_enhanced DROP CONSTRAINT IF EXISTS chk_start_before_graduation;"
        ),
        migrations.RunSQL(
            "ALTER TABLE hrms_employee_education_enhanced ADD CONSTRAINT chk_rank_within_class CHECK (class_rank <= class_size);",
            reverse_sql="ALTER TABLE hrms_employee_education_enhanced DROP CONSTRAINT IF EXISTS chk_rank_within_class;"
        ),
        migrations.RunSQL(
            "ALTER TABLE hrms_employee_insurance_enhanced ADD CONSTRAINT chk_end_after_start_insurance CHECK (end_date >= start_date);",
            reverse_sql="ALTER TABLE hrms_employee_insurance_enhanced DROP CONSTRAINT IF EXISTS chk_end_after_start_insurance;"
        ),
        migrations.RunSQL(
            "ALTER TABLE hrms_employee_vehicle_enhanced ADD CONSTRAINT chk_return_after_assignment CHECK (return_date >= assigned_date);",
            reverse_sql="ALTER TABLE hrms_employee_vehicle_enhanced DROP CONSTRAINT IF EXISTS chk_return_after_assignment;"
        ),
        migrations.RunSQL(
            "ALTER TABLE hrms_employee_emergency_contact ADD CONSTRAINT unique_employee_priority UNIQUE (employee_id, priority);",
            reverse_sql="ALTER TABLE hrms_employee_emergency_contact DROP CONSTRAINT IF EXISTS unique_employee_priority;"
        ),
    ]