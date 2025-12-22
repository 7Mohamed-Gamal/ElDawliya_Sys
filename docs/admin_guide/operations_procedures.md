# توثيق العمليات والإجراءات - نظام الدولية

## 🚀 إجراءات النشر والصيانة

### إجراءات النشر الآمن

#### التحضير للنشر
```bash
# 1. إنشاء نسخة احتياطية كاملة
./scripts/backup_before_deployment.sh

# 2. اختبار التحديثات في بيئة التجريب
git checkout staging
git pull origin main
python manage.py migrate --dry-run
python manage.py test

# 3. مراجعة التغييرات
git log --oneline HEAD~10..HEAD
git diff HEAD~1 HEAD

# 4. التحقق من المتطلبات الجديدة
pip-compile requirements/production.in
diff requirements/production.txt requirements/production.txt.new
```

#### تنفيذ النشر
```bash
#!/bin/bash
# deploy.sh - سكريبت النشر الآمن

set -e  # إيقاف عند أول خطأ

echo "=== بدء عملية النشر ==="
DATE=$(date '+%Y%m%d_%H%M%S')
BACKUP_DIR="/backups/pre_deploy_$DATE"

# 1. إنشاء نسخة احتياطية
echo "إنشاء نسخة احتياطية..."
mkdir -p $BACKUP_DIR
mysqldump -u backup_user -p eldawliya_db > $BACKUP_DIR/database.sql
cp -r /opt/eldawliya/app $BACKUP_DIR/app_backup

# 2. إيقاف الخدمات
echo "إيقاف الخدمات..."
sudo systemctl stop eldawliya-web
sudo systemctl stop eldawliya-worker

# 3. تحديث الكود
echo "تحديث الكود..."
cd /opt/eldawliya/app
git pull origin main

# 4. تحديث المتطلبات
echo "تحديث المتطلبات..."
source /opt/eldawliya/venv/bin/activate
pip install -r requirements/production.txt

# 5. تطبيق الهجرات
echo "تطبيق هجرات قاعدة البيانات..."
python manage.py migrate

# 6. جمع الملفات الثابتة
echo "جمع الملفات الثابتة..."
python manage.py collectstatic --noinput

# 7. إعادة تشغيل الخدمات
echo "إعادة تشغيل الخدمات..."
sudo systemctl start eldawliya-worker
sleep 5
sudo systemctl start eldawliya-web

# 8. اختبار النظام
echo "اختبار النظام..."
sleep 10
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ النشر تم بنجاح"
    echo "النسخة الاحتياطية في: $BACKUP_DIR"
else
    echo "❌ فشل النشر - بدء الاستعادة"
    ./scripts/rollback.sh $BACKUP_DIR
    exit 1
fi

echo "=== انتهى النشر ==="
```

#### إجراءات التراجع
```bash
#!/bin/bash
# rollback.sh - سكريبت التراجع

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ]; then
    echo "خطأ: يجب تحديد مجلد النسخة الاحتياطية"
    exit 1
fi

echo "=== بدء عملية التراجع ==="

# 1. إيقاف الخدمات
sudo systemctl stop eldawliya-web eldawliya-worker

# 2. استعادة قاعدة البيانات
echo "استعادة قاعدة البيانات..."
mysql -u root -p eldawliya_db < $BACKUP_DIR/database.sql

# 3. استعادة الكود
echo "استعادة الكود..."
rm -rf /opt/eldawliya/app
mv $BACKUP_DIR/app_backup /opt/eldawliya/app

# 4. إعادة تشغيل الخدمات
echo "إعادة تشغيل الخدمات..."
sudo systemctl start eldawliya-worker eldawliya-web

echo "✅ تم التراجع بنجاح"
```

### الصيانة الدورية

#### الصيانة اليومية
```bash
#!/bin/bash
# daily_maintenance.sh

echo "=== الصيانة اليومية $(date) ==="

# 1. فحص حالة الخدمات
echo "فحص الخدمات..."
systemctl is-active eldawliya-web eldawliya-worker mysql redis nginx

# 2. فحص مساحة القرص
echo "فحص مساحة القرص..."
df -h | grep -E '(/$|/opt|/var)'

# 3. فحص استخدام الذاكرة
echo "فحص الذاكرة..."
free -h

# 4. فحص السجلات للأخطاء
echo "فحص الأخطاء..."
tail -n 100 /opt/eldawliya/logs/error.log | grep -i error | tail -10

# 5. تنظيف الملفات المؤقتة
echo "تنظيف الملفات المؤقتة..."
find /tmp -name "*.tmp" -mtime +1 -delete
find /opt/eldawliya/logs -name "*.log.*" -mtime +7 -delete

# 6. النسخ الاحتياطي اليومي
echo "النسخ الاحتياطي..."
./backup_daily.sh

echo "=== انتهت الصيانة اليومية ==="
```

#### الصيانة الأسبوعية
```bash
#!/bin/bash
# weekly_maintenance.sh

echo "=== الصيانة الأسبوعية $(date) ==="

# 1. تحديث النظام
echo "تحديث النظام..."
sudo apt update && sudo apt upgrade -y

# 2. تحسين قاعدة البيانات
echo "تحسين قاعدة البيانات..."
mysql -u root -p -e "
    OPTIMIZE TABLE employees;
    OPTIMIZE TABLE attendance;
    OPTIMIZE TABLE products;
    OPTIMIZE TABLE audit_logs;
"

# 3. تنظيف سجلات التدقيق القديمة
echo "تنظيف سجلات التدقيق..."
python manage.py shell -c "
from core.models import AuditLog
from datetime import datetime, timedelta
old_logs = AuditLog.objects.filter(
    created_at__lt=datetime.now() - timedelta(days=90)
)
count = old_logs.count()
old_logs.delete()
print(f'تم حذف {count} سجل قديم')
"

# 4. فحص الأمان
echo "فحص الأمان..."
./security_scan.sh

# 5. تقرير الأداء
echo "تقرير الأداء..."
./performance_report.sh

echo "=== انتهت الصيانة الأسبوعية ==="
```

## 🗄️ إدارة النظام والمراقبة

### مراقبة الأداء

#### سكريبت مراقبة الموارد
```bash
#!/bin/bash
# monitor_resources.sh

LOG_FILE="/opt/eldawliya/logs/monitoring.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# فحص استخدام المعالج
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

# فحص استخدام الذاكرة
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')

# فحص مساحة القرص
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)

# فحص عدد الاتصالات النشطة
ACTIVE_CONNECTIONS=$(netstat -an | grep :8000 | grep ESTABLISHED | wc -l)

# تسجيل البيانات
echo "$DATE,CPU:${CPU_USAGE}%,Memory:${MEMORY_USAGE}%,Disk:${DISK_USAGE}%,Connections:$ACTIVE_CONNECTIONS" >> $LOG_FILE

# إرسال تنبيهات إذا تجاوزت الحدود
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "تحذير: استخدام المعالج عالي ($CPU_USAGE%)" | mail -s "تنبيه نظام الدولية" admin@company.com
fi

if (( $(echo "$MEMORY_USAGE > 85" | bc -l) )); then
    echo "تحذير: استخدام الذاكرة عالي ($MEMORY_USAGE%)" | mail -s "تنبيه نظام الدولية" admin@company.com
fi

if (( DISK_USAGE > 90 )); then
    echo "تحذير: مساحة القرص ممتلئة ($DISK_USAGE%)" | mail -s "تنبيه نظام الدولية" admin@company.com
fi
```

#### مراقبة قاعدة البيانات
```bash
#!/bin/bash
# monitor_database.sh

echo "=== مراقبة قاعدة البيانات ==="

# فحص الاتصالات النشطة
echo "الاتصالات النشطة:"
mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"

# فحص العمليات الطويلة
echo "العمليات الطويلة:"
mysql -u root -p -e "
SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO 
FROM information_schema.PROCESSLIST 
WHERE TIME > 30 AND COMMAND != 'Sleep';"

# فحص حجم الجداول
echo "أكبر الجداول:"
mysql -u root -p -e "
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'eldawliya_db'
ORDER BY (data_length + index_length) DESC
LIMIT 10;"

# فحص الاستعلامات البطيئة
echo "الاستعلامات البطيئة (آخر 24 ساعة):"
if [ -f /var/log/mysql/mysql-slow.log ]; then
    tail -n 1000 /var/log/mysql/mysql-slow.log | grep -A 5 "Query_time"
fi
```

### إدارة السجلات

#### تدوير السجلات
```bash
# /etc/logrotate.d/eldawliya
/opt/eldawliya/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 eldawliya eldawliya
    postrotate
        systemctl reload eldawliya-web
        systemctl reload eldawliya-worker
    endscript
}

/var/log/nginx/eldawliya*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data adm
    postrotate
        systemctl reload nginx
    endscript
}
```

#### تحليل السجلات
```bash
#!/bin/bash
# analyze_logs.sh

echo "=== تحليل السجلات ==="

LOG_DIR="/opt/eldawliya/logs"
TODAY=$(date '+%Y-%m-%d')

# تحليل أخطاء Django
echo "أخطاء Django اليوم:"
grep "$TODAY" $LOG_DIR/error.log | grep ERROR | wc -l

# أكثر الأخطاء شيوعاً
echo "أكثر الأخطاء شيوعاً:"
grep ERROR $LOG_DIR/error.log | awk '{print $NF}' | sort | uniq -c | sort -nr | head -5

# تحليل الوصول
echo "طلبات اليوم:"
grep "$TODAY" /var/log/nginx/eldawliya_access.log | wc -l

# أكثر الصفحات زيارة
echo "أكثر الصفحات زيارة:"
awk '{print $7}' /var/log/nginx/eldawliya_access.log | sort | uniq -c | sort -nr | head -10

# رموز الاستجابة
echo "رموز الاستجابة:"
awk '{print $9}' /var/log/nginx/eldawliya_access.log | sort | uniq -c | sort -nr
```

## 💾 النسخ الاحتياطي والاستعادة

### استراتيجية النسخ الاحتياطي

#### النسخ الاحتياطي التلقائي
```bash
#!/bin/bash
# backup_system.sh

BACKUP_ROOT="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$DATE"
RETENTION_DAYS=30

echo "=== بدء النسخ الاحتياطي $DATE ==="

# إنشاء مجلد النسخة
mkdir -p $BACKUP_DIR

# 1. نسخ قاعدة البيانات
echo "نسخ قاعدة البيانات..."
mysqldump -u backup_user -p \
    --single-transaction \
    --routines \
    --triggers \
    eldawliya_db > $BACKUP_DIR/database.sql

# 2. نسخ ملفات الوسائط
echo "نسخ ملفات الوسائط..."
tar -czf $BACKUP_DIR/media.tar.gz /opt/eldawliya/media/

# 3. نسخ ملفات التكوين
echo "نسخ ملفات التكوين..."
cp /opt/eldawliya/app/.env $BACKUP_DIR/
cp -r /etc/nginx/sites-available/eldawliya $BACKUP_DIR/nginx.conf
cp -r /etc/systemd/system/eldawliya-*.service $BACKUP_DIR/

# 4. نسخ السجلات المهمة
echo "نسخ السجلات..."
tar -czf $BACKUP_DIR/logs.tar.gz /opt/eldawliya/logs/

# 5. إنشاء ملف معلومات النسخة
echo "إنشاء ملف المعلومات..."
cat > $BACKUP_DIR/backup_info.txt << EOF
تاريخ النسخة: $DATE
إصدار النظام: $(cd /opt/eldawliya/app && git rev-parse HEAD)
حجم قاعدة البيانات: $(du -h $BACKUP_DIR/database.sql | cut -f1)
حجم الوسائط: $(du -h $BACKUP_DIR/media.tar.gz | cut -f1)
المستخدم: $(whoami)
الخادم: $(hostname)
EOF

# 6. ضغط النسخة الكاملة
echo "ضغط النسخة..."
cd $BACKUP_ROOT
tar -czf "eldawliya_backup_$DATE.tar.gz" $DATE/
rm -rf $DATE/

# 7. حذف النسخ القديمة
echo "حذف النسخ القديمة..."
find $BACKUP_ROOT -name "eldawliya_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# 8. التحقق من سلامة النسخة
echo "التحقق من سلامة النسخة..."
if tar -tzf "$BACKUP_ROOT/eldawliya_backup_$DATE.tar.gz" > /dev/null; then
    echo "✅ النسخة الاحتياطية سليمة"
    
    # إرسال تقرير نجاح
    echo "تم إنشاء النسخة الاحتياطية بنجاح: eldawliya_backup_$DATE.tar.gz" | \
    mail -s "تقرير النسخ الاحتياطي - نجح" admin@company.com
else
    echo "❌ النسخة الاحتياطية تالفة"
    
    # إرسال تقرير فشل
    echo "فشل في إنشاء النسخة الاحتياطية!" | \
    mail -s "تقرير النسخ الاحتياطي - فشل" admin@company.com
    exit 1
fi

echo "=== انتهى النسخ الاحتياطي ==="
```

#### استعادة النسخ الاحتياطية
```bash
#!/bin/bash
# restore_backup.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "الاستخدام: $0 <backup_file.tar.gz>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "خطأ: ملف النسخة الاحتياطية غير موجود"
    exit 1
fi

echo "=== بدء استعادة النسخة الاحتياطية ==="
echo "الملف: $BACKUP_FILE"

# تأكيد من المستخدم
read -p "هل أنت متأكد من استعادة هذه النسخة؟ (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "تم إلغاء العملية"
    exit 0
fi

# إنشاء مجلد مؤقت
TEMP_DIR="/tmp/restore_$(date +%s)"
mkdir -p $TEMP_DIR

# استخراج النسخة الاحتياطية
echo "استخراج النسخة الاحتياطية..."
tar -xzf $BACKUP_FILE -C $TEMP_DIR

# العثور على مجلد النسخة
BACKUP_DIR=$(find $TEMP_DIR -maxdepth 1 -type d -name "20*" | head -1)

if [ -z "$BACKUP_DIR" ]; then
    echo "خطأ: لم يتم العثور على مجلد النسخة الاحتياطية"
    exit 1
fi

# إيقاف الخدمات
echo "إيقاف الخدمات..."
sudo systemctl stop eldawliya-web eldawliya-worker

# استعادة قاعدة البيانات
echo "استعادة قاعدة البيانات..."
mysql -u root -p eldawliya_db < $BACKUP_DIR/database.sql

# استعادة ملفات الوسائط
echo "استعادة ملفات الوسائط..."
rm -rf /opt/eldawliya/media/*
tar -xzf $BACKUP_DIR/media.tar.gz -C /

# استعادة ملفات التكوين
echo "استعادة ملفات التكوين..."
cp $BACKUP_DIR/.env /opt/eldawliya/app/
sudo cp $BACKUP_DIR/nginx.conf /etc/nginx/sites-available/eldawliya
sudo cp $BACKUP_DIR/eldawliya-*.service /etc/systemd/system/

# إعادة تحميل التكوين
sudo systemctl daemon-reload
sudo nginx -t && sudo systemctl reload nginx

# إعادة تشغيل الخدمات
echo "إعادة تشغيل الخدمات..."
sudo systemctl start eldawliya-worker eldawliya-web

# التحقق من النظام
echo "التحقق من النظام..."
sleep 10
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ تم استعادة النسخة الاحتياطية بنجاح"
else
    echo "❌ فشل في استعادة النسخة الاحتياطية"
    exit 1
fi

# تنظيف الملفات المؤقتة
rm -rf $TEMP_DIR

echo "=== انتهت استعادة النسخة الاحتياطية ==="
```

### اختبار النسخ الاحتياطية
```bash
#!/bin/bash
# test_backup.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "الاستخدام: $0 <backup_file.tar.gz>"
    exit 1
fi

echo "=== اختبار النسخة الاحتياطية ==="

# 1. فحص سلامة الملف المضغوط
echo "فحص سلامة الملف..."
if tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
    echo "✅ الملف المضغوط سليم"
else
    echo "❌ الملف المضغوط تالف"
    exit 1
fi

# 2. استخراج مؤقت
TEMP_DIR="/tmp/backup_test_$(date +%s)"
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

BACKUP_DIR=$(find $TEMP_DIR -maxdepth 1 -type d -name "20*" | head -1)

# 3. فحص محتويات النسخة
echo "فحص محتويات النسخة..."

if [ -f "$BACKUP_DIR/database.sql" ]; then
    echo "✅ ملف قاعدة البيانات موجود"
    
    # فحص سلامة SQL
    if mysql --execute="source $BACKUP_DIR/database.sql" --database=test_restore 2>/dev/null; then
        echo "✅ ملف قاعدة البيانات صالح"
        mysql --execute="DROP DATABASE IF EXISTS test_restore"
    else
        echo "❌ ملف قاعدة البيانات تالف"
    fi
else
    echo "❌ ملف قاعدة البيانات مفقود"
fi

if [ -f "$BACKUP_DIR/media.tar.gz" ]; then
    echo "✅ ملف الوسائط موجود"
    
    if tar -tzf "$BACKUP_DIR/media.tar.gz" > /dev/null 2>&1; then
        echo "✅ ملف الوسائط صالح"
    else
        echo "❌ ملف الوسائط تالف"
    fi
else
    echo "❌ ملف الوسائط مفقود"
fi

if [ -f "$BACKUP_DIR/.env" ]; then
    echo "✅ ملف التكوين موجود"
else
    echo "❌ ملف التكوين مفقود"
fi

if [ -f "$BACKUP_DIR/backup_info.txt" ]; then
    echo "✅ ملف معلومات النسخة موجود"
    echo "محتوى ملف المعلومات:"
    cat $BACKUP_DIR/backup_info.txt
else
    echo "❌ ملف معلومات النسخة مفقود"
fi

# تنظيف
rm -rf $TEMP_DIR

echo "=== انتهى اختبار النسخة الاحتياطية ==="
```## 🚨 خطط
 الطوارئ والاستمرارية

### خطة الاستجابة للطوارئ

#### إجراءات الطوارئ العامة
```
🚨 في حالة انقطاع النظام الكامل:

1. التقييم الفوري (5 دقائق)
   - فحص حالة الخادم والشبكة
   - تحديد نطاق المشكلة
   - إشعار الفريق والإدارة

2. الاحتواء (10 دقائق)
   - عزل المشكلة إن أمكن
   - تفعيل النظام البديل
   - توثيق الحادث

3. الاستعادة (30 دقيقة)
   - تطبيق الحل المناسب
   - اختبار النظام
   - إشعار المستخدمين

4. المتابعة (24 ساعة)
   - مراقبة الاستقرار
   - تحليل السبب الجذري
   - تحديث الإجراءات
```

#### سيناريوهات الطوارئ المحددة

##### انقطاع الكهرباء
```bash
#!/bin/bash
# power_outage_response.sh

echo "=== الاستجابة لانقطاع الكهرباء ==="

# 1. التحقق من حالة UPS
echo "فحص UPS..."
upsc ups@localhost

# 2. إيقاف آمن للخدمات
echo "إيقاف آمن للخدمات..."
sudo systemctl stop eldawliya-web
sudo systemctl stop eldawliya-worker
sudo systemctl stop mysql

# 3. إنشاء نسخة احتياطية طارئة
echo "نسخة احتياطية طارئة..."
./emergency_backup.sh

# 4. إيقاف النظام
echo "إيقاف النظام..."
sudo shutdown -h +2 "إيقاف طارئ بسبب انقطاع الكهرباء"
```

##### فشل قاعدة البيانات
```bash
#!/bin/bash
# database_failure_response.sh

echo "=== الاستجابة لفشل قاعدة البيانات ==="

# 1. إيقاف التطبيق
sudo systemctl stop eldawliya-web eldawliya-worker

# 2. فحص سلامة قاعدة البيانات
echo "فحص سلامة قاعدة البيانات..."
mysqlcheck -u root -p --all-databases --check --auto-repair

# 3. إذا فشل الإصلاح، استعادة من النسخة الاحتياطية
if [ $? -ne 0 ]; then
    echo "فشل الإصلاح - استعادة من النسخة الاحتياطية..."
    LATEST_BACKUP=$(ls -t /backups/eldawliya_backup_*.tar.gz | head -1)
    ./restore_backup.sh $LATEST_BACKUP
fi

# 4. إعادة تشغيل الخدمات
sudo systemctl start eldawliya-worker eldawliya-web
```

##### اختراق أمني
```bash
#!/bin/bash
# security_breach_response.sh

echo "=== الاستجابة للاختراق الأمني ==="

# 1. عزل النظام فوراً
echo "عزل النظام..."
sudo iptables -A INPUT -j DROP
sudo iptables -A OUTPUT -j DROP

# 2. إنشاء نسخة من الأدلة
echo "حفظ الأدلة..."
EVIDENCE_DIR="/tmp/security_evidence_$(date +%s)"
mkdir -p $EVIDENCE_DIR
cp -r /opt/eldawliya/logs $EVIDENCE_DIR/
cp /var/log/auth.log $EVIDENCE_DIR/
cp /var/log/syslog $EVIDENCE_DIR/

# 3. تغيير جميع كلمات المرور
echo "تغيير كلمات المرور..."
./change_all_passwords.sh

# 4. فحص شامل للنظام
echo "فحص النظام..."
./security_scan.sh > $EVIDENCE_DIR/security_scan.log

# 5. إشعار فريق الأمان
echo "إشعار فريق الأمان..."
echo "تم اكتشاف اختراق أمني محتمل. الأدلة في: $EVIDENCE_DIR" | \
mail -s "تنبيه أمني عاجل" security@company.com
```

### خطة استمرارية الأعمال

#### النظام البديل
```bash
#!/bin/bash
# activate_backup_system.sh

echo "=== تفعيل النظام البديل ==="

# 1. تحديث DNS للإشارة للخادم البديل
echo "تحديث DNS..."
# هذا يعتمد على مزود DNS المستخدم

# 2. مزامنة البيانات
echo "مزامنة البيانات..."
rsync -avz /opt/eldawliya/ backup-server:/opt/eldawliya/

# 3. تشغيل الخدمات على الخادم البديل
echo "تشغيل الخدمات على الخادم البديل..."
ssh backup-server "
    sudo systemctl start mysql
    sudo systemctl start redis
    sudo systemctl start eldawliya-worker
    sudo systemctl start eldawliya-web
    sudo systemctl start nginx
"

# 4. اختبار النظام البديل
echo "اختبار النظام البديل..."
if curl -f http://backup-server/health/ > /dev/null 2>&1; then
    echo "✅ النظام البديل يعمل"
    
    # إشعار المستخدمين
    echo "تم تفعيل النظام البديل. يرجى استخدام الرابط الجديد." | \
    mail -s "تفعيل النظام البديل" all-users@company.com
else
    echo "❌ فشل في تشغيل النظام البديل"
    exit 1
fi
```

#### خطة التعافي من الكوارث
```
📋 خطة التعافي من الكوارث

المرحلة 1: التقييم والاستجابة الفورية (0-4 ساعات)
- تقييم الأضرار
- تفعيل فريق الطوارئ
- إشعار الإدارة والمستخدمين
- تفعيل النظام البديل إن أمكن

المرحلة 2: الاستعادة المؤقتة (4-24 ساعة)
- إعداد بيئة عمل مؤقتة
- استعادة البيانات الحرجة
- تشغيل الوظائف الأساسية
- تحديث المستخدمين

المرحلة 3: الاستعادة الكاملة (1-7 أيام)
- إصلاح أو استبدال الأجهزة
- استعادة جميع البيانات
- اختبار شامل للنظام
- العودة للعمليات العادية

المرحلة 4: المراجعة والتحسين (7-30 يوم)
- تحليل الحادث
- تحديث خطط الطوارئ
- تدريب إضافي للفريق
- تحسين الإجراءات
```

## 🔒 إجراءات الأمان والامتثال

### إجراءات الأمان اليومية

#### فحص الأمان اليومي
```bash
#!/bin/bash
# daily_security_check.sh

echo "=== فحص الأمان اليومي ==="
DATE=$(date '+%Y-%m-%d')
REPORT_FILE="/opt/eldawliya/logs/security_daily_$DATE.log"

# 1. فحص محاولات تسجيل الدخول الفاشلة
echo "محاولات تسجيل الدخول الفاشلة:" >> $REPORT_FILE
grep "authentication failure" /var/log/auth.log | grep "$DATE" | wc -l >> $REPORT_FILE

# 2. فحص الاتصالات المشبوهة
echo "الاتصالات المشبوهة:" >> $REPORT_FILE
netstat -an | grep :8000 | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -10 >> $REPORT_FILE

# 3. فحص تغييرات الملفات الحساسة
echo "تغييرات الملفات الحساسة:" >> $REPORT_FILE
find /etc /opt/eldawliya/app -name "*.py" -o -name "*.conf" -o -name ".env" -mtime -1 >> $REPORT_FILE

# 4. فحص العمليات المشبوهة
echo "العمليات المشبوهة:" >> $REPORT_FILE
ps aux | grep -E "(nc|netcat|nmap|wget|curl)" | grep -v grep >> $REPORT_FILE

# 5. فحص استخدام الموارد غير العادي
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
if (( $(echo "$CPU_USAGE > 90" | bc -l) )); then
    echo "تحذير: استخدام معالج عالي جداً ($CPU_USAGE%)" >> $REPORT_FILE
fi

# إرسال التقرير إذا وجدت مشاكل
if [ -s $REPORT_FILE ]; then
    mail -s "تقرير الأمان اليومي - $DATE" security@company.com < $REPORT_FILE
fi
```

#### تدوير كلمات المرور
```bash
#!/bin/bash
# rotate_passwords.sh

echo "=== تدوير كلمات المرور ==="

# 1. إنشاء كلمات مرور جديدة
NEW_DB_PASSWORD=$(openssl rand -base64 32)
NEW_API_KEY=$(openssl rand -hex 32)
NEW_SECRET_KEY=$(openssl rand -base64 64)

# 2. تحديث قاعدة البيانات
echo "تحديث كلمة مرور قاعدة البيانات..."
mysql -u root -p -e "
    ALTER USER 'eldawliya_user'@'localhost' IDENTIFIED BY '$NEW_DB_PASSWORD';
    FLUSH PRIVILEGES;
"

# 3. تحديث ملف التكوين
echo "تحديث ملف التكوين..."
sed -i "s/DATABASE_PASSWORD=.*/DATABASE_PASSWORD=$NEW_DB_PASSWORD/" /opt/eldawliya/app/.env
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$NEW_SECRET_KEY/" /opt/eldawliya/app/.env

# 4. إعادة تشغيل الخدمات
echo "إعادة تشغيل الخدمات..."
sudo systemctl restart eldawliya-web eldawliya-worker

# 5. اختبار النظام
sleep 10
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ تم تدوير كلمات المرور بنجاح"
else
    echo "❌ فشل في تدوير كلمات المرور"
    exit 1
fi
```

### إجراءات الامتثال

#### تقرير الامتثال الشهري
```bash
#!/bin/bash
# compliance_report.sh

MONTH=$(date '+%Y-%m')
REPORT_FILE="/opt/eldawliya/reports/compliance_$MONTH.html"

cat > $REPORT_FILE << EOF
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تقرير الامتثال - $MONTH</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
        th { background-color: #f2f2f2; }
        .pass { color: green; }
        .fail { color: red; }
    </style>
</head>
<body>
    <h1>تقرير الامتثال - $MONTH</h1>
    
    <h2>أمان البيانات</h2>
    <table>
        <tr><th>المعيار</th><th>الحالة</th><th>التفاصيل</th></tr>
EOF

# فحص التشفير
if grep -q "SECURE_SSL_REDIRECT = True" /opt/eldawliya/app/ElDawliya_sys/settings/production.py; then
    echo "<tr><td>تشفير البيانات</td><td class='pass'>✅ مطبق</td><td>HTTPS مفعل</td></tr>" >> $REPORT_FILE
else
    echo "<tr><td>تشفير البيانات</td><td class='fail'>❌ غير مطبق</td><td>HTTPS غير مفعل</td></tr>" >> $REPORT_FILE
fi

# فحص النسخ الاحتياطية
BACKUP_COUNT=$(find /backups -name "eldawliya_backup_*.tar.gz" -mtime -30 | wc -l)
if [ $BACKUP_COUNT -ge 30 ]; then
    echo "<tr><td>النسخ الاحتياطية</td><td class='pass'>✅ مطبق</td><td>$BACKUP_COUNT نسخة في آخر 30 يوم</td></tr>" >> $REPORT_FILE
else
    echo "<tr><td>النسخ الاحتياطية</td><td class='fail'>❌ غير كافي</td><td>$BACKUP_COUNT نسخة فقط</td></tr>" >> $REPORT_FILE
fi

# فحص سجلات التدقيق
AUDIT_COUNT=$(mysql -u root -p -se "SELECT COUNT(*) FROM audit_logs WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY);" eldawliya_db)
echo "<tr><td>سجلات التدقيق</td><td class='pass'>✅ مطبق</td><td>$AUDIT_COUNT سجل في آخر 30 يوم</td></tr>" >> $REPORT_FILE

cat >> $REPORT_FILE << EOF
    </table>
    
    <h2>إدارة المستخدمين</h2>
    <table>
        <tr><th>المعيار</th><th>الحالة</th><th>التفاصيل</th></tr>
EOF

# فحص المستخدمين النشطين
ACTIVE_USERS=$(mysql -u root -p -se "SELECT COUNT(*) FROM auth_user WHERE is_active = 1;" eldawliya_db)
echo "<tr><td>المستخدمين النشطين</td><td class='pass'>✅</td><td>$ACTIVE_USERS مستخدم نشط</td></tr>" >> $REPORT_FILE

# فحص كلمات المرور المنتهية الصلاحية
EXPIRED_PASSWORDS=$(mysql -u root -p -se "SELECT COUNT(*) FROM auth_user WHERE password_changed_at < DATE_SUB(NOW(), INTERVAL 90 DAY);" eldawliya_db 2>/dev/null || echo "0")
if [ $EXPIRED_PASSWORDS -gt 0 ]; then
    echo "<tr><td>كلمات المرور المنتهية</td><td class='fail'>❌</td><td>$EXPIRED_PASSWORDS كلمة مرور منتهية</td></tr>" >> $REPORT_FILE
else
    echo "<tr><td>كلمات المرور المنتهية</td><td class='pass'>✅</td><td>جميع كلمات المرور محدثة</td></tr>" >> $REPORT_FILE
fi

cat >> $REPORT_FILE << EOF
    </table>
    
    <h2>الأداء والتوفر</h2>
    <table>
        <tr><th>المعيار</th><th>الحالة</th><th>التفاصيل</th></tr>
EOF

# حساب وقت التشغيل
UPTIME=$(uptime | awk '{print $3,$4}' | sed 's/,//')
echo "<tr><td>وقت التشغيل</td><td class='pass'>✅</td><td>$UPTIME</td></tr>" >> $REPORT_FILE

cat >> $REPORT_FILE << EOF
    </table>
    
    <p><strong>تاريخ التقرير:</strong> $(date)</p>
    <p><strong>تم إنشاؤه بواسطة:</strong> نظام الدولية التلقائي</p>
</body>
</html>
EOF

echo "تم إنشاء تقرير الامتثال: $REPORT_FILE"

# إرسال التقرير
mail -s "تقرير الامتثال - $MONTH" -a "Content-Type: text/html" \
    compliance@company.com < $REPORT_FILE
```

## 📋 قوائم التحقق والمراجعة

### قائمة التحقق اليومية
```
☐ فحص حالة جميع الخدمات
☐ مراجعة سجلات الأخطاء
☐ فحص استخدام الموارد (CPU, Memory, Disk)
☐ التحقق من نجاح النسخ الاحتياطية
☐ مراجعة تنبيهات الأمان
☐ فحص الاتصالات النشطة
☐ مراجعة أداء قاعدة البيانات
☐ تحديث سجل الصيانة
```

### قائمة التحقق الأسبوعية
```
☐ تحديث النظام والحزم
☐ تحسين قاعدة البيانات
☐ مراجعة سجلات التدقيق
☐ فحص أمان شامل
☐ اختبار النسخ الاحتياطية
☐ مراجعة أداء النظام
☐ تنظيف الملفات القديمة
☐ مراجعة صلاحيات المستخدمين
☐ تحديث التوثيق
☐ تقرير الحالة الأسبوعي
```

### قائمة التحقق الشهرية
```
☐ مراجعة شاملة للأمان
☐ تدوير كلمات المرور
☐ مراجعة النسخ الاحتياطية
☐ تحليل الأداء الشهري
☐ مراجعة سعة النظام
☐ تحديث خطط الطوارئ
☐ تدريب الفريق
☐ مراجعة الامتثال
☐ تقييم المخاطر
☐ تحديث الوثائق
```

## 📞 جهات الاتصال للطوارئ

### فريق الاستجابة للطوارئ

| الدور | الاسم | الهاتف | البريد الإلكتروني | المسؤوليات |
|-------|-------|---------|-------------------|-------------|
| **مدير النظام الرئيسي** | أحمد محمد | 123-456 | ahmed@company.com | القرارات الحرجة، التنسيق العام |
| **مطور النظام** | سارة أحمد | 123-457 | sara@company.com | المشاكل التقنية، تطبيق الإصلاحات |
| **مدير قاعدة البيانات** | محمد علي | 123-458 | mohamed@company.com | مشاكل قاعدة البيانات، استعادة البيانات |
| **مسؤول الأمان** | فاطمة حسن | 123-459 | fatima@company.com | الحوادث الأمنية، التحقيقات |
| **مدير الشبكة** | خالد سالم | 123-460 | khalid@company.com | مشاكل الشبكة والاتصالات |

### جهات الاتصال الخارجية

| الخدمة | الشركة | الهاتف | البريد الإلكتروني |
|--------|---------|---------|-------------------|
| **استضافة الخوادم** | شركة الاستضافة | 800-123-456 | support@hosting.com |
| **الإنترنت** | مزود الخدمة | 800-789-012 | technical@isp.com |
| **الكهرباء** | شركة الكهرباء | 920-001-100 | emergency@power.com |
| **الأمان السيبراني** | شركة الأمان | 800-555-999 | incident@security.com |

### إجراءات التصعيد

```
المستوى 1: مشكلة بسيطة (< 30 دقيقة)
- مدير النظام يحل المشكلة
- توثيق الحل في السجل

المستوى 2: مشكلة متوسطة (30 دقيقة - 2 ساعة)
- إشراك المطور أو المختص
- إشعار مدير تقنية المعلومات
- تحديث المستخدمين

المستوى 3: مشكلة حرجة (> 2 ساعة)
- تفعيل فريق الطوارئ الكامل
- إشعار الإدارة العليا
- تفعيل خطة الطوارئ
- إشعار العملاء/المستخدمين

المستوى 4: كارثة (انقطاع كامل)
- تفعيل خطة استمرارية الأعمال
- إشعار جميع الأطراف المعنية
- تفعيل النظام البديل
- إدارة الأزمة على أعلى مستوى
```

---

**هذا التوثيق يجب مراجعته وتحديثه بانتظام للتأكد من دقته وفعاليته.**

**آخر تحديث**: ديسمبر 2024  
**المراجعة التالية**: مارس 2025