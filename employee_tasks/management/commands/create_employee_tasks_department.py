from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import Group
from administrator.models import Department, Module

# اسم القسم الرئيسي لمهام الموظفين
DEPARTMENT_NAME = "مهام الموظفين"

class Command(BaseCommand):
    help = 'إنشاء قسم مهام الموظفين وإضافته إلى القائمة الجانبية'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # 1. إنشاء أو الحصول على قسم مهام الموظفين
                employee_tasks_department, created = Department.objects.get_or_create(
                    name=DEPARTMENT_NAME,
                    defaults={
                        'description': 'قسم إدارة مهام الموظفين',
                        'icon': 'fas fa-tasks',
                        'url_name': 'employee_tasks',
                        'order': 5,  # ترتيب القسم في القائمة الجانبية
                        'is_active': True,
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'تم إنشاء قسم مهام الموظفين: {employee_tasks_department.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'تم استخدام قسم مهام الموظفين الموجود: {employee_tasks_department.name}'))

                # 2. إضافة المجموعات المسموح لها بالوصول إلى القسم
                admin_group, _ = Group.objects.get_or_create(name='admin')
                employee_group, _ = Group.objects.get_or_create(name='employee')
                
                # إضافة المجموعات إلى القسم
                employee_tasks_department.groups.add(admin_group)
                employee_tasks_department.groups.add(employee_group)

                # 3. إنشاء الوحدات (الموديولات) داخل القسم
                modules_data = [
                    {
                        'name': 'لوحة التحكم',
                        'icon': 'fas fa-tachometer-alt',
                        'url': '/employee-tasks/',
                        'bg_color': '#3498db',
                        'order': 1,
                    },
                    {
                        'name': 'قائمة المهام',
                        'icon': 'fas fa-list',
                        'url': '/employee-tasks/tasks/',
                        'bg_color': '#3498db',
                        'order': 2,
                    },
                    {
                        'name': 'مهامي',
                        'icon': 'fas fa-user-check',
                        'url': '/employee-tasks/tasks/my/',
                        'bg_color': '#3498db',
                        'order': 3,
                    },
                    {
                        'name': 'المهام المسندة إلي',
                        'icon': 'fas fa-clipboard-check',
                        'url': '/employee-tasks/tasks/assigned/',
                        'bg_color': '#3498db',
                        'order': 4,
                    },
                    {
                        'name': 'إنشاء مهمة جديدة',
                        'icon': 'fas fa-plus',
                        'url': '/employee-tasks/tasks/create/',
                        'bg_color': '#3498db',
                        'order': 5,
                    },
                    {
                        'name': 'التقويم',
                        'icon': 'fas fa-calendar-alt',
                        'url': '/employee-tasks/calendar/',
                        'bg_color': '#3498db',
                        'order': 6,
                    },
                    {
                        'name': 'التحليلات',
                        'icon': 'fas fa-chart-bar',
                        'url': '/employee-tasks/analytics/',
                        'bg_color': '#3498db',
                        'order': 7,
                    },
                    {
                        'name': 'التصنيفات',
                        'icon': 'fas fa-tags',
                        'url': '/employee-tasks/categories/',
                        'bg_color': '#3498db',
                        'order': 8,
                    },
                ]

                # إنشاء الوحدات
                for module_data in modules_data:
                    module, created = Module.objects.get_or_create(
                        department=employee_tasks_department,
                        name=module_data['name'],
                        defaults={
                            'icon': module_data['icon'],
                            'url': module_data['url'],
                            'bg_color': module_data['bg_color'],
                            'order': module_data['order'],
                            'is_active': True,
                        }
                    )

                    # إضافة المجموعات إلى الوحدة
                    module.groups.add(admin_group)
                    module.groups.add(employee_group)

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'تم إنشاء وحدة: {module.name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'تم تحديث وحدة: {module.name}'))

                self.stdout.write(self.style.SUCCESS('تم إنشاء قسم مهام الموظفين والوحدات بنجاح'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'حدث خطأ: {str(e)}'))
