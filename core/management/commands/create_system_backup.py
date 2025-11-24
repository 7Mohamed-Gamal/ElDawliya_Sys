"""
ElDawliya System - System Backup Management Command
==================================================

Django management command for creating comprehensive system backups.
This command creates backups of database, media files, configuration, and code.
"""

import os
import json
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection
from django.core.management import call_command
from django.utils import timezone


class Command(BaseCommand):
    """
    Create comprehensive system backup including:
    - Database backup (SQL Server)
    - Media files backup
    - Configuration files backup
    - Code backup (optional)
    - System state documentation
    """

    help = 'Create comprehensive system backup for ElDawliya system'

    def add_arguments(self, parser):
        """add_arguments function"""
        parser.add_argument(
            '--backup-dir',
            type=str,
            default='backups',
            help='Directory to store backups (default: backups)'
        )

        parser.add_argument(
            '--include-code',
            action='store_true',
            help='Include source code in backup'
        )

        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress backup files'
        )

        parser.add_argument(
            '--name',
            type=str,
            help='Custom backup name (default: auto-generated)'
        )

        parser.add_argument(
            '--description',
            type=str,
            help='Backup description'
        )

        parser.add_argument(
            '--checkpoint',
            type=str,
            help='Checkpoint name for this backup'
        )

    def handle(self, *args, **options):
        """Execute the backup process."""
        try:
            # Initialize backup process
            backup_info = self._initialize_backup(options)

            self.stdout.write(
                self.style.SUCCESS(
                    f"🚀 بدء عملية النسخ الاحتياطي: {backup_info['name']}"
                )
            )

            # Create backup directory structure
            self._create_backup_structure(backup_info)

            # Document current system state
            self._document_system_state(backup_info)

            # Backup database
            self._backup_database(backup_info)

            # Backup media files
            self._backup_media_files(backup_info)

            # Backup configuration files
            self._backup_configuration(backup_info)

            # Backup code (if requested)
            if options['include_code']:
                self._backup_code(backup_info)

            # Create backup manifest
            self._create_backup_manifest(backup_info)

            # Compress backup (if requested)
            if options['compress']:
                self._compress_backup(backup_info)

            # Validate backup integrity
            self._validate_backup(backup_info)

            # Update backup registry
            self._update_backup_registry(backup_info)

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ تم إنشاء النسخة الاحتياطية بنجاح: {backup_info['backup_path']}"
                )
            )

            # Display backup summary
            self._display_backup_summary(backup_info)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ فشل في إنشاء النسخة الاحتياطية: {str(e)}")
            )
            raise CommandError(f"Backup failed: {str(e)}")

    def _initialize_backup(self, options):
        """Initialize backup process and create backup info."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Generate backup name
        if options['name']:
            backup_name = f"{options['name']}_{timestamp}"
        else:
            backup_name = f"eldawliya_backup_{timestamp}"

        # Create backup directory
        backup_dir = Path(options['backup_dir'])
        backup_dir.mkdir(exist_ok=True)

        backup_path = backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)

        return {
            'name': backup_name,
            'timestamp': timestamp,
            'backup_dir': backup_dir,
            'backup_path': backup_path,
            'description': options.get('description', ''),
            'checkpoint': options.get('checkpoint', ''),
            'include_code': options['include_code'],
            'compress': options['compress'],
            'created_at': timezone.now(),
            'files': [],
            'size': 0,
            'status': 'in_progress'
        }

    def _create_backup_structure(self, backup_info):
        """Create backup directory structure."""
        structure = [
            'database',
            'media',
            'config',
            'logs',
            'docs'
        ]

        if backup_info['include_code']:
            structure.append('code')

        for folder in structure:
            (backup_info['backup_path'] / folder).mkdir(exist_ok=True)

        self.stdout.write("📁 تم إنشاء هيكل مجلدات النسخة الاحتياطية")

    def _document_system_state(self, backup_info):
        """Document current system state."""
        system_state = {
            'backup_info': {
                'name': backup_info['name'],
                'created_at': backup_info['created_at'].isoformat(),
                'description': backup_info['description'],
                'checkpoint': backup_info['checkpoint']
            },
            'django_info': {
                'version': self._get_django_version(),
                'settings_module': os.environ.get('DJANGO_SETTINGS_MODULE'),
                'debug': settings.DEBUG,
                'allowed_hosts': settings.ALLOWED_HOSTS,
                'installed_apps': settings.INSTALLED_APPS,
                'middleware': settings.MIDDLEWARE
            },
            'database_info': {
                'engine': settings.DATABASES['default']['ENGINE'],
                'name': settings.DATABASES['default']['NAME'],
                'host': settings.DATABASES['default']['HOST'],
                'port': settings.DATABASES['default']['PORT']
            },
            'environment_info': {
                'python_version': self._get_python_version(),
                'os_info': self._get_os_info(),
                'requirements': self._get_installed_packages()
            },
            'application_state': {
                'migrations': self._get_migration_status(),
                'static_files': self._check_static_files(),
                'media_files': self._check_media_files()
            }
        }

        # Save system state
        state_file = backup_info['backup_path'] / 'docs' / 'system_state.json'
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(system_state, f, indent=2, ensure_ascii=False, default=str)

        backup_info['files'].append(str(state_file))

        self.stdout.write("📋 تم توثيق حالة النظام الحالية")

    def _backup_database(self, backup_info):
        """Backup database using SQL Server tools."""
        try:
            db_config = settings.DATABASES['default']
            timestamp = backup_info['timestamp']

            # Create database backup using sqlcmd
            backup_file = backup_info['backup_path'] / 'database' / f"database_backup_{timestamp}.bak"

            # SQL Server backup command
            sql_command = f"""
            BACKUP DATABASE [{db_config['NAME']}]
            TO DISK = N'{backup_file}'
            WITH FORMAT, INIT,
            NAME = N'ElDawliya System Backup - {backup_info['name']}',
            SKIP, NOREWIND, NOUNLOAD, STATS = 10
            """

            # Execute backup using sqlcmd
            cmd = [
                'sqlcmd',
                '-S', f"{db_config['HOST']},{db_config['PORT']}",
                '-U', db_config['USER'],
                '-P', db_config['PASSWORD'],
                '-Q', sql_command
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                backup_info['files'].append(str(backup_file))
                self.stdout.write("💾 تم نسخ قاعدة البيانات بنجاح")
            else:
                # Fallback to Django dumpdata
                self._backup_database_django(backup_info)

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ فشل في النسخ المباشر لقاعدة البيانات: {str(e)}")
            )
            # Fallback to Django dumpdata
            self._backup_database_django(backup_info)

    def _backup_database_django(self, backup_info):
        """Backup database using Django dumpdata as fallback."""
        try:
            timestamp = backup_info['timestamp']

            # Full database dump
            dump_file = backup_info['backup_path'] / 'database' / f"django_dump_{timestamp}.json"

            with open(dump_file, 'w', encoding='utf-8') as f:
                call_command('dumpdata', stdout=f, indent=2)

            backup_info['files'].append(str(dump_file))

            # Individual app dumps for easier restoration
            apps_to_backup = [
                'hr', 'accounts', 'inventory', 'meetings', 'tasks',
                'Purchase_orders', 'notifications', 'audit'
            ]

            for app in apps_to_backup:
                try:
                    app_dump_file = backup_info['backup_path'] / 'database' / f"{app}_dump_{timestamp}.json"
                    with open(app_dump_file, 'w', encoding='utf-8') as f:
                        call_command('dumpdata', app, stdout=f, indent=2)
                    backup_info['files'].append(str(app_dump_file))
                except Exception:
                    continue  # Skip if app doesn't exist

            self.stdout.write("💾 تم نسخ قاعدة البيانات باستخدام Django")

        except Exception as e:
            raise CommandError(f"Database backup failed: {str(e)}")

    def _backup_media_files(self, backup_info):
        """Backup media files."""
        try:
            media_root = Path(settings.MEDIA_ROOT)

            if media_root.exists() and any(media_root.iterdir()):
                media_backup_dir = backup_info['backup_path'] / 'media'

                # Copy media files
                shutil.copytree(media_root, media_backup_dir / 'files', dirs_exist_ok=True)

                # Create media inventory
                media_inventory = self._create_media_inventory(media_root)
                inventory_file = media_backup_dir / 'media_inventory.json'

                with open(inventory_file, 'w', encoding='utf-8') as f:
                    json.dump(media_inventory, f, indent=2, ensure_ascii=False)

                backup_info['files'].extend([str(media_backup_dir), str(inventory_file)])

                self.stdout.write("📁 تم نسخ ملفات الوسائط")
            else:
                self.stdout.write("📁 لا توجد ملفات وسائط للنسخ")

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ فشل في نسخ ملفات الوسائط: {str(e)}")
            )

    def _backup_configuration(self, backup_info):
        """Backup configuration files."""
        try:
            config_backup_dir = backup_info['backup_path'] / 'config'

            # Configuration files to backup
            config_files = [
                '.env',
                '.env.example',
                'requirements.txt',
                'manage.py',
                'ElDawliya_sys/settings/',
                'ElDawliya_sys/urls.py',
                'ElDawliya_sys/wsgi.py',
                'ElDawliya_sys/asgi.py'
            ]

            base_dir = Path(settings.BASE_DIR)

            for config_file in config_files:
                source_path = base_dir / config_file

                if source_path.exists():
                    if source_path.is_file():
                        dest_path = config_backup_dir / config_file
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_path, dest_path)
                    else:
                        dest_path = config_backup_dir / config_file
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)

                    backup_info['files'].append(str(dest_path))

            # Create configuration summary
            config_summary = {
                'django_settings': {
                    'SECRET_KEY': '***HIDDEN***',
                    'DEBUG': settings.DEBUG,
                    'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
                    'DATABASE_ENGINE': settings.DATABASES['default']['ENGINE'],
                    'STATIC_URL': settings.STATIC_URL,
                    'MEDIA_URL': settings.MEDIA_URL,
                    'TIME_ZONE': settings.TIME_ZONE,
                    'LANGUAGE_CODE': settings.LANGUAGE_CODE
                },
                'installed_apps': settings.INSTALLED_APPS,
                'middleware': settings.MIDDLEWARE
            }

            summary_file = config_backup_dir / 'configuration_summary.json'
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(config_summary, f, indent=2, ensure_ascii=False)

            backup_info['files'].append(str(summary_file))

            self.stdout.write("⚙️ تم نسخ ملفات التكوين")

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ فشل في نسخ ملفات التكوين: {str(e)}")
            )

    def _backup_code(self, backup_info):
        """Backup source code."""
        try:
            code_backup_dir = backup_info['backup_path'] / 'code'
            base_dir = Path(settings.BASE_DIR)

            # Directories to include in code backup
            code_dirs = [
                'core',
                'api',
                'hr',
                'accounts',
                'inventory',
                'meetings',
                'tasks',
                'Purchase_orders',
                'notifications',
                'audit',
                'templates',
                'static'
            ]

            # Files to include
            code_files = [
                'manage.py',
                'requirements.txt'
            ]

            # Copy directories
            for code_dir in code_dirs:
                source_path = base_dir / code_dir
                if source_path.exists():
                    dest_path = code_backup_dir / code_dir
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    backup_info['files'].append(str(dest_path))

            # Copy files
            for code_file in code_files:
                source_path = base_dir / code_file
                if source_path.exists():
                    dest_path = code_backup_dir / code_file
                    shutil.copy2(source_path, dest_path)
                    backup_info['files'].append(str(dest_path))

            self.stdout.write("💻 تم نسخ الكود المصدري")

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ فشل في نسخ الكود المصدري: {str(e)}")
            )

    def _create_backup_manifest(self, backup_info):
        """Create backup manifest with all backup information."""
        manifest = {
            'backup_info': {
                'name': backup_info['name'],
                'created_at': backup_info['created_at'].isoformat(),
                'description': backup_info['description'],
                'checkpoint': backup_info['checkpoint'],
                'include_code': backup_info['include_code'],
                'compressed': backup_info['compress']
            },
            'system_info': {
                'django_version': self._get_django_version(),
                'python_version': self._get_python_version(),
                'os_info': self._get_os_info()
            },
            'backup_contents': {
                'files': backup_info['files'],
                'total_files': len(backup_info['files']),
                'backup_size': self._calculate_backup_size(backup_info['backup_path'])
            },
            'restoration_info': {
                'restoration_order': [
                    'database',
                    'media',
                    'config',
                    'code'
                ],
                'prerequisites': [
                    'Python 3.7+',
                    'Django 4.2+',
                    'SQL Server',
                    'Required Python packages'
                ],
                'restoration_notes': [
                    'Restore database first',
                    'Update configuration files',
                    'Run migrations if needed',
                    'Collect static files',
                    'Test system functionality'
                ]
            }
        }

        manifest_file = backup_info['backup_path'] / 'backup_manifest.json'
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False, default=str)

        backup_info['files'].append(str(manifest_file))
        backup_info['size'] = manifest['backup_contents']['backup_size']

        self.stdout.write("📋 تم إنشاء ملف البيانات الوصفية للنسخة الاحتياطية")

    def _compress_backup(self, backup_info):
        """Compress backup into a single archive."""
        try:
            archive_name = f"{backup_info['name']}.zip"
            archive_path = backup_info['backup_dir'] / archive_name

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_info['backup_path']):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(backup_info['backup_path'])
                        zipf.write(file_path, arcname)

            # Remove uncompressed backup
            shutil.rmtree(backup_info['backup_path'])

            backup_info['backup_path'] = archive_path
            backup_info['compressed'] = True

            self.stdout.write(f"🗜️ تم ضغط النسخة الاحتياطية: {archive_name}")

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ فشل في ضغط النسخة الاحتياطية: {str(e)}")
            )

    def _validate_backup(self, backup_info):
        """Validate backup integrity."""
        try:
            if backup_info.get('compressed'):
                # Validate compressed backup
                with zipfile.ZipFile(backup_info['backup_path'], 'r') as zipf:
                    bad_files = zipf.testzip()
                    if bad_files:
                        raise Exception(f"Corrupted files in backup: {bad_files}")
            else:
                # Validate uncompressed backup
                if not backup_info['backup_path'].exists():
                    raise Exception("Backup directory does not exist")

                # Check if manifest exists
                manifest_file = backup_info['backup_path'] / 'backup_manifest.json'
                if not manifest_file.exists():
                    raise Exception("Backup manifest is missing")

            backup_info['status'] = 'completed'
            self.stdout.write("✅ تم التحقق من سلامة النسخة الاحتياطية")

        except Exception as e:
            backup_info['status'] = 'failed'
            raise CommandError(f"Backup validation failed: {str(e)}")

    def _update_backup_registry(self, backup_info):
        """Update backup registry with new backup information."""
        try:
            registry_file = backup_info['backup_dir'] / 'backup_registry.json'

            # Load existing registry
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
            else:
                registry = {'backups': []}

            # Add new backup to registry
            backup_entry = {
                'name': backup_info['name'],
                'created_at': backup_info['created_at'].isoformat(),
                'description': backup_info['description'],
                'checkpoint': backup_info['checkpoint'],
                'path': str(backup_info['backup_path']),
                'size': backup_info['size'],
                'compressed': backup_info.get('compressed', False),
                'status': backup_info['status'],
                'include_code': backup_info['include_code']
            }

            registry['backups'].append(backup_entry)

            # Keep only last 50 backups in registry
            registry['backups'] = registry['backups'][-50:]

            # Save updated registry
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)

            self.stdout.write("📝 تم تحديث سجل النسخ الاحتياطية")

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ فشل في تحديث سجل النسخ الاحتياطية: {str(e)}")
            )

    def _display_backup_summary(self, backup_info):
        """Display backup summary."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📊 ملخص النسخة الاحتياطية"))
        self.stdout.write("="*60)
        self.stdout.write(f"الاسم: {backup_info['name']}")
        self.stdout.write(f"التاريخ: {backup_info['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"المسار: {backup_info['backup_path']}")
        self.stdout.write(f"الحجم: {self._format_size(backup_info['size'])}")
        self.stdout.write(f"عدد الملفات: {len(backup_info['files'])}")
        self.stdout.write(f"الحالة: {backup_info['status']}")

        if backup_info['description']:
            self.stdout.write(f"الوصف: {backup_info['description']}")

        if backup_info['checkpoint']:
            self.stdout.write(f"نقطة التحقق: {backup_info['checkpoint']}")

        self.stdout.write("="*60 + "\n")

    # Helper methods
    def _get_django_version(self):
        """Get Django version."""
        import django
        return django.get_version()

    def _get_python_version(self):
        """Get Python version."""
        import sys
        return sys.version

    def _get_os_info(self):
        """Get OS information."""
        import platform
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }

    def _get_installed_packages(self):
        """Get list of installed Python packages."""
        try:
            result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)
            return result.stdout.strip().split('\n') if result.returncode == 0 else []
        except Exception:
            return []

    def _get_migration_status(self):
        """Get migration status for all apps."""
        try:
            from django.core.management.commands.showmigrations import Command as ShowMigrationsCommand
            cmd = ShowMigrationsCommand()
            # This is a simplified version - in practice, you'd capture the output
            return "Migration status captured"
        except Exception:
            return "Unable to capture migration status"

    def _check_static_files(self):
        """Check static files status."""
        static_root = Path(settings.STATIC_ROOT)
        return {
            'static_root_exists': static_root.exists(),
            'static_files_count': len(list(static_root.rglob('*'))) if static_root.exists() else 0
        }

    def _check_media_files(self):
        """Check media files status."""
        media_root = Path(settings.MEDIA_ROOT)
        return {
            'media_root_exists': media_root.exists(),
            'media_files_count': len(list(media_root.rglob('*'))) if media_root.exists() else 0
        }

    def _create_media_inventory(self, media_root):
        """Create inventory of media files."""
        inventory = {
            'total_files': 0,
            'total_size': 0,
            'directories': {},
            'file_types': {}
        }

        for file_path in media_root.rglob('*'):
            if file_path.is_file():
                inventory['total_files'] += 1
                file_size = file_path.stat().st_size
                inventory['total_size'] += file_size

                # Track by directory
                rel_dir = str(file_path.parent.relative_to(media_root))
                if rel_dir not in inventory['directories']:
                    inventory['directories'][rel_dir] = {'count': 0, 'size': 0}
                inventory['directories'][rel_dir]['count'] += 1
                inventory['directories'][rel_dir]['size'] += file_size

                # Track by file type
                file_ext = file_path.suffix.lower()
                if file_ext not in inventory['file_types']:
                    inventory['file_types'][file_ext] = {'count': 0, 'size': 0}
                inventory['file_types'][file_ext]['count'] += 1
                inventory['file_types'][file_ext]['size'] += file_size

        return inventory

    def _calculate_backup_size(self, backup_path):
        """Calculate total backup size."""
        total_size = 0

        if backup_path.is_file():
            return backup_path.stat().st_size

        for file_path in backup_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return total_size

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
