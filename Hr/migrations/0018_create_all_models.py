# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('Hr', '0017_merge_20240101_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='اسم الموظف')),
            ],
            options={
                'verbose_name': 'موظف',
                'verbose_name_plural': 'الموظفين',
                'db_table': 'Hr_Employee',
                'managed': True,
            },
        ),
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
        migrations.CreateModel(
            name='EmployeeLeave',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='تاريخ البداية')),
                ('end_date', models.DateField(verbose_name='تاريخ النهاية')),
                ('days_count', models.PositiveIntegerField(verbose_name='عدد الأيام')),
                ('reason', models.TextField(verbose_name='السبب')),
                ('status', models.CharField(choices=[('pending', 'قيد الانتظار'), ('approved', 'موافق عليه'), ('rejected', 'مرفوض'), ('cancelled', 'ملغى')], default='pending', max_length=20, verbose_name='الحالة')),
                ('approval_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الموافقة')),
                ('rejection_reason', models.TextField(blank=True, null=True, verbose_name='سبب الرفض')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_leaves', to='accounts.users_login_new', verbose_name='تمت الموافقة بواسطة')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaves', to='Hr.employee', verbose_name='الموظف')),
                ('leave_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_leaves', to='Hr.leavetype', verbose_name='نوع الإجازة')),
            ],
            options={
                'verbose_name': 'إجازة الموظف',
                'verbose_name_plural': 'إجازات الموظفين',
                'db_table': 'Hr_EmployeeLeave',
                'ordering': ['-start_date'],
                'managed': True,
            },
        ),
    ]