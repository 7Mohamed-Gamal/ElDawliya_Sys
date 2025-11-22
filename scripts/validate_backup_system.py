#!/usr/bin/env python
"""
ElDawliya System - Backup System Validation Script
==================================================

This script validates the backup and restore system by creating test backups
and verifying their integrity and restoration capabilities.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings.development')

import django
django.setup()

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.db import connection


class BackupSystemValidator:
    """
    Validates the backup and restore system functionality.
    """
    
    def __init__(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix='eldawliya_backup_test_'))
        self.results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'errors': [],
            'warnings': []
        }
        
        print(f"🧪 بدء اختبار نظام النسخ الاحتياطي")
        print(f"📁 مجلد الاختبار: {self.test_dir}")
    
    def run_all_tests(self):
        """Run all backup system validation tests."""
        try:
            # Test 1: Basic backup creation
            self.test_backup_creation()
            
            # Test 2: Backup validation
            self.test_backup_validation()
            
            # Test 3: Backup listing and management
            self.test_backup_management()
            
            # Test 4: Checkpoint system
            self.test_checkpoint_system()
            
            # Test 5: Backup restoration (dry run)
            self.test_backup_restoration()
            
            # Test 6: Registry management
            self.test_registry_management()
            
            # Test 7: Error handling
            self.test_error_handling()
            
            # Display results
            self.display_results()
            
        except Exception as e:
            self.results['errors'].append(f"Critical error during testing: {str(e)}")
            self.display_results()
            return False
        
        finally:
            # Cleanup
            self.cleanup()
        
        return self.results['tests_failed'] == 0
    
    def test_backup_creation(self):
        """Test backup creation functionality."""
        print("\n🔧 اختبار إنشاء النسخ الاحتياطية...")
        
        try:
            # Test basic backup creation
            self._run_test(
                "إنشاء نسخة احتياطية أساسية",
                lambda: call_command(
                    'create_system_backup',
                    name='test_backup',
                    description='Test backup for validation',
                    backup_dir=str(self.test_dir),
                    verbosity=0
                )
            )
            
            # Test compressed backup creation
            self._run_test(
                "إنشاء نسخة احتياطية مضغوطة",
                lambda: call_command(
                    'create_system_backup',
                    name='test_backup_compressed',
                    description='Compressed test backup',
                    backup_dir=str(self.test_dir),
                    compress=True,
                    verbosity=0
                )
            )
            
            # Test backup with code inclusion
            self._run_test(
                "إنشاء نسخة احتياطية مع الكود",
                lambda: call_command(
                    'create_system_backup',
                    name='test_backup_with_code',
                    description='Test backup with source code',
                    backup_dir=str(self.test_dir),
                    include_code=True,
                    verbosity=0
                )
            )
            
        except Exception as e:
            self.results['errors'].append(f"Backup creation test failed: {str(e)}")
    
    def test_backup_validation(self):
        """Test backup validation functionality."""
        print("\n🔍 اختبار التحقق من النسخ الاحتياطية...")
        
        try:
            # Test validation of existing backups
            self._run_test(
                "التحقق من النسخ الاحتياطية الموجودة",
                lambda: call_command(
                    'manage_backups',
                    'validate',
                    backup_dir=str(self.test_dir),
                    verbosity=0
                )
            )
            
            # Test validation of specific backup
            backup_names = self._get_created_backup_names()
            if backup_names:
                self._run_test(
                    "التحقق من نسخة احتياطية محددة",
                    lambda: call_command(
                        'manage_backups',
                        'validate',
                        backup_name=backup_names[0],
                        backup_dir=str(self.test_dir),
                        verbosity=0
                    )
                )
            
        except Exception as e:
            self.results['errors'].append(f"Backup validation test failed: {str(e)}")
    
    def test_backup_management(self):
        """Test backup management functionality."""
        print("\n📋 اختبار إدارة النسخ الاحتياطية...")
        
        try:
            # Test listing backups
            self._run_test(
                "عرض قائمة النسخ الاحتياطية",
                lambda: call_command(
                    'manage_backups',
                    'list',
                    backup_dir=str(self.test_dir),
                    verbosity=0
                )
            )
            
            # Test showing backup details
            backup_names = self._get_created_backup_names()
            if backup_names:
                self._run_test(
                    "عرض تفاصيل النسخة الاحتياطية",
                    lambda: call_command(
                        'manage_backups',
                        'details',
                        backup_name=backup_names[0],
                        backup_dir=str(self.test_dir),
                        verbosity=0
                    )
                )
            
        except Exception as e:
            self.results['errors'].append(f"Backup management test failed: {str(e)}")
    
    def test_checkpoint_system(self):
        """Test checkpoint system functionality."""
        print("\n🎯 اختبار نظام نقاط التحقق...")
        
        try:
            # Test checkpoint creation
            self._run_test(
                "إنشاء نقطة تحقق",
                lambda: call_command(
                    'create_checkpoint',
                    'initial',
                    backup_dir=str(self.test_dir),
                    verbosity=0
                )
            )
            
            # Test custom checkpoint creation
            self._run_test(
                "إنشاء نقطة تحقق مخصصة",
                lambda: call_command(
                    'create_checkpoint',
                    'custom',
                    name='test_custom_checkpoint',
                    description='Custom test checkpoint',
                    backup_dir=str(self.test_dir),
                    verbosity=0
                )
            )
            
            # Test listing checkpoints
            self._run_test(
                "عرض قائمة نقاط التحقق",
                lambda: call_command(
                    'list_checkpoints',
                    'list',
                    backup_dir=str(self.test_dir),
                    verbosity=0
                )
            )
            
        except Exception as e:
            self.results['errors'].append(f"Checkpoint system test failed: {str(e)}")
    
    def test_backup_restoration(self):
        """Test backup restoration functionality (dry run only)."""
        print("\n🔄 اختبار استعادة النسخ الاحتياطية (محاكاة)...")
        
        try:
            backup_names = self._get_created_backup_names()
            
            if backup_names:
                # Find backup path
                backup_path = self._find_backup_path(backup_names[0])
                
                if backup_path:
                    # Test dry run restoration
                    self._run_test(
                        "محاكاة استعادة النسخة الاحتياطية",
                        lambda: call_command(
                            'restore_system_backup',
                            str(backup_path),
                            restore_all=True,
                            dry_run=True,
                            verbosity=0
                        )
                    )
            else:
                self.results['warnings'].append("No backups available for restoration test")
            
        except Exception as e:
            self.results['errors'].append(f"Backup restoration test failed: {str(e)}")
    
    def test_registry_management(self):
        """Test backup registry management."""
        print("\n📝 اختبار إدارة سجل النسخ الاحتياطية...")
        
        try:
            # Test registry file existence
            registry_file = self.test_dir / 'backup_registry.json'
            
            self._run_test(
                "وجود ملف سجل النسخ الاحتياطية",
                lambda: self._assert_true(
                    registry_file.exists(),
                    "Backup registry file should exist"
                )
            )
            
            # Test registry content
            if registry_file.exists():
                self._run_test(
                    "صحة محتوى سجل النسخ الاحتياطية",
                    lambda: self._validate_registry_content(registry_file)
                )
            
            # Test checkpoint registry
            checkpoint_registry_file = self.test_dir / 'checkpoint_registry.json'
            
            if checkpoint_registry_file.exists():
                self._run_test(
                    "صحة محتوى سجل نقاط التحقق",
                    lambda: self._validate_checkpoint_registry_content(checkpoint_registry_file)
                )
            
        except Exception as e:
            self.results['errors'].append(f"Registry management test failed: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling in backup system."""
        print("\n⚠️ اختبار معالجة الأخطاء...")
        
        try:
            # Test invalid backup directory
            self._run_test(
                "معالجة مجلد نسخ احتياطية غير صالح",
                lambda: self._test_invalid_backup_dir(),
                expect_error=True
            )
            
            # Test invalid backup name for restoration
            self._run_test(
                "معالجة اسم نسخة احتياطية غير صالح",
                lambda: self._test_invalid_backup_name(),
                expect_error=True
            )
            
        except Exception as e:
            self.results['errors'].append(f"Error handling test failed: {str(e)}")
    
    def _run_test(self, test_name, test_func, expect_error=False):
        """Run a single test and record results."""
        self.results['tests_run'] += 1
        
        try:
            test_func()
            
            if expect_error:
                self.results['tests_failed'] += 1
                self.results['errors'].append(f"{test_name}: Expected error but test passed")
                print(f"  ❌ {test_name}: متوقع خطأ لكن الاختبار نجح")
            else:
                self.results['tests_passed'] += 1
                print(f"  ✅ {test_name}: نجح")
                
        except Exception as e:
            if expect_error:
                self.results['tests_passed'] += 1
                print(f"  ✅ {test_name}: نجح (خطأ متوقع)")
            else:
                self.results['tests_failed'] += 1
                self.results['errors'].append(f"{test_name}: {str(e)}")
                print(f"  ❌ {test_name}: فشل - {str(e)}")
    
    def _assert_true(self, condition, message):
        """Assert that condition is true."""
        if not condition:
            raise AssertionError(message)
    
    def _get_created_backup_names(self):
        """Get list of created backup names."""
        registry_file = self.test_dir / 'backup_registry.json'
        
        if not registry_file.exists():
            return []
        
        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            return [backup['name'] for backup in registry.get('backups', [])]
        except Exception:
            return []
    
    def _find_backup_path(self, backup_name):
        """Find backup path for given backup name."""
        # Check for compressed backup
        zip_path = self.test_dir / f"{backup_name}.zip"
        if zip_path.exists():
            return zip_path
        
        # Check for directory backup
        dir_path = self.test_dir / backup_name
        if dir_path.exists():
            return dir_path
        
        return None
    
    def _validate_registry_content(self, registry_file):
        """Validate backup registry content."""
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Check required fields
        self._assert_true('backups' in registry, "Registry should have 'backups' field")
        
        for backup in registry['backups']:
            required_fields = ['name', 'created_at', 'path', 'status']
            for field in required_fields:
                self._assert_true(
                    field in backup,
                    f"Backup entry should have '{field}' field"
                )
    
    def _validate_checkpoint_registry_content(self, registry_file):
        """Validate checkpoint registry content."""
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Check required fields
        self._assert_true('checkpoints' in registry, "Registry should have 'checkpoints' field")
        
        for checkpoint in registry['checkpoints']:
            required_fields = ['stage', 'name', 'created_at', 'order']
            for field in required_fields:
                self._assert_true(
                    field in checkpoint,
                    f"Checkpoint entry should have '{field}' field"
                )
    
    def _test_invalid_backup_dir(self):
        """Test handling of invalid backup directory."""
        try:
            call_command(
                'manage_backups',
                'list',
                backup_dir='/nonexistent/directory',
                verbosity=0
            )
            raise AssertionError("Should have raised CommandError for invalid directory")
        except CommandError:
            # Expected error
            pass
    
    def _test_invalid_backup_name(self):
        """Test handling of invalid backup name."""
        try:
            call_command(
                'manage_backups',
                'details',
                backup_name='nonexistent_backup',
                backup_dir=str(self.test_dir),
                verbosity=0
            )
            raise AssertionError("Should have raised CommandError for invalid backup name")
        except CommandError:
            # Expected error
            pass
    
    def display_results(self):
        """Display test results."""
        print("\n" + "="*60)
        print("📊 نتائج اختبار نظام النسخ الاحتياطي")
        print("="*60)
        print(f"إجمالي الاختبارات: {self.results['tests_run']}")
        print(f"الاختبارات الناجحة: {self.results['tests_passed']}")
        print(f"الاختبارات الفاشلة: {self.results['tests_failed']}")
        
        if self.results['warnings']:
            print(f"\nالتحذيرات ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"  ⚠️ {warning}")
        
        if self.results['errors']:
            print(f"\nالأخطاء ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                print(f"  ❌ {error}")
        
        success_rate = (self.results['tests_passed'] / self.results['tests_run']) * 100 if self.results['tests_run'] > 0 else 0
        print(f"\nمعدل النجاح: {success_rate:.1f}%")
        
        if self.results['tests_failed'] == 0:
            print("✅ جميع الاختبارات نجحت - نظام النسخ الاحتياطي يعمل بشكل صحيح")
        else:
            print("❌ بعض الاختبارات فشلت - يحتاج نظام النسخ الاحتياطي إلى مراجعة")
        
        print("="*60)
    
    def cleanup(self):
        """Clean up test files."""
        try:
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
                print(f"🗑️ تم تنظيف ملفات الاختبار: {self.test_dir}")
        except Exception as e:
            print(f"⚠️ فشل في تنظيف ملفات الاختبار: {str(e)}")


def main():
    """Main function to run backup system validation."""
    print("🚀 ElDawliya System - Backup System Validation")
    print("=" * 50)
    
    validator = BackupSystemValidator()
    success = validator.run_all_tests()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())