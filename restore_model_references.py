#!/usr/bin/env python
"""
Restore the original model references after migrations are complete.
"""

import os
import shutil
from pathlib import Path

def restore_attendance_models():
    """Restore the attendance models file"""
    file_path = Path('Hr/models/attendance_models.py')
    backup_path = Path('Hr/models/attendance_models.py.backup_temp')
    
    if not backup_path.exists():
        print(f"✗ Backup not found: {backup_path}")
        return False
    
    if not file_path.exists():
        print(f"✗ Original file not found: {file_path}")
        return False
    
    # Restore from backup
    shutil.copy2(backup_path, file_path)
    os.remove(backup_path)
    print(f"✓ Restored {file_path}")
    return True

def restore_attendance_forms():
    """Restore the attendance forms file"""
    file_path = Path('Hr/forms/attendance_forms.py')
    backup_path = Path('Hr/forms/attendance_forms.py.backup_temp')

    if not backup_path.exists():
        print(f"✗ Backup not found: {backup_path}")
        return False

    if not file_path.exists():
        print(f"✗ Original file not found: {file_path}")
        return False

    # Restore from backup
    shutil.copy2(backup_path, file_path)
    os.remove(backup_path)
    print(f"✓ Restored {file_path}")
    return True

def main():
    print("Restoring Original Model References")
    print("=" * 40)

    # Restore the attendance models
    models_restored = restore_attendance_models()

    # Restore the attendance forms
    forms_restored = restore_attendance_forms()

    if models_restored and forms_restored:
        print(f"\n✓ Model and form references restored!")
        print("The original files have been restored.")
    else:
        print("\n✗ Failed to restore some references")
        print("You may need to manually restore the files.")

if __name__ == '__main__':
    main()
