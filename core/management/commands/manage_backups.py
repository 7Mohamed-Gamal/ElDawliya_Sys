"""
ElDawliya System - Backup Management Command
===========================================

Django management command for managing system backups.
This command provides utilities to list, validate, and clean up backups.
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    """
    Manage system backups:
    - List available backups
    - Validate backup integrity
    - Clean up old backups
    - Show backup details
    """
    
    help = 'Manage ElDawliya system backups'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['list', 'validate', 'cleanup', 'details', 'delete'],
            help='Action to perform'
        )
        
        parser.add_argument(
            '--backup-dir',
            type=str,
            default='backups',
            help='Directory containing backups (default: backups)'
        )
        
        parser.add_argument(
            '--backup-name',
            type=str,
            help='Specific backup name for details/delete actions'
        )
        
        parser.add_argument(
            '--older-than',
            type=int,
            help='Clean up backups older than N days'
        )
        
        parser.add_argument(
            '--keep-count',
            type=int,
            default=10,
            help='Number of recent backups to keep during cleanup (default: 10)'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force action without confirmation'
        )
    
    def handle(self, *args, **options):
        """Execute the backup management action."""
        try:
            backup_dir = Path(options['backup_dir'])
            
            if not backup_dir.exists():
                raise CommandError(f"Backup directory does not exist: {backup_dir}")
            
            action = options['action']
            
            if action == 'list':
                self._list_backups(backup_dir)
            elif action == 'validate':
                self._validate_backups(backup_dir, options.get('backup_name'))
            elif action == 'cleanup':
                self._cleanup_backups(backup_dir, options)
            elif action == 'details':
                self._show_backup_details(backup_dir, options['backup_name'])
            elif action == 'delete':
                self._delete_backup(backup_dir, options['backup_name'], options['force'])
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ فشل في إدارة النسخ الاحتياطية: {str(e)}")
            )
            raise CommandError(f"Backup management failed: {str(e)}")
    
    def _list_backups(self, backup_dir):
        """List all available backups."""
        self.stdout.write(self.style.SUCCESS("📋 قائمة النسخ الاحتياطية المتاحة"))
        self.stdout.write("="*80)
        
        registry = self._load_backup_registry(backup_dir)
        
        if not registry or not registry.get('backups'):
            self.stdout.write("لا توجد نسخ احتياطية مسجلة")
            return
        
        # Sort backups by creation date (newest first)
        backups = sorted(
            registry['backups'],
            key=lambda x: x['created_at'],
            reverse=True
        )
        
        # Display table header
        self.stdout.write(
            f"{'الاسم':<30} {'التاريخ':<20} {'الحجم':<10} {'الحالة':<10} {'الوصف':<30}"
        )
        self.stdout.write("-"*80)
        
        for backup in backups:
            name = backup['name'][:28] + '..' if len(backup['name']) > 30 else backup['name']
            created_at = backup['created_at'][:19]  # Remove microseconds
            size = self._format_size(backup.get('size', 0))
            status = backup.get('status', 'unknown')
            description = backup.get('description', '')[:28] + '..' if len(backup.get('description', '')) > 30 else backup.get('description', '')
            
            # Color code status
            if status == 'completed':
                status_colored = self.style.SUCCESS(status)
            elif status == 'failed':
                status_colored = self.style.ERROR(status)
            else:
                status_colored = self.style.WARNING(status)
            
            self.stdout.write(
                f"{name:<30} {created_at:<20} {size:<10} {status_colored:<10} {description:<30}"
            )
        
        self.stdout.write("-"*80)
        self.stdout.write(f"إجمالي النسخ الاحتياطية: {len(backups)}")
    
    def _validate_backups(self, backup_dir, backup_name=None):
        """Validate backup integrity."""
        if backup_name:
            self.stdout.write(f"🔍 التحقق من النسخة الاحتياطية: {backup_name}")
            self._validate_single_backup(backup_dir, backup_name)
        else:
            self.stdout.write("🔍 التحقق من جميع النسخ الاحتياطية")
            self._validate_all_backups(backup_dir)
    
    def _validate_single_backup(self, backup_dir, backup_name):
        """Validate a single backup."""
        registry = self._load_backup_registry(backup_dir)
        
        if not registry:
            raise CommandError("Backup registry not found")
        
        backup_info = None
        for backup in registry.get('backups', []):
            if backup['name'] == backup_name:
                backup_info = backup
                break
        
        if not backup_info:
            raise CommandError(f"Backup not found: {backup_name}")
        
        backup_path = Path(backup_info['path'])
        
        if not backup_path.exists():
            self.stdout.write(
                self.style.ERROR(f"❌ ملف النسخة الاحتياطية غير موجود: {backup_path}")
            )
            return False
        
        # Validate based on backup type
        if backup_info.get('compressed', False):
            return self._validate_compressed_backup(backup_path)
        else:
            return self._validate_directory_backup(backup_path)
    
    def _validate_all_backups(self, backup_dir):
        """Validate all backups."""
        registry = self._load_backup_registry(backup_dir)
        
        if not registry or not registry.get('backups'):
            self.stdout.write("لا توجد نسخ احتياطية للتحقق منها")
            return
        
        valid_count = 0
        invalid_count = 0
        
        for backup in registry['backups']:
            backup_name = backup['name']
            
            try:
                if self._validate_single_backup(backup_dir, backup_name):
                    self.stdout.write(f"✅ {backup_name}: صالحة")
                    valid_count += 1
                else:
                    self.stdout.write(f"❌ {backup_name}: تالفة")
                    invalid_count += 1
            except Exception as e:
                self.stdout.write(f"❌ {backup_name}: خطأ - {str(e)}")
                invalid_count += 1
        
        self.stdout.write("-"*50)
        self.stdout.write(f"النسخ الصالحة: {valid_count}")
        self.stdout.write(f"النسخ التالفة: {invalid_count}")
    
    def _validate_compressed_backup(self, backup_path):
        """Validate compressed backup."""
        try:
            import zipfile
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Test zip integrity
                bad_files = zipf.testzip()
                if bad_files:
                    self.stdout.write(f"❌ ملفات تالفة: {bad_files}")
                    return False
                
                # Check for required files
                required_files = ['backup_manifest.json']
                file_list = zipf.namelist()
                
                for required_file in required_files:
                    if required_file not in file_list:
                        self.stdout.write(f"❌ ملف مطلوب مفقود: {required_file}")
                        return False
                
                return True
                
        except Exception as e:
            self.stdout.write(f"❌ خطأ في التحقق من الملف المضغوط: {str(e)}")
            return False
    
    def _validate_directory_backup(self, backup_path):
        """Validate directory backup."""
        try:
            # Check if manifest exists
            manifest_file = backup_path / 'backup_manifest.json'
            if not manifest_file.exists():
                self.stdout.write("❌ ملف البيانات الوصفية مفقود")
                return False
            
            # Load and validate manifest
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Check required directories
            required_dirs = ['database', 'config', 'docs']
            for req_dir in required_dirs:
                dir_path = backup_path / req_dir
                if not dir_path.exists():
                    self.stdout.write(f"❌ مجلد مطلوب مفقود: {req_dir}")
                    return False
            
            return True
            
        except Exception as e:
            self.stdout.write(f"❌ خطأ في التحقق من مجلد النسخة الاحتياطية: {str(e)}")
            return False
    
    def _cleanup_backups(self, backup_dir, options):
        """Clean up old backups."""
        registry = self._load_backup_registry(backup_dir)
        
        if not registry or not registry.get('backups'):
            self.stdout.write("لا توجد نسخ احتياطية للتنظيف")
            return
        
        backups = registry['backups']
        backups_to_delete = []
        
        # Sort backups by creation date (oldest first)
        sorted_backups = sorted(backups, key=lambda x: x['created_at'])
        
        # Apply cleanup criteria
        if options.get('older_than'):
            cutoff_date = timezone.now() - timedelta(days=options['older_than'])
            
            for backup in sorted_backups:
                backup_date = datetime.fromisoformat(backup['created_at'].replace('Z', '+00:00'))
                if backup_date < cutoff_date:
                    backups_to_delete.append(backup)
        
        # Keep only specified number of recent backups
        keep_count = options['keep_count']
        if len(sorted_backups) > keep_count:
            backups_to_delete.extend(sorted_backups[:-keep_count])
        
        # Remove duplicates
        backups_to_delete = list({backup['name']: backup for backup in backups_to_delete}.values())
        
        if not backups_to_delete:
            self.stdout.write("لا توجد نسخ احتياطية تحتاج للحذف")
            return
        
        # Show cleanup plan
        self.stdout.write(f"🗑️ سيتم حذف {len(backups_to_delete)} نسخة احتياطية:")
        for backup in backups_to_delete:
            self.stdout.write(f"  - {backup['name']} ({backup['created_at']})")
        
        # Confirm deletion
        if not options['force']:
            response = input("\nهل تريد المتابعة؟ (yes/no): ")
            if response.lower() not in ['yes', 'y', 'نعم', 'ن']:
                self.stdout.write("تم إلغاء عملية التنظيف")
                return
        
        # Delete backups
        deleted_count = 0
        for backup in backups_to_delete:
            try:
                backup_path = Path(backup['path'])
                if backup_path.exists():
                    if backup_path.is_file():
                        backup_path.unlink()
                    else:
                        shutil.rmtree(backup_path)
                    deleted_count += 1
                    self.stdout.write(f"✅ تم حذف: {backup['name']}")
                
                # Remove from registry
                registry['backups'] = [b for b in registry['backups'] if b['name'] != backup['name']]
                
            except Exception as e:
                self.stdout.write(f"❌ فشل في حذف {backup['name']}: {str(e)}")
        
        # Update registry
        self._save_backup_registry(backup_dir, registry)
        
        self.stdout.write(f"🗑️ تم حذف {deleted_count} نسخة احتياطية")
    
    def _show_backup_details(self, backup_dir, backup_name):
        """Show detailed information about a backup."""
        if not backup_name:
            raise CommandError("Backup name is required for details action")
        
        registry = self._load_backup_registry(backup_dir)
        
        if not registry:
            raise CommandError("Backup registry not found")
        
        backup_info = None
        for backup in registry.get('backups', []):
            if backup['name'] == backup_name:
                backup_info = backup
                break
        
        if not backup_info:
            raise CommandError(f"Backup not found: {backup_name}")
        
        # Load detailed information from manifest
        backup_path = Path(backup_info['path'])
        
        try:
            if backup_info.get('compressed', False):
                # Extract manifest from compressed backup
                import zipfile
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    manifest_data = zipf.read('backup_manifest.json')
                    manifest = json.loads(manifest_data.decode('utf-8'))
            else:
                # Load manifest from directory
                manifest_file = backup_path / 'backup_manifest.json'
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
            
            # Display detailed information
            self._display_backup_details(backup_info, manifest)
            
        except Exception as e:
            self.stdout.write(f"❌ فشل في تحميل تفاصيل النسخة الاحتياطية: {str(e)}")
    
    def _display_backup_details(self, backup_info, manifest):
        """Display detailed backup information."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"📋 تفاصيل النسخة الاحتياطية: {backup_info['name']}"))
        self.stdout.write("="*60)
        
        # Basic information
        self.stdout.write("المعلومات الأساسية:")
        self.stdout.write(f"  الاسم: {backup_info['name']}")
        self.stdout.write(f"  تاريخ الإنشاء: {backup_info['created_at']}")
        self.stdout.write(f"  الحجم: {self._format_size(backup_info.get('size', 0))}")
        self.stdout.write(f"  الحالة: {backup_info.get('status', 'unknown')}")
        self.stdout.write(f"  مضغوط: {'نعم' if backup_info.get('compressed', False) else 'لا'}")
        self.stdout.write(f"  المسار: {backup_info['path']}")
        
        if backup_info.get('description'):
            self.stdout.write(f"  الوصف: {backup_info['description']}")
        
        if backup_info.get('checkpoint'):
            self.stdout.write(f"  نقطة التحقق: {backup_info['checkpoint']}")
        
        # System information
        if 'system_info' in manifest:
            system_info = manifest['system_info']
            self.stdout.write("\nمعلومات النظام:")
            self.stdout.write(f"  إصدار Django: {system_info.get('django_version', 'غير معروف')}")
            self.stdout.write(f"  إصدار Python: {system_info.get('python_version', 'غير معروف')}")
        
        # Backup contents
        if 'backup_contents' in manifest:
            contents = manifest['backup_contents']
            self.stdout.write("\nمحتويات النسخة الاحتياطية:")
            self.stdout.write(f"  عدد الملفات: {contents.get('total_files', 0)}")
            self.stdout.write(f"  الحجم الإجمالي: {self._format_size(contents.get('backup_size', 0))}")
        
        # Restoration information
        if 'restoration_info' in manifest:
            restoration = manifest['restoration_info']
            self.stdout.write("\nمعلومات الاستعادة:")
            self.stdout.write("  ترتيب الاستعادة:")
            for step in restoration.get('restoration_order', []):
                self.stdout.write(f"    - {step}")
            
            self.stdout.write("  المتطلبات المسبقة:")
            for req in restoration.get('prerequisites', []):
                self.stdout.write(f"    - {req}")
        
        self.stdout.write("="*60 + "\n")
    
    def _delete_backup(self, backup_dir, backup_name, force):
        """Delete a specific backup."""
        if not backup_name:
            raise CommandError("Backup name is required for delete action")
        
        registry = self._load_backup_registry(backup_dir)
        
        if not registry:
            raise CommandError("Backup registry not found")
        
        backup_info = None
        for backup in registry.get('backups', []):
            if backup['name'] == backup_name:
                backup_info = backup
                break
        
        if not backup_info:
            raise CommandError(f"Backup not found: {backup_name}")
        
        # Confirm deletion
        if not force:
            self.stdout.write(f"⚠️ سيتم حذف النسخة الاحتياطية: {backup_name}")
            self.stdout.write(f"المسار: {backup_info['path']}")
            response = input("هل تريد المتابعة؟ (yes/no): ")
            if response.lower() not in ['yes', 'y', 'نعم', 'ن']:
                self.stdout.write("تم إلغاء عملية الحذف")
                return
        
        # Delete backup
        try:
            backup_path = Path(backup_info['path'])
            if backup_path.exists():
                if backup_path.is_file():
                    backup_path.unlink()
                else:
                    shutil.rmtree(backup_path)
                
                self.stdout.write(f"✅ تم حذف النسخة الاحتياطية: {backup_name}")
            else:
                self.stdout.write(f"⚠️ ملف النسخة الاحتياطية غير موجود: {backup_path}")
            
            # Remove from registry
            registry['backups'] = [b for b in registry['backups'] if b['name'] != backup_name]
            self._save_backup_registry(backup_dir, registry)
            
        except Exception as e:
            raise CommandError(f"Failed to delete backup: {str(e)}")
    
    def _load_backup_registry(self, backup_dir):
        """Load backup registry."""
        registry_file = backup_dir / 'backup_registry.json'
        
        if not registry_file.exists():
            return None
        
        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _save_backup_registry(self, backup_dir, registry):
        """Save backup registry."""
        registry_file = backup_dir / 'backup_registry.json'
        
        try:
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.stdout.write(f"⚠️ فشل في حفظ سجل النسخ الاحتياطية: {str(e)}")
    
    def _format_size(self, size_bytes):
        """Format size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"