from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0005_alter_employeenote_table'),
    ]

    operations = [
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_employeenote')
            BEGIN
                CREATE TABLE hr_employeenote (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    title NVARCHAR(100) NOT NULL,
                    content NVARCHAR(MAX) NOT NULL,
                    employee_id INT NOT NULL,
                    created_by_id BIGINT NULL,
                    is_important BIT NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (employee_id) REFERENCES Tbl_Employee(Emp_ID),
                    FOREIGN KEY (created_by_id) REFERENCES accounts_users_login_new(id)
                );
            END
            """,
            "DROP TABLE IF EXISTS hr_employeenote"
        ),
    ]