# Generated manually to ensure SystemSettings table exists

from django.db import migrations, models
from django.utils import timezone

def create_default_settings(apps, schema_editor):
    """Create default system settings if none exist"""
    SystemSettings = apps.get_model('administrator', 'SystemSettings')
    if not SystemSettings.objects.exists():
        SystemSettings.objects.create(
            db_host='localhost',
            db_name='El_Dawliya_International',
            db_user='sa',
            db_password='password',
            db_port='1433',
            company_name='الشركة الدولية',
            company_address='',
            company_phone='',
            company_email='',
            company_website='',
            system_name='نظام الدولية',
            enable_debugging=False,
            maintenance_mode=False,
            timezone='Asia/Riyadh',
            date_format='Y-m-d',
            language='ar',
            font_family='cairo',
            text_direction='rtl',
            last_modified=timezone.now()
        )

class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0010_merge_20240101_0000'),
    ]

    operations = [
        # Run the function to create default settings
        migrations.RunPython(create_default_settings),
    ]
