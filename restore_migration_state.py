#!/usr/bin/env python
"""
Restore the original model and form files after migrations are applied.
"""

import os
import shutil
from pathlib import Path

def restore_file(file_path, backup_path):
    """Restore file from backup"""
    if Path(backup_path).exists():
        shutil.copy2(backup_path, file_path)
        os.remove(backup_path)
        print(f"✓ Restored {file_path}")
        return True
    else:
        print(f"✗ Backup not found: {backup_path}")
        return False

def restore_all_files():
    """Restore all backed up files"""
    files_to_restore = [
        ('Hr/models/attendance_models.py', 'Hr/models/attendance_models.py.migration_backup'),
        ('Hr/forms/attendance_forms.py', 'Hr/forms/attendance_forms.py.migration_backup')
    ]
    
    restored_count = 0
    for original_path, backup_path in files_to_restore:
        if restore_file(original_path, backup_path):
            restored_count += 1
    
    return restored_count

def main():
    print("Restoring Migration State Files")
    print("=" * 40)
    
    restored_count = restore_all_files()
    
    if restored_count > 0:
        print(f"\n✓ Successfully restored {restored_count} files!")
        print("The original model and form files have been restored.")
        print("\nYou can now run: python manage.py makemigrations")
        print("to create any additional migrations if needed.")
    else:
        print("\n✗ No files were restored. Check if backups exist.")

if __name__ == '__main__':
    main()
