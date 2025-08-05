# Generated manually to fix migration issue

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0029_fix_migration'),
    ]

    operations = [
        # Skip problematic operations for now
        migrations.RunSQL(
            "SELECT 1",  # Dummy SQL that does nothing
            reverse_sql="SELECT 1"
        ),
    ]