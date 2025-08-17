# Generated manually for enhanced education fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0031_enhanced_models_final'),
    ]

    operations = [
        # Add enhanced fields to EmployeeEducation
        migrations.AddField(
            model_name='employeeeducation',
            name='is_relevant_to_job',
            field=models.BooleanField(default=True, help_text='هل هذا المؤهل مرتبط بالوظيفة الحالية؟', verbose_name='مرتبط بالوظيفة'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='relevance_score',
            field=models.DecimalField(blank=True, decimal_places=1, help_text='درجة من 1 إلى 10 لمدى صلة المؤهل بالوظيفة', max_digits=3, null=True, verbose_name='درجة الصلة'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='is_accredited',
            field=models.BooleanField(default=False, help_text='هل المؤسسة معتمدة رسمياً؟', verbose_name='معتمد'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='accreditation_body',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='جهة الاعتماد'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='language_of_instruction',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='لغة التدريس'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='التكلفة'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='cost_currency',
            field=models.CharField(default='SAR', max_length=10, verbose_name='عملة التكلفة'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='funding_type',
            field=models.CharField(blank=True, choices=[('self', 'تمويل ذاتي'), ('company', 'تمويل الشركة'), ('scholarship', 'منحة دراسية'), ('government', 'تمويل حكومي'), ('mixed', 'تمويل مختلط')], max_length=20, null=True, verbose_name='نوع التمويل'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='delivery_mode',
            field=models.CharField(blank=True, choices=[('online', 'عبر الإنترنت'), ('offline', 'حضوري'), ('hybrid', 'مختلط')], max_length=20, null=True, verbose_name='طريقة التدريس'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='skills_gained',
            field=models.JSONField(blank=True, default=list, help_text='قائمة بالمهارات التي تم اكتسابها', verbose_name='المهارات المكتسبة'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='thesis_title',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='عنوان الرسالة/المشروع'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='thesis_supervisor',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='المشرف على الرسالة'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='has_expiry',
            field=models.BooleanField(default=False, verbose_name='له تاريخ انتهاء'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='expiry_date',
            field=models.DateField(blank=True, null=True, verbose_name='تاريخ الانتهاء'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='renewal_required',
            field=models.BooleanField(default=False, verbose_name='يتطلب تجديد'),
        ),
        migrations.AddField(
            model_name='employeeeducation',
            name='priority',
            field=models.PositiveIntegerField(default=1, help_text='1 = أعلى أولوية، 5 = أقل أولوية', verbose_name='الأولوية'),
        ),
    ]