"""
Script to fix the Hr migration conflicts and model issues
This script provides multiple solutions to resolve the migration failure
"""

import os
import sys
import django
from django.db import connection

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

def solution_1_fake_migration():
    """
    Solution 1: Fake the problematic migration
    This marks the migration as applied without actually running it
    """
    print("Solution 1: Fake the problematic migration")
    print("-" * 40)
    print("Run this command to fake the migration:")
    print("python manage.py migrate Hr 0011 --fake")
    print()
    print("This will mark the migration as applied without running the SQL.")
    print("Use this if the database schema is already correct.")

def solution_2_create_custom_migration():
    """
    Solution 2: Create a custom migration to handle the conflict
    """
    print("Solution 2: Create a custom migration")
    print("-" * 40)
    
    migration_content = '''# Custom migration to fix Hr.0011 conflicts
# Generated to resolve model conflicts and table name issues

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0010_add_legacy_employee_model'),
    ]

    operations = [
        # Create LegacyEmployee model (this part should work)
        migrations.CreateModel(
            name='LegacyEmployee',
            fields=[
                ('emp_id', models.IntegerField(db_column='Emp_ID', primary_key=True, serialize=False, verbose_name='رقم الموظف')),
                ('emp_first_name', models.CharField(blank=True, db_column='Emp_First_Name', max_length=50, null=True, verbose_name='الاسم الأول')),
                ('emp_second_name', models.CharField(blank=True, db_column='Emp_Second_Name', max_length=50, null=True, verbose_name='الاسم الثاني')),
                ('emp_full_name', models.CharField(blank=True, db_column='Emp_Full_Name', max_length=100, null=True, verbose_name='الاسم الكامل')),
                ('working_condition', models.CharField(blank=True, choices=[('سارى', 'سارى'), ('إجازة', 'إجازة'), ('استقالة', 'استقالة'), ('انقطاع عن العمل', 'انقطاع عن العمل')], db_column='Working_Condition', max_length=50, null=True, verbose_name='حالة العمل')),
                ('insurance_status', models.CharField(blank=True, choices=[('مؤمن عليه', 'مؤمن عليه'), ('غير مؤمن عليه', 'غير مؤمن عليه')], db_column='Insurance_Status', max_length=50, null=True, verbose_name='حالة التأمين')),
                ('national_id', models.CharField(blank=True, db_column='National_ID', max_length=14, null=True, verbose_name='الرقم القومي')),
                ('date_birth', models.DateField(blank=True, db_column='Date_Birth', null=True, verbose_name='تاريخ الميلاد')),
                ('emp_date_hiring', models.DateField(blank=True, db_column='Emp_Date_Hiring', null=True, verbose_name='تاريخ التوظيف')),
                ('dept_name', models.CharField(blank=True, db_column='Dept_Name', max_length=50, null=True, verbose_name='اسم القسم')),
                ('jop_code', models.IntegerField(blank=True, db_column='Jop_Code', null=True, verbose_name='كود الوظيفة')),
            ],
            options={
                'verbose_name': 'الموظف',
                'verbose_name_plural': 'الموظفون',
                'db_table': 'Tbl_Employee',
                'managed': False,
            },
        ),
        
        # Skip the problematic Job model operations
        # The Job model operations are commented out because:
        # 1. There's a conflict between Hr.Job and Hr.HrJob models
        # 2. Both models use the same db_table 'Tbl_Jop'
        # 3. The migration is looking for 'Tbl_Job' which doesn't exist
        
        # migrations.RemoveField(
        #     model_name='job',
        #     name='is_active',
        # ),
        # migrations.RemoveField(
        #     model_name='job',
        #     name='note',
        # ),
        # migrations.AddField(
        #     model_name='job',
        #     name='department',
        #     field=models.ForeignKey(blank=True, db_column='Dept_Code', null=True, on_delete=django.db.models.deletion.SET_NULL, to='Hr.legacydepartment', verbose_name='القسم'),
        # ),
        # migrations.AlterField(
        #     model_name='job',
        #     name='jop_code',
        #     field=models.IntegerField(db_column='Jop_Code', primary_key=True, serialize=False, verbose_name='رمز الوظيفة'),
        # ),
        # migrations.AlterField(
        #     model_name='job',
        #     name='jop_name',
        #     field=models.CharField(db_column='Jop_Name', max_length=50, verbose_name='اسم الوظيفة'),
        # ),
        # migrations.AlterModelTable(
        #     name='job',
        #     table='Tbl_Jop',
        # ),
    ]
'''
    
    print("Create a new migration file:")
    print("Hr/migrations/0011_fixed_legacyemployee_only.py")
    print()
    print("Content:")
    print(migration_content)

def solution_3_remove_duplicate_model():
    """
    Solution 3: Remove the duplicate HrJob model
    """
    print("Solution 3: Remove duplicate HrJob model")
    print("-" * 40)
    print("1. Remove or rename Hr/models/job_models.py")
    print("2. Update imports to use only the legacy Job model")
    print("3. Update views that use HrJob to use the legacy Job model")
    print()
    print("Files to modify:")
    print("- Hr/models/job_models.py (remove or rename)")
    print("- Hr/views/job_views.py (update imports)")
    print("- Any other files importing HrJob")

def solution_4_mark_models_unmanaged():
    """
    Solution 4: Mark conflicting models as unmanaged
    """
    print("Solution 4: Mark models as unmanaged")
    print("-" * 40)
    print("Modify the HrJob model to be unmanaged:")
    print()
    print("class HrJob(models.Model):")
    print("    # ... fields ...")
    print("    class Meta:")
    print("        managed = False  # Change this to False")
    print("        db_table = 'Tbl_Jop'")
    print()
    print("This prevents Django from trying to manage the table structure.")

def main():
    print("Hr Migration Conflict Resolution")
    print("=" * 50)
    print()
    print("Problem Summary:")
    print("- Migration 0011 is looking for 'Tbl_Job' table which doesn't exist")
    print("- The actual table is 'Tbl_Jop'")
    print("- Both Hr.Job and Hr.HrJob models use the same db_table")
    print("- This creates conflicts during migration")
    print()
    
    print("Available Solutions:")
    print("=" * 50)
    
    solution_1_fake_migration()
    print()
    
    solution_2_create_custom_migration()
    print()
    
    solution_3_remove_duplicate_model()
    print()
    
    solution_4_mark_models_unmanaged()
    print()
    
    print("Recommended Approach:")
    print("=" * 50)
    print("1. First, try Solution 1 (fake migration) if the database schema is correct")
    print("2. If that doesn't work, use Solution 3 (remove duplicate model)")
    print("3. Then create a new migration for any remaining changes")
    print()
    print("Commands to run:")
    print("1. python manage.py migrate Hr 0011 --fake")
    print("2. python manage.py makemigrations Hr")
    print("3. python manage.py migrate Hr")

if __name__ == "__main__":
    main()
