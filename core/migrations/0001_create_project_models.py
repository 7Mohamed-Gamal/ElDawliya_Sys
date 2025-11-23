# Generated migration for project models

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),  # Depends on base models
    ]

    operations = [
        # Project Category
        migrations.CreateModel(
            name='ProjectCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='تاريخ ووقت إنشاء السجل', verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='تاريخ ووقت آخر تحديث للسجل', verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, help_text='هل هذا السجل نشط أم لا', verbose_name='نشط')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='اسم التصنيف')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف التصنيف')),
                ('color', models.CharField(default='#3498db', help_text='لون التصنيف بصيغة HEX', max_length=7, verbose_name='اللون')),
                ('icon', models.CharField(default='fas fa-project-diagram', max_length=50, verbose_name='الأيقونة')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='core.projectcategory', verbose_name='التصنيف الأب')),
                ('updated_by', models.ForeignKey(blank=True, help_text='المستخدم الذي قام بآخر تحديث لهذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'تصنيف المشروع',
                'verbose_name_plural': 'تصنيفات المشاريع',
                'db_table': 'project_categories',
                'ordering': ['name'],
            },
        ),
        
        # Project
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='تاريخ ووقت إنشاء السجل', verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='تاريخ ووقت آخر تحديث للسجل', verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, help_text='هل هذا السجل نشط أم لا', verbose_name='نشط')),
                ('version', models.PositiveIntegerField(default=1, help_text='رقم إصدار السجل للتتبع', verbose_name='رقم الإصدار')),
                ('notes', models.TextField(blank=True, help_text='ملاحظات إضافية حول السجل', null=True, verbose_name='ملاحظات')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='تاريخ ووقت حذف السجل', null=True, verbose_name='تاريخ الحذف')),
                ('name', models.CharField(max_length=200, verbose_name='اسم المشروع')),
                ('code', models.CharField(help_text='رمز فريد للمشروع', max_length=20, unique=True, verbose_name='رمز المشروع')),
                ('description', models.TextField(verbose_name='وصف المشروع')),
                ('status', models.CharField(choices=[('planning', 'تخطيط'), ('active', 'نشط'), ('on_hold', 'معلق'), ('completed', 'مكتمل'), ('cancelled', 'ملغي'), ('archived', 'مؤرشف')], default='planning', max_length=20, verbose_name='حالة المشروع')),
                ('priority', models.CharField(choices=[('low', 'منخفضة'), ('medium', 'متوسطة'), ('high', 'عالية'), ('critical', 'حرجة')], default='medium', max_length=20, verbose_name='الأولوية')),
                ('start_date', models.DateField(verbose_name='تاريخ البدء')),
                ('end_date', models.DateField(verbose_name='تاريخ الانتهاء المخطط')),
                ('actual_end_date', models.DateField(blank=True, null=True, verbose_name='تاريخ الانتهاء الفعلي')),
                ('budget', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='الميزانية')),
                ('actual_cost', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='التكلفة الفعلية')),
                ('progress_percentage', models.PositiveIntegerField(default=0, help_text='من 0 إلى 100', verbose_name='نسبة الإنجاز (%)')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects', to='core.projectcategory', verbose_name='التصنيف')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('deleted_by', models.ForeignKey(blank=True, help_text='المستخدم الذي حذف هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_deleted', to=settings.AUTH_USER_MODEL, verbose_name='حُذف بواسطة')),
                ('manager', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_projects', to=settings.AUTH_USER_MODEL, verbose_name='مدير المشروع')),
                ('parent_project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subprojects', to='core.project', verbose_name='المشروع الأب')),
                ('updated_by', models.ForeignKey(blank=True, help_text='المستخدم الذي قام بآخر تحديث لهذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'مشروع',
                'verbose_name_plural': 'المشاريع',
                'db_table': 'projects',
                'ordering': ['-created_at'],
                'permissions': [('view_project_dashboard', 'Can view project dashboard'), ('manage_project_team', 'Can manage project team'), ('view_project_reports', 'Can view project reports'), ('export_project_data', 'Can export project data')],
            },
        ),
        
        # Project Phase
        migrations.CreateModel(
            name='ProjectPhase',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='تاريخ ووقت إنشاء السجل', verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='تاريخ ووقت آخر تحديث للسجل', verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, help_text='هل هذا السجل نشط أم لا', verbose_name='نشط')),
                ('version', models.PositiveIntegerField(default=1, help_text='رقم إصدار السجل للتتبع', verbose_name='رقم الإصدار')),
                ('notes', models.TextField(blank=True, help_text='ملاحظات إضافية حول السجل', null=True, verbose_name='ملاحظات')),
                ('name', models.CharField(max_length=200, verbose_name='اسم المرحلة')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف المرحلة')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='الترتيب')),
                ('status', models.CharField(choices=[('not_started', 'لم تبدأ'), ('in_progress', 'قيد التنفيذ'), ('completed', 'مكتملة'), ('on_hold', 'معلقة'), ('cancelled', 'ملغاة')], default='not_started', max_length=20, verbose_name='الحالة')),
                ('start_date', models.DateField(verbose_name='تاريخ البدء')),
                ('end_date', models.DateField(verbose_name='تاريخ الانتهاء المخطط')),
                ('actual_end_date', models.DateField(blank=True, null=True, verbose_name='تاريخ الانتهاء الفعلي')),
                ('progress_percentage', models.PositiveIntegerField(default=0, help_text='من 0 إلى 100', verbose_name='نسبة الإنجاز (%)')),
                ('budget', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='ميزانية المرحلة')),
                ('actual_cost', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='التكلفة الفعلية')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phases', to='core.project', verbose_name='المشروع')),
                ('responsible_person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='responsible_phases', to=settings.AUTH_USER_MODEL, verbose_name='المسؤول عن المرحلة')),
                ('updated_by', models.ForeignKey(blank=True, help_text='المستخدم الذي قام بآخر تحديث لهذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'مرحلة مشروع',
                'verbose_name_plural': 'مراحل المشاريع',
                'db_table': 'project_phases',
                'ordering': ['project', 'order'],
            },
        ),
        
        # Project Milestone
        migrations.CreateModel(
            name='ProjectMilestone',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='تاريخ ووقت إنشاء السجل', verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='تاريخ ووقت آخر تحديث للسجل', verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, help_text='هل هذا السجل نشط أم لا', verbose_name='نشط')),
                ('version', models.PositiveIntegerField(default=1, help_text='رقم إصدار السجل للتتبع', verbose_name='رقم الإصدار')),
                ('notes', models.TextField(blank=True, help_text='ملاحظات إضافية حول السجل', null=True, verbose_name='ملاحظات')),
                ('name', models.CharField(max_length=200, verbose_name='اسم المعلم')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف المعلم')),
                ('target_date', models.DateField(verbose_name='التاريخ المستهدف')),
                ('actual_date', models.DateField(blank=True, null=True, verbose_name='التاريخ الفعلي')),
                ('status', models.CharField(choices=[('pending', 'قيد الانتظار'), ('achieved', 'تم تحقيقه'), ('missed', 'فائت'), ('cancelled', 'ملغي')], default='pending', max_length=20, verbose_name='الحالة')),
                ('importance', models.PositiveIntegerField(default=5, help_text='من 1 إلى 10', verbose_name='الأهمية')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('phase', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='core.projectphase', verbose_name='المرحلة')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='core.project', verbose_name='المشروع')),
                ('updated_by', models.ForeignKey(blank=True, help_text='المستخدم الذي قام بآخر تحديث لهذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'معلم مشروع',
                'verbose_name_plural': 'معالم المشاريع',
                'db_table': 'project_milestones',
                'ordering': ['project', 'target_date'],
            },
        ),
        
        # Project Member
        migrations.CreateModel(
            name='ProjectMember',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='تاريخ ووقت إنشاء السجل', verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='تاريخ ووقت آخر تحديث للسجل', verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, help_text='هل هذا السجل نشط أم لا', verbose_name='نشط')),
                ('role', models.CharField(choices=[('manager', 'مدير المشروع'), ('lead', 'قائد الفريق'), ('developer', 'مطور'), ('analyst', 'محلل'), ('designer', 'مصمم'), ('tester', 'مختبر'), ('consultant', 'استشاري'), ('stakeholder', 'صاحب مصلحة'), ('observer', 'مراقب')], default='developer', max_length=20, verbose_name='الدور')),
                ('joined_date', models.DateField(default=django.utils.timezone.now, verbose_name='تاريخ الانضمام')),
                ('left_date', models.DateField(blank=True, null=True, verbose_name='تاريخ المغادرة')),
                ('hourly_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='المعدل بالساعة')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='core.project', verbose_name='المشروع')),
                ('updated_by', models.ForeignKey(blank=True, help_text='المستخدم الذي قام بآخر تحديث لهذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_memberships', to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'عضو فريق المشروع',
                'verbose_name_plural': 'أعضاء فرق المشاريع',
                'db_table': 'project_members',
            },
        ),
        
        # Task
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='تاريخ ووقت إنشاء السجل', verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='تاريخ ووقت آخر تحديث للسجل', verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, help_text='هل هذا السجل نشط أم لا', verbose_name='نشط')),
                ('version', models.PositiveIntegerField(default=1, help_text='رقم إصدار السجل للتتبع', verbose_name='رقم الإصدار')),
                ('notes', models.TextField(blank=True, help_text='ملاحظات إضافية حول السجل', null=True, verbose_name='ملاحظات')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='تاريخ ووقت حذف السجل', null=True, verbose_name='تاريخ الحذف')),
                ('title', models.CharField(max_length=200, verbose_name='عنوان المهمة')),
                ('description', models.TextField(verbose_name='وصف المهمة')),
                ('task_type', models.CharField(choices=[('regular', 'مهمة عادية'), ('meeting', 'مهمة اجتماع'), ('milestone', 'مهمة معلم'), ('phase', 'مهمة مرحلة')], default='regular', max_length=20, verbose_name='نوع المهمة')),
                ('status', models.CharField(choices=[('pending', 'قيد الانتظار'), ('in_progress', 'قيد التنفيذ'), ('completed', 'مكتملة'), ('cancelled', 'ملغاة'), ('deferred', 'مؤجلة'), ('blocked', 'محجوبة')], default='pending', max_length=20, verbose_name='الحالة')),
                ('priority', models.CharField(choices=[('low', 'منخفضة'), ('medium', 'متوسطة'), ('high', 'عالية'), ('urgent', 'عاجلة'), ('critical', 'حرجة')], default='medium', max_length=20, verbose_name='الأولوية')),
                ('start_date', models.DateTimeField(verbose_name='تاريخ البدء')),
                ('due_date', models.DateTimeField(verbose_name='تاريخ الاستحقاق')),
                ('completed_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الإنجاز')),
                ('estimated_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='الساعات المقدرة')),
                ('actual_hours', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='الساعات الفعلية')),
                ('progress_percentage', models.PositiveIntegerField(default=0, help_text='من 0 إلى 100', verbose_name='نسبة الإنجاز (%)')),
                ('is_private', models.BooleanField(default=False, help_text='إذا كان خاصًا، فلن يراه إلا المنشئ والمكلف', verbose_name='خاص')),
                ('tags', models.CharField(blank=True, help_text='علامات مفصولة بفواصل', max_length=500, null=True, verbose_name='العلامات')),
                ('assigned_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL, verbose_name='مكلف إلى')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('deleted_by', models.ForeignKey(blank=True, help_text='المستخدم الذي حذف هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_deleted', to=settings.AUTH_USER_MODEL, verbose_name='حُذف بواسطة')),
                ('milestone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='core.projectmilestone', verbose_name='المعلم')),
                ('parent_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subtasks', to='core.task', verbose_name='المهمة الأب')),
                ('phase', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='core.projectphase', verbose_name='المرحلة')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='core.project', verbose_name='المشروع')),
                ('updated_by', models.ForeignKey(blank=True, help_text='المستخدم الذي قام بآخر تحديث لهذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'مهمة',
                'verbose_name_plural': 'المهام',
                'db_table': 'tasks',
                'ordering': ['-created_at'],
                'permissions': [('view_task_dashboard', 'Can view task dashboard'), ('view_all_tasks', 'Can view all tasks'), ('manage_task_assignments', 'Can manage task assignments'), ('view_task_reports', 'Can view task reports'), ('export_task_data', 'Can export task data')],
            },
        ),
        
        # Task Step
        migrations.CreateModel(
            name='TaskStep',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='تاريخ ووقت إنشاء السجل', verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='تاريخ ووقت آخر تحديث للسجل', verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, help_text='هل هذا السجل نشط أم لا', verbose_name='نشط')),
                ('description', models.TextField(verbose_name='وصف الخطوة')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('completed', models.BooleanField(default=False, verbose_name='مكتملة')),
                ('completion_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الإنجاز')),
                ('hours_spent', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='الساعات المستغرقة')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='core.task', verbose_name='المهمة')),
                ('updated_by', models.ForeignKey(blank=True, help_text='المستخدم الذي قام بآخر تحديث لهذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'خطوة مهمة',
                'verbose_name_plural': 'خطوات المهام',
                'db_table': 'task_steps',
                'ordering': ['-created_at'],
            },
        ),
        
        # Time Entry
        migrations.CreateModel(
            name='TimeEntry',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='تاريخ ووقت إنشاء السجل', verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='تاريخ ووقت آخر تحديث للسجل', verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, help_text='هل هذا السجل نشط أم لا', verbose_name='نشط')),
                ('start_time', models.DateTimeField(verbose_name='وقت البدء')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='وقت الانتهاء')),
                ('duration_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='المدة بالساعات')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف العمل المنجز')),
                ('is_billable', models.BooleanField(default=True, verbose_name='قابل للفوترة')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_entries', to='core.task', verbose_name='المهمة')),
                ('updated_by', models.ForeignKey(blank=True, help_text='المستخدم الذي قام بآخر تحديث لهذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_entries', to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'إدخال وقت',
                'verbose_name_plural': 'إدخالات الوقت',
                'db_table': 'time_entries',
                'ordering': ['-start_time'],
            },
        ),
        
        # Meeting
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='تاريخ ووقت إنشاء السجل', verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='تاريخ ووقت آخر تحديث للسجل', verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, help_text='هل هذا السجل نشط أم لا', verbose_name='نشط')),
                ('version', models.PositiveIntegerField(default=1, help_text='رقم إصدار السجل للتتبع', verbose_name='رقم الإصدار')),
                ('notes', models.TextField(blank=True, help_text='ملاحظات إضافية حول السجل', null=True, verbose_name='ملاحظات')),
                ('title', models.CharField(max_length=200, verbose_name='عنوان الاجتماع')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف الاجتماع')),
                ('meeting_type', models.CharField(choices=[('project', 'اجتماع مشروع'), ('team', 'اجتماع فريق'), ('client', 'اجتماع عميل'), ('review', 'اجتماع مراجعة'), ('planning', 'اجتماع تخطيط'), ('standup', 'اجتماع يومي'), ('other', 'أخرى')], default='team', max_length=20, verbose_name='نوع الاجتماع')),
                ('start_datetime', models.DateTimeField(verbose_name='تاريخ ووقت البدء')),
                ('end_datetime', models.DateTimeField(verbose_name='تاريخ ووقت الانتهاء')),
                ('location', models.CharField(blank=True, max_length=200, null=True, verbose_name='المكان')),
                ('virtual_link', models.URLField(blank=True, null=True, verbose_name='رابط الاجتماع الافتراضي')),
                ('status', models.CharField(choices=[('scheduled', 'مجدول'), ('in_progress', 'قيد التنفيذ'), ('completed', 'مكتمل'), ('cancelled', 'ملغي'), ('postponed', 'مؤجل')], default='scheduled', max_length=20, verbose_name='حالة الاجتماع')),
                ('agenda', models.TextField(blank=True, null=True, verbose_name='جدول الأعمال')),
                ('minutes', models.TextField(blank=True, null=True, verbose_name='محضر الاجتماع')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organized_meetings', to=settings.AUTH_USER_MODEL, verbose_name='منظم الاجتماع')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='core.project', verbose_name='المشروع المرتبط')),
                ('updated_by', models.ForeignKey(blank=True, help_text='المستخدم الذي قام بآخر تحديث لهذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'اجتماع',
                'verbose_name_plural': 'الاجتماعات',
                'db_table': 'meetings',
                'ordering': ['-start_datetime'],
                'permissions': [('view_meeting_dashboard', 'Can view meeting dashboard'), ('manage_meeting_attendees', 'Can manage meeting attendees'), ('view_meeting_reports', 'Can view meeting reports'), ('export_meeting_data', 'Can export meeting data')],
            },
        ),
        
        # Meeting Attendee
        migrations.CreateModel(
            name='MeetingAttendee',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='تاريخ ووقت إنشاء السجل', verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='تاريخ ووقت آخر تحديث للسجل', verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, help_text='هل هذا السجل نشط أم لا', verbose_name='نشط')),
                ('role', models.CharField(choices=[('organizer', 'منظم'), ('presenter', 'مقدم'), ('participant', 'مشارك'), ('observer', 'مراقب'), ('required', 'مطلوب'), ('optional', 'اختياري')], default='participant', max_length=20, verbose_name='الدور')),
                ('attendance_status', models.CharField(choices=[('invited', 'مدعو'), ('accepted', 'قبل'), ('declined', 'رفض'), ('tentative', 'مؤقت'), ('attended', 'حضر'), ('absent', 'غائب')], default='invited', max_length=20, verbose_name='حالة الحضور')),
                ('response_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الرد')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendee_records', to='core.meeting', verbose_name='الاجتماع')),
                ('updated_by', models.ForeignKey(blank=True, help_text='المستخدم الذي قام بآخر تحديث لهذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meeting_attendances', to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'حضور اجتماع',
                'verbose_name_plural': 'حضور الاجتماعات',
                'db_table': 'meeting_attendees',
            },
        ),
        
        # Document
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='المعرف الفريد')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='تاريخ ووقت إنشاء السجل', verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='تاريخ ووقت آخر تحديث للسجل', verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, help_text='هل هذا السجل نشط أم لا', verbose_name='نشط')),
                ('version', models.PositiveIntegerField(default=1, help_text='رقم إصدار السجل للتتبع', verbose_name='رقم الإصدار')),
                ('notes', models.TextField(blank=True, help_text='ملاحظات إضافية حول السجل', null=True, verbose_name='ملاحظات')),
                ('deleted_at', models.DateTimeField(blank=True, help_text='تاريخ ووقت حذف السجل', null=True, verbose_name='تاريخ الحذف')),
                ('name', models.CharField(max_length=200, verbose_name='اسم الوثيقة')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف الوثيقة')),
                ('document_type', models.CharField(choices=[('project_doc', 'وثيقة مشروع'), ('meeting_doc', 'وثيقة اجتماع'), ('task_doc', 'وثيقة مهمة'), ('contract', 'عقد'), ('specification', 'مواصفات'), ('report', 'تقرير'), ('presentation', 'عرض تقديمي'), ('image', 'صورة'), ('other', 'أخرى')], default='other', max_length=20, verbose_name='نوع الوثيقة')),
                ('file', models.FileField(upload_to='documents/%Y/%m/', verbose_name='الملف')),
                ('file_size', models.PositiveIntegerField(blank=True, null=True, verbose_name='حجم الملف (بايت)')),
                ('mime_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='نوع MIME')),
                ('version', models.CharField(default='1.0', max_length=20, verbose_name='الإصدار')),
                ('is_confidential', models.BooleanField(default=False, verbose_name='سري')),
                ('tags', models.CharField(blank=True, help_text='علامات مفصولة بفواصل', max_length=500, null=True, verbose_name='العلامات')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('deleted_by', models.ForeignKey(blank=True, help_text='المستخدم الذي حذف هذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_deleted', to=settings.AUTH_USER_MODEL, verbose_name='حُذف بواسطة')),
                ('meeting', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='core.meeting', verbose_name='الاجتماع')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='core.project', verbose_name='المشروع')),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='core.task', verbose_name='المهمة')),
                ('updated_by', models.ForeignKey(blank=True, help_text='المستخدم الذي قام بآخر تحديث لهذا السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'وثيقة',
                'verbose_name_plural': 'الوثائق',
                'db_table': 'documents',
                'ordering': ['-created_at'],
                'permissions': [('view_confidential_documents', 'Can view confidential documents'), ('manage_document_versions', 'Can manage document versions')],
            },
        ),
        
        # Add many-to-many relationship for project team members
        migrations.AddField(
            model_name='project',
            name='team_members',
            field=models.ManyToManyField(related_name='projects', through='core.ProjectMember', to=settings.AUTH_USER_MODEL, verbose_name='أعضاء الفريق'),
        ),
        
        # Add many-to-many relationship for meeting attendees
        migrations.AddField(
            model_name='meeting',
            name='attendees',
            field=models.ManyToManyField(related_name='meetings', through='core.MeetingAttendee', to=settings.AUTH_USER_MODEL, verbose_name='الحضور'),
        ),
        
        # Add many-to-many relationship for project member permissions
        migrations.AddField(
            model_name='projectmember',
            name='permissions',
            field=models.ManyToManyField(blank=True, related_name='project_members', to='core.permission', verbose_name='الصلاحيات'),
        ),
        
        # Add constraints and indexes
        migrations.AlterUniqueTogether(
            name='projectphase',
            unique_together={('project', 'order')},
        ),
        migrations.AlterUniqueTogether(
            name='projectmember',
            unique_together={('project', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='meetingattendee',
            unique_together={('meeting', 'user')},
        ),
        
        # Add database indexes
        migrations.RunSQL(
            "CREATE INDEX idx_projects_status ON projects(status);",
            reverse_sql="DROP INDEX idx_projects_status ON projects;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_projects_priority ON projects(priority);",
            reverse_sql="DROP INDEX idx_projects_priority ON projects;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_projects_manager ON projects(manager_id);",
            reverse_sql="DROP INDEX idx_projects_manager ON projects;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_projects_start_date ON projects(start_date);",
            reverse_sql="DROP INDEX idx_projects_start_date ON projects;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_projects_end_date ON projects(end_date);",
            reverse_sql="DROP INDEX idx_projects_end_date ON projects;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_projects_category ON projects(category_id);",
            reverse_sql="DROP INDEX idx_projects_category ON projects;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_project_phases_project_status ON project_phases(project_id, status);",
            reverse_sql="DROP INDEX idx_project_phases_project_status ON project_phases;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_project_phases_start_date ON project_phases(start_date);",
            reverse_sql="DROP INDEX idx_project_phases_start_date ON project_phases;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_project_phases_end_date ON project_phases(end_date);",
            reverse_sql="DROP INDEX idx_project_phases_end_date ON project_phases;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_project_milestones_project_status ON project_milestones(project_id, status);",
            reverse_sql="DROP INDEX idx_project_milestones_project_status ON project_milestones;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_project_milestones_target_date ON project_milestones(target_date);",
            reverse_sql="DROP INDEX idx_project_milestones_target_date ON project_milestones;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_project_milestones_phase ON project_milestones(phase_id);",
            reverse_sql="DROP INDEX idx_project_milestones_phase ON project_milestones;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_project_members_project_role ON project_members(project_id, role);",
            reverse_sql="DROP INDEX idx_project_members_project_role ON project_members;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_project_members_user ON project_members(user_id);",
            reverse_sql="DROP INDEX idx_project_members_user ON project_members;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_tasks_status ON tasks(status);",
            reverse_sql="DROP INDEX idx_tasks_status ON tasks;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_tasks_priority ON tasks(priority);",
            reverse_sql="DROP INDEX idx_tasks_priority ON tasks;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to_id);",
            reverse_sql="DROP INDEX idx_tasks_assigned_to ON tasks;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_tasks_project ON tasks(project_id);",
            reverse_sql="DROP INDEX idx_tasks_project ON tasks;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_tasks_due_date ON tasks(due_date);",
            reverse_sql="DROP INDEX idx_tasks_due_date ON tasks;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_tasks_task_type ON tasks(task_type);",
            reverse_sql="DROP INDEX idx_tasks_task_type ON tasks;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_tasks_status_assigned_to ON tasks(status, assigned_to_id);",
            reverse_sql="DROP INDEX idx_tasks_status_assigned_to ON tasks;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);",
            reverse_sql="DROP INDEX idx_tasks_project_status ON tasks;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_task_steps_task ON task_steps(task_id);",
            reverse_sql="DROP INDEX idx_task_steps_task ON task_steps;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_task_steps_completed ON task_steps(completed);",
            reverse_sql="DROP INDEX idx_task_steps_completed ON task_steps;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_time_entries_task_user ON time_entries(task_id, user_id);",
            reverse_sql="DROP INDEX idx_time_entries_task_user ON time_entries;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_time_entries_start_time ON time_entries(start_time);",
            reverse_sql="DROP INDEX idx_time_entries_start_time ON time_entries;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_time_entries_user ON time_entries(user_id);",
            reverse_sql="DROP INDEX idx_time_entries_user ON time_entries;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_meetings_start_datetime ON meetings(start_datetime);",
            reverse_sql="DROP INDEX idx_meetings_start_datetime ON meetings;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_meetings_status ON meetings(status);",
            reverse_sql="DROP INDEX idx_meetings_status ON meetings;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_meetings_project ON meetings(project_id);",
            reverse_sql="DROP INDEX idx_meetings_project ON meetings;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_meetings_organizer ON meetings(organizer_id);",
            reverse_sql="DROP INDEX idx_meetings_organizer ON meetings;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_meeting_attendees_meeting_status ON meeting_attendees(meeting_id, attendance_status);",
            reverse_sql="DROP INDEX idx_meeting_attendees_meeting_status ON meeting_attendees;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_meeting_attendees_user ON meeting_attendees(user_id);",
            reverse_sql="DROP INDEX idx_meeting_attendees_user ON meeting_attendees;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_documents_document_type ON documents(document_type);",
            reverse_sql="DROP INDEX idx_documents_document_type ON documents;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_documents_project ON documents(project_id);",
            reverse_sql="DROP INDEX idx_documents_project ON documents;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_documents_task ON documents(task_id);",
            reverse_sql="DROP INDEX idx_documents_task ON documents;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_documents_meeting ON documents(meeting_id);",
            reverse_sql="DROP INDEX idx_documents_meeting ON documents;"
        ),
    ]