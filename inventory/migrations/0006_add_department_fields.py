# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_department_remove_invoiceitem_invoice_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='code',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='كود القسم'),
        ),
        migrations.AddField(
            model_name='department',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='الموقع'),
        ),
        migrations.AddField(
            model_name='department',
            name='manager',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='مدير القسم'),
        ),
        migrations.AddField(
            model_name='department',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='ملاحظات'),
        ),
    ]
