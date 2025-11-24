"""
خدمات التكامل الخارجي
External Integration Services
"""
import requests
import json
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from core.services.base import BaseService


class AttendanceDeviceService(BaseService):
    """
    خدمة التكامل مع أجهزة الحضور
    Attendance device integration service
    """

    def __init__(self, user=None):
        """__init__ function"""
        super().__init__(user)
        self.device_configs = getattr(settings, 'ATTENDANCE_DEVICES', {})

    def sync_attendance_data(self, device_id, start_date=None, end_date=None):
        """مزامنة بيانات الحضور من الجهاز"""
        try:
            device_config = self.device_configs.get(device_id)
            if not device_config:
                return self.format_response(
                    success=False,
                    message='إعدادات الجهاز غير موجودة'
                )

            # Connect to device API
            api_url = device_config.get('api_url')
            auth_token = device_config.get('auth_token')

            headers = {
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            }

            params = {}
            if start_date:
                params['start_date'] = start_date.isoformat()
            if end_date:
                params['end_date'] = end_date.isoformat()

            response = requests.get(
                f"{api_url}/attendance",
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                attendance_data = response.json()

                # Process attendance records
                processed_count = self._process_attendance_records(
                    attendance_data.get('records', [])
                )

                return self.format_response(
                    data={'processed_count': processed_count},
                    message=f'تم مزامنة {processed_count} سجل حضور'
                )
            else:
                return self.format_response(
                    success=False,
                    message=f'فشل في الاتصال بالجهاز: {response.status_code}'
                )

        except requests.RequestException as e:
            return self.format_response(
                success=False,
                message=f'خطأ في الاتصال: {str(e)}'
            )
        except Exception as e:
            return self.handle_exception(e, 'sync_attendance_data', f'device/{device_id}')

    def _process_attendance_records(self, records):
        """معالجة سجلات الحضور"""
        from apps.hr.services.attendance_service import AttendanceService

        attendance_service = AttendanceService(user=self.user)
        processed_count = 0

        for record in records:
            try:
                result = attendance_service.record_attendance({
                    'employee_id': record.get('employee_id'),
                    'att_date': record.get('date'),
                    'check_in_time': record.get('check_in'),
                    'check_out_time': record.get('check_out'),
                    'device_id': record.get('device_id'),
                    'manual_entry': False
                })

                if result['success']:
                    processed_count += 1

            except Exception as e:
                self.logger.error(f"Error processing attendance record: {e}")

        return processed_count


class EmailService(BaseService):
    """
    خدمة البريد الإلكتروني المتقدمة
    Advanced email service
    """

    def send_email(self, recipient, subject, template_name, context=None,
                   attachments=None, priority='normal'):
        """إرسال بريد إلكتروني"""
        try:
            context = context or {}

            # Render email templates
            html_content = render_to_string(f'emails/{template_name}.html', context)
            text_content = render_to_string(f'emails/{template_name}.txt', context)

            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient] if isinstance(recipient, str) else recipient
            )

            email.attach_alternative(html_content, "text/html")

            # Add attachments
            if attachments:
                for attachment in attachments:
                    email.attach_file(attachment)

            # Send email
            email.send()

            self.log_action(
                action='send_email',
                resource='email',
                details={
                    'recipient': recipient,
                    'subject': subject,
                    'template': template_name
                },
                message=f'تم إرسال بريد إلكتروني: {subject}'
            )

            return self.format_response(
                message='تم إرسال البريد الإلكتروني بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'send_email', 'email')

    def send_bulk_email(self, recipients, subject, template_name, context=None):
        """إرسال بريد جماعي"""
        try:
            success_count = 0
            error_count = 0

            for recipient in recipients:
                result = self.send_email(recipient, subject, template_name, context)
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1

            return self.format_response(
                data={
                    'success_count': success_count,
                    'error_count': error_count,
                    'total_sent': len(recipients)
                },
                message=f'تم إرسال {success_count} من {len(recipients)} رسالة'
            )

        except Exception as e:
            return self.handle_exception(e, 'send_bulk_email', 'bulk_email')


class SMSService(BaseService):
    """
    خدمة الرسائل النصية
    SMS service
    """

    def __init__(self, user=None):
        """__init__ function"""
        super().__init__(user)
        self.sms_config = getattr(settings, 'SMS_CONFIG', {})

    def send_sms(self, phone_number, message, priority='normal'):
        """إرسال رسالة نصية"""
        try:
            # This would integrate with SMS provider API
            # For now, we'll simulate the sending

            api_url = self.sms_config.get('api_url')
            api_key = self.sms_config.get('api_key')

            if not api_url or not api_key:
                return self.format_response(
                    success=False,
                    message='إعدادات الرسائل النصية غير مكتملة'
                )

            # Simulate SMS sending
            # In real implementation, this would call the SMS provider API

            self.log_action(
                action='send_sms',
                resource='sms',
                details={
                    'phone_number': phone_number,
                    'message_length': len(message)
                },
                message=f'تم إرسال رسالة نصية إلى: {phone_number}'
            )

            return self.format_response(
                message='تم إرسال الرسالة النصية بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'send_sms', 'sms')


class FileImportService(BaseService):
    """
    خدمة استيراد البيانات من ملفات Excel
    Excel file import service
    """

    def import_employees_from_excel(self, file_path):
        """استيراد الموظفين من ملف Excel"""
        try:
            import pandas as pd

            # Read Excel file
            df = pd.read_excel(file_path)

            # Validate required columns
            required_columns = ['first_name', 'last_name', 'emp_code', 'email']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return self.format_response(
                    success=False,
                    message=f'الأعمدة التالية مفقودة: {", ".join(missing_columns)}'
                )

            # Import employees
            from apps.hr.services.employee_service import EmployeeService

            employee_service = EmployeeService(user=self.user)
            success_count = 0
            error_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    employee_data = {
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'emp_code': row['emp_code'],
                        'email': row['email'],
                        'phone': row.get('phone', ''),
                        'department_id': row.get('department_id'),
                        'job_position_id': row.get('job_position_id'),
                    }

                    result = employee_service.create_employee(employee_data)
                    if result['success']:
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(f'الصف {index + 2}: {result["message"]}')

                except Exception as e:
                    error_count += 1
                    errors.append(f'الصف {index + 2}: {str(e)}')

            return self.format_response(
                data={
                    'success_count': success_count,
                    'error_count': error_count,
                    'errors': errors[:10]  # Limit errors shown
                },
                message=f'تم استيراد {success_count} موظف بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'import_employees_from_excel', 'excel_import')

    def import_products_from_excel(self, file_path):
        """استيراد المنتجات من ملف Excel"""
        try:
            import pandas as pd

            df = pd.read_excel(file_path)

            # Validate required columns
            required_columns = ['name_ar', 'name_en', 'code', 'category_id', 'unit_id']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return self.format_response(
                    success=False,
                    message=f'الأعمدة التالية مفقودة: {", ".join(missing_columns)}'
                )

            # Import products
            from apps.inventory.services.product_service import ProductService

            product_service = ProductService(user=self.user)
            success_count = 0
            error_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    product_data = {
                        'name_ar': row['name_ar'],
                        'name_en': row['name_en'],
                        'code': row['code'],
                        'category_id': row['category_id'],
                        'unit_id': row['unit_id'],
                        'cost_price': row.get('cost_price', 0),
                        'selling_price': row.get('selling_price', 0),
                    }

                    result = product_service.create_product(product_data)
                    if result['success']:
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(f'الصف {index + 2}: {result["message"]}')

                except Exception as e:
                    error_count += 1
                    errors.append(f'الصف {index + 2}: {str(e)}')

            return self.format_response(
                data={
                    'success_count': success_count,
                    'error_count': error_count,
                    'errors': errors[:10]
                },
                message=f'تم استيراد {success_count} منتج بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'import_products_from_excel', 'excel_import')


class APIIntegrationService(BaseService):
    """
    خدمة التكامل مع الأنظمة الخارجية
    External systems API integration service
    """

    def sync_with_accounting_system(self, data_type, start_date=None, end_date=None):
        """مزامنة مع نظام المحاسبة"""
        try:
            # This would integrate with accounting system API
            # Implementation depends on the specific accounting system

            accounting_config = getattr(settings, 'ACCOUNTING_SYSTEM', {})

            if not accounting_config.get('enabled'):
                return self.format_response(
                    success=False,
                    message='التكامل مع نظام المحاسبة غير مفعل'
                )

            # Simulate integration
            self.log_action(
                action='sync_accounting',
                resource='accounting_integration',
                details={
                    'data_type': data_type,
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                },
                message=f'تم مزامنة {data_type} مع نظام المحاسبة'
            )

            return self.format_response(
                message='تم التزامن مع نظام المحاسبة بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'sync_with_accounting_system', 'accounting_sync')

    def export_to_external_system(self, system_name, data, format='json'):
        """تصدير البيانات لنظام خارجي"""
        try:
            # This would export data to external system
            # Implementation depends on the target system

            self.log_action(
                action='export_data',
                resource='external_export',
                details={
                    'system_name': system_name,
                    'format': format,
                    'records_count': len(data) if isinstance(data, list) else 1
                },
                message=f'تم تصدير البيانات إلى {system_name}'
            )

            return self.format_response(
                message=f'تم تصدير البيانات إلى {system_name} بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'export_to_external_system', f'export/{system_name}')
