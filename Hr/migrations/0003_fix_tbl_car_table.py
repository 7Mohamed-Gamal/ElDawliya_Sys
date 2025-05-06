# Generated manually to fix the Tbl_Car table issue

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0002_initial'),
    ]

    operations = [
        # This migration checks if the Tbl_Car table already exists and skips creating it if it does
        migrations.RunSQL(
            """
            IF OBJECT_ID('Tbl_Car', 'U') IS NOT NULL
            BEGIN
                -- Table already exists, do nothing
                PRINT 'Tbl_Car table already exists, skipping creation'
            END
            """,
            reverse_sql="SELECT 1"  # No-op for reversing
        ),
    ]
