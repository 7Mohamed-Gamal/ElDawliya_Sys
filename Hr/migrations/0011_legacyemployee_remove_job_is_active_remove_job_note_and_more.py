# Custom migration to fix Hr.0011 conflicts
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
        
        # These operations will be handled separately after resolving model conflicts:
        # - Remove fields: is_active, note from Job model
        # - Add field: department to Job model
        # - Alter fields: jop_code, jop_name in Job model
        # - Alter model table: Job model to use 'Tbl_Jop'
    ]
