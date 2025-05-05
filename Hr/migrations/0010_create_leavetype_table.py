# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0010_create_employee_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='اسم نوع الإجازة')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='كود نوع الإجازة')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف')),
                ('max_days_per_year', models.PositiveIntegerField(default=0, verbose_name='الحد الأقصى للأيام في السنة')),
                ('is_paid', models.BooleanField(default=True, verbose_name='مدفوعة الأجر')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
            ],
            options={
                'verbose_name': 'نوع الإجازة',
                'verbose_name_plural': 'أنواع الإجازات',
                'db_table': 'Hr_LeaveType',
                'ordering': ['name'],
                'managed': True,
            },
        ),
    ]