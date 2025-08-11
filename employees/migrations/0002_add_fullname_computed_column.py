from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                """
                IF COL_LENGTH('Employees', 'FullName') IS NULL
                BEGIN
                    ALTER TABLE Employees ADD FullName AS (
                        ISNULL(FirstName, '') + ' ' + ISNULL(SecondName, '') + ' ' + ISNULL(ThirdName, '') + ' ' + ISNULL(LastName, '')
                    )
                END
                """
            ),
            reverse_sql=(
                """
                IF COL_LENGTH('Employees', 'FullName') IS NOT NULL
                BEGIN
                    ALTER TABLE Employees DROP COLUMN FullName
                END
                """
            )
        )
    ]

