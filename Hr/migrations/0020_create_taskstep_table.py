from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0019_merge_20240101_0003'),
    ]

    operations = [
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Hr_taskstep')
            BEGIN
                CREATE TABLE Hr_taskstep (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    task_id INT NOT NULL,
                    description NVARCHAR(MAX) NOT NULL,
                    completed BIT NOT NULL DEFAULT 0,
                    completion_date DATE NULL,
                    created_by_id INT NULL,
                    created_at DATETIME NOT NULL DEFAULT GETDATE(),
                    updated_at DATETIME NOT NULL DEFAULT GETDATE()
                );
            END
            """,
            "DROP TABLE IF EXISTS Hr_taskstep"
        ),
    ]
