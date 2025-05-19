from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('administrator', '9998_remove_rbac_models'),  # This should depend on the previous migration
    ]

    operations = [
        migrations.RemoveField(
            model_name='permissionauditlog',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='permissionauditlog',
            name='user',
        ),
        migrations.DeleteModel(
            name='PermissionAuditLog',
        ),
    ]
