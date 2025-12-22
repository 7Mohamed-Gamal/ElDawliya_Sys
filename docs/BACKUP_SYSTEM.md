# نظام النسخ الاحتياطي والاستعادة - نظام الدولية
# ElDawliya System Backup and Recovery Documentation

## نظرة عامة

نظام النسخ الاحتياطي في نظام الدولية مصمم لضمان حماية البيانات وإمكانية الاستعادة السريعة في حالة حدوث مشاكل. يتضمن النظام إنشاء نسخ احتياطية شاملة، نظام نقاط التحقق، وإجراءات الاستعادة المتقدمة.

## المكونات الرئيسية

### 1. أوامر إدارة النسخ الاحتياطية

#### إنشاء نسخة احتياطية
```bash
# نسخة احتياطية أساسية
python manage.py create_system_backup --name my_backup --description "وصف النسخة الاحتياطية"

# نسخة احتياطية مضغوطة مع الكود
python manage.py create_system_backup --name full_backup --include-code --compress

# نسخة احتياطية في مجلد مخصص
python manage.py create_system_backup --backup-dir /path/to/backups --name custom_backup
```

#### إدارة النسخ الاحتياطية
```bash
# عرض قائمة النسخ الاحتياطية
python manage.py manage_backups list

# التحقق من سلامة النسخ الاحتياطية
python manage.py manage_backups validate

# عرض تفاصيل نسخة احتياطية محددة
python manage.py manage_backups details --backup-name backup_name

# حذف نسخة احتياطية
python manage.py manage_backups delete --backup-name backup_name

# تنظيف النسخ القديمة
python manage.py manage_backups cleanup --older-than 30 --keep-count 10
```

#### استعادة النسخ الاحتياطية
```bash
# استعادة كاملة
python manage.py restore_system_backup /path/to/backup --restore-all

# استعادة قاعدة البيانات فقط
python manage.py restore_system_backup /path/to/backup --restore-database

# استعادة ملفات الوسائط فقط
python manage.py restore_system_backup /path/to/backup --restore-media

# استعادة ملفات التكوين فقط
python manage.py restore_system_backup /path/to/backup --restore-config

# محاكاة الاستعادة (عرض فقط)
python manage.py restore_system_backup /path/to/backup --restore-all --dry-run
```

### 2. نظام نقاط التحقق (Checkpoints)

#### إنشاء نقاط التحقق
```bash
# نقطة تحقق للمرحلة الأولية
python manage.py create_checkpoint initial

# نقطة تحقق لتنظيف الملفات
python manage.py create_checkpoint file_cleanup

# نقطة تحقق مخصصة
python manage.py create_checkpoint custom --name "my_checkpoint" --description "وصف النقطة"

# نقطة تحقق مع التحقق التلقائي من النظام
python manage.py create_checkpoint database_restructure --auto-validate
```

#### إدارة نقاط التحقق
```bash
# عرض قائمة نقاط التحقق
python manage.py list_checkpoints list

# عرض نقاط تحقق مرحلة محددة
python manage.py list_checkpoints list --stage initial

# عرض تفاصيل نقطة تحقق
python manage.py list_checkpoints show --checkpoint checkpoint_name

# استعادة من نقطة تحقق
python manage.py list_checkpoints restore --checkpoint checkpoint_name

# استعادة من آخر نقطة تحقق
python manage.py list_checkpoints restore --latest

# حذف نقطة تحقق
python manage.py list_checkpoints delete --checkpoint checkpoint_name
```

## مراحل نقاط التحقق المحددة مسبقاً

### 1. النقطة الأولية (initial)
- **الغرض**: حفظ حالة النظام قبل بدء أي تغييرات
- **المحتوى**: النظام الكامل بحالته الأصلية
- **الاستخدام**: نقطة العودة الأساسية

### 2. تنظيف الملفات (file_cleanup)
- **الغرض**: بعد إزالة الملفات غير المرغوبة
- **المحتوى**: النظام بعد التنظيف الأولي
- **الاستخدام**: التراجع إذا تم حذف ملفات مهمة

### 3. إعادة تنظيم الهيكل (structure_reorganization)
- **الغرض**: بعد إعادة تنظيم هيكل المشروع
- **المحتوى**: النظام مع الهيكل الجديد
- **الاستخدام**: التراجع إذا فشلت إعادة الهيكلة

### 4. إعادة هيكلة قاعدة البيانات (database_restructure)
- **الغرض**: بعد تحديث نماذج قاعدة البيانات
- **المحتوى**: النظام مع النماذج والهجرات الجديدة
- **الاستخدام**: التراجع إذا فشلت هجرات قاعدة البيانات

### 5. تطوير الخدمات (services_development)
- **الغرض**: بعد تطوير طبقة الخدمات
- **المحتوى**: النظام مع الخدمات الجديدة
- **الاستخدام**: التراجع إذا فشلت الخدمات

### 6. تطوير API (api_development)
- **الغرض**: بعد تطوير واجهات برمجة التطبيقات
- **المحتوى**: النظام مع API محدث
- **الاستخدام**: التراجع إذا فشلت واجهات API

### 7. تحديث الواجهة (frontend_update)
- **الغرض**: بعد تحديث واجهة المستخدم
- **المحتوى**: النظام مع الواجهة الجديدة
- **الاستخدام**: التراجع إذا فشلت الواجهة

### 8. تطبيق الأمان (security_implementation)
- **الغرض**: بعد تطبيق نظام الأمان
- **المحتوى**: النظام مع الأمان المحدث
- **الاستخدام**: التراجع إذا فشل نظام الأمان

### 9. تحسين الأداء (performance_optimization)
- **الغرض**: بعد تحسين الأداء
- **المحتوى**: النظام المحسن
- **الاستخدام**: التراجع إذا تدهور الأداء

### 10. إكمال الاختبارات (testing_completion)
- **الغرض**: بعد إكمال جميع الاختبارات
- **المحتوى**: النظام المختبر بالكامل
- **الاستخدام**: نقطة مرجعية للجودة

### 11. جاهز للإنتاج (production_ready)
- **الغرض**: النظام جاهز للنشر
- **المحتوى**: النسخة النهائية للإنتاج
- **الاستخدام**: نقطة النشر الأساسية

## هيكل النسخة الاحتياطية

### محتويات النسخة الاحتياطية
```
backup_name/
├── backup_manifest.json          # ملف البيانات الوصفية
├── database/                     # نسخ قاعدة البيانات
│   ├── database_backup.bak       # نسخة SQL Server
│   ├── django_dump.json          # نسخة Django
│   └── app_dumps/                # نسخ التطبيقات المنفصلة
├── media/                        # ملفات الوسائط
│   ├── files/                    # الملفات الفعلية
│   └── media_inventory.json      # فهرس الملفات
├── config/                       # ملفات التكوين
│   ├── .env.example              # مثال متغيرات البيئة
│   ├── requirements.txt          # متطلبات Python
│   ├── ElDawliya_sys/           # إعدادات Django
│   └── configuration_summary.json # ملخص التكوين
├── code/                         # الكود المصدري (اختياري)
│   ├── core/
│   ├── api/
│   ├── hr/
│   └── ...
├── logs/                         # سجلات النظام
└── docs/                         # التوثيق والحالة
    └── system_state.json         # حالة النظام
```

### ملف البيانات الوصفية (backup_manifest.json)
```json
{
  "backup_info": {
    "name": "backup_name",
    "created_at": "2024-01-01T12:00:00Z",
    "description": "وصف النسخة الاحتياطية",
    "checkpoint": "stage_name",
    "include_code": true,
    "compressed": false
  },
  "system_info": {
    "django_version": "4.2.22",
    "python_version": "3.11.0",
    "os_info": {...}
  },
  "backup_contents": {
    "files": [...],
    "total_files": 1234,
    "backup_size": 1073741824
  },
  "restoration_info": {
    "restoration_order": ["database", "media", "config", "code"],
    "prerequisites": [...],
    "restoration_notes": [...]
  }
}
```

## إجراءات الاستعادة

### 1. الاستعادة السريعة
```bash
# إنشاء نسخة احتياطية من الحالة الحالية
python manage.py create_system_backup --name pre_restore_backup

# استعادة من آخر نقطة تحقق
python manage.py list_checkpoints restore --latest --force

# التحقق من سلامة النظام
python manage.py check
python manage.py migrate --check
```

### 2. الاستعادة الكاملة
```bash
# استعادة من النسخة الاحتياطية الأولية
python manage.py restore_system_backup backups/initial_backup --restore-all

# تطبيق الهجرات إذا لزم الأمر
python manage.py migrate

# جمع الملفات الثابتة
python manage.py collectstatic --noinput

# اختبار النظام
python manage.py test --keepdb
```

### 3. الاستعادة الجزئية
```bash
# استعادة قاعدة البيانات فقط
python manage.py restore_system_backup backup_path --restore-database

# استعادة ملفات التكوين فقط
python manage.py restore_system_backup backup_path --restore-config

# استعادة ملفات الوسائط فقط
python manage.py restore_system_backup backup_path --restore-media
```

## التحقق من سلامة النسخ الاحتياطية

### التحقق التلقائي
```bash
# التحقق من جميع النسخ الاحتياطية
python manage.py manage_backups validate

# التحقق من نسخة احتياطية محددة
python manage.py manage_backups validate --backup-name backup_name
```

### التحقق اليدوي
```bash
# فحص ملف البيانات الوصفية
cat backups/backup_name/backup_manifest.json | jq .

# فحص محتويات قاعدة البيانات
ls -la backups/backup_name/database/

# فحص ملفات الوسائط
ls -la backups/backup_name/media/

# فحص ملفات التكوين
ls -la backups/backup_name/config/
```

## اختبار نظام النسخ الاحتياطي

### تشغيل اختبارات التحقق
```bash
# تشغيل اختبارات شاملة لنظام النسخ الاحتياطي
python scripts/validate_backup_system.py
```

### اختبارات دورية
```bash
# اختبار أسبوعي - استعادة قاعدة البيانات
python manage.py restore_system_backup latest_backup --restore-database --dry-run

# اختبار شهري - استعادة كاملة
python manage.py restore_system_backup latest_backup --restore-all --dry-run

# اختبار ربع سنوي - محاكاة طوارئ
python scripts/validate_backup_system.py
```

## أفضل الممارسات

### 1. جدولة النسخ الاحتياطية
- **يومياً**: نسخة احتياطية أساسية لقاعدة البيانات
- **أسبوعياً**: نسخة احتياطية كاملة مضغوطة
- **شهرياً**: نسخة احتياطية مع الكود المصدري
- **عند كل تحديث مهم**: نقطة تحقق مناسبة

### 2. تسمية النسخ الاحتياطية
```bash
# استخدم أسماء وصفية
python manage.py create_system_backup --name "pre_production_deploy_$(date +%Y%m%d)"

# أضف وصف مفيد
python manage.py create_system_backup --description "نسخة احتياطية قبل تحديث نظام الأمان"
```

### 3. إدارة المساحة
```bash
# تنظيف دوري للنسخ القديمة
python manage.py manage_backups cleanup --older-than 90 --keep-count 20

# ضغط النسخ الكبيرة
python manage.py create_system_backup --compress --include-code
```

### 4. التحقق من السلامة
```bash
# تحقق دوري من سلامة النسخ
python manage.py manage_backups validate

# اختبار استعادة دوري
python manage.py restore_system_backup latest --restore-all --dry-run
```

## استكشاف الأخطاء وإصلاحها

### مشاكل شائعة وحلولها

#### 1. فشل في إنشاء النسخة الاحتياطية
```bash
# تحقق من المساحة المتاحة
df -h

# تحقق من صلاحيات الكتابة
ls -la backups/

# تحقق من اتصال قاعدة البيانات
python manage.py dbshell
```

#### 2. فشل في الاستعادة
```bash
# تحقق من سلامة النسخة الاحتياطية
python manage.py manage_backups validate --backup-name backup_name

# تحقق من ملف البيانات الوصفية
cat backups/backup_name/backup_manifest.json

# استخدم الاستعادة الجزئية
python manage.py restore_system_backup backup_path --restore-database
```

#### 3. نسخة احتياطية تالفة
```bash
# استخدم نسخة احتياطية أقدم
python manage.py manage_backups list

# تحقق من النسخ المتاحة
python manage.py manage_backups validate

# استعد من نقطة تحقق سابقة
python manage.py list_checkpoints restore --checkpoint previous_checkpoint
```

## الأمان والحماية

### 1. حماية النسخ الاحتياطية
- تشفير النسخ الاحتياطية الحساسة
- تخزين النسخ في مواقع آمنة
- تقييد الوصول للنسخ الاحتياطية
- مراقبة عمليات النسخ والاستعادة

### 2. التحقق من الهوية
- استخدام صلاحيات محددة لعمليات النسخ
- تسجيل جميع عمليات النسخ والاستعادة
- التحقق من صحة المستخدم قبل الاستعادة

### 3. النسخ البعيدة
```bash
# نسخ النسخة الاحتياطية لموقع بعيد
rsync -avz backups/ remote_server:/backup/eldawliya/

# استخدام التخزين السحابي
aws s3 sync backups/ s3://eldawliya-backups/
```

## المراقبة والتنبيهات

### 1. مراقبة حالة النسخ الاحتياطية
```bash
# فحص دوري لحالة النسخ
python manage.py manage_backups validate > backup_status.log

# تنبيه في حالة فشل النسخ
if [ $? -ne 0 ]; then
    echo "فشل في التحقق من النسخ الاحتياطية" | mail -s "تنبيه نظام النسخ" admin@company.com
fi
```

### 2. تقارير دورية
```bash
# تقرير أسبوعي عن حالة النسخ
python manage.py manage_backups list > weekly_backup_report.txt

# إحصائيات النسخ الاحتياطية
python scripts/backup_statistics.py
```

## الصيانة والتحديث

### 1. صيانة دورية
- تنظيف النسخ القديمة
- فحص سلامة النسخ الموجودة
- تحديث إجراءات النسخ حسب الحاجة
- اختبار عمليات الاستعادة

### 2. تحديث النظام
- مراجعة إجراءات النسخ بعد التحديثات
- تحديث نقاط التحقق المحددة مسبقاً
- تحسين أداء عمليات النسخ والاستعادة

---

**ملاحظة مهمة**: يجب اختبار جميع إجراءات النسخ والاستعادة في بيئة تجريبية قبل تطبيقها في بيئة الإنتاج.