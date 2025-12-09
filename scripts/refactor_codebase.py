import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Mappings for AppConfig updates (file_path -> (old_name, new_name))
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
}

# Mappings for Import updates (regex_pattern -> replacement)
# We use regex to be careful about what we replace.
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
    # Inventory might be tricky if it was already in apps/inventory or root
    # Assuming root inventory -> apps.inventory
    (r'from apps.inventory', r'from apps.inventory'),
    (r'import apps.inventory', r'import apps.inventory'),
]

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
        # Skip venv, .git, etc.
        if '.venv' in root or '.git' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = Path(root) / file
            try:
                content = file_path.read_text(encoding='utf-8')
                original_content = content
                
                for pattern, replacement in IMPORT_REPLACEMENTS:
                    # Simple regex replacement
                    # We add word boundaries to avoid replacing substrings incorrectly
                    # But for imports like 'from apps.hr.employees.models', 'employees' is at the start or after space
                    
                    # Regex explanation:
                    # (from|import)\s+  -> match 'from ' or 'import '
                    # old_name          -> match the old package name
                    # (?=\s|\.|$)       -> lookahead to ensure it ends with space, dot, or EOL
                    
                    # Actually, the simple patterns above are safer if we iterate carefully.
                    # Let's use the patterns defined in the list directly.
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    file_path.write_text(content, encoding='utf-8')
                    print(f"Updated imports in {file_path.relative_to(BASE_DIR)}")
            except Exception as e:
                print(f"Could not process {file_path}: {e}")

if __name__ == '__main__':
    update_app_configs()
    update_imports()
