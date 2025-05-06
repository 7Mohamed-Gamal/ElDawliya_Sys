from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0005_alter_employeenote_table'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS hr_employeenote (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                employee_id INTEGER NOT NULL,
                created_by_id INTEGER NULL,
                is_important INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES Tbl_Employee(Emp_ID),
                FOREIGN KEY (created_by_id) REFERENCES accounts_users_login_new(id)
            );
            """,
            "DROP TABLE IF EXISTS hr_employeenote"
        ),
    ]