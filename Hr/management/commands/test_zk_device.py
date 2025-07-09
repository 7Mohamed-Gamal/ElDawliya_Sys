"""
Management command to test ZK device connection and functionality
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from Hr.utils import ZKDeviceService, AttendanceProcessor
from Hr.models.attendance_models import HrAttendanceMachine as AttendanceMachine


class Command(BaseCommand):
    help = 'Test ZK device connection and functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ip',
            type=str,
            default='192.168.1.201',
            help='IP address of the ZK device'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=4370,
            help='Port of the ZK device'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='',
            help='Password for the ZK device'
        )
        parser.add_argument(
            '--test-connection',
            action='store_true',
            help='Test connection to the device'
        )
        parser.add_argument(
            '--fetch-records',
            action='store_true',
            help='Fetch attendance records from the device'
        )

    def handle(self, *args, **options):
        ip_address = options['ip']
        port = options['port']
        password = options['password']

        self.stdout.write(
            self.style.SUCCESS(f'Testing ZK device at {ip_address}:{port}')
        )

        if options['test_connection']:
            self.test_connection(ip_address, port, password)

        if options['fetch_records']:
            self.fetch_records(ip_address, port, password)

    def test_connection(self, ip_address, port, password):
        """Test connection to ZK device"""
        self.stdout.write('Testing connection...')
        
        try:
            with ZKDeviceService(ip_address, port, password) as zk_device:
                if zk_device.is_connected:
                    self.stdout.write(
                        self.style.SUCCESS('✓ Connection successful!')
                    )
                    
                    # Get device info
                    device_info = zk_device.get_device_info()
                    self.stdout.write(f'Device info: {device_info}')
                else:
                    self.stdout.write(
                        self.style.ERROR('✗ Connection failed!')
                    )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Connection error: {str(e)}')
            )

    def fetch_records(self, ip_address, port, password):
        """Fetch records from ZK device"""
        self.stdout.write('Fetching attendance records...')
        
        try:
            with ZKDeviceService(ip_address, port, password) as zk_device:
                if not zk_device.is_connected:
                    self.stdout.write(
                        self.style.ERROR('✗ Cannot connect to device!')
                    )
                    return

                # Fetch records
                records = zk_device.get_attendance_records()
                
                if records:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Fetched {len(records)} records')
                    )
                    
                    # Show first few records
                    for i, record in enumerate(records[:5]):
                        self.stdout.write(f'  Record {i+1}: {record}')
                    
                    if len(records) > 5:
                        self.stdout.write(f'  ... and {len(records) - 5} more records')
                        
                    # Test validation
                    processor = AttendanceProcessor()
                    valid_records, validation_errors = processor.validate_zk_records(records)
                    
                    self.stdout.write(f'Valid records: {len(valid_records)}')
                    if validation_errors:
                        self.stdout.write(f'Validation errors: {len(validation_errors)}')
                        for error in validation_errors[:3]:
                            self.stdout.write(f'  - {error}')
                else:
                    self.stdout.write(
                        self.style.WARNING('No records found on device')
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error fetching records: {str(e)}')
            )
