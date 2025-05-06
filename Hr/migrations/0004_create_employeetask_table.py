from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0003_alter_employeetask_table'),
    ]

    operations = [
        migrations.RunSQL(
            """
            IF OBJECT_ID('hr_employeetask', 'U') IS NULL
            BEGIN
                CREATE TABLE hr_employeetask (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    title NVARCHAR(200) NOT NULL,
                    description NVARCHAR(MAX) NOT NULL,
                    employee_id INT NOT NULL,
                    assigned_by_id INT NULL,
                    status NVARCHAR(20) NOT NULL,
                    priority NVARCHAR(20) NOT NULL,
                    start_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    completion_date DATE NULL,
                    progress INT NOT NULL,
                    notes NVARCHAR(MAX) NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    CONSTRAINT FK_EmployeeTask_Employee FOREIGN KEY (employee_id) REFERENCES Tbl_Employee(Emp_ID),
                    CONSTRAINT FK_EmployeeTask_User FOREIGN KEY (assigned_by_id) REFERENCES accounts_users_login_new(id)
                );
                PRINT 'Created hr_employeetask table';
            END
            ELSE
            BEGIN
                PRINT 'hr_employeetask table already exists';
            END
            """,
            """
            IF OBJECT_ID('hr_employeetask', 'U') IS NOT NULL
            BEGIN
                DROP TABLE hr_employeetask;
            END
            """
        ),
    ]