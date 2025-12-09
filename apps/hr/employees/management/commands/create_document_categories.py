"""
Management command to create default employee document categories
"""
from django.core.management.base import BaseCommand
from apps.hr.employees.models_extended import EmployeeDocumentCategory


class Command(BaseCommand):
    """Command class"""
    help = 'Create default employee document categories'

    def handle(self, *args, **options):
        """handle function"""
        categories = [
            {
                'category_name': 'عقد العمل',
                'category_code': 'CONTRACT',
                'description': 'عقود العمل والاتفاقيات الوظيفية',
                'is_required': True,
                'max_file_size_mb': 10,
                'allowed_extensions': 'pdf,doc,docx',
                'sort_order': 1
            },
            {
                'category_name': 'صورة الهوية الوطنية',
                'category_code': 'NATIONAL_ID',
                'description': 'صورة من الهوية الوطنية أو الإقامة',
                'is_required': True,
                'max_file_size_mb': 5,
                'allowed_extensions': 'pdf,jpg,jpeg,png',
                'sort_order': 2
            },
            {
                'category_name': 'صورة جواز السفر',
                'category_code': 'PASSPORT',
                'description': 'صورة من جواز السفر',
                'is_required': False,
                'max_file_size_mb': 5,
                'allowed_extensions': 'pdf,jpg,jpeg,png',
                'sort_order': 3
            },
            {
                'category_name': 'الشهادات العلمية',
                'category_code': 'CERTIFICATES',
                'description': 'الشهادات الجامعية والدبلومات والدورات',
                'is_required': True,
                'max_file_size_mb': 10,
                'allowed_extensions': 'pdf,jpg,jpeg,png',
                'sort_order': 4
            },
            {
                'category_name': 'شهادات الخبرة',
                'category_code': 'EXPERIENCE',
                'description': 'شهادات الخبرة من أماكن العمل السابقة',
                'is_required': False,
                'max_file_size_mb': 10,
                'allowed_extensions': 'pdf,doc,docx,jpg,jpeg,png',
                'sort_order': 5
            },
            {
                'category_name': 'التقارير الطبية',
                'category_code': 'MEDICAL',
                'description': 'التقارير والشهادات الطبية',
                'is_required': False,
                'max_file_size_mb': 10,
                'allowed_extensions': 'pdf,jpg,jpeg,png',
                'sort_order': 6
            },
            {
                'category_name': 'صورة شخصية',
                'category_code': 'PHOTO',
                'description': 'الصورة الشخصية للموظف',
                'is_required': True,
                'max_file_size_mb': 2,
                'allowed_extensions': 'jpg,jpeg,png',
                'sort_order': 7
            },
            {
                'category_name': 'وثائق التأمين',
                'category_code': 'INSURANCE',
                'description': 'وثائق التأمين الصحي والاجتماعي',
                'is_required': False,
                'max_file_size_mb': 10,
                'allowed_extensions': 'pdf,doc,docx,jpg,jpeg,png',
                'sort_order': 8
            },
            {
                'category_name': 'وثائق أخرى',
                'category_code': 'OTHER',
                'description': 'وثائق ومستندات أخرى متنوعة',
                'is_required': False,
                'max_file_size_mb': 15,
                'allowed_extensions': 'pdf,doc,docx,jpg,jpeg,png',
                'sort_order': 9
            }
        ]

        created_count = 0
        updated_count = 0

        for category_data in categories:
            category, created = EmployeeDocumentCategory.objects.get_or_create(
                category_code=category_data['category_code'],
                defaults=category_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.category_name}')
                )
            else:
                # Update existing category
                for key, value in category_data.items():
                    if key != 'category_code':
                        setattr(category, key, value)
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated category: {category.category_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {created_count + updated_count} document categories '
                f'({created_count} created, {updated_count} updated)'
            )
        )
