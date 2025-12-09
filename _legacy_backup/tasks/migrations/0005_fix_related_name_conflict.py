# Generated manually to fix related_name conflict

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_enhance_task_model'),
    ]

    operations = [
        # Fix the related_name conflict for TaskStep.created_by
        migrations.AlterField(
            model_name='taskstep',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_tasks_steps',
                to='accounts.users_login_new',
                verbose_name='تم الإنشاء بواسطة'
            ),
        ),
    ]
