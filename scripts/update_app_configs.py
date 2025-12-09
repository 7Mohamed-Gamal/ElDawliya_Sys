import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

UPDATES = {
    'apps/hr/payroll/apps.py': ('payrolls', 'apps.hr.payroll'),
    'apps/procurement/purchase_orders/apps.py': ('Purchase_orders', 'apps.procurement.purchase_orders'),
    'apps/projects/meetings/apps.py': ('meetings', 'apps.projects.meetings'),
    'apps/projects/tasks/apps.py': ('tasks', 'apps.projects.tasks'),
    'apps/hr/employees/apps.py': ('employees', 'apps.hr.employees'),
    'apps/hr/attendance/apps.py': ('attendance', 'apps.hr.attendance'),
    'apps/hr/leaves/apps.py': ('leaves', 'apps.hr.leaves'),
    'apps/hr/evaluations/apps.py': ('evaluations', 'apps.hr.evaluations'),
    'apps/hr/training/apps.py': ('training', 'apps.hr.training'),
}

def update_configs():
    print("Updating AppConfig names...")
    for rel_path, (old_name, new_name) in UPDATES.items():
        file_path = BASE_DIR / rel_path
        if not file_path.exists():
            print(f"Skipping {rel_path} (not found)")
            continue
            
        content = file_path.read_text(encoding='utf-8')
        
        # Regex to find name = 'old_name' or name = "old_name"
        pattern = f"name\\s*=\\s*['\"]{old_name}['\"]"
        replacement = f"name = '{new_name}'"
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"Updated {rel_path}: {old_name} -> {new_name}")
        else:
            print(f"No change needed for {rel_path} (or pattern not found)")

if __name__ == '__main__':
    update_configs()
