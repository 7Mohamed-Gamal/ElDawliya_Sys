# Generated manually to fix related_name conflicts

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0033_merge_20250806_1603'),
    ]

    operations = [
        # Fix related_name conflicts for shift assignment models
        migrations.AlterField(
            model_name='employeeshiftassignmentenhanced',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_shift_assignments_enhanced',
                to=settings.AUTH_USER_MODEL,
                verbose_name='أنشئ بواسطة'
            ),
        ),
        migrations.AlterField(
            model_name='shiftassignment',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='created_shift_assignments_basic',
                to=settings.AUTH_USER_MODEL,
                verbose_name='أنشئ بواسطة'
            ),
        ),
    ]