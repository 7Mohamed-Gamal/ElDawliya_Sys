import os
import re
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = BASE_DIR / 'apps'

# 1. App Moves (Source -> Destination relative to BASE_DIR)
APP_MOVES = {
    'loans': 'apps/hr/loans',
    'disciplinary': 'apps/hr/disciplinary',
    'insurance': 'apps/hr/insurance',
    'cars': 'apps/administration/cars',
    'tickets': 'apps/administration/tickets',
    'assets': 'apps/administration/assets',
    'banks': 'apps/finance/banks',
    'workflow': 'apps/workflow',
    'rbac': 'apps/rbac',
    'reports': 'apps/reports',
    'syssettings': 'apps/syssettings',
}

# 2. AppConfig Updates (Path to apps.py -> (old_name, new_name))
APP_CONFIG_UPDATES = {
    'apps/hr/payroll/apps.py': ('payrolls', 'apps.hr.payroll'),
    'apps/procurement/purchase_orders/apps.py': ('Purchase_orders', 'apps.procurement.purchase_orders'),
    'apps/projects/meetings/apps.py': ('meetings', 'apps.projects.meetings'),
    'apps/projects/tasks/apps.py': ('tasks', 'apps.projects.tasks'),
    'apps/hr/employees/apps.py': ('employees', 'apps.hr.employees'),
    'apps/hr/attendance/apps.py': ('attendance', 'apps.hr.attendance'),
    'apps/hr/leaves/apps.py': ('leaves', 'apps.hr.leaves'),
    'apps/hr/evaluations/apps.py': ('evaluations', 'apps.hr.evaluations'),
    'apps/hr/training/apps.py': ('training', 'apps.hr.training'),
    
    # New moves
    'apps/hr/loans/apps.py': ('loans', 'apps.hr.loans'),
    'apps/hr/disciplinary/apps.py': ('disciplinary', 'apps.hr.disciplinary'),
    'apps/hr/insurance/apps.py': ('insurance', 'apps.hr.insurance'),
    'apps/administration/cars/apps.py': ('cars', 'apps.administration.cars'),
    'apps/administration/tickets/apps.py': ('tickets', 'apps.administration.tickets'),
    'apps/administration/assets/apps.py': ('assets', 'apps.administration.assets'),
    'apps/finance/banks/apps.py': ('banks', 'apps.finance.banks'),
    'apps/workflow/apps.py': ('workflow', 'apps.workflow'),
    'apps/rbac/apps.py': ('rbac', 'apps.rbac'),
    'apps/reports/apps.py': ('reports', 'apps.reports'),
    'apps/syssettings/apps.py': ('syssettings', 'apps.syssettings'),
}

# 3. Import Replacements (Regex Pattern -> Replacement)
IMPORT_REPLACEMENTS = [
    (r'from apps.hr.employees', r'from apps.hr.employees'),
    (r'import apps.hr.employees', r'import apps.hr.employees'),
    (r'from apps.hr.attendance', r'from apps.hr.attendance'),
    (r'import apps.hr.attendance', r'import apps.hr.attendance'),
    (r'from apps.hr.leaves', r'from apps.hr.leaves'),
    (r'import apps.hr.leaves', r'import apps.hr.leaves'),
    (r'from apps.hr.payroll', r'from apps.hr.payroll'),
    (r'import apps.hr.payroll', r'import apps.hr.payroll'),
    (r'from apps.hr.evaluations', r'from apps.hr.evaluations'),
    (r'import apps.hr.evaluations', r'import apps.hr.evaluations'),
    (r'from apps.hr.training', r'from apps.hr.training'),
    (r'import apps.hr.training', r'import apps.hr.training'),
    (r'from apps.procurement.purchase_orders', r'from apps.procurement.purchase_orders'),
    (r'import apps.procurement.purchase_orders', r'import apps.procurement.purchase_orders'),
    (r'from apps.projects.meetings', r'from apps.projects.meetings'),
    (r'import apps.projects.meetings', r'import apps.projects.meetings'),
    (r'from apps.projects.tasks', r'from apps.projects.tasks'),
    (r'import apps.projects.tasks', r'import apps.projects.tasks'),
    (r'from apps.inventory', r'from apps.inventory'),
    (r'import apps.inventory', r'import apps.inventory'),
    
    # New moves imports
    (r'from apps.hr.loans', r'from apps.hr.loans'),
    (r'import apps.hr.loans', r'import apps.hr.loans'),
    (r'from apps.hr.disciplinary', r'from apps.hr.disciplinary'),
    (r'import apps.hr.disciplinary', r'import apps.hr.disciplinary'),
    (r'from apps.hr.insurance', r'from apps.hr.insurance'),
    (r'import apps.hr.insurance', r'import apps.hr.insurance'),
    (r'from apps.administration.cars', r'from apps.administration.cars'),
    (r'import apps.administration.cars', r'import apps.administration.cars'),
    (r'from apps.administration.tickets', r'from apps.administration.tickets'),
    (r'import apps.administration.tickets', r'import apps.administration.tickets'),
    (r'from apps.administration.assets', r'from apps.administration.assets'),
    (r'import apps.administration.assets', r'import apps.administration.assets'),
    (r'from apps.finance.banks', r'from apps.finance.banks'),
    (r'import apps.finance.banks', r'import apps.finance.banks'),
    (r'from apps.workflow', r'from apps.workflow'),
    (r'import apps.workflow', r'import apps.workflow'),
    (r'from apps.rbac', r'from apps.rbac'),
    (r'import apps.rbac', r'import apps.rbac'),
    (r'from apps.reports', r'from apps.reports'),
    (r'import apps.reports', r'import apps.reports'),
    (r'from apps.syssettings', r'from apps.syssettings'),
    (r'import apps.syssettings', r'import apps.syssettings'),
]

def move_apps():
    print("Moving remaining apps...")
    for src_name, dest_rel_path in APP_MOVES.items():
        src_path = BASE_DIR / src_name
        dest_path = BASE_DIR / dest_rel_path
        
        if not src_path.exists():
            print(f"Skipping move {src_name} (not found)")
            continue
            
        if dest_path.exists():
            print(f"Destination {dest_rel_path} already exists. Merging/Skipping...")
            # Simple merge: copy contents if not exists
            # For now, just warn
            continue
            
        print(f"Moving {src_name} -> {dest_rel_path}")
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dest_path))

def update_app_configs():
    print("Updating AppConfig names...")
    for rel_path, (old_name, new_name) in APP_CONFIG_UPDATES.items():
        file_path = BASE_DIR / rel_path
        if not file_path.exists():
            continue
            
        content = file_path.read_text(encoding='utf-8')
        pattern = f"name\\s*=\\s*['\"]{old_name}['\"]"
        replacement = f"name = '{new_name}'"
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"Updated config in {rel_path}")

def update_imports():
    print("Updating imports in all .py files...")
    for root, dirs, files in os.walk(BASE_DIR):
        if '.venv' in root or '.git' in root or '__pycache__' in root or '_legacy_backup' in root:
            continue
            
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = Path(root) / file
            try:
                content = file_path.read_text(encoding='utf-8')
                original_content = content
                
                for pattern, replacement in IMPORT_REPLACEMENTS:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    file_path.write_text(content, encoding='utf-8')
                    print(f"Updated imports in {file_path.relative_to(BASE_DIR)}")
            except Exception as e:
                print(f"Could not process {file_path}: {e}")

if __name__ == '__main__':
    move_apps()
    update_app_configs()
    update_imports()
