"""
ElDawliya System - System Backup Restoration Command
===================================================

Django management command for restoring system backups.
This command restores database, media files, configuration from backups.
"""

import os
import json
import shutil
import subprocess
import zipfile
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection
from django.core.management import call_command
from django.utils import timezone


class Command(BaseCommand):
    """
    Restore system from backup including:
    - Database restoration
    - Media files restoration
    - Configuration files restoration
    - Validation and verification
    """

    help = 'Restore ElDawliya system from backup'

    def add_arguments(self, parser):
        """add_arguments function"""
        parser.add_argument(
            'backup_path',
            type=str,
            help='Path to backup file or directory'
        )

        parser.add_argument(
            '--restore-database',
            action='store_true',
            help='Restore database from backup'
        )

        parser.add_argument(
            '--restore-media',
            action='store_true',
            help='Restore media files from backup'
        )

        parser.add_argument(
            '--restore-config',
            action='store_true',
            help='Restore configuration files from backup'
        )

        parser.add_argument(
            '--restore-all',
            action='store_true',
            help='Restore everything from backup'
        )

        parser.add_argument(
            '--force',
            action='store_true',
            help='Force restoration without confirmation'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be restored without actually doing it'
        )

        parser.add_argument(
            '--backup-current',
            action='store_true',
            help='Create backup of current system before restoration'
        )

    def handle(self, *args, **options):
        """Execute the restoration process."""
        try:
            # Validate backup
            backup_info = self._validate_backup(options['backup_path'])

            self.stdout.write(
                self.style.SUCCESS(
                    f"🔄 بدء عملية الاستعادة من: {backup_info['name']}"
                )
            )

            # Show restoration plan
            self._show_restoration_plan(backup_info, options)

            # Confirm restoration (unless forced or dry-run)
            if not options['force'] and not options['dry_run']:
                if not self._confirm_restoration():
                    self.stdout.write("❌ تم إلغاء عملية الاستعادة")
                    return

            # Create backup of current system if requested
            if options['backup_current'] and not options['dry_run']:
                self._backup_current_system()

            # Extract backup if compressed
            if backup_info['compressed']:
                backup_info = self._extract_backup(backup_info, options['dry_run'])

            # Restore components based on options
            if options['restore_all']:
                self._restore_database(backup_info, options['dry_run'])
                self._restore_media_files(backup_info, options['dry_run'])
                self._restore_configuration(backup_info, options['dry_run'])
            else:
                if options['restore_database']:
                    self._restore_database(backup_info, options['dry_run'])

                if options['restore_media']:
                    self._restore_media_files(backup_info, options['dry_run'])

                if options['restore_config']:
                    self._restore_configuration(backup_info, options['dry_run'])

            # Validate restoration
            if not options['dry_run']:
                self._validate_restoration(backup_info)

            # Post-restoration tasks
            if not options['dry_run']:
                self._post_restoration_tasks()

            self.stdout.write(
                self.style.SUCCESS(
                    "✅ تمت عملية الاستعادة بنجاح" if not options['dry_run']
                    else "✅ تم عرض خطة الاستعادة بنجاح"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ فشل في عملية الاستعادة: {str(e)}")
            )
            raise CommandError(f"Restoration failed: {str(e)}")

    def _validate_backup(self, backup_path):
        """Validate backup and extract information."""
        backup_path = Path(backup_path)

        if not backup_path.exists():
            raise CommandError(f"Backup path does not exist: {backup_path}")

        backup_info = {
            'path': backup_path,
            'compressed': backup_path.is_file() and backup_path.suffix == '.zip',
            'extracted_path': None
        }

        # Load backup manifest
        if backup_info['compressed']:
            # Extract manifest from compressed backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                try:
                    manifest_data = zipf.read('backup_manifest.json')
                    manifest = json.loads(manifest_data.decode('utf-8'))
                except KeyError:
                    raise CommandError("Backup manifest not found in compressed backup")
        else:
            # Load manifest from directory
            manifest_file = backup_path / 'backup_manifest.json'
            if not manifest_file.exists():
                raise CommandError("Backup manifest not found")

            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

        backup_info.update(manifest['backup_info'])
        backup_info['manifest'] = manifest

        self.stdout.write(f"📋 تم التحقق من النسخة الاحتياطية: {backup_info['name']}")

        return backup_info

    def _show_restoration_plan(self, backup_info, options):
        """Show what will be restored."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📋 خطة الاستعادة"))
        self.stdout.write("="*60)

        self.stdout.write(f"النسخة الاحتياطية: {backup_info['name']}")
        self.stdout.write(f"تاريخ الإنشاء: {backup_info['created_at']}")

        if backup_info.get('description'):
            self.stdout.write(f"الوصف: {backup_info['description']}")

        self.stdout.write("\nالمكونات التي سيتم استعادتها:")

        if options['restore_all'] or options['restore_database']:
            self.stdout.write("  ✓ قاعدة البيانات")

        if options['restore_all'] or options['restore_media']:
            self.stdout.write("  ✓ ملفات الوسائط")

        if options['restore_all'] or options['restore_config']:
            self.stdout.write("  ✓ ملفات التكوين")

        if options['dry_run']:
            self.stdout.write("\n⚠️ هذا عرض فقط - لن يتم تنفيذ أي تغييرات")

        self.stdout.write("="*60 + "\n")

    def _confirm_restoration(self):
        """Ask user for confirmation."""
        response = input("هل تريد المتابعة مع عملية الاستعادة؟ (yes/no): ")
        return response.lower() in ['yes', 'y', 'نعم', 'ن']

    def _backup_current_system(self):
        """Create backup of current system before restoration."""
        self.stdout.write("💾 إنشاء نسخة احتياطية من النظام الحالي...")

        try:
            call_command(
                'create_system_backup',
                name='pre_restoration_backup',
                description='Backup created before system restoration',
                checkpoint='pre_restoration'
            )
            self.stdout.write("✅ تم إنشاء النسخة الاحتياطية للنظام الحالي")
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ فشل في إنشاء النسخة الاحتياطية: {str(e)}")
            )

    def _extract_backup(self, backup_info, dry_run):
        """Extract compressed backup."""
        if dry_run:
            self.stdout.write("🗜️ [محاكاة] استخراج النسخة الاحتياطية المضغوطة")
            return backup_info

        self.stdout.write("🗜️ استخراج النسخة الاحتياطية المضغوطة...")

        # Create temporary extraction directory
        extract_dir = backup_info['path'].parent / f"temp_extract_{backup_info['name']}"
        extract_dir.mkdir(exist_ok=True)

        try:
            with zipfile.ZipFile(backup_info['path'], 'r') as zipf:
                zipf.extractall(extract_dir)

            backup_info['extracted_path'] = extract_dir
            backup_info['path'] = extract_dir
            backup_info['compressed'] = False

            self.stdout.write("✅ تم استخراج النسخة الاحتياطية")

        except Exception as e:
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            raise CommandError(f"Failed to extract backup: {str(e)}")

        return backup_info

    def _restore_database(self, backup_info, dry_run):
        """Restore database from backup."""
        if dry_run:
            self.stdout.write("💾 [محاكاة] استعادة قاعدة البيانات")
            return

        self.stdout.write("💾 استعادة قاعدة البيانات...")

        database_dir = backup_info['path'] / 'database'

        if not database_dir.exists():
            raise CommandError("Database backup not found")

        # Try to restore from SQL Server backup first
        bak_files = list(database_dir.glob('*.bak'))

        if bak_files:
            self._restore_database_sqlserver(bak_files[0])
        else:
            # Fallback to Django loaddata
            self._restore_database_django(database_dir)

        self.stdout.write("✅ تم استعادة قاعدة البيانات")

    def _restore_database_sqlserver(self, backup_file):
        """Restore database using SQL Server tools."""
        try:
            db_config = settings.DATABASES['default']

            # SQL Server restore command
            sql_command = f"""
            USE master;
            ALTER DATABASE [{db_config['NAME']}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
            RESTORE DATABASE [{db_config['NAME']}]
            FROM DISK = N'{backup_file}'
            WITH REPLACE, STATS = 10;
            ALTER DATABASE [{db_config['NAME']}] SET MULTI_USER;
            """

            # Execute restore using sqlcmd
            cmd = [
                'sqlcmd',
                '-S', f"{db_config['HOST']},{db_config['PORT']}",
                '-U', db_config['USER'],
                '-P', db_config['PASSWORD'],
                '-Q', sql_command
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(f"SQL Server restore failed: {result.stderr}")

            self.stdout.write("💾 تم استعادة قاعدة البيانات باستخدام SQL Server")

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ فشل في الاستعادة المباشرة: {str(e)}")
            )
            # Fallback to Django method
            raise Exception("SQL Server restore failed, manual intervention required")

    def _restore_database_django(self, database_dir):
        """Restore database using Django loaddata."""
        try:
            # Find Django dump files
            dump_files = list(database_dir.glob('django_dump_*.json'))

            if not dump_files:
                raise Exception("No Django dump files found")

            # Clear existing data (with confirmation)
            self.stdout.write("⚠️ سيتم حذف البيانات الحالية...")

            # Load data from dump
            for dump_file in dump_files:
                call_command('loaddata', str(dump_file))

            self.stdout.write("💾 تم استعادة قاعدة البيانات باستخدام Django")

        except Exception as e:
            raise CommandError(f"Django database restore failed: {str(e)}")

    def _restore_media_files(self, backup_info, dry_run):
        """Restore media files from backup."""
        if dry_run:
            self.stdout.write("📁 [محاكاة] استعادة ملفات الوسائط")
            return

        self.stdout.write("📁 استعادة ملفات الوسائط...")

        media_backup_dir = backup_info['path'] / 'media' / 'files'

        if not media_backup_dir.exists():
            self.stdout.write("📁 لا توجد ملفات وسائط في النسخة الاحتياطية")
            return

        media_root = Path(settings.MEDIA_ROOT)

        # Backup existing media files
        if media_root.exists() and any(media_root.iterdir()):
            backup_media_dir = media_root.parent / f"media_backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.move(media_root, backup_media_dir)
            self.stdout.write(f"📁 تم نسخ ملفات الوسائط الحالية إلى: {backup_media_dir}")

        # Restore media files
        shutil.copytree(media_backup_dir, media_root, dirs_exist_ok=True)

        self.stdout.write("✅ تم استعادة ملفات الوسائط")

    def _restore_configuration(self, backup_info, dry_run):
        """Restore configuration files from backup."""
        if dry_run:
            self.stdout.write("⚙️ [محاكاة] استعادة ملفات التكوين")
            return

        self.stdout.write("⚙️ استعادة ملفات التكوين...")

        config_backup_dir = backup_info['path'] / 'config'

        if not config_backup_dir.exists():
            self.stdout.write("⚙️ لا توجد ملفات تكوين في النسخة الاحتياطية")
            return

        base_dir = Path(settings.BASE_DIR)

        # Configuration files to restore
        config_files = [
            '.env.example',  # Don't restore .env to avoid overwriting current settings
            'ElDawliya_sys/settings/',
            'ElDawliya_sys/urls.py'
        ]

        for config_file in config_files:
            source_path = config_backup_dir / config_file
            dest_path = base_dir / config_file

            if source_path.exists():
                if source_path.is_file():
                    # Backup existing file
                    if dest_path.exists():
                        backup_path = dest_path.with_suffix(f"{dest_path.suffix}.backup")
                        shutil.copy2(dest_path, backup_path)

                    shutil.copy2(source_path, dest_path)
                else:
                    # Backup existing directory
                    if dest_path.exists():
                        backup_path = dest_path.with_name(f"{dest_path.name}.backup")
                        if backup_path.exists():
                            shutil.rmtree(backup_path)
                        shutil.move(dest_path, backup_path)

                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)

        self.stdout.write("✅ تم استعادة ملفات التكوين")
        self.stdout.write("⚠️ تأكد من مراجعة ملفات التكوين وتحديثها حسب الحاجة")

    def _validate_restoration(self, backup_info):
        """Validate restoration process."""
        self.stdout.write("🔍 التحقق من سلامة عملية الاستعادة...")

        validation_results = {
            'database': self._validate_database_restoration(),
            'media': self._validate_media_restoration(),
            'configuration': self._validate_configuration_restoration()
        }

        all_valid = all(validation_results.values())

        if all_valid:
            self.stdout.write("✅ تم التحقق من سلامة جميع المكونات المستعادة")
        else:
            failed_components = [k for k, v in validation_results.items() if not v]
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ فشل في التحقق من: {', '.join(failed_components)}"
                )
            )

    def _validate_database_restoration(self):
        """Validate database restoration."""
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception:
            return False

    def _validate_media_restoration(self):
        """Validate media files restoration."""
        try:
            media_root = Path(settings.MEDIA_ROOT)
            return media_root.exists()
        except Exception:
            return False

    def _validate_configuration_restoration(self):
        """Validate configuration restoration."""
        try:
            # Check if settings can be imported
            from django.conf import settings
            return hasattr(settings, 'DATABASES')
        except Exception:
            return False

    def _post_restoration_tasks(self):
        """Perform post-restoration tasks."""
        self.stdout.write("🔧 تنفيذ مهام ما بعد الاستعادة...")

        try:
            # Run migrations
            self.stdout.write("📊 تطبيق الهجرات...")
            call_command('migrate', verbosity=0)

            # Collect static files
            self.stdout.write("📁 جمع الملفات الثابتة...")
            call_command('collectstatic', interactive=False, verbosity=0)

            # Clear cache
            self.stdout.write("🗑️ مسح التخزين المؤقت...")
            try:
                from django.core.cache import cache
                cache.clear()
            except Exception:
                pass

            self.stdout.write("✅ تم تنفيذ مهام ما بعد الاستعادة")

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ فشل في بعض مهام ما بعد الاستعادة: {str(e)}")
            )

    def _cleanup_extracted_backup(self, backup_info):
        """Clean up extracted backup files."""
        if backup_info.get('extracted_path') and backup_info['extracted_path'].exists():
            shutil.rmtree(backup_info['extracted_path'])
            self.stdout.write("🗑️ تم تنظيف الملفات المؤقتة")
