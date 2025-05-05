from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0007_alter_employeefile_table'),
    ]

    operations = [
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_employeefile')
            BEGIN
                CREATE TABLE hr_employeefile (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    title NVARCHAR(100) NOT NULL,
                    file_type NVARCHAR(20) NOT NULL,
                    [file] NVARCHAR(100) NOT NULL,
                    description NVARCHAR(MAX) NULL,
                    employee_id INT NOT NULL,
                    uploaded_by_id BIGINT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (employee_id) REFERENCES Tbl_Employee(Emp_ID),
                    FOREIGN KEY (uploaded_by_id) REFERENCES accounts_users_login_new(id)
                );
            END
            """,
            "DROP TABLE IF EXISTS hr_employeefile"
        ),
    ]