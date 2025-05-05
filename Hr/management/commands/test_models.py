from django.core.management.base import BaseCommand
from Hr.models import Employee, LeaveType, EmployeeLeave


class Command(BaseCommand):
    help = 'Test the Hr models'

    def handle(self, *args, **options):
        # Test Employee model
        employee_count = Employee.objects.count()
        self.stdout.write(f'Employee count: {employee_count}')
        
        # Test LeaveType model
        leave_type_count = LeaveType.objects.count()
        self.stdout.write(f'LeaveType count: {leave_type_count}')
        
        # Test EmployeeLeave model
        employee_leave_count = EmployeeLeave.objects.count()
        self.stdout.write(f'EmployeeLeave count: {employee_leave_count}')
        
        # Create a test employee
        try:
            employee = Employee.objects.create(name='Test Employee')
            self.stdout.write(self.style.SUCCESS(f'Created employee: {employee.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating employee: {e}'))
        
        # Create a test leave type
        try:
            leave_type = LeaveType.objects.create(
                name='Test Leave Type',
                code='TEST',
                max_days_per_year=10,
                is_paid=True,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created leave type: {leave_type.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating leave type: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Test completed successfully'))