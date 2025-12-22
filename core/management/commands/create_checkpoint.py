"""
ElDawliya System - Checkpoint Management Command
===============================================

Django management command for creating and managing system checkpoints.
Checkpoints are special backups created at important stages of development.
"""

import json
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.utils import timezone


class Command(BaseCommand):
    """
    Create and manage system checkpoints for safe development progression.
    Checkpoints are named backups created at important development stages.
    """

    help = 'Create system checkpoint for ElDawliya system'

    # Predefined checkpoint stages
    CHECKPOINT_STAGES = {
        'initial': {
            'name': 'النقطة الأولية',
            'description': 'حالة النظام قبل بدء أي تغييرات',
            'order': 1
        },
        'file_cleanup': {
            'name': 'تنظيف الملفات',
            'description': 'بعد تنظيف الملفات غير المرغوبة والمكررة',
            'order': 2
        },
        'structure_reorganization': {
            'name': 'إعادة تنظيم الهيكل',
            'description': 'بعد إعادة تنظيم هيكل المشروع والمجلدات',
            'order': 3
        },
        'database_restructure': {
            'name': 'إعادة هيكلة قاعدة البيانات',
            'description': 'بعد تحديث نماذج قاعدة البيانات والهجرات',
            'order': 4
        },
        'services_development': {
            'name': 'تطوير الخدمات',
            'description': 'بعد تطوير طبقة الخدمات والمنطق التجاري',
            'order': 5
        },
        'api_development': {
            'name': 'تطوير API',
            'description': 'بعد تطوير واجهات برمجة التطبيقات',
            'order': 6
        },
        'frontend_update': {
            'name': 'تحديث الواجهة',
            'description': 'بعد تحديث واجهة المستخدم والتصميم',
            'order': 7
        },
        'security_implementation': {
            'name': 'تطبيق الأمان',
            'description': 'بعد تطبيق نظام الأمان والصلاحيات',
            'order': 8
        },
        'performance_optimization': {
            'name': 'تحسين الأداء',
            'description': 'بعد تحسين الأداء والاستقرار',
            'order': 9
        },
        'testing_completion': {
            'name': 'إكمال الاختبارات',
            'description': 'بعد إكمال جميع الاختبارات والتحقق من الجودة',
            'order': 10
        },
        'production_ready': {
            'name': 'جاهز للإنتاج',
            'description': 'النظام جاهز للنشر في بيئة الإنتاج',
            'order': 11
        }
    }

    def add_arguments(self, parser):
        """add_arguments function"""
        parser.add_argument(
            'stage',
            choices=list(self.CHECKPOINT_STAGES.keys()) + ['custom'],
            help='Checkpoint stage or "custom" for custom checkpoint'
        )

        parser.add_argument(
            '--name',
            type=str,
            help='Custom checkpoint name (required for custom stage)'
        )

        parser.add_argument(
            '--description',
            type=str,
            help='Custom checkpoint description'
        )

        parser.add_argument(
            '--backup-dir',
            type=str,
            default='backups',
            help='Directory to store checkpoints (default: backups)'
        )

        parser.add_argument(
            '--include-code',
            action='store_true',
            help='Include source code in checkpoint'
        )

        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress checkpoint files'
        )

        parser.add_argument(
            '--auto-validate',
            action='store_true',
            help='Automatically validate system before creating checkpoint'
        )

    def handle(self, *args, **options):
        """Execute checkpoint creation."""
        try:
            stage = options['stage']

            # Validate system if requested
            if options['auto_validate']:
                self._validate_system()

            # Prepare checkpoint information
            checkpoint_info = self._prepare_checkpoint_info(stage, options)

            self.stdout.write(
                self.style.SUCCESS(
                    f"🎯 إنشاء نقطة تحقق: {checkpoint_info['display_name']}"
                )
            )

            # Create the checkpoint backup
            self._create_checkpoint_backup(checkpoint_info, options)

            # Update checkpoint registry
            self._update_checkpoint_registry(checkpoint_info, options)

            # Display checkpoint summary
            self._display_checkpoint_summary(checkpoint_info)

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ تم إنشاء نقطة التحقق بنجاح: {checkpoint_info['name']}"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ فشل في إنشاء نقطة التحقق: {str(e)}")
            )
            raise CommandError(f"Checkpoint creation failed: {str(e)}")

    def _validate_system(self):
        """Validate system before creating checkpoint."""
        self.stdout.write("🔍 التحقق من سلامة النظام...")

        validation_results = {
            'django_check': self._run_django_check(),
            'database_check': self._check_database_connection(),
            'migrations_check': self._check_migrations_status(),
            'static_files_check': self._check_static_files()
        }

        failed_checks = [check for check, result in validation_results.items() if not result]

        if failed_checks:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ فشل في بعض الفحوصات: {', '.join(failed_checks)}"
                )
            )

            response = input("هل تريد المتابعة رغم الأخطاء؟ (yes/no): ")
            if response.lower() not in ['yes', 'y', 'نعم', 'ن']:
                raise CommandError("تم إلغاء إنشاء نقطة التحقق")
        else:
            self.stdout.write("✅ تم التحقق من سلامة النظام")

    def _run_django_check(self):
        """Run Django system check."""
        try:
            call_command('check', verbosity=0)
            return True
        except Exception:
            return False

    def _check_database_connection(self):
        """Check database connection."""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception:
            return False

    def _check_migrations_status(self):
        """Check if there are unapplied migrations."""
        try:
            from django.core.management.commands.migrate import Command as MigrateCommand
            from django.db.migrations.executor import MigrationExecutor
            from django.db import connection

            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

            # If plan is empty, all migrations are applied
            return len(plan) == 0
        except Exception:
            return False

    def _check_static_files(self):
        """Check static files configuration."""
        try:
            from django.conf import settings
            static_root = Path(settings.STATIC_ROOT)
            return static_root.exists()
        except Exception:
            return False

    def _prepare_checkpoint_info(self, stage, options):
        """Prepare checkpoint information."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if stage == 'custom':
            if not options['name']:
                raise CommandError("Custom checkpoint name is required")

            checkpoint_info = {
                'stage': 'custom',
                'name': f"checkpoint_{options['name']}_{timestamp}",
                'display_name': options['name'],
                'description': options.get('description', f"Custom checkpoint: {options['name']}"),
                'order': 999  # Custom checkpoints have high order
            }
        else:
            stage_info = self.CHECKPOINT_STAGES[stage]
            checkpoint_info = {
                'stage': stage,
                'name': f"checkpoint_{stage}_{timestamp}",
                'display_name': stage_info['name'],
                'description': options.get('description', stage_info['description']),
                'order': stage_info['order']
            }

        checkpoint_info.update({
            'timestamp': timestamp,
            'created_at': timezone.now(),
            'include_code': options['include_code'],
            'compressed': options['compress']
        })

        return checkpoint_info

    def _create_checkpoint_backup(self, checkpoint_info, options):
        """Create the actual backup for the checkpoint."""
        backup_args = [
            'create_system_backup',
            '--name', checkpoint_info['name'],
            '--description', checkpoint_info['description'],
            '--checkpoint', checkpoint_info['stage'],
            '--backup-dir', options['backup_dir']
        ]

        if checkpoint_info['include_code']:
            backup_args.append('--include-code')

        if checkpoint_info['compressed']:
            backup_args.append('--compress')

        # Create the backup
        call_command(*backup_args)

    def _update_checkpoint_registry(self, checkpoint_info, options):
        """Update checkpoint registry with new checkpoint."""
        backup_dir = Path(options['backup_dir'])
        registry_file = backup_dir / 'checkpoint_registry.json'

        # Load existing registry
        if registry_file.exists():
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
            except Exception:
                registry = {'checkpoints': []}
        else:
            registry = {'checkpoints': []}

        # Add new checkpoint to registry
        checkpoint_entry = {
            'stage': checkpoint_info['stage'],
            'name': checkpoint_info['name'],
            'display_name': checkpoint_info['display_name'],
            'description': checkpoint_info['description'],
            'created_at': checkpoint_info['created_at'].isoformat(),
            'order': checkpoint_info['order'],
            'include_code': checkpoint_info['include_code'],
            'compressed': checkpoint_info['compressed']
        }

        registry['checkpoints'].append(checkpoint_entry)

        # Sort checkpoints by order and creation date
        registry['checkpoints'].sort(key=lambda x: (x['order'], x['created_at']))

        # Keep only last 20 checkpoints
        registry['checkpoints'] = registry['checkpoints'][-20:]

        # Save updated registry
        try:
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ فشل في تحديث سجل نقاط التحقق: {str(e)}")
            )

    def _display_checkpoint_summary(self, checkpoint_info):
        """Display checkpoint creation summary."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📊 ملخص نقطة التحقق"))
        self.stdout.write("="*60)
        self.stdout.write(f"المرحلة: {checkpoint_info['display_name']}")
        self.stdout.write(f"الاسم: {checkpoint_info['name']}")
        self.stdout.write(f"الوصف: {checkpoint_info['description']}")
        self.stdout.write(f"التاريخ: {checkpoint_info['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"يتضمن الكود: {'نعم' if checkpoint_info['include_code'] else 'لا'}")
        self.stdout.write(f"مضغوط: {'نعم' if checkpoint_info['compressed'] else 'لا'}")
        self.stdout.write("="*60 + "\n")

    def _get_next_stage_suggestion(self, current_stage):
        """Get suggestion for next checkpoint stage."""
        current_order = self.CHECKPOINT_STAGES.get(current_stage, {}).get('order', 0)

        next_stages = [
            (stage, info) for stage, info in self.CHECKPOINT_STAGES.items()
            if info['order'] > current_order
        ]

        if next_stages:
            next_stage = min(next_stages, key=lambda x: x[1]['order'])
            return next_stage[0], next_stage[1]['name']

        return None, None
