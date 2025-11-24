"""
Automatic Backup Service for ElDawliya System
============================================

This module provides comprehensive backup functionality including:
- Automatic database backups
- File and media backups
- Backup rotation and cleanup
- Backup integrity verification
- Emergency restore capabilities
"""

import os
import shutil
import gzip
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


class BackupService:
    """خدمة النسخ الاحتياطي التلقائي"""
    
    def __init__(self):
        self.backup_dir = Path(getattr(settings, 'BACKUP_DIR', 'backups'))
        self.backup_dir.mkdir(exist_ok=True)
        
        self.config = {
            'database_backup_enabled': True,
            'media_backup_enabled': True,
            'static_backup_enabled': False,
            'compress_backups': True,
            'max_backup_age_days': 30,
            'max_backup_count': 50,
            'verify_backups': True,
            'email_notifications': True,
            'notification_email': getattr(settings, 'BACKUP_NOTIFICATION_EMAIL', None),
        }
        
        # Backup directories
        self.db_backup_dir = self.backup_dir / 'database'
        self.media_backup_dir = self.backup_dir / 'media'
        self.static_backup_dir = self.backup_dir / 'static'
        self.logs_backup_dir = self.backup_dir / 'logs'
        
        # Create backup directories
        for backup_dir in [self.db_backup_dir, self.media_backup_dir, 
                          self.static_backup_dir, self.logs_backup_dir]:
            backup_dir.mkdir(exist_ok=True)
    
    def create_full_backup(self) -> Dict[str, any]:
        """إنشاء نسخة احتياطية كاملة"""
        
        backup_info = {
            'timestamp': timezone.now().isoformat(),
            'type': 'full',
            'status': 'started',
            'components': {},
            'errors': [],
            'warnings': [],
        }
        
        logger.info("Starting full backup process")
        
        try:
            # Database backup
            if self.config['database_backup_enabled']:
                db_result = self.backup_database()
                backup_info['components']['database'] = db_result
            
            # Media files backup
            if self.config['media_backup_enabled']:
                media_result = self.backup_media_files()
                backup_info['components']['media'] = media_result
            
            # Static files backup
            if self.config['static_backup_enabled']:
                static_result = self.backup_static_files()
                backup_info['components']['static'] = static_result
            
            # Logs backup
            logs_result = self.backup_logs()
            backup_info['components']['logs'] = logs_result
            
            # Verify backups
            if self.config['verify_backups']:
                verification_result = self.verify_backup_integrity(backup_info)
                backup_info['verification'] = verification_result
            
            # Cleanup old backups
            cleanup_result = self.cleanup_old_backups()
            backup_info['cleanup'] = cleanup_result
            
            backup_info['status'] = 'completed'
            backup_info['completed_at'] = timezone.now().isoformat()
            
            logger.info("Full backup completed successfully")
            
            # Send notification
            if self.config['email_notifications']:
                self.send_backup_notification(backup_info)
            
        except Exception as e:
            backup_info['status'] = 'failed'
            backup_info['error'] = str(e)
            backup_info['failed_at'] = timezone.now().isoformat()
            
            logger.error(f"Full backup failed: {e}")
            
            # Send error notification
            if self.config['email_notifications']:
                self.send_backup_notification(backup_info)
            
            raise
        
        # Save backup info
        self.save_backup_info(backup_info)
        
        return backup_info   
 
    def backup_database(self) -> Dict[str, any]:
        """نسخ احتياطي لقاعدة البيانات"""
        
        result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
            'files': [],
            'size_bytes': 0,
        }
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"database_backup_{timestamp}.sql"
            backup_path = self.db_backup_dir / backup_filename
            
            # Create database backup using Django's dumpdata
            with open(backup_path, 'w', encoding='utf-8') as f:
                call_command('dumpdata', 
                           exclude=['contenttypes', 'auth.permission', 'sessions'],
                           stdout=f,
                           format='json',
                           indent=2)
            
            # Compress if enabled
            if self.config['compress_backups']:
                compressed_path = backup_path.with_suffix('.sql.gz')
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed file
                backup_path.unlink()
                backup_path = compressed_path
            
            result['files'].append(str(backup_path))
            result['size_bytes'] = backup_path.stat().st_size
            result['status'] = 'completed'
            result['completed_at'] = timezone.now().isoformat()
            
            logger.info(f"Database backup created: {backup_path}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"Database backup failed: {e}")
            raise
        
        return result
    
    def backup_media_files(self) -> Dict[str, any]:
        """نسخ احتياطي للملفات والوسائط"""
        
        result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
            'files': [],
            'size_bytes': 0,
            'file_count': 0,
        }
        
        try:
            media_root = Path(settings.MEDIA_ROOT)
            if not media_root.exists():
                result['status'] = 'skipped'
                result['reason'] = 'Media directory does not exist'
                return result
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"media_backup_{timestamp}"
            
            if self.config['compress_backups']:
                backup_path = self.media_backup_dir / f"{backup_filename}.tar.gz"
                shutil.make_archive(
                    str(backup_path.with_suffix('')),
                    'gztar',
                    str(media_root.parent),
                    str(media_root.name)
                )
            else:
                backup_path = self.media_backup_dir / backup_filename
                shutil.copytree(media_root, backup_path)
            
            result['files'].append(str(backup_path))
            result['size_bytes'] = self.get_path_size(backup_path)
            result['file_count'] = self.count_files_in_directory(media_root)
            result['status'] = 'completed'
            result['completed_at'] = timezone.now().isoformat()
            
            logger.info(f"Media backup created: {backup_path}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"Media backup failed: {e}")
            raise
        
        return result
    
    def backup_static_files(self) -> Dict[str, any]:
        """نسخ احتياطي للملفات الثابتة"""
        
        result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
            'files': [],
            'size_bytes': 0,
            'file_count': 0,
        }
        
        try:
            static_root = Path(settings.STATIC_ROOT)
            if not static_root.exists():
                result['status'] = 'skipped'
                result['reason'] = 'Static directory does not exist'
                return result
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"static_backup_{timestamp}"
            
            if self.config['compress_backups']:
                backup_path = self.static_backup_dir / f"{backup_filename}.tar.gz"
                shutil.make_archive(
                    str(backup_path.with_suffix('')),
                    'gztar',
                    str(static_root.parent),
                    str(static_root.name)
                )
            else:
                backup_path = self.static_backup_dir / backup_filename
                shutil.copytree(static_root, backup_path)
            
            result['files'].append(str(backup_path))
            result['size_bytes'] = self.get_path_size(backup_path)
            result['file_count'] = self.count_files_in_directory(static_root)
            result['status'] = 'completed'
            result['completed_at'] = timezone.now().isoformat()
            
            logger.info(f"Static files backup created: {backup_path}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"Static files backup failed: {e}")
            raise
        
        return result
    
    def backup_logs(self) -> Dict[str, any]:
        """نسخ احتياطي للسجلات"""
        
        result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
            'files': [],
            'size_bytes': 0,
            'file_count': 0,
        }
        
        try:
            logs_dir = Path('logs')
            if not logs_dir.exists():
                result['status'] = 'skipped'
                result['reason'] = 'Logs directory does not exist'
                return result
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"logs_backup_{timestamp}"
            
            if self.config['compress_backups']:
                backup_path = self.logs_backup_dir / f"{backup_filename}.tar.gz"
                shutil.make_archive(
                    str(backup_path.with_suffix('')),
                    'gztar',
                    str(logs_dir.parent),
                    str(logs_dir.name)
                )
            else:
                backup_path = self.logs_backup_dir / backup_filename
                shutil.copytree(logs_dir, backup_path)
            
            result['files'].append(str(backup_path))
            result['size_bytes'] = self.get_path_size(backup_path)
            result['file_count'] = self.count_files_in_directory(logs_dir)
            result['status'] = 'completed'
            result['completed_at'] = timezone.now().isoformat()
            
            logger.info(f"Logs backup created: {backup_path}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"Logs backup failed: {e}")
            raise
        
        return result 
   
    def verify_backup_integrity(self, backup_info: Dict) -> Dict[str, any]:
        """التحقق من سلامة النسخ الاحتياطية"""
        
        verification_result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
            'verified_components': {},
            'errors': [],
        }
        
        try:
            for component_name, component_info in backup_info['components'].items():
                if component_info['status'] == 'completed':
                    component_verification = self.verify_component_backup(
                        component_name, component_info
                    )
                    verification_result['verified_components'][component_name] = component_verification
            
            # Check if all verifications passed
            all_passed = all(
                comp['status'] == 'verified' 
                for comp in verification_result['verified_components'].values()
            )
            
            verification_result['status'] = 'completed' if all_passed else 'failed'
            verification_result['completed_at'] = timezone.now().isoformat()
            
            logger.info(f"Backup verification completed: {verification_result['status']}")
            
        except Exception as e:
            verification_result['status'] = 'failed'
            verification_result['error'] = str(e)
            logger.error(f"Backup verification failed: {e}")
        
        return verification_result
    
    def verify_component_backup(self, component_name: str, component_info: Dict) -> Dict[str, any]:
        """التحقق من سلامة مكون معين من النسخة الاحتياطية"""
        
        verification = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
            'checks': {},
        }
        
        try:
            for file_path in component_info['files']:
                file_path = Path(file_path)
                
                # Check file exists
                verification['checks']['file_exists'] = file_path.exists()
                
                # Check file size
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    verification['checks']['file_size'] = file_size
                    verification['checks']['size_valid'] = file_size > 0
                    
                    # Check file is readable
                    try:
                        with open(file_path, 'rb') as f:
                            f.read(1024)  # Read first 1KB
                        verification['checks']['file_readable'] = True
                    except Exception:
                        verification['checks']['file_readable'] = False
                    
                    # Component-specific verification
                    if component_name == 'database':
                        verification['checks']['database_valid'] = self.verify_database_backup(file_path)
                    elif component_name in ['media', 'static', 'logs']:
                        verification['checks']['archive_valid'] = self.verify_archive_backup(file_path)
            
            # Determine overall status
            all_checks_passed = all(verification['checks'].values())
            verification['status'] = 'verified' if all_checks_passed else 'failed'
            verification['completed_at'] = timezone.now().isoformat()
            
        except Exception as e:
            verification['status'] = 'failed'
            verification['error'] = str(e)
        
        return verification
    
    def verify_database_backup(self, backup_path: Path) -> bool:
        """التحقق من سلامة نسخة قاعدة البيانات الاحتياطية"""
        
        try:
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                    content = f.read(1000)  # Read first 1000 characters
            else:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)
            
            # Check if it looks like valid JSON
            if content.strip().startswith('[') or content.strip().startswith('{'):
                try:
                    json.loads(content[:500])  # Try to parse first part
                    return True
                except json.JSONDecodeError:
                    pass
            
            return False
            
        except Exception as e:
            logger.error(f"Database backup verification failed: {e}")
            return False
    
    def verify_archive_backup(self, backup_path: Path) -> bool:
        """التحقق من سلامة الأرشيف المضغوط"""
        
        try:
            if backup_path.suffix == '.gz':
                import tarfile
                with tarfile.open(backup_path, 'r:gz') as tar:
                    # Check if archive can be opened and has files
                    return len(tar.getnames()) > 0
            else:
                # For directory backups, check if directory exists and has content
                return backup_path.is_dir() and any(backup_path.iterdir())
            
        except Exception as e:
            logger.error(f"Archive backup verification failed: {e}")
            return False
    
    def cleanup_old_backups(self) -> Dict[str, any]:
        """تنظيف النسخ الاحتياطية القديمة"""
        
        cleanup_result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
            'deleted_files': [],
            'freed_space_bytes': 0,
        }
        
        try:
            cutoff_date = timezone.now() - timedelta(days=self.config['max_backup_age_days'])
            
            for backup_subdir in [self.db_backup_dir, self.media_backup_dir, 
                                 self.static_backup_dir, self.logs_backup_dir]:
                
                if not backup_subdir.exists():
                    continue
                
                # Get all backup files sorted by modification time
                backup_files = sorted(
                    backup_subdir.glob('*'),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )
                
                # Remove files older than cutoff date
                for backup_file in backup_files:
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    file_time = timezone.make_aware(file_time)
                    
                    if file_time < cutoff_date:
                        file_size = self.get_path_size(backup_file)
                        
                        if backup_file.is_dir():
                            shutil.rmtree(backup_file)
                        else:
                            backup_file.unlink()
                        
                        cleanup_result['deleted_files'].append(str(backup_file))
                        cleanup_result['freed_space_bytes'] += file_size
                
                # Keep only max_backup_count most recent files
                if len(backup_files) > self.config['max_backup_count']:
                    files_to_delete = backup_files[self.config['max_backup_count']:]
                    
                    for backup_file in files_to_delete:
                        if backup_file.exists():  # Check if not already deleted by age
                            file_size = self.get_path_size(backup_file)
                            
                            if backup_file.is_dir():
                                shutil.rmtree(backup_file)
                            else:
                                backup_file.unlink()
                            
                            cleanup_result['deleted_files'].append(str(backup_file))
                            cleanup_result['freed_space_bytes'] += file_size
            
            cleanup_result['status'] = 'completed'
            cleanup_result['completed_at'] = timezone.now().isoformat()
            
            logger.info(f"Backup cleanup completed. Freed {cleanup_result['freed_space_bytes']} bytes")
            
        except Exception as e:
            cleanup_result['status'] = 'failed'
            cleanup_result['error'] = str(e)
            logger.error(f"Backup cleanup failed: {e}")
        
        return cleanup_result 
   
    def restore_from_backup(self, backup_info_file: str, components: List[str] = None) -> Dict[str, any]:
        """استعادة من النسخة الاحتياطية"""
        
        restore_result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
            'restored_components': {},
            'errors': [],
        }
        
        try:
            # Load backup info
            backup_info_path = self.backup_dir / backup_info_file
            with open(backup_info_path, 'r', encoding='utf-8') as f:
                backup_info = json.load(f)
            
            # Default to all components if none specified
            if components is None:
                components = list(backup_info['components'].keys())
            
            # Restore each component
            for component_name in components:
                if component_name in backup_info['components']:
                    component_info = backup_info['components'][component_name]
                    
                    if component_info['status'] == 'completed':
                        restore_component_result = self.restore_component(
                            component_name, component_info
                        )
                        restore_result['restored_components'][component_name] = restore_component_result
                    else:
                        restore_result['errors'].append(
                            f"Component {component_name} backup was not completed successfully"
                        )
            
            # Check if all restorations were successful
            all_successful = all(
                comp['status'] == 'completed' 
                for comp in restore_result['restored_components'].values()
            )
            
            restore_result['status'] = 'completed' if all_successful else 'partial'
            restore_result['completed_at'] = timezone.now().isoformat()
            
            logger.info(f"Restore completed: {restore_result['status']}")
            
        except Exception as e:
            restore_result['status'] = 'failed'
            restore_result['error'] = str(e)
            logger.error(f"Restore failed: {e}")
        
        return restore_result
    
    def restore_component(self, component_name: str, component_info: Dict) -> Dict[str, any]:
        """استعادة مكون معين"""
        
        result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
        }
        
        try:
            if component_name == 'database':
                result = self.restore_database(component_info)
            elif component_name == 'media':
                result = self.restore_media_files(component_info)
            elif component_name == 'static':
                result = self.restore_static_files(component_info)
            elif component_name == 'logs':
                result = self.restore_logs(component_info)
            else:
                result['status'] = 'failed'
                result['error'] = f"Unknown component: {component_name}"
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"Component {component_name} restore failed: {e}")
        
        return result
    
    def restore_database(self, component_info: Dict) -> Dict[str, any]:
        """استعادة قاعدة البيانات"""
        
        result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
        }
        
        try:
            backup_file = Path(component_info['files'][0])
            
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            # Extract if compressed
            if backup_file.suffix == '.gz':
                extracted_file = backup_file.with_suffix('')
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(extracted_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_file = extracted_file
            
            # Load data using Django's loaddata
            call_command('loaddata', str(backup_file))
            
            result['status'] = 'completed'
            result['completed_at'] = timezone.now().isoformat()
            
            logger.info(f"Database restored from: {backup_file}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"Database restore failed: {e}")
            raise
        
        return result
    
    def restore_media_files(self, component_info: Dict) -> Dict[str, any]:
        """استعادة ملفات الوسائط"""
        
        result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
        }
        
        try:
            backup_file = Path(component_info['files'][0])
            media_root = Path(settings.MEDIA_ROOT)
            
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            # Remove existing media directory
            if media_root.exists():
                shutil.rmtree(media_root)
            
            # Extract backup
            if backup_file.suffix == '.gz':
                import tarfile
                with tarfile.open(backup_file, 'r:gz') as tar:
                    tar.extractall(path=media_root.parent)
            else:
                shutil.copytree(backup_file, media_root)
            
            result['status'] = 'completed'
            result['completed_at'] = timezone.now().isoformat()
            
            logger.info(f"Media files restored from: {backup_file}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"Media files restore failed: {e}")
            raise
        
        return result
    
    def restore_static_files(self, component_info: Dict) -> Dict[str, any]:
        """استعادة الملفات الثابتة"""
        
        result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
        }
        
        try:
            backup_file = Path(component_info['files'][0])
            static_root = Path(settings.STATIC_ROOT)
            
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            # Remove existing static directory
            if static_root.exists():
                shutil.rmtree(static_root)
            
            # Extract backup
            if backup_file.suffix == '.gz':
                import tarfile
                with tarfile.open(backup_file, 'r:gz') as tar:
                    tar.extractall(path=static_root.parent)
            else:
                shutil.copytree(backup_file, static_root)
            
            result['status'] = 'completed'
            result['completed_at'] = timezone.now().isoformat()
            
            logger.info(f"Static files restored from: {backup_file}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"Static files restore failed: {e}")
            raise
        
        return result
    
    def restore_logs(self, component_info: Dict) -> Dict[str, any]:
        """استعادة السجلات"""
        
        result = {
            'status': 'started',
            'timestamp': timezone.now().isoformat(),
        }
        
        try:
            backup_file = Path(component_info['files'][0])
            logs_dir = Path('logs')
            
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            # Create backup of current logs
            if logs_dir.exists():
                backup_current_logs = logs_dir.parent / f"logs_backup_current_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(logs_dir, backup_current_logs)
            
            # Extract backup
            if backup_file.suffix == '.gz':
                import tarfile
                with tarfile.open(backup_file, 'r:gz') as tar:
                    tar.extractall(path=logs_dir.parent)
            else:
                shutil.copytree(backup_file, logs_dir)
            
            result['status'] = 'completed'
            result['completed_at'] = timezone.now().isoformat()
            
            logger.info(f"Logs restored from: {backup_file}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"Logs restore failed: {e}")
            raise
        
        return result    
  
  def list_backups(self) -> List[Dict[str, any]]:
        """قائمة النسخ الاحتياطية المتاحة"""
        
        backups = []
        
        try:
            # Find all backup info files
            info_files = list(self.backup_dir.glob('backup_info_*.json'))
            
            for info_file in sorted(info_files, key=lambda p: p.stat().st_mtime, reverse=True):
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        backup_info = json.load(f)
                    
                    # Add file info
                    backup_info['info_file'] = info_file.name
                    backup_info['created'] = datetime.fromtimestamp(info_file.stat().st_mtime)
                    
                    # Calculate total size
                    total_size = 0
                    for component_info in backup_info.get('components', {}).values():
                        for file_path in component_info.get('files', []):
                            if Path(file_path).exists():
                                total_size += self.get_path_size(Path(file_path))
                    
                    backup_info['total_size_bytes'] = total_size
                    backup_info['total_size_human'] = self.format_bytes(total_size)
                    
                    backups.append(backup_info)
                    
                except Exception as e:
                    logger.error(f"Error reading backup info {info_file}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
        
        return backups
    
    def get_backup_statistics(self) -> Dict[str, any]:
        """إحصائيات النسخ الاحتياطية"""
        
        stats = {
            'total_backups': 0,
            'total_size_bytes': 0,
            'total_size_human': '0 B',
            'oldest_backup': None,
            'newest_backup': None,
            'successful_backups': 0,
            'failed_backups': 0,
            'components_stats': {},
        }
        
        try:
            backups = self.list_backups()
            
            if not backups:
                return stats
            
            stats['total_backups'] = len(backups)
            stats['total_size_bytes'] = sum(b.get('total_size_bytes', 0) for b in backups)
            stats['total_size_human'] = self.format_bytes(stats['total_size_bytes'])
            
            # Find oldest and newest
            backup_dates = [b['created'] for b in backups if 'created' in b]
            if backup_dates:
                stats['oldest_backup'] = min(backup_dates)
                stats['newest_backup'] = max(backup_dates)
            
            # Count successful/failed
            for backup in backups:
                if backup.get('status') == 'completed':
                    stats['successful_backups'] += 1
                else:
                    stats['failed_backups'] += 1
            
            # Component statistics
            component_counts = {}
            for backup in backups:
                for component_name in backup.get('components', {}):
                    if component_name not in component_counts:
                        component_counts[component_name] = 0
                    component_counts[component_name] += 1
            
            stats['components_stats'] = component_counts
            
        except Exception as e:
            logger.error(f"Error calculating backup statistics: {e}")
        
        return stats
    
    def send_backup_notification(self, backup_info: Dict):
        """إرسال إشعار النسخة الاحتياطية"""
        
        if not self.config['notification_email']:
            return
        
        try:
            status = backup_info['status']
            timestamp = backup_info['timestamp']
            
            if status == 'completed':
                subject = f"[ElDawliya] Backup Completed Successfully - {timestamp}"
                
                # Calculate total size
                total_size = 0
                component_details = []
                
                for component_name, component_info in backup_info.get('components', {}).items():
                    size = component_info.get('size_bytes', 0)
                    total_size += size
                    
                    component_details.append(
                        f"- {component_name}: {self.format_bytes(size)} "
                        f"({component_info.get('status', 'unknown')})"
                    )
                
                message = f"""
نسخة احتياطية مكتملة بنجاح
============================

الوقت: {timestamp}
الحجم الإجمالي: {self.format_bytes(total_size)}

المكونات:
{chr(10).join(component_details)}

التحقق من السلامة: {'تم' if backup_info.get('verification', {}).get('status') == 'completed' else 'لم يتم'}

تنظيف النسخ القديمة: {'تم' if backup_info.get('cleanup', {}).get('status') == 'completed' else 'لم يتم'}

---
نظام النسخ الاحتياطي التلقائي - نظام الدولية
                """
                
            else:
                subject = f"[ElDawliya] Backup Failed - {timestamp}"
                
                message = f"""
فشل في إنشاء النسخة الاحتياطية
==============================

الوقت: {timestamp}
الخطأ: {backup_info.get('error', 'Unknown error')}

يرجى التحقق من السجلات لمزيد من التفاصيل.

---
نظام النسخ الاحتياطي التلقائي - نظام الدولية
                """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.config['notification_email']],
                fail_silently=True
            )
            
            logger.info(f"Backup notification sent to {self.config['notification_email']}")
            
        except Exception as e:
            logger.error(f"Failed to send backup notification: {e}")
    
    def save_backup_info(self, backup_info: Dict):
        """حفظ معلومات النسخة الاحتياطية"""
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            info_filename = f"backup_info_{timestamp}.json"
            info_path = self.backup_dir / info_filename
            
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Backup info saved: {info_path}")
            
        except Exception as e:
            logger.error(f"Failed to save backup info: {e}")
    
    # Utility methods
    def get_path_size(self, path: Path) -> int:
        """حساب حجم المسار (ملف أو مجلد)"""
        
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        else:
            return 0
    
    def count_files_in_directory(self, directory: Path) -> int:
        """عد الملفات في المجلد"""
        
        if not directory.is_dir():
            return 0
        
        return sum(1 for f in directory.rglob('*') if f.is_file())
    
    def format_bytes(self, bytes_size: int) -> str:
        """تنسيق حجم البايتات"""
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"


# Global instance
backup_service = BackupService()