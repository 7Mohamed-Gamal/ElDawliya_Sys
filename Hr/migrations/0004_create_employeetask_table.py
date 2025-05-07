from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0003_alter_employeetask_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='عنوان المهمة')),
                ('description', models.TextField(verbose_name='وصف المهمة')),
                ('status', models.CharField(choices=[('pending', 'قيد الانتظار'), ('in_progress', 'قيد التنفيذ'), ('completed', 'مكتملة'), ('cancelled', 'ملغية')], default='pending', max_length=20, verbose_name='الحالة')),
                ('priority', models.CharField(choices=[('low', 'منخفضة'), ('medium', 'متوسطة'), ('high', 'عالية'), ('urgent', 'عاجلة')], default='medium', max_length=20, verbose_name='الأولوية')),
                ('start_date', models.DateField(verbose_name='تاريخ البدء')),
                ('due_date', models.DateField(verbose_name='تاريخ الاستحقاق')),
                ('completion_date', models.DateField(blank=True, null=True, verbose_name='تاريخ الإكمال')),
                ('progress', models.IntegerField(default=0, verbose_name='نسبة الإنجاز')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
            ],
            options={
                'verbose_name': 'مهمة موظف',
                'verbose_name_plural': 'مهام الموظفين',
                'db_table': 'hr_employeetask',
            },
        ),
    ]