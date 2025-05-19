from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('administrator', '0001_initial'),  # Update this to the latest migration in your project
    ]

    operations = [
        migrations.RemoveField(
            model_name='permission',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='module',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='users',
        ),
        migrations.RemoveField(
            model_name='templatepermission',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='templatepermission',
            name='users',
        ),
        migrations.RemoveField(
            model_name='usermoduleppermission',
            name='module',
        ),
        migrations.RemoveField(
            model_name='usermoduleppermission',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userdepartmentpermission',
            name='department',
        ),
        migrations.RemoveField(
            model_name='userdepartmentpermission',
            name='user',
        ),
        migrations.RemoveField(
            model_name='usergroup',
            name='group',
        ),
        migrations.RemoveField(
            model_name='usergroup',
            name='user',
        ),
        migrations.RemoveField(
            model_name='groupprofile',
            name='group',
        ),
        migrations.DeleteModel(
            name='Permission',
        ),
        migrations.DeleteModel(
            name='TemplatePermission',
        ),
        migrations.DeleteModel(
            name='UserModulePermission',
        ),
        migrations.DeleteModel(
            name='UserDepartmentPermission',
        ),
        migrations.DeleteModel(
            name='UserGroup',
        ),
        migrations.DeleteModel(
            name='GroupProfile',
        ),
    ]
