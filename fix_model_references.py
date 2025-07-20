#!/usr/bin/env python
"""
Temporarily fix model references to allow migrations to run.
This script will:
1. Comment out problematic foreign key references
2. Run the migrations
3. Restore the original references
"""

import os
import shutil
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the file"""
    backup_path = f"{file_path}.backup_temp"
    shutil.copy2(file_path, backup_path)
    print(f"✓ Backed up {file_path}")
    return backup_path

def restore_file(file_path, backup_path):
    """Restore file from backup"""
    shutil.copy2(backup_path, file_path)
    os.remove(backup_path)
    print(f"✓ Restored {file_path}")

def fix_attendance_models():
    """Fix the attendance models file"""
    file_path = Path('Hr/models/attendance_models.py')
    
    if not file_path.exists():
        print(f"✗ File not found: {file_path}")
        return None
    
    backup_path = backup_file(file_path)
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the problematic references
    fixes = [
        # Comment out the machine field in HrAttendanceRecord
        (
            "machine = models.ForeignKey(HrAttendanceMachine, on_delete=models.SET_NULL, null=True, blank=True, related_name='records', verbose_name=_('الماكينة'))",
            "# TEMPORARILY COMMENTED OUT FOR MIGRATION\n    # machine = models.ForeignKey(HrAttendanceMachine, on_delete=models.SET_NULL, null=True, blank=True, related_name='records', verbose_name=_('الماكينة'))"
        ),
        # Comment out the attendance_rule field in HrEmployeeAttendanceRule
        (
            "attendance_rule = models.ForeignKey(HrAttendanceRule, on_delete=models.CASCADE, related_name='employees', verbose_name=_('قاعدة الحضور'))",
            "# TEMPORARILY COMMENTED OUT FOR MIGRATION\n    # attendance_rule = models.ForeignKey(HrAttendanceRule, on_delete=models.CASCADE, related_name='employees', verbose_name=_('قاعدة الحضور'))"
        )
    ]
    
    for old_text, new_text in fixes:
        if old_text in content:
            content = content.replace(old_text, new_text)
            print(f"✓ Fixed reference: {old_text[:50]}...")
    
    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed {file_path}")
    return backup_path

def fix_attendance_forms():
    """Fix the attendance forms file"""
    file_path = Path('Hr/forms/attendance_forms.py')

    if not file_path.exists():
        print(f"✗ File not found: {file_path}")
        return None

    backup_path = backup_file(file_path)

    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the problematic references
    fixes = [
        # Remove attendance_rule from fields list
        (
            "fields = ['employee', 'attendance_rule', 'effective_date', 'end_date', 'is_active']",
            "fields = ['employee', 'effective_date', 'end_date', 'is_active']  # TEMPORARILY REMOVED attendance_rule"
        ),
        # Remove attendance_rule from widgets
        (
            "'attendance_rule': forms.Select(attrs={'class': 'form-select'}),",
            "# TEMPORARILY COMMENTED OUT\n            # 'attendance_rule': forms.Select(attrs={'class': 'form-select'}),"
        ),
        # Remove machine from AttendanceRecord fields list
        (
            "fields = ['employee', 'record_date', 'record_time', 'record_type', 'machine', 'notes']",
            "fields = ['employee', 'record_date', 'record_time', 'record_type', 'notes']  # TEMPORARILY REMOVED machine"
        ),
        # Remove machine from widgets
        (
            "'machine': forms.Select(attrs={'class': 'form-select'}),",
            "# TEMPORARILY COMMENTED OUT\n            # 'machine': forms.Select(attrs={'class': 'form-select'}),"
        )
    ]

    for old_text, new_text in fixes:
        if old_text in content:
            content = content.replace(old_text, new_text)
            print(f"✓ Fixed form reference: {old_text[:50]}...")

    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Fixed {file_path}")
    return backup_path

def main():
    print("Fixing Model References for Migration")
    print("=" * 40)

    # Fix the attendance models
    models_backup = fix_attendance_models()

    # Fix the attendance forms
    forms_backup = fix_attendance_forms()

    if models_backup and forms_backup:
        print(f"\n✓ Model and form references fixed!")
        print(f"Model backup: {models_backup}")
        print(f"Forms backup: {forms_backup}")
        print("\nNext steps:")
        print("1. Run: python manage.py migrate Hr")
        print("2. Run: python restore_model_references.py")
    else:
        print("\n✗ Failed to fix some references")

if __name__ == '__main__':
    main()
