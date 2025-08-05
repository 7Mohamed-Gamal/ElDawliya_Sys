# Generated manually to fix migration issue

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0028_hrpermission_notification_notificationdelivery_and_more'),
    ]

    operations = [
        # Skip the problematic operations for now
        migrations.RunSQL(
            "SELECT 1",  # Dummy SQL that does nothing
            reverse_sql="SELECT 1"
        ),
    ]