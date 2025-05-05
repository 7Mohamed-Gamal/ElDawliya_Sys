from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0009_create_employee_table'),
    ]

    operations = [
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_hrtask')
            BEGIN
                CREATE TABLE hr_hrtask (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    title NVARCHAR(200) NOT NULL,
                    description NVARCHAR(MAX) NOT NULL,
                    task_type NVARCHAR(20) NOT NULL,
                    status NVARCHAR(20) NOT NULL,
                    priority NVARCHAR(20) NOT NULL,
                    start_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    completion_date DATE NULL,
                    progress INT NOT NULL,
                    steps_taken NVARCHAR(MAX) NULL,
                    reminder_days INT NOT NULL,
                    assigned_to_id BIGINT NULL,
                    created_by_id BIGINT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (assigned_to_id) REFERENCES accounts_users_login_new(id),
                    FOREIGN KEY (created_by_id) REFERENCES accounts_users_login_new(id)
                );
            END
            """,
            "DROP TABLE IF EXISTS hr_hrtask"
        ),
    ]