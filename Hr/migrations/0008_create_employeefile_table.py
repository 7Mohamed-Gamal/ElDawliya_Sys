from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0007_alter_employeefile_table'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS hr_employeefile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file TEXT NOT NULL,
                description TEXT NULL,
                employee_id INTEGER NOT NULL,
                uploaded_by_id INTEGER NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES Tbl_Employee(Emp_ID),
                FOREIGN KEY (uploaded_by_id) REFERENCES accounts_users_login_new(id)
            );
            """,
            "DROP TABLE IF EXISTS hr_employeefile"
        ),
    ]