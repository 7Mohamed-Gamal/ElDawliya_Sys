from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0008_permissionauditlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppModule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='اسم التطبيق')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='كود التطبيق')),
                ('description', models.TextField(blank=True, verbose_name='وصف التطبيق')),
                ('icon', models.CharField(blank=True, max_length=50, verbose_name='أيقونة التطبيق')),
                ('order', models.IntegerField(default=0, verbose_name='الترتيب')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
            ],
            options={
                'verbose_name': 'تطبيق',
                'verbose_name_plural': 'التطبيقات',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='OperationPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='اسم العملية')),
                ('permission_type', models.CharField(choices=[('view', 'عرض'), ('add', 'إضافة'), ('edit', 'تعديل'), ('delete', 'حذف'), ('print', 'طباعة')], max_length=10, verbose_name='نوع الصلاحية')),
                ('code', models.CharField(max_length=100, verbose_name='كود العملية')),
                ('description', models.TextField(blank=True, verbose_name='وصف العملية')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('app_module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operations', to='administrator.AppModule', verbose_name='التطبيق')),
            ],
            options={
                'verbose_name': 'صلاحية عملية',
                'verbose_name_plural': 'صلاحيات العمليات',
                'ordering': ['app_module__name', 'name', 'permission_type'],
                'unique_together': {('app_module', 'code', 'permission_type')},
            },
        ),
        migrations.CreateModel(
            name='PagePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='اسم الصفحة')),
                ('url_pattern', models.CharField(max_length=255, verbose_name='نمط URL')),
                ('template_path', models.CharField(blank=True, max_length=255, verbose_name='مسار القالب')),
                ('description', models.TextField(blank=True, verbose_name='وصف الصفحة')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('app_module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='administrator.AppModule', verbose_name='التطبيق')),
            ],
            options={
                'verbose_name': 'صلاحية صفحة',
                'verbose_name_plural': 'صلاحيات الصفحات',
                'ordering': ['app_module__name', 'name'],
                'unique_together': {('app_module', 'url_pattern')},
            },
        ),
        migrations.CreateModel(
            name='UserPagePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_permissions', to='administrator.PagePermission', verbose_name='الصفحة')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_permissions', to='accounts.Users_Login_New', verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'صلاحية صفحة للمستخدم',
                'verbose_name_plural': 'صلاحيات الصفحات للمستخدمين',
                'unique_together': {('user', 'page')},
            },
        ),
        migrations.CreateModel(
            name='UserOperationPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_permissions', to='administrator.OperationPermission', verbose_name='العملية')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operation_permissions', to='accounts.Users_Login_New', verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'صلاحية عملية للمستخدم',
                'verbose_name_plural': 'صلاحيات العمليات للمستخدمين',
                'unique_together': {('user', 'operation')},
            },
        ),
    ]