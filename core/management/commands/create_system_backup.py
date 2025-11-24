"""
أداة إنشاء النسخ الاحتياطية الشاملة
===================================

هذه الأداة تقوم بإنشاء نسخة احتياطية شاملة من النظام تشمل:
- قاعدة البيانات
- ملفات المشروع
- الإعدادات
- ملفات الوسائط
"""

import os
import shutil
import sqlite3
import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from django.db import connection
import logging


class SystemBackupManager:
    """مدير النسخ الاحتياطية للنظام"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.base_dir = Path(settings.BASE_DIR)
        self.backup_dir = self.base_dir / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
    def _setup_logging(self) -> logging.Logger:
        """إعداد نظام التسجيل"""
        logger = logging.getLogger('system_backup')
        logger.setLevel(logging.INFO)
        
        # إنشاء معالج الملف
        log_file = Path(settings.BASE_DIR) / 'logs' / 'system_backup.log'
        log_file.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # إنشاء معالج وحدة التحكم
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # تنسيق الرسائل
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def create_full_backup(self, backup_name: Optional[str] = None) -> str:
        """إنشاء نسخة احتياطية شاملة"""
        if not backup_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"system_backup_{timestamp}"
            
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        self.logger.info(f"بدء إنشاء النسخة الاحتياطية: {backup_name}")
        
        try:
            # 1. نسخ احتياطي من قاعدة البيانات
            db_backup_path = self._backup_database(backup_path)
            
            # 2. نسخ احتياطي من ملفات المشروع
            project_backup_path = self._backup_project_files(backup_path)
            
            # 3. نسخ احتياطي من الإعدادات
            settings_backup_path = self._backup_settings(backup_path)
            
            # 4. نسخ احتياطي من ملفات الوسائط
            media_backup_path = self._backup_media_files(backup_path)
            
            # 5. إنشاء ملف معلومات النسخة الاحتياطية
            info_file = self._create_backup_info(backup_path, {
                'database': db_backup_path,
                'project_files': project_backup_path,
                'settings': settings_backup_path,
                'media_files': media_backup_path
            })
            
            # 6. ضغط النسخة الاحتياطية
            zip_path = self._compress_backup(backup_path)
            
            self.logger.info(f"تم إنشاء النسخة الاحتياطية بنجاح: {zip_path}")
            return str(zip_path)
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            raise
    
    def _backup_database(self, backup_path: Path) -> str:
        """نسخ احتياطي من قاعدة البيانات"""
        self.logger.info("إنشاء نسخة احتياطية من قاعدة البيانات...")
        
        db_backup_dir = backup_path / 'database'
        db_backup_dir.mkdir(exist_ok=True)
        
        try:
            # التحقق من نوع قاعدة البيانات
            db_config = settings.DATABASES['default']
            
            if db_config['ENGINE'] == 'django.db.backends.sqlite3':
                # نسخ احتياطي من SQLite
                db_file = Path(db_config['NAME'])
                if db_file.exists():
                    backup_db_file = db_backup_dir / f"database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
                    shutil.copy2(db_file, backup_db_file)
                    self.logger.info(f"تم نسخ قاعدة البيانات SQLite: {backup_db_file}")
                    return str(backup_db_file)
            
            elif 'mssql' in db_config['ENGINE']:
                # نسخ احتياطي من SQL Server باستخدام Django dumpdata
                dump_file = db_backup_dir / f"database_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                with open(dump_file, 'w', encoding='utf-8') as f:
                    call_command('dumpdata', stdout=f, indent=2)
                
                self.logger.info(f"تم إنشاء dump من قاعدة البيانات: {dump_file}")
                return str(dump_file)
            
            else:
                # نسخ احتياطي عام باستخدام dumpdata
                dump_file = db_backup_dir / f"database_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                with open(dump_file, 'w', encoding='utf-8') as f:
                    call_command('dumpdata', stdout=f, indent=2)
                
                self.logger.info(f"تم إنشاء dump عام من قاعدة البيانات: {dump_file}")
                return str(dump_file)
                
        except Exception as e:
            self.logger.error(f"خطأ في نسخ قاعدة البيانات: {e}")
            raise
    
    def _backup_project_files(self, backup_path: Path) -> str:
        """نسخ احتياطي من ملفات المشروع"""
        self.logger.info("إنشاء نسخة احتياطية من ملفات المشروع...")
        
        project_backup_dir = backup_path / 'project_files'
        project_backup_dir.mkdir(exist_ok=True)
        
        # قائمة الملفات والمجلدات المهمة للنسخ الاحتياطي
        important_items = [
            'manage.py',
            'requirements.txt',
            '.env.example',
            'ElDawliya_sys',
            'api',
            'accounts',
            'administrator',
            'notifications',
            'core',
            'templates',
            'static',
            'docs',
            'scripts',
        ]
        
        # قائمة الملفات والمجلدات المستبعدة
        excluded_items = [
            '__pycache__',
            '*.pyc',
            '.git',
            'logs',
            'media',
            'staticfiles',
            'backups',
            '.env',
            'db.sqlite3',
            '*.log'
        ]
        
        try:
            for item in important_items:
                source_path = self.base_dir / item
                if source_path.exists():
                    dest_path = project_backup_dir / item
                    
                    if source_path.is_file():
                        shutil.copy2(source_path, dest_path)
                    else:
                        shutil.copytree(source_path, dest_path, 
                                      ignore=shutil.ignore_patterns(*excluded_items))
                    
                    self.logger.info(f"تم نسخ: {item}")
            
            self.logger.info("تم إنشاء نسخة احتياطية من ملفات المشروع")
            return str(project_backup_dir)
            
        except Exception as e:
            self.logger.error(f"خطأ في نسخ ملفات المشروع: {e}")
            raise
    
    def _backup_settings(self, backup_path: Path) -> str:
        """نسخ احتياطي من الإعدادات"""
        self.logger.info("إنشاء نسخة احتياطية من الإعدادات...")
        
        settings_backup_dir = backup_path / 'settings'
        settings_backup_dir.mkdir(exist_ok=True)
        
        try:
            # حفظ إعدادات Django الحالية
            settings_info = {
                'INSTALLED_APPS': settings.INSTALLED_APPS,
                'MIDDLEWARE': settings.MIDDLEWARE,
                'DATABASES': {
                    'default': {
                        'ENGINE': settings.DATABASES['default']['ENGINE'],
                        'NAME': settings.DATABASES['default'].get('NAME', ''),
                        # لا نحفظ كلمات المرور في النسخة الاحتياطية
                    }
                },
                'LANGUAGE_CODE': settings.LANGUAGE_CODE,
                'TIME_ZONE': settings.TIME_ZONE,
                'DEBUG': settings.DEBUG,
                'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
            }
            
            settings_file = settings_backup_dir / 'django_settings.json'
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_info, f, indent=2, ensure_ascii=False)
            
            # نسخ ملفات الإعدادات
            settings_dir = self.base_dir / 'ElDawliya_sys' / 'settings'
            if settings_dir.exists():
                dest_settings_dir = settings_backup_dir / 'settings_files'
                shutil.copytree(settings_dir, dest_settings_dir)
            
            self.logger.info("تم إنشاء نسخة احتياطية من الإعدادات")
            return str(settings_backup_dir)
            
        except Exception as e:
            self.logger.error(f"خطأ في نسخ الإعدادات: {e}")
            raise
    
    def _backup_media_files(self, backup_path: Path) -> str:
        """نسخ احتياطي من ملفات الوسائط"""
        self.logger.info("إنشاء نسخة احتياطية من ملفات الوسائط...")
        
        media_backup_dir = backup_path / 'media_files'
        media_backup_dir.mkdir(exist_ok=True)
        
        try:
            media_dir = Path(settings.MEDIA_ROOT)
            if media_dir.exists() and any(media_dir.iterdir()):
                shutil.copytree(media_dir, media_backup_dir / 'media')
                self.logger.info("تم نسخ ملفات الوسائط")
            else:
                self.logger.info("لا توجد ملفات وسائط للنسخ")
            
            return str(media_backup_dir)
            
        except Exception as e:
            self.logger.error(f"خطأ في نسخ ملفات الوسائط: {e}")
            raise
    
    def _create_backup_info(self, backup_path: Path, backup_components: Dict[str, str]) -> str:
        """إنشاء ملف معلومات النسخة الاحتياطية"""
        backup_info = {
            'backup_name': backup_path.name,
            'created_at': datetime.now().isoformat(),
            'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            'system_info': {
                'platform': os.name,
                'base_dir': str(self.base_dir),
            },
            'components': backup_components,
            'installed_apps': list(settings.INSTALLED_APPS),
            'backup_size': self._calculate_backup_size(backup_path),
        }
        
        info_file = backup_path / 'backup_info.json'
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(backup_info, f, indent=2, ensure_ascii=False)
        
        return str(info_file)
    
    def _calculate_backup_size(self, backup_path: Path) -> int:
        """حساب حجم النسخة الاحتياطية"""
        total_size = 0
        for file_path in backup_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    def _compress_backup(self, backup_path: Path) -> str:
        """ضغط النسخة الاحتياطية"""
        self.logger.info("ضغط النسخة الاحتياطية...")
        
        zip_path = backup_path.with_suffix('.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(backup_path.parent)
                    zipf.write(file_path, arcname)
        
        # حذف المجلد غير المضغوط
        shutil.rmtree(backup_path)
        
        self.logger.info(f"تم ضغط النسخة الاحتياطية: {zip_path}")
        return str(zip_path)
    
    def list_backups(self) -> List[Dict[str, str]]:
        """عرض قائمة النسخ الاحتياطية المتاحة"""
        backups = []
        
        for backup_file in self.backup_dir.glob('*.zip'):
            backup_info = {
                'name': backup_file.stem,
                'file': str(backup_file),
                'size': backup_file.stat().st_size,
                'created': datetime.fromtimestamp(backup_file.stat().st_ctime).isoformat(),
            }
            backups.append(backup_info)
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def restore_backup(self, backup_file: str) -> bool:
        """استعادة نسخة احتياطية"""
        self.logger.info(f"بدء استعادة النسخة الاحتياطية: {backup_file}")
        
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                raise FileNotFoundError(f"ملف النسخة الاحتياطية غير موجود: {backup_file}")
            
            # استخراج النسخة الاحتياطية
            extract_dir = self.backup_dir / 'restore_temp'
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # قراءة معلومات النسخة الاحتياطية
            info_file = extract_dir / backup_path.stem / 'backup_info.json'
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    backup_info = json.load(f)
                self.logger.info(f"معلومات النسخة الاحتياطية: {backup_info['created_at']}")
            
            # يمكن إضافة منطق الاستعادة هنا
            self.logger.warning("وظيفة الاستعادة قيد التطوير")
            
            # تنظيف الملفات المؤقتة
            shutil.rmtree(extract_dir)
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في استعادة النسخة الاحتياطية: {e}")
            return False


class Command(BaseCommand):
    """أمر Django لإنشاء النسخ الاحتياطية"""
    
    help = 'إنشاء نسخة احتياطية شاملة من النظام'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            help='اسم النسخة الاحتياطية'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='عرض قائمة النسخ الاحتياطية المتاحة'
        )
        parser.add_argument(
            '--restore',
            type=str,
            help='استعادة نسخة احتياطية محددة'
        )
    
    def handle(self, *args, **options):
        backup_manager = SystemBackupManager()
        
        if options['list']:
            # عرض قائمة النسخ الاحتياطية
            backups = backup_manager.list_backups()
            
            if not backups:
                self.stdout.write("لا توجد نسخ احتياطية متاحة")
                return
            
            self.stdout.write("النسخ الاحتياطية المتاحة:")
            self.stdout.write("-" * 50)
            
            for backup in backups:
                size_mb = backup['size'] / (1024 * 1024)
                created = datetime.fromisoformat(backup['created']).strftime('%Y-%m-%d %H:%M:%S')
                self.stdout.write(f"  {backup['name']}")
                self.stdout.write(f"    الحجم: {size_mb:.2f} MB")
                self.stdout.write(f"    التاريخ: {created}")
                self.stdout.write("")
        
        elif options['restore']:
            # استعادة نسخة احتياطية
            backup_file = options['restore']
            self.stdout.write(f"استعادة النسخة الاحتياطية: {backup_file}")
            
            success = backup_manager.restore_backup(backup_file)
            if success:
                self.stdout.write(
                    self.style.SUCCESS("تم استعادة النسخة الاحتياطية بنجاح")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("فشل في استعادة النسخة الاحتياطية")
                )
        
        else:
            # إنشاء نسخة احتياطية جديدة
            backup_name = options.get('name')
            self.stdout.write("بدء إنشاء النسخة الاحتياطية...")
            
            try:
                backup_file = backup_manager.create_full_backup(backup_name)
                
                self.stdout.write(
                    self.style.SUCCESS(f"تم إنشاء النسخة الاحتياطية بنجاح: {backup_file}")
                )
                
                # عرض معلومات النسخة الاحتياطية
                backup_path = Path(backup_file)
                size_mb = backup_path.stat().st_size / (1024 * 1024)
                self.stdout.write(f"حجم النسخة الاحتياطية: {size_mb:.2f} MB")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"فشل في إنشاء النسخة الاحتياطية: {e}")
                )