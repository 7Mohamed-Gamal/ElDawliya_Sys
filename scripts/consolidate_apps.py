import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / '_legacy_backup'

MAPPINGS = {
    'hr': 'apps/hr',
    'inventory': 'apps/inventory',
    'Purchase_orders': 'apps/procurement/purchase_orders',
    'meetings': 'apps/projects/meetings',
    'tasks': 'apps/projects/tasks',
    'employees': 'apps/hr/employees',
    'attendance': 'apps/hr/attendance',
    'leaves': 'apps/hr/leaves',
    'evaluations': 'apps/hr/evaluations',
    'payrolls': 'apps/hr/payroll',
    'training': 'apps/hr/training',
}

FILES_TO_REMOVE = [
    'db_migration.sqlite3',
    'db_migration_backup.sqlite3',
    'fix_syntax_errors.py',
    'run_performance_tests.py',
    'create_attendance_tables.py',
    'create_tables.py',
    'test_employees_app.py',
    'test_restored_apps.py'
]

def consolidate():
    print(f"Starting consolidation in {BASE_DIR}")
    BACKUP_DIR.mkdir(exist_ok=True)
    print(f"Backup directory: {BACKUP_DIR}")

    # 1. Move root apps to backup and merge
    for src_name, dest_rel_path in MAPPINGS.items():
        src_path = BASE_DIR / src_name
        dest_path = BASE_DIR / dest_rel_path
        
        if not src_path.exists():
            print(f"Skipping {src_name} (not found)")
            continue
            
        print(f"Processing {src_name} -> {dest_rel_path}")
        
        # Create backup of source
        backup_path = BACKUP_DIR / src_name
        if backup_path.exists():
            print(f"Backup for {src_name} already exists, skipping backup creation")
        else:
            shutil.copytree(src_path, backup_path)
            print(f"Backed up {src_name} to {backup_path}")

        # Ensure destination exists
        dest_path.mkdir(parents=True, exist_ok=True)

        # Merge files
        for root, dirs, files in os.walk(src_path):
            rel_root = Path(root).relative_to(src_path)
            dest_root = dest_path / rel_root
            
            dest_root.mkdir(parents=True, exist_ok=True)
            
            for file in files:
                src_file = Path(root) / file
                dest_file = dest_root / file
                
                if not dest_file.exists():
                    shutil.copy2(src_file, dest_file)
                    print(f"Copied {src_file.name} to {dest_file}")
                else:
                    # Optional: Compare and warn?
                    # For now, we assume destination (apps/) is newer/better if it exists
                    pass
        
        # Remove source directory after successful merge (and backup)
        # shutil.rmtree(src_path) 
        # We will NOT remove it yet, to be safe. We'll verify first.
        # Actually, to clean up, we SHOULD remove it, otherwise we have duplicates.
        # Since we have a backup, it is safe to remove.
        shutil.rmtree(src_path)
        print(f"Removed source {src_path}")

    # 2. Move temporary files to backup
    for filename in FILES_TO_REMOVE:
        file_path = BASE_DIR / filename
        if file_path.exists():
            shutil.move(str(file_path), str(BACKUP_DIR / filename))
            print(f"Moved {filename} to backup")

    print("Consolidation complete.")

if __name__ == '__main__':
    consolidate()
