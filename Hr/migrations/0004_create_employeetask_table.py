from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0003_alter_employeetask_table'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS hr_employeetask (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                employee_id INTEGER NOT NULL,
                assigned_by_id INTEGER NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                start_date DATE NOT NULL,
                due_date DATE NOT NULL,
                completion_date DATE NULL,
                progress INTEGER NOT NULL,
                notes TEXT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES Tbl_Employee(Emp_ID),
                FOREIGN KEY (assigned_by_id) REFERENCES accounts_users_login_new(id)
            );
            """,
            "DROP TABLE IF EXISTS hr_employeetask"
        ),
    ]