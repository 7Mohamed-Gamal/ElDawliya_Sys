from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix migration history for Hr app'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Delete the problematic migration records
            cursor.execute("""
                DELETE FROM django_migrations
                WHERE app = 'Hr' AND name IN (
                    '0010_create_leavetype_table',
                    '0011_create_employeeleave_table',
                    '0010_create_employee_table'
                );
            """)
            
            self.stdout.write(self.style.SUCCESS('Successfully fixed migration history'))