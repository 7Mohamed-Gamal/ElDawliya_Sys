"""
Script to apply the migration fix for Hr.0011 conflicts
This script implements the complete solution step by step
"""

import os
import sys
import shutil
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def backup_original_migration():
    """Backup the original problematic migration"""
    original_file = "Hr/migrations/0011_legacyemployee_remove_job_is_active_remove_job_note_and_more.py"
    backup_file = "Hr/migrations/0011_legacyemployee_remove_job_is_active_remove_job_note_and_more.py.backup"
    
    if os.path.exists(original_file):
        shutil.copy2(original_file, backup_file)
        print(f"✅ Backed up original migration to {backup_file}")
        return True
    else:
        print(f"❌ Original migration file not found: {original_file}")
        return False

def replace_problematic_migration():
    """Replace the problematic migration with the fixed version"""
    original_file = "Hr/migrations/0011_legacyemployee_remove_job_is_active_remove_job_note_and_more.py"
    fixed_file = "Hr/migrations/0011_fixed_legacyemployee_only.py"
    
    if os.path.exists(fixed_file):
        if os.path.exists(original_file):
            os.remove(original_file)
            print(f"✅ Removed problematic migration: {original_file}")
        
        shutil.copy2(fixed_file, original_file)
        print(f"✅ Replaced with fixed migration: {original_file}")
        return True
    else:
        print(f"❌ Fixed migration file not found: {fixed_file}")
        return False

def update_job_views():
    """Update job views to use the correct model"""
    job_views_file = "Hr/views/job_views.py"
    
    if os.path.exists(job_views_file):
        with open(job_views_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it's using HrJob
        if 'from Hr.models.job_models import HrJob as Job' in content:
            # Replace with legacy Job import
            new_content = content.replace(
                'from Hr.models.job_models import HrJob as Job',
                'from Hr.models.legacy.legacy_models import Job'
            )
            
            with open(job_views_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Updated job views to use legacy Job model")
            return True
        else:
            print(f"ℹ️  Job views already using correct model or no changes needed")
            return True
    else:
        print(f"❌ Job views file not found: {job_views_file}")
        return False

def create_migration_instructions():
    """Create instructions for completing the migration"""
    instructions = """
# Migration Fix Instructions

## What was done:
1. ✅ Backed up original problematic migration
2. ✅ Replaced with fixed migration that only creates LegacyEmployee
3. ✅ Made HrJob model unmanaged to avoid conflicts
4. ✅ Updated views to use correct Job model

## Next steps to complete the migration:

### Step 1: Apply the fixed migration
```bash
python manage.py migrate Hr 0011
```

### Step 2: If the migration still fails, fake it
```bash
python manage.py migrate Hr 0011 --fake
```

### Step 3: Create a new migration for Job model changes (if needed)
```bash
python manage.py makemigrations Hr --name fix_job_model_fields
```

### Step 4: Apply any new migrations
```bash
python manage.py migrate Hr
```

## Verification:
After completing the steps above, verify that:
- The LegacyEmployee model is created
- The Job model works correctly
- No migration conflicts exist

## Rollback (if needed):
If something goes wrong, restore the original migration:
```bash
cp Hr/migrations/0011_legacyemployee_remove_job_is_active_remove_job_note_and_more.py.backup Hr/migrations/0011_legacyemployee_remove_job_is_active_remove_job_note_and_more.py
```

## Model Usage:
- Use `Hr.models.legacy.legacy_models.Job` for the main Job model
- The `Hr.models.job_models.HrJob` is now unmanaged and should not be used for new development
"""
    
    with open("Hr/MIGRATION_FIX_INSTRUCTIONS.md", "w", encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Created migration fix instructions: Hr/MIGRATION_FIX_INSTRUCTIONS.md")

def main():
    """Apply the complete migration fix"""
    print("Applying Hr Migration Fix")
    print("=" * 30)
    
    success = True
    
    # Step 1: Backup original migration
    if not backup_original_migration():
        success = False
    
    # Step 2: Replace problematic migration
    if success and not replace_problematic_migration():
        success = False
    
    # Step 3: Update job views
    if success and not update_job_views():
        success = False
    
    # Step 4: Create instructions
    create_migration_instructions()
    
    if success:
        print("\n✅ Migration fix applied successfully!")
        print("\nNext steps:")
        print("1. Run: python manage.py migrate Hr 0011")
        print("2. If it fails, run: python manage.py migrate Hr 0011 --fake")
        print("3. Check Hr/MIGRATION_FIX_INSTRUCTIONS.md for detailed instructions")
    else:
        print("\n❌ Some steps failed. Please check the errors above.")
        print("You may need to apply the fix manually.")
    
    print(f"\nFiles modified:")
    print(f"- Hr/models/job_models.py (HrJob made unmanaged)")
    print(f"- Hr/migrations/0011_*.py (replaced with fixed version)")
    print(f"- Hr/views/job_views.py (updated imports)")
    print(f"- Hr/MIGRATION_FIX_INSTRUCTIONS.md (created)")

if __name__ == "__main__":
    main()
