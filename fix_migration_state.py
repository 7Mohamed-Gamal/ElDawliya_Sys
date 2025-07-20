#!/usr/bin/env python
"""
Fix migration state inconsistency by temporarily removing problematic model references,
applying pending migrations, then restoring the references.
"""

import os
import shutil
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the file"""
    backup_path = f"{file_path}.migration_backup"
    shutil.copy2(file_path, backup_path)
    print(f"✓ Backed up {file_path}")
    return backup_path

def restore_file(file_path, backup_path):
    """Restore file from backup"""
    if Path(backup_path).exists():
        shutil.copy2(backup_path, file_path)
        os.remove(backup_path)
        print(f"✓ Restored {file_path}")
        return True
    return False

def temporarily_fix_models():
    """Temporarily comment out problematic foreign key references"""
    file_path = Path('Hr/models/attendance_models.py')
    
    if not file_path.exists():
        print(f"✗ File not found: {file_path}")
        return None
    
    backup_path = backup_file(file_path)
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Temporarily comment out problematic references
    fixes = [
        # Comment out attendance_rule field in HrEmployeeAttendanceRule
        (
            "attendance_rule = models.ForeignKey(HrAttendanceRule, on_delete=models.CASCADE, related_name='employees', verbose_name=_('قاعدة الحضور'))",
            "# TEMPORARILY COMMENTED FOR MIGRATION STATE FIX\n    # attendance_rule = models.ForeignKey(HrAttendanceRule, on_delete=models.CASCADE, related_name='employees', verbose_name=_('قاعدة الحضور'))"
        ),
        # Comment out machine field in HrAttendanceRecord
        (
            "machine = models.ForeignKey(HrAttendanceMachine, on_delete=models.SET_NULL, null=True, blank=True, related_name='records', verbose_name=_('الماكينة'))",
            "# TEMPORARILY COMMENTED FOR MIGRATION STATE FIX\n    # machine = models.ForeignKey(HrAttendanceMachine, on_delete=models.SET_NULL, null=True, blank=True, related_name='records', verbose_name=_('الماكينة'))"
        )
    ]
    
    for old_text, new_text in fixes:
        if old_text in content:
            content = content.replace(old_text, new_text)
            print(f"✓ Temporarily commented out: {old_text[:50]}...")
    
    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Temporarily fixed {file_path}")
    return backup_path

def temporarily_fix_forms():
    """Temporarily fix forms to remove references to commented fields"""
    file_path = Path('Hr/forms/attendance_forms.py')
    
    if not file_path.exists():
        print(f"✗ File not found: {file_path}")
        return None
    
    backup_path = backup_file(file_path)
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Temporarily fix form references
    fixes = [
        # Remove attendance_rule from EmployeeAttendanceRuleForm fields
        (
            "fields = ['employee', 'attendance_rule', 'effective_date', 'end_date', 'is_active']",
            "fields = ['employee', 'effective_date', 'end_date', 'is_active']  # TEMPORARILY REMOVED attendance_rule"
        ),
        # Comment out attendance_rule widget
        (
            "'attendance_rule': forms.Select(attrs={'class': 'form-select'}),",
            "# TEMPORARILY COMMENTED FOR MIGRATION STATE FIX\n            # 'attendance_rule': forms.Select(attrs={'class': 'form-select'}),"
        ),
        # Remove machine from AttendanceRecordForm fields
        (
            "fields = ['employee', 'record_date', 'record_time', 'record_type', 'machine', 'notes']",
            "fields = ['employee', 'record_date', 'record_time', 'record_type', 'notes']  # TEMPORARILY REMOVED machine"
        ),
        # Comment out machine widget
        (
            "'machine': forms.Select(attrs={'class': 'form-select'}),",
            "# TEMPORARILY COMMENTED FOR MIGRATION STATE FIX\n            # 'machine': forms.Select(attrs={'class': 'form-select'}),"
        )
    ]
    
    for old_text, new_text in fixes:
        if old_text in content:
            content = content.replace(old_text, new_text)
            print(f"✓ Temporarily fixed form: {old_text[:50]}...")
    
    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Temporarily fixed {file_path}")
    return backup_path

def restore_all_files():
    """Restore all backed up files"""
    files_to_restore = [
        'Hr/models/attendance_models.py.migration_backup',
        'Hr/forms/attendance_forms.py.migration_backup'
    ]
    
    restored_count = 0
    for backup_path in files_to_restore:
        if Path(backup_path).exists():
            original_path = backup_path.replace('.migration_backup', '')
            if restore_file(original_path, backup_path):
                restored_count += 1
    
    return restored_count

def main():
    print("Django Migration State Fix")
    print("=" * 40)
    
    # Step 1: Temporarily fix models and forms
    print("\n1. Temporarily fixing model and form references...")
    models_backup = temporarily_fix_models()
    forms_backup = temporarily_fix_forms()
    
    if models_backup and forms_backup:
        print(f"\n✓ Temporary fixes applied!")
        print(f"Model backup: {models_backup}")
        print(f"Forms backup: {forms_backup}")
        print("\nNext steps:")
        print("1. Run: python manage.py migrate")
        print("2. Run: python restore_migration_state.py")
    else:
        print("\n✗ Failed to apply temporary fixes")

if __name__ == '__main__':
    main()
