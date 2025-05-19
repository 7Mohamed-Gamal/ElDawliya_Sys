from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('admin_permissions', '0001_initial'),  # Update this to the latest migration in your project
    ]

    operations = [
        migrations.RemoveField(
            model_name='permissionauditlog',
            name='affected_groups',
        ),
        migrations.RemoveField(
            model_name='permissionauditlog',
            name='affected_users',
        ),
        migrations.RemoveField(
            model_name='permissionauditlog',
            name='user',
        ),
        migrations.RemoveField(
            model_name='departmentpermissioncache',
            name='user',
        ),
        migrations.RemoveField(
            model_name='modulepermissioncache',
            name='user',
        ),
        migrations.DeleteModel(
            name='PermissionAuditLog',
        ),
        migrations.DeleteModel(
            name='DepartmentPermissionCache',
        ),
        migrations.DeleteModel(
            name='ModulePermissionCache',
        ),
    ]
