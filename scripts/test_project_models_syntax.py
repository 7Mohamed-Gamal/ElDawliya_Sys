#!/usr/bin/env python
"""
Syntax validation script for the unified project models.
This script checks for Python syntax errors and basic Django model structure.
"""
import ast
import sys
from pathlib import Path


def check_python_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def check_django_model_structure(file_path):
    """Check basic Django model structure"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        models_found = []
        imports_found = []
        
        # Check for required imports
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'django.db':
                    imports_found.extend([alias.name for alias in node.names])
                elif node.module and 'django' in node.module:
                    imports_found.append(node.module)
            elif isinstance(node, ast.Import):
                imports_found.extend([alias.name for alias in node.names])
        
        # Check for model classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's likely a Django model
                for base in node.bases:
                    if isinstance(base, ast.Attribute):
                        if (isinstance(base.value, ast.Name) and 
                            base.value.id == 'models' and 
                            base.attr == 'Model'):
                            models_found.append(node.name)
                        elif (isinstance(base.value, ast.Attribute) and
                              base.attr in ['BaseModel', 'AuditableModel', 'SoftDeleteModel']):
                            models_found.append(node.name)
                    elif isinstance(base, ast.Name):
                        if base.id in ['BaseModel', 'AuditableModel', 'SoftDeleteModel']:
                            models_found.append(node.name)
        
        return True, {
            'models': models_found,
            'imports': imports_found
        }
        
    except Exception as e:
        return False, f"Error analyzing structure: {e}"


def validate_model_fields(file_path):
    """Validate that models have proper field definitions"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common Django field patterns
        required_patterns = [
            'models.CharField',
            'models.TextField',
            'models.DateTimeField',
            'models.ForeignKey',
            'verbose_name',
            'class Meta:',
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            return False, f"Missing patterns: {missing_patterns}"
        
        return True, "All required patterns found"
        
    except Exception as e:
        return False, f"Error validating fields: {e}"


def check_model_meta_classes(file_path):
    """Check that models have proper Meta classes"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        models_with_meta = []
        models_without_meta = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a model class
                is_model = False
                for base in node.bases:
                    if isinstance(base, ast.Attribute):
                        if (isinstance(base.value, ast.Name) and 
                            base.value.id == 'models' and 
                            base.attr == 'Model'):
                            is_model = True
                        elif (isinstance(base.value, ast.Attribute) and
                              base.attr in ['BaseModel', 'AuditableModel', 'SoftDeleteModel']):
                            is_model = True
                    elif isinstance(base, ast.Name):
                        if base.id in ['BaseModel', 'AuditableModel', 'SoftDeleteModel']:
                            is_model = True
                
                if is_model:
                    # Check for Meta class
                    has_meta = False
                    for item in node.body:
                        if isinstance(item, ast.ClassDef) and item.name == 'Meta':
                            has_meta = True
                            break
                    
                    if has_meta:
                        models_with_meta.append(node.name)
                    else:
                        models_without_meta.append(node.name)
        
        return True, {
            'with_meta': models_with_meta,
            'without_meta': models_without_meta
        }
        
    except Exception as e:
        return False, f"Error checking Meta classes: {e}"


def main():
    """Run all syntax validation tests"""
    print("=" * 60)
    print("PROJECT MODELS SYNTAX VALIDATION")
    print("=" * 60)
    
    # Path to the project models file
    project_root = Path(__file__).parent.parent
    models_file = project_root / 'core' / 'models' / 'projects.py'
    
    if not models_file.exists():
        print(f"✗ Models file not found: {models_file}")
        return False
    
    print(f"Validating: {models_file}")
    print("-" * 60)
    
    # Test 1: Python syntax
    print("1. Checking Python syntax...")
    syntax_ok, syntax_error = check_python_syntax(models_file)
    if syntax_ok:
        print("   ✓ Python syntax is valid")
    else:
        print(f"   ✗ Python syntax error: {syntax_error}")
        return False
    
    # Test 2: Django model structure
    print("\n2. Checking Django model structure...")
    structure_ok, structure_info = check_django_model_structure(models_file)
    if structure_ok:
        print(f"   ✓ Found {len(structure_info['models'])} model classes:")
        for model in structure_info['models']:
            print(f"     - {model}")
    else:
        print(f"   ✗ Structure error: {structure_info}")
        return False
    
    # Test 3: Model fields validation
    print("\n3. Checking model fields...")
    fields_ok, fields_info = validate_model_fields(models_file)
    if fields_ok:
        print(f"   ✓ Model fields validation passed: {fields_info}")
    else:
        print(f"   ✗ Model fields validation failed: {fields_info}")
        return False
    
    # Test 4: Meta classes
    print("\n4. Checking Meta classes...")
    meta_ok, meta_info = check_model_meta_classes(models_file)
    if meta_ok:
        print(f"   ✓ Models with Meta classes: {len(meta_info['with_meta'])}")
        for model in meta_info['with_meta']:
            print(f"     - {model}")
        if meta_info['without_meta']:
            print(f"   ! Models without Meta classes: {len(meta_info['without_meta'])}")
            for model in meta_info['without_meta']:
                print(f"     - {model}")
    else:
        print(f"   ✗ Meta classes check failed: {meta_info}")
        return False
    
    # Test 5: Check for expected models
    print("\n5. Checking for expected models...")
    expected_models = [
        'ProjectCategory',
        'Project',
        'ProjectPhase',
        'ProjectMilestone',
        'ProjectMember',
        'Task',
        'TaskStep',
        'TimeEntry',
        'Meeting',
        'MeetingAttendee',
        'Document',
    ]
    
    found_models = structure_info['models']
    missing_models = [model for model in expected_models if model not in found_models]
    extra_models = [model for model in found_models if model not in expected_models]
    
    if not missing_models:
        print("   ✓ All expected models found")
    else:
        print(f"   ! Missing models: {missing_models}")
    
    if extra_models:
        print(f"   + Extra models found: {extra_models}")
    
    # Test 6: Check file size and complexity
    print("\n6. Checking file metrics...")
    try:
        with open(models_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        print(f"   ✓ File metrics:")
        print(f"     - Total lines: {total_lines}")
        print(f"     - Non-empty lines: {non_empty_lines}")
        print(f"     - Comment lines: {comment_lines}")
        print(f"     - Code density: {(non_empty_lines - comment_lines) / total_lines * 100:.1f}%")
        
    except Exception as e:
        print(f"   ! Could not calculate file metrics: {e}")
    
    print("\n" + "=" * 60)
    print("SYNTAX VALIDATION SUMMARY")
    print("=" * 60)
    
    if syntax_ok and structure_ok and fields_ok and meta_ok and not missing_models:
        print("✓ All syntax validation tests passed!")
        print("✓ The project models file is syntactically correct and well-structured.")
        return True
    else:
        print("✗ Some validation tests failed.")
        print("Please review the issues above before proceeding.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)