# مجلد النسخ الاحتياطية - نظام الدولية

هذا المجلد يحتوي على النسخ الاحتياطية لنظام الدولية.

## الملفات المتوقعة:
- `backup_registry.json`: سجل النسخ الاحتياطية
- `checkpoint_registry.json`: سجل نقاط التحقق
- مجلدات النسخ الاحتياطية أو ملفات مضغوطة

## الاستخدام:
```bash
# عرض النسخ المتاحة
python manage.py manage_backups list

# إنشاء نسخة احتياطية
python manage.py create_system_backup --name my_backup

# استعادة من نسخة احتياطية
python manage.py restore_system_backup backup_path --restore-all
```
