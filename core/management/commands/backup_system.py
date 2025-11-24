"""
System Backup Management Command
===============================

Command to manage system backups including creation, restoration, and maintenance
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
import json

from core.services.backup_service import backup_service


class Command(BaseCommand):
    help = 'Manage system backups'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['create', 'restore', 'list', 'stats', 'cleanup', 'verify'],
            help='Action to perform',
        )
        parser.add_argument(
            '--backup-file',
            type=str,
            help='Backup info file for restore operation',
        )
        parser.add_argument(
            '--components',
            nargs='+',
            choices=['database', 'media', 'static', 'logs'],
            help='Components to backup or restore',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force operation without confirmation',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output',
        )

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.verbose = options['verbose']
        
        action = options['action']
        
        if action == 'create':
            self.create_backup()
        elif action == 'restore':
            self.restore_backup(options)
        elif action == 'list':
            self.list_backups()
        elif action == 'stats':
            self.show_statistics()
        elif action == 'cleanup':
            self.cleanup_backups(options)
        elif action == 'verify':
            self.verify_backups()

    def create_backup(self):
        """Create a full system backup"""
        
        self.stdout.write('Creating full system backup...')
        
        try:
            backup_info = backup_service.create_full_backup()
            
            if backup_info['status'] == 'completed':
                self.stdout.write(
                    self.style.SUCCESS('✅ Backup completed successfully')
                )
                
                if self.verbose:
                    self.display_backup_info(backup_info)
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Backup failed: {backup_info.get("error", "Unknown error")}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Backup failed: {e}')
            )

    def restore_backup(self, options):
        """Restore from backup"""
        
        backup_file = options.get('backup_file')
        components = options.get('components')
        force = options.get('force')
        
        if not backup_file:
            self.stdout.write(
                self.style.ERROR('❌ Backup file is required for restore operation')
            )
            return
        
        if not force:
            self.stdout.write(
                self.style.WARNING('⚠️  This will overwrite existing data!')
            )
            
            confirm = input('Are you sure you want to continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write('Restore cancelled')
                return
        
        self.stdout.write(f'Restoring from backup: {backup_file}')
        
        try:
            restore_result = backup_service.restore_from_backup(backup_file, components)
            
            if restore_result['status'] == 'completed':
                self.stdout.write(
                    self.style.SUCCESS('✅ Restore completed successfully')
                )
            elif restore_result['status'] == 'partial':
                self.stdout.write(
                    self.style.WARNING('⚠️  Restore completed with some errors')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Restore failed: {restore_result.get("error", "Unknown error")}')
                )
            
            if self.verbose:
                self.display_restore_info(restore_result)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Restore failed: {e}')
            )

    def list_backups(self):
        """List available backups"""
        
        self.stdout.write('Available backups:')
        self.stdout.write('=' * 80)
        
        try:
            backups = backup_service.list_backups()
            
            if not backups:
                self.stdout.write('No backups found')
                return
            
            for backup in backups:
                status_color = self.style.SUCCESS if backup.get('status') == 'completed' else self.style.ERROR
                
                self.stdout.write(
                    f"{status_color(backup.get('status', 'unknown').upper())} "
                    f"{backup.get('timestamp', 'Unknown time')} "
                    f"({backup.get('total_size_human', '0 B')})"
                )
                
                if self.verbose:
                    self.stdout.write(f"  File: {backup.get('info_file', 'Unknown')}")
                    
                    components = backup.get('components', {})
                    if components:
                        self.stdout.write("  Components:")
                        for comp_name, comp_info in components.items():
                            comp_status = comp_info.get('status', 'unknown')
                            comp_size = comp_info.get('size_bytes', 0)
                            self.stdout.write(
                                f"    - {comp_name}: {comp_status} "
                                f"({backup_service.format_bytes(comp_size)})"
                            )
                    
                    self.stdout.write("")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error listing backups: {e}')
            )

    def show_statistics(self):
        """Show backup statistics"""
        
        self.stdout.write('Backup Statistics:')
        self.stdout.write('=' * 50)
        
        try:
            stats = backup_service.get_backup_statistics()
            
            self.stdout.write(f"Total backups: {stats['total_backups']}")
            self.stdout.write(f"Total size: {stats['total_size_human']}")
            self.stdout.write(f"Successful backups: {stats['successful_backups']}")
            self.stdout.write(f"Failed backups: {stats['failed_backups']}")
            
            if stats['oldest_backup']:
                self.stdout.write(f"Oldest backup: {stats['oldest_backup']}")
            
            if stats['newest_backup']:
                self.stdout.write(f"Newest backup: {stats['newest_backup']}")
            
            if stats['components_stats']:
                self.stdout.write("\nComponent statistics:")
                for component, count in stats['components_stats'].items():
                    self.stdout.write(f"  {component}: {count} backups")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error getting statistics: {e}')
            )

    def cleanup_backups(self, options):
        """Clean up old backups"""
        
        force = options.get('force')
        
        if not force:
            confirm = input('This will delete old backup files. Continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write('Cleanup cancelled')
                return
        
        self.stdout.write('Cleaning up old backups...')
        
        try:
            cleanup_result = backup_service.cleanup_old_backups()
            
            if cleanup_result['status'] == 'completed':
                deleted_count = len(cleanup_result['deleted_files'])
                freed_space = backup_service.format_bytes(cleanup_result['freed_space_bytes'])
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Cleanup completed: {deleted_count} files deleted, '
                        f'{freed_space} freed'
                    )
                )
                
                if self.verbose and cleanup_result['deleted_files']:
                    self.stdout.write("\nDeleted files:")
                    for deleted_file in cleanup_result['deleted_files']:
                        self.stdout.write(f"  - {deleted_file}")
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Cleanup failed: {cleanup_result.get("error", "Unknown error")}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Cleanup failed: {e}')
            )

    def verify_backups(self):
        """Verify backup integrity"""
        
        self.stdout.write('Verifying backup integrity...')
        
        try:
            backups = backup_service.list_backups()
            
            if not backups:
                self.stdout.write('No backups to verify')
                return
            
            verified_count = 0
            failed_count = 0
            
            for backup in backups:
                if backup.get('status') != 'completed':
                    continue
                
                self.stdout.write(f"Verifying backup: {backup.get('timestamp', 'Unknown')}")
                
                verification_result = backup_service.verify_backup_integrity(backup)
                
                if verification_result['status'] == 'completed':
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✅ Verification passed")
                    )
                    verified_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f"  ❌ Verification failed")
                    )
                    failed_count += 1
                    
                    if self.verbose:
                        for comp_name, comp_verification in verification_result.get('verified_components', {}).items():
                            if comp_verification['status'] != 'verified':
                                self.stdout.write(f"    - {comp_name}: {comp_verification.get('error', 'Failed')}")
            
            self.stdout.write(f"\nVerification summary: {verified_count} passed, {failed_count} failed")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Verification failed: {e}')
            )

    def display_backup_info(self, backup_info):
        """Display detailed backup information"""
        
        self.stdout.write("\nBackup Details:")
        self.stdout.write("-" * 40)
        
        self.stdout.write(f"Status: {backup_info['status']}")
        self.stdout.write(f"Started: {backup_info['timestamp']}")
        
        if 'completed_at' in backup_info:
            self.stdout.write(f"Completed: {backup_info['completed_at']}")
        
        if 'components' in backup_info:
            self.stdout.write("\nComponents:")
            for comp_name, comp_info in backup_info['components'].items():
                status = comp_info.get('status', 'unknown')
                size = comp_info.get('size_bytes', 0)
                
                self.stdout.write(
                    f"  {comp_name}: {status} ({backup_service.format_bytes(size)})"
                )
        
        if 'verification' in backup_info:
            verification = backup_info['verification']
            self.stdout.write(f"\nVerification: {verification['status']}")
        
        if 'cleanup' in backup_info:
            cleanup = backup_info['cleanup']
            self.stdout.write(f"Cleanup: {cleanup['status']}")

    def display_restore_info(self, restore_result):
        """Display detailed restore information"""
        
        self.stdout.write("\nRestore Details:")
        self.stdout.write("-" * 40)
        
        self.stdout.write(f"Status: {restore_result['status']}")
        self.stdout.write(f"Started: {restore_result['timestamp']}")
        
        if 'completed_at' in restore_result:
            self.stdout.write(f"Completed: {restore_result['completed_at']}")
        
        if 'restored_components' in restore_result:
            self.stdout.write("\nRestored Components:")
            for comp_name, comp_info in restore_result['restored_components'].items():
                status = comp_info.get('status', 'unknown')
                self.stdout.write(f"  {comp_name}: {status}")
        
        if restore_result.get('errors'):
            self.stdout.write("\nErrors:")
            for error in restore_result['errors']:
                self.stdout.write(f"  - {error}")