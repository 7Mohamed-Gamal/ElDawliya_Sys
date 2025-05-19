from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('administrator', '9999_remove_custom_permission_models'),  # This should depend on the previous migration
    ]

    operations = [
        migrations.RemoveField(
            model_name='operationpermission',
            name='app_module',
        ),
        migrations.RemoveField(
            model_name='pagepermission',
            name='app_module',
        ),
        migrations.RemoveField(
            model_name='useroperationpermission',
            name='operation',
        ),
        migrations.RemoveField(
            model_name='useroperationpermission',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userpagepermission',
            name='page',
        ),
        migrations.RemoveField(
            model_name='userpagepermission',
            name='user',
        ),
        migrations.DeleteModel(
            name='AppModule',
        ),
        migrations.DeleteModel(
            name='OperationPermission',
        ),
        migrations.DeleteModel(
            name='PagePermission',
        ),
        migrations.DeleteModel(
            name='UserOperationPermission',
        ),
        migrations.DeleteModel(
            name='UserPagePermission',
        ),
    ]
