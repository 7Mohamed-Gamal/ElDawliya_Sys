# Generated manually for enhanced task model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_task_created_at_task_title_task_updated_at_and_more'),
    ]

    operations = [
        # Add priority field to Task
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.CharField(
                choices=[('low', 'منخفضة'), ('medium', 'متوسطة'), ('high', 'عالية'), ('urgent', 'عاجلة')],
                default='medium',
                max_length=20,
                verbose_name='الأولوية'
            ),
        ),
        
        # Enhance TaskStep model
        migrations.AddField(
            model_name='taskstep',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='ملاحظات'),
        ),
        migrations.AddField(
            model_name='taskstep',
            name='completed',
            field=models.BooleanField(default=False, verbose_name='مكتملة'),
        ),
        migrations.AddField(
            model_name='taskstep',
            name='completion_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الإنجاز'),
        ),
        migrations.AddField(
            model_name='taskstep',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_task_steps',
                to='accounts.users_login_new',
                verbose_name='تم الإنشاء بواسطة'
            ),
        ),
        migrations.AddField(
            model_name='taskstep',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث'),
        ),
        
        # Update model metadata
        migrations.AlterModelOptions(
            name='task',
            options={
                'ordering': ['-created_at'],
                'permissions': [
                    ('view_dashboard', 'Can view tasks dashboard'),
                    ('view_mytask', 'Can view my tasks'),
                    ('view_report', 'Can view task reports'),
                    ('export_report', 'Can export task reports'),
                    ('bulk_update', 'Can perform bulk updates on tasks'),
                ],
                'verbose_name': 'مهمة',
                'verbose_name_plural': 'المهام',
            },
        ),
        migrations.AlterModelOptions(
            name='taskstep',
            options={
                'ordering': ['-date'],
                'verbose_name': 'خطوة مهمة',
                'verbose_name_plural': 'خطوات المهام',
            },
        ),
        
        # Add database indexes for better performance (SQL Server compatible)
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'tasks_task_status_idx')
            CREATE INDEX tasks_task_status_idx ON tasks_task (status);
            """,
            reverse_sql="DROP INDEX tasks_task_status_idx ON tasks_task;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'tasks_task_assigned_to_idx')
            CREATE INDEX tasks_task_assigned_to_idx ON tasks_task (assigned_to_id);
            """,
            reverse_sql="DROP INDEX tasks_task_assigned_to_idx ON tasks_task;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'tasks_task_end_date_idx')
            CREATE INDEX tasks_task_end_date_idx ON tasks_task (end_date);
            """,
            reverse_sql="DROP INDEX tasks_task_end_date_idx ON tasks_task;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'tasks_task_priority_idx')
            CREATE INDEX tasks_task_priority_idx ON tasks_task (priority);
            """,
            reverse_sql="DROP INDEX tasks_task_priority_idx ON tasks_task;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'tasks_task_status_assigned_to_idx')
            CREATE INDEX tasks_task_status_assigned_to_idx ON tasks_task (status, assigned_to_id);
            """,
            reverse_sql="DROP INDEX tasks_task_status_assigned_to_idx ON tasks_task;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'tasks_taskstep_task_idx')
            CREATE INDEX tasks_taskstep_task_idx ON tasks_taskstep (task_id);
            """,
            reverse_sql="DROP INDEX tasks_taskstep_task_idx ON tasks_taskstep;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'tasks_taskstep_completed_idx')
            CREATE INDEX tasks_taskstep_completed_idx ON tasks_taskstep (completed);
            """,
            reverse_sql="DROP INDEX tasks_taskstep_completed_idx ON tasks_taskstep;"
        ),
    ]
