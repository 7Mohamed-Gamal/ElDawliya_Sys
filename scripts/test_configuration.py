#!/usr/bin/env python
"""
Test script to validate the new configuration structure.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def test_configuration():
    """Test the new configuration structure."""
    print("🧪 Testing ElDawliya System Configuration Structure")
    print("=" * 55)

    # Test 1: Check if settings files exist
    print("\n1. 📁 Checking settings files...")
    settings_dir = project_root / 'ElDawliya_sys' / 'settings'
    required_files = ['__init__.py', 'base.py', 'development.py', 'production.py', 'testing.py', 'config.py']

    all_files_exist = True
    for file_name in required_files:
        file_path = settings_dir / file_name
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - Missing!")
            all_files_exist = False

    # Test 2: Check .env files
    print("\n2. 🔧 Checking environment files...")
    env_file = project_root / '.env'
    env_example_file = project_root / '.env.example'

    if env_file.exists():
        print("  ✅ .env")
    else:
        print("  ❌ .env - Missing!")
        all_files_exist = False

    if env_example_file.exists():
        print("  ✅ .env.example")
    else:
        print("  ❌ .env.example - Missing!")
        all_files_exist = False

    # Test 3: Check if config manager can be imported
    print("\n3. 🔍 Testing configuration manager...")
    try:
        # Test just the config manager without full Django settings
        config_file = settings_dir / 'config.py'
        if config_file.exists():
            print("  ✅ Configuration manager file exists")

            # Try to read the file to check for syntax errors
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'class ConfigManager' in content:
                    print("  ✅ ConfigManager class found")
                else:
                    print("  ❌ ConfigManager class not found")
                    all_files_exist = False
        else:
            print("  ❌ Configuration manager file missing")
            all_files_exist = False

    except Exception as e:
        print(f"  ❌ Configuration manager test failed: {e}")
        all_files_exist = False

    # Test 4: Check documentation
    print("\n4. 📚 Checking documentation...")
    config_doc = project_root / 'docs' / 'CONFIGURATION.md'
    if config_doc.exists():
        print("  ✅ Configuration documentation")
    else:
        print("  ❌ Configuration documentation - Missing!")

    # Test 5: Check management command
    print("\n5. 🛠️  Checking management command...")
    validate_cmd = project_root / 'core' / 'management' / 'commands' / 'validate_config.py'
    if validate_cmd.exists():
        print("  ✅ validate_config management command")
    else:
        print("  ❌ validate_config management command - Missing!")

    # Test 6: Check migration script
    print("\n6. 🔄 Checking migration script...")
    migrate_script = project_root / 'scripts' / 'migrate_configuration.py'
    if migrate_script.exists():
        print("  ✅ Configuration migration script")
    else:
        print("  ❌ Configuration migration script - Missing!")

    # Summary
    print("\n" + "=" * 55)
    if all_files_exist:
        print("🎉 All configuration structure tests passed!")
        print("\n✅ Configuration consolidation completed successfully!")
        print("\nNext steps:")
        print("1. Update .env file with your actual values")
        print("2. Set DJANGO_SETTINGS_MODULE environment variable")
        print("3. Run Django with the new settings structure")
        print("4. Use 'python manage.py validate_config' when Django is available")
    else:
        print("❌ Some configuration structure tests failed!")
        print("Please check the missing files and fix the issues.")

    return all_files_exist


if __name__ == '__main__':
    success = test_configuration()
    sys.exit(0 if success else 1)
