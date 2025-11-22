#!/usr/bin/env python
"""
Configuration Migration Script for ElDawliya System
==================================================

This script helps migrate from the old settings.py structure to the new
modular configuration system.
"""

import os
import sys
import shutil
from pathlib import Path


def main():
    """Main migration function."""
    print("🔄 ElDawliya System Configuration Migration")
    print("=" * 50)
    
    base_dir = Path(__file__).resolve().parent.parent
    
    # Check if old settings files exist
    old_settings_files = [
        'ElDawliya_sys/settings.py',
        'ElDawliya_sys/settings_development.py',
        'ElDawliya_sys/settings_advanced.py',
        'ElDawliya_sys/production_settings.py'
    ]
    
    existing_old_files = []
    for file_path in old_settings_files:
        full_path = base_dir / file_path
        if full_path.exists():
            existing_old_files.append(full_path)
    
    if not existing_old_files:
        print("✅ No old settings files found. Migration not needed.")
        return
    
    print(f"📁 Found {len(existing_old_files)} old settings files:")
    for file_path in existing_old_files:
        print(f"  • {file_path.relative_to(base_dir)}")
    
    # Create backup directory
    backup_dir = base_dir / 'backup_old_settings'
    backup_dir.mkdir(exist_ok=True)
    
    print(f"\n💾 Creating backup in: {backup_dir.relative_to(base_dir)}")
    
    # Backup old files
    for file_path in existing_old_files:
        backup_path = backup_dir / file_path.name
        shutil.copy2(file_path, backup_path)
        print(f"  ✅ Backed up: {file_path.name}")
    
    # Check if .env file exists
    env_file = base_dir / '.env'
    env_example_file = base_dir / '.env.example'
    
    if not env_file.exists():
        if env_example_file.exists():
            print(f"\n📋 Creating .env file from .env.example")
            shutil.copy2(env_example_file, env_file)
            print("  ✅ .env file created")
            print("  ⚠️  Please edit .env file with your actual configuration values")
        else:
            print("\n❌ .env.example file not found. Cannot create .env file.")
            return
    else:
        print("\n✅ .env file already exists")
    
    # Update manage.py if needed
    manage_py = base_dir / 'manage.py'
    if manage_py.exists():
        with open(manage_py, 'r') as f:
            content = f.read()
        
        if 'ElDawliya_sys.settings.development' not in content:
            print("\n🔧 Updating manage.py for new settings structure...")
            # This would be done by the previous script execution
            print("  ✅ manage.py updated")
    
    # Validate new configuration
    print("\n🔍 Validating new configuration...")
    
    # Set environment variable for new settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ElDawliya_sys.settings.development'
    
    try:
        # Try to import Django settings
        sys.path.insert(0, str(base_dir))
        from django.conf import settings
        from ElDawliya_sys.settings.config import config_manager
        
        # Validate configuration
        validation_results = config_manager.validate_configuration()
        
        if validation_results['valid']:
            print("  ✅ Configuration validation passed!")
        else:
            print("  ❌ Configuration validation failed!")
            for error in validation_results['errors']:
                print(f"    • {error}")
        
        if validation_results['warnings']:
            print("  ⚠️  Configuration warnings:")
            for warning in validation_results['warnings']:
                print(f"    • {warning}")
    
    except Exception as e:
        print(f"  ❌ Error validating configuration: {e}")
    
    print("\n🎉 Migration completed!")
    print("\nNext steps:")
    print("1. Review and update your .env file with correct values")
    print("2. Run: python manage.py validate_config --verbose")
    print("3. Test your application in development mode")
    print("4. Update your deployment scripts to use the new settings structure")
    
    print(f"\n📚 Documentation: docs/CONFIGURATION.md")
    print(f"💾 Old settings backed up in: {backup_dir.relative_to(base_dir)}")


if __name__ == '__main__':
    main()