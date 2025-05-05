# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0010_create_leavetype_table'),
        ('accounts', '0001_initial'),
    ]

    operations = [
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