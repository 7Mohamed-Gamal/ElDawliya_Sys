# Generated manually to update SystemSettings model choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0003_remove_pagepermission_app_module_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemsettings',
            name='timezone',
            field=models.CharField(
                choices=[
                    ('Asia/Riyadh', 'الرياض (Asia/Riyadh)'),
                    ('Asia/Dubai', 'دبي (Asia/Dubai)'),
                    ('Asia/Kuwait', 'الكويت (Asia/Kuwait)'),
                    ('Asia/Qatar', 'قطر (Asia/Qatar)'),
                    ('Asia/Bahrain', 'البحرين (Asia/Bahrain)'),
                    ('Africa/Cairo', 'القاهرة (Africa/Cairo)'),
                    ('UTC', 'التوقيت العالمي (UTC)'),
                ],
                default='Asia/Riyadh',
                max_length=50,
                verbose_name='المنطقة الزمنية'
            ),
        ),
        migrations.AlterField(
            model_name='systemsettings',
            name='date_format',
            field=models.CharField(
                choices=[
                    ('Y-m-d', 'YYYY-MM-DD (2024-01-15)'),
                    ('d/m/Y', 'DD/MM/YYYY (15/01/2024)'),
                    ('m/d/Y', 'MM/DD/YYYY (01/15/2024)'),
                    ('d-m-Y', 'DD-MM-YYYY (15-01-2024)'),
                ],
                default='Y-m-d',
                max_length=50,
                verbose_name='تنسيق التاريخ'
            ),
        ),
    ]
