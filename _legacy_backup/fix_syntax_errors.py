#!/usr/bin/env python3
"""
Script to fix all syntax errors in the ElDawliya system
"""

import os
import re

def fix_syntax_errors_in_file(file_path):
    """Fix syntax errors in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the main syntax error pattern
        # Pattern: .something()
        pattern1 = r'\.prefetch_related\(\)\s*#\s*TODO:.*?\.([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))'
        content = re.sub(pattern1, r'.\1', content)
        
        # Pattern: .something()
        pattern1b = r'\.select_related\(\)\s*#\s*TODO:.*?\.([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))'
        content = re.sub(pattern1b, r'.\1', content)
        
        # Pattern: 
        pattern2 = r'\.prefetch_related\(\)\s*#\s*TODO:.*?fields'
        content = re.sub(pattern2, '', content)
        
        # Pattern: 
        pattern2b = r'\.select_related\(\)\s*#\s*TODO:.*?fields'
        content = re.sub(pattern2b, '', content)
        
        # Pattern: date.today().year
        pattern3 = r'date\.today\(\)\.prefetch_related\(\)\s*#\s*TODO:.*?fields\.year'
        content = re.sub(pattern3, 'date.today().year', content)
        
        # Pattern: date.today().replace(day=1)
        pattern4 = r'date\.today\(\)\.prefetch_related\(\)\s*#\s*TODO:.*?fields\.replace\(([^)]*)\)'
        content = re.sub(pattern4, r'date.today().replace(\1)', content)
        
        # Pattern: timedelta(days=7)
        pattern5 = r'timedelta\(days=7\)\.prefetch_related\(\)\s*#\s*TODO:.*?fields'
        content = re.sub(pattern5, 'timedelta(days=7)', content)
        
        # Pattern: Q(...) |
        pattern6 = r'Q\([^)]+\)\.prefetch_related\(\)\s*#\s*TODO:.*?fields\s*\|'
        content = re.sub(pattern6, lambda m: m.group(0).split('.prefetch_related')[0] + ' |', content)
        
        # Pattern: .all(),
        pattern7 = r'\.all\(\)\.select_related\(\)\s*#\s*TODO:.*?fields,'
        content = re.sub(pattern7, '.all(),', content)
        
        # Pattern: .all(),
        pattern8 = r'\.all\(\)\.prefetch_related\(\)\s*#\s*TODO:.*?fields,'
        content = re.sub(pattern8, '.all(),', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed syntax errors in {file_path}")
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def find_python_files():
    """Find all Python files in the project"""
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def main():
    """Main function to fix all syntax errors"""
    # Find all Python files
    python_files = find_python_files()
    
    # Filter files that likely contain the syntax errors
    files_to_fix = []
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'prefetch_related()  # TODO:' in content or 'select_related()  # TODO:' in content:
                    files_to_fix.append(file_path)
        except:
            continue
    
    print(f"Found {len(files_to_fix)} files with syntax errors to fix:")
    for file_path in files_to_fix:
        print(f"  - {file_path}")
    
    fixed_count = 0
    for file_path in files_to_fix:
        if fix_syntax_errors_in_file(file_path):
            fixed_count += 1
    
    print(f"\nFixed syntax errors in {fixed_count} files")

if __name__ == "__main__":
    main()