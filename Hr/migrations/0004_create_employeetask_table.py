from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0003_alter_employeetask_table'),
    ]

    operations = [
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_employeetask')
            BEGIN
                CREATE TABLE hr_employeetask (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    title NVARCHAR(200) NOT NULL,
                    description NVARCHAR(MAX) NOT NULL,
                    employee_id INT NOT NULL,
                    assigned_by_id BIGINT NULL,
                    status NVARCHAR(20) NOT NULL,
                    priority NVARCHAR(20) NOT NULL,
                    start_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    completion_date DATE NULL,
                    progress INT NOT NULL,
                    notes NVARCHAR(MAX) NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (employee_id) REFERENCES Tbl_Employee(Emp_ID),
                    FOREIGN KEY (assigned_by_id) REFERENCES accounts_users_login_new(id)
                );
            END
            """,
            "DROP TABLE IF EXISTS hr_employeetask"
        ),
    ]