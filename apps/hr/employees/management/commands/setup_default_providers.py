"""
Management command to set up default health insurance providers and work schedules
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import time
from decimal import Decimal
from apps.hr.employees.models_extended import ExtendedHealthInsuranceProvider, WorkSchedule


class Command(BaseCommand):
    """Command class"""
    help = 'Set up default health insurance providers and work schedules for the system'

    def add_arguments(self, parser):
        """add_arguments function"""
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if providers already exist',
        )

    def handle(self, *args, **options):
        """handle function"""
        self.stdout.write(self.style.SUCCESS('Setting up default health insurance providers and work schedules...'))

        # Setup health insurance providers
        self.setup_health_insurance_providers(options)

        # Setup work schedules
        self.setup_work_schedules(options)

        self.stdout.write(
            self.style.SUCCESS('\n🎉 All default data setup completed successfully!')
        )

    def setup_health_insurance_providers(self, options):
        """Set up default health insurance providers"""
        self.stdout.write(self.style.SUCCESS('\n📋 Setting up health insurance providers...'))

        providers_data = [
            {
                'provider_code': 'DEFAULT',
                'provider_name': 'مقدم خدمة افتراضي',
                'contact_person': 'غير محدد',
                'phone': '',
                'email': '',
                'address': '',
                'is_active': True,
            },
            {
                'provider_code': 'BUPA',
                'provider_name': 'بوبا العربية للتأمين الصحي',
                'contact_person': 'خدمة العملاء',
                'phone': '920003344',
                'email': 'info@bupa.com.sa',
                'address': 'الرياض، المملكة العربية السعودية',
                'is_active': True,
            },
            {
                'provider_code': 'TAWUNIYA',
                'provider_name': 'الشركة التعاونية للتأمين',
                'contact_person': 'خدمة العملاء',
                'phone': '920001177',
                'email': 'info@tawuniya.com.sa',
                'address': 'الرياض، المملكة العربية السعودية',
                'is_active': True,
            },
            {
                'provider_code': 'MEDGULF',
                'provider_name': 'الخليج للتأمين التعاوني',
                'contact_person': 'خدمة العملاء',
                'phone': '920000342',
                'email': 'info@medgulf.com.sa',
                'address': 'الرياض، المملكة العربية السعودية',
                'is_active': True,
            },
        ]

        created_count = 0
        updated_count = 0

        try:
            with transaction.atomic():
                for provider_data in providers_data:
                    provider, created = ExtendedHealthInsuranceProvider.objects.get_or_create(
                        provider_code=provider_data['provider_code'],
                        defaults=provider_data
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Created provider: {provider.provider_name}')
                        )
                    else:
                        if options['force']:
                            # Update existing provider
                            for key, value in provider_data.items():
                                if key != 'provider_code':
                                    setattr(provider, key, value)
                            provider.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'↻ Updated provider: {provider.provider_name}')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'- Provider already exists: {provider.provider_name}')
                            )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Health insurance providers setup completed!'
                        f'\n- Created: {created_count} providers'
                        f'\n- Updated: {updated_count} providers'
                        f'\n- Total providers in system: {ExtendedHealthInsuranceProvider.objects.count()}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error setting up providers: {str(e)}')
            )
            raise

    def setup_work_schedules(self, options):
        """Set up default work schedules"""
        self.stdout.write(self.style.SUCCESS('\n⏰ Setting up work schedules...'))

        schedules_data = [
            {
                'schedule_code': 'DEFAULT',
                'schedule_name': 'جدول عمل افتراضي',
                'daily_hours': Decimal('8.00'),
                'weekly_hours': Decimal('40.00'),
                'start_time': time(8, 0),
                'end_time': time(16, 0),
                'break_duration': 60,
                'is_flexible': False,
                'overtime_applicable': True,
                'is_active': True,
                'description': 'جدول العمل الافتراضي للنظام - 8 ساعات يومياً من 8 صباحاً إلى 4 عصراً',
            },
            {
                'schedule_code': 'STANDARD',
                'schedule_name': 'جدول العمل القياسي',
                'daily_hours': Decimal('8.00'),
                'weekly_hours': Decimal('40.00'),
                'start_time': time(9, 0),
                'end_time': time(17, 0),
                'break_duration': 60,
                'is_flexible': False,
                'overtime_applicable': True,
                'is_active': True,
                'description': 'جدول العمل القياسي - 8 ساعات يومياً من 9 صباحاً إلى 5 مساءً',
            },
            {
                'schedule_code': 'FLEXIBLE',
                'schedule_name': 'جدول عمل مرن',
                'daily_hours': Decimal('8.00'),
                'weekly_hours': Decimal('40.00'),
                'start_time': time(8, 0),
                'end_time': time(16, 0),
                'break_duration': 60,
                'is_flexible': True,
                'overtime_applicable': True,
                'is_active': True,
                'description': 'جدول عمل مرن يسمح بتعديل أوقات الحضور والانصراف',
            },
            {
                'schedule_code': 'PART_TIME',
                'schedule_name': 'دوام جزئي',
                'daily_hours': Decimal('4.00'),
                'weekly_hours': Decimal('20.00'),
                'start_time': time(9, 0),
                'end_time': time(13, 0),
                'break_duration': 0,
                'is_flexible': False,
                'overtime_applicable': False,
                'is_active': True,
                'description': 'دوام جزئي - 4 ساعات يومياً',
            },
        ]

        created_count = 0
        updated_count = 0

        try:
            with transaction.atomic():
                for schedule_data in schedules_data:
                    schedule, created = WorkSchedule.objects.get_or_create(
                        schedule_code=schedule_data['schedule_code'],
                        defaults=schedule_data
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Created work schedule: {schedule.schedule_name}')
                        )
                    else:
                        if options['force']:
                            # Update existing schedule
                            for key, value in schedule_data.items():
                                if key != 'schedule_code':
                                    setattr(schedule, key, value)
                            schedule.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'↻ Updated work schedule: {schedule.schedule_name}')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'- Work schedule already exists: {schedule.schedule_name}')
                            )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Work schedules setup completed!'
                        f'\n- Created: {created_count} schedules'
                        f'\n- Updated: {updated_count} schedules'
                        f'\n- Total schedules in system: {WorkSchedule.objects.count()}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error setting up work schedules: {str(e)}')
            )
            raise

    def get_version(self):
        """get_version function"""
        return '1.0.0'
