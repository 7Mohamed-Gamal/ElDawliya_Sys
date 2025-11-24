"""
ElDawliya System - Checkpoint Listing Command
=============================================

Django management command for listing and managing system checkpoints.
"""

import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    """
    List and manage system checkpoints.
    """

    help = 'List and manage ElDawliya system checkpoints'

    def add_arguments(self, parser):
        """add_arguments function"""
        parser.add_argument(
            'action',
            choices=['list', 'show', 'restore', 'delete'],
            help='Action to perform'
        )

        parser.add_argument(
            '--backup-dir',
            type=str,
            default='backups',
            help='Directory containing checkpoints (default: backups)'
        )

        parser.add_argument(
            '--checkpoint',
            type=str,
            help='Specific checkpoint name for show/restore/delete actions'
        )

        parser.add_argument(
            '--stage',
            type=str,
            help='Filter checkpoints by stage'
        )

        parser.add_argument(
            '--latest',
            action='store_true',
            help='Show/restore latest checkpoint'
        )

        parser.add_argument(
            '--force',
            action='store_true',
            help='Force action without confirmation'
        )

    def handle(self, *args, **options):
        """Execute checkpoint management action."""
        try:
            backup_dir = Path(options['backup_dir'])

            if not backup_dir.exists():
                raise CommandError(f"Backup directory does not exist: {backup_dir}")

            action = options['action']

            if action == 'list':
                self._list_checkpoints(backup_dir, options)
            elif action == 'show':
                self._show_checkpoint(backup_dir, options)
            elif action == 'restore':
                self._restore_checkpoint(backup_dir, options)
            elif action == 'delete':
                self._delete_checkpoint(backup_dir, options)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ فشل في إدارة نقاط التحقق: {str(e)}")
            )
            raise CommandError(f"Checkpoint management failed: {str(e)}")

    def _list_checkpoints(self, backup_dir, options):
        """List all available checkpoints."""
        self.stdout.write(self.style.SUCCESS("🎯 قائمة نقاط التحقق المتاحة"))
        self.stdout.write("="*80)

        registry = self._load_checkpoint_registry(backup_dir)

        if not registry or not registry.get('checkpoints'):
            self.stdout.write("لا توجد نقاط تحقق مسجلة")
            return

        checkpoints = registry['checkpoints']

        # Filter by stage if specified
        if options.get('stage'):
            checkpoints = [cp for cp in checkpoints if cp['stage'] == options['stage']]

        if not checkpoints:
            self.stdout.write(f"لا توجد نقاط تحقق للمرحلة: {options['stage']}")
            return

        # Display table header
        self.stdout.write(
            f"{'المرحلة':<20} {'الاسم':<30} {'التاريخ':<20} {'الوصف':<30}"
        )
        self.stdout.write("-"*80)

        for checkpoint in checkpoints:
            stage = checkpoint.get('display_name', checkpoint['stage'])[:18]
            name = checkpoint['name'][:28]
            created_at = checkpoint['created_at'][:19]  # Remove microseconds
            description = checkpoint.get('description', '')[:28]

            self.stdout.write(
                f"{stage:<20} {name:<30} {created_at:<20} {description:<30}"
            )

        self.stdout.write("-"*80)
        self.stdout.write(f"إجمالي نقاط التحقق: {len(checkpoints)}")

        # Show available stages
        stages = set(cp['stage'] for cp in registry['checkpoints'])
        self.stdout.write(f"المراحل المتاحة: {', '.join(sorted(stages))}")

    def _show_checkpoint(self, backup_dir, options):
        """Show detailed information about a checkpoint."""
        checkpoint_name = self._get_checkpoint_name(backup_dir, options)

        if not checkpoint_name:
            raise CommandError("Checkpoint name is required")

        registry = self._load_checkpoint_registry(backup_dir)

        if not registry:
            raise CommandError("Checkpoint registry not found")

        checkpoint_info = None
        for checkpoint in registry.get('checkpoints', []):
            if checkpoint['name'] == checkpoint_name:
                checkpoint_info = checkpoint
                break

        if not checkpoint_info:
            raise CommandError(f"Checkpoint not found: {checkpoint_name}")

        # Display detailed information
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"🎯 تفاصيل نقطة التحقق: {checkpoint_name}"))
        self.stdout.write("="*60)

        self.stdout.write(f"المرحلة: {checkpoint_info.get('display_name', checkpoint_info['stage'])}")
        self.stdout.write(f"الاسم: {checkpoint_info['name']}")
        self.stdout.write(f"تاريخ الإنشاء: {checkpoint_info['created_at']}")
        self.stdout.write(f"الوصف: {checkpoint_info.get('description', 'غير متوفر')}")
        self.stdout.write(f"الترتيب: {checkpoint_info.get('order', 'غير محدد')}")
        self.stdout.write(f"يتضمن الكود: {'نعم' if checkpoint_info.get('include_code', False) else 'لا'}")
        self.stdout.write(f"مضغوط: {'نعم' if checkpoint_info.get('compressed', False) else 'لا'}")

        # Check if backup files exist
        backup_exists = self._check_backup_exists(backup_dir, checkpoint_name)
        status = "متوفر" if backup_exists else "مفقود"
        status_style = self.style.SUCCESS if backup_exists else self.style.ERROR
        self.stdout.write(f"حالة الملفات: {status_style(status)}")

        self.stdout.write("="*60 + "\n")

        # Show restoration command
        if backup_exists:
            self.stdout.write("أمر الاستعادة:")
            self.stdout.write(f"python manage.py list_checkpoints restore --checkpoint {checkpoint_name}")

    def _restore_checkpoint(self, backup_dir, options):
        """Restore from a checkpoint."""
        checkpoint_name = self._get_checkpoint_name(backup_dir, options)

        if not checkpoint_name:
            raise CommandError("Checkpoint name is required")

        # Check if checkpoint exists
        if not self._check_backup_exists(backup_dir, checkpoint_name):
            raise CommandError(f"Checkpoint backup files not found: {checkpoint_name}")

        # Get checkpoint info
        registry = self._load_checkpoint_registry(backup_dir)
        checkpoint_info = None

        if registry:
            for checkpoint in registry.get('checkpoints', []):
                if checkpoint['name'] == checkpoint_name:
                    checkpoint_info = checkpoint
                    break

        # Show restoration plan
        self.stdout.write(f"🔄 استعادة من نقطة التحقق: {checkpoint_name}")

        if checkpoint_info:
            self.stdout.write(f"المرحلة: {checkpoint_info.get('display_name', checkpoint_info['stage'])}")
            self.stdout.write(f"الوصف: {checkpoint_info.get('description', 'غير متوفر')}")

        # Confirm restoration
        if not options['force']:
            self.stdout.write("\n⚠️ تحذير: سيتم استبدال النظام الحالي بحالة نقطة التحقق")
            response = input("هل تريد المتابعة؟ (yes/no): ")
            if response.lower() not in ['yes', 'y', 'نعم', 'ن']:
                self.stdout.write("تم إلغاء عملية الاستعادة")
                return

        # Find backup file/directory
        backup_path = self._find_backup_path(backup_dir, checkpoint_name)

        if not backup_path:
            raise CommandError(f"Backup files not found for checkpoint: {checkpoint_name}")

        # Restore using the restore command
        restore_args = [
            'restore_system_backup',
            str(backup_path),
            '--restore-all'
        ]

        if options['force']:
            restore_args.append('--force')

        # Create backup of current system before restoration
        restore_args.append('--backup-current')

        call_command(*restore_args)

        self.stdout.write(
            self.style.SUCCESS(f"✅ تم الاستعادة من نقطة التحقق: {checkpoint_name}")
        )

    def _delete_checkpoint(self, backup_dir, options):
        """Delete a checkpoint."""
        checkpoint_name = self._get_checkpoint_name(backup_dir, options)

        if not checkpoint_name:
            raise CommandError("Checkpoint name is required")

        # Get checkpoint info
        registry = self._load_checkpoint_registry(backup_dir)
        checkpoint_info = None

        if registry:
            for checkpoint in registry.get('checkpoints', []):
                if checkpoint['name'] == checkpoint_name:
                    checkpoint_info = checkpoint
                    break

        if not checkpoint_info:
            raise CommandError(f"Checkpoint not found in registry: {checkpoint_name}")

        # Confirm deletion
        if not options['force']:
            self.stdout.write(f"⚠️ سيتم حذف نقطة التحقق: {checkpoint_name}")
            if checkpoint_info:
                self.stdout.write(f"المرحلة: {checkpoint_info.get('display_name', checkpoint_info['stage'])}")
            response = input("هل تريد المتابعة؟ (yes/no): ")
            if response.lower() not in ['yes', 'y', 'نعم', 'ن']:
                self.stdout.write("تم إلغاء عملية الحذف")
                return

        # Delete using backup management command
        call_command(
            'manage_backups',
            'delete',
            '--backup-name', checkpoint_name,
            '--backup-dir', str(backup_dir),
            '--force' if options['force'] else ''
        )

        # Remove from checkpoint registry
        if registry:
            registry['checkpoints'] = [
                cp for cp in registry['checkpoints']
                if cp['name'] != checkpoint_name
            ]
            self._save_checkpoint_registry(backup_dir, registry)

        self.stdout.write(
            self.style.SUCCESS(f"✅ تم حذف نقطة التحقق: {checkpoint_name}")
        )

    def _get_checkpoint_name(self, backup_dir, options):
        """Get checkpoint name from options or latest checkpoint."""
        if options.get('checkpoint'):
            return options['checkpoint']

        if options.get('latest'):
            return self._get_latest_checkpoint(backup_dir)

        return None

    def _get_latest_checkpoint(self, backup_dir):
        """Get the latest checkpoint name."""
        registry = self._load_checkpoint_registry(backup_dir)

        if not registry or not registry.get('checkpoints'):
            return None

        # Sort by creation date and get the latest
        checkpoints = sorted(
            registry['checkpoints'],
            key=lambda x: x['created_at'],
            reverse=True
        )

        return checkpoints[0]['name'] if checkpoints else None

    def _check_backup_exists(self, backup_dir, checkpoint_name):
        """Check if backup files exist for checkpoint."""
        backup_path = self._find_backup_path(backup_dir, checkpoint_name)
        return backup_path is not None and backup_path.exists()

    def _find_backup_path(self, backup_dir, checkpoint_name):
        """Find backup path for checkpoint."""
        # Check for compressed backup
        zip_path = backup_dir / f"{checkpoint_name}.zip"
        if zip_path.exists():
            return zip_path

        # Check for directory backup
        dir_path = backup_dir / checkpoint_name
        if dir_path.exists():
            return dir_path

        return None

    def _load_checkpoint_registry(self, backup_dir):
        """Load checkpoint registry."""
        registry_file = backup_dir / 'checkpoint_registry.json'

        if not registry_file.exists():
            return None

        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def _save_checkpoint_registry(self, backup_dir, registry):
        """Save checkpoint registry."""
        registry_file = backup_dir / 'checkpoint_registry.json'

        try:
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.stdout.write(f"⚠️ فشل في حفظ سجل نقاط التحقق: {str(e)}")
