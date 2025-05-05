# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0009_alter_hrtask_table'),
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
    ]