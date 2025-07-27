"""
خدمات التكامل مع الأنظمة الخارجية
"""

import logging
import json
import requests
import socket
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.db import transaction
from celery import shared_task

from ..models_integrations import (
    ExternalSystem, IntegrationMapping, SyncJob, 
    DataImportTemplate, ImportJob, EmailTemplate
)

logger = logging.getLogger('hr_integration')


class BaseIntegrationService:
    """خدمة التكامل الأساسية"""
    
    def __init__(self, external_system: ExternalSystem):
        self.external_system = external_system
        self.timeout = external_system.timeout
        self.retry_attempts = external_system.retry_attempts
        self.retry_delay = external_system.retry_delay
    
    def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال مع النظام الخارجي"""
        try:
            if self.external_system.connection_type == 'api':
                return self._test_api_connection()
            elif self.external_system.connection_type == 'database':
                return self._test_database_connection()
            elif self.external_system.connection_type == 'tcp_socket':
                return self._test_socket_connection()
            else:
                return {'success': False, 'error': 'نوع اتصال غير مدعوم'}
                
        except Exception as e:
            logger.error(f"Connection test failed for {self.external_system.name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _test_api_connection(self) -> Dict[str, Any]:
        """اختبار اتصال API"""
        try:
            headers = {}
            if self.external_system.api_key:
                headers['Authorization'] = f'Bearer {self.external_system.api_key}'
            elif self.external_system.token:
                headers['Authorization'] = f'Token {self.external_system.token}'
            
            response = requests.get(
                self.external_system.endpoint_url,
                headers=headers,
                timeout=self.timeout,
                auth=(self.external_system.username, self.external_system.password) 
                     if self.external_system.username else None
            )
            
            if response.status_code == 200:
                return {'success': True, 'response_time': response.elapsed.total_seconds()}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def _test_database_connection(self) -> Dict[str, Any]:
        """اختبار اتصال قاعدة البيانات"""
        # هذا مثال بسيط - يحتاج تطوير حسب نوع قاعدة البيانات
        try:
            import pymssql  # مثال لـ SQL Server
            
            conn = pymssql.connect(
                server=self.external_system.host,
                port=self.external_system.port,
                user=self.external_system.username,
                password=self.external_system.password,
                timeout=self.timeout
            )
            conn.close()
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_socket_connection(self) -> Dict[str, Any]:
        """اختبار اتصال Socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            result = sock.connect_ex((
                self.external_system.host, 
                self.external_system.port
            ))
            
            sock.close()
            
            if result == 0:
                return {'success': True}
            else:
                return {'success': False, 'error': f'Connection failed: {result}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
class
 AttendanceDeviceService(BaseIntegrationService):
    """خدمة التكامل مع أجهزة الحضور"""
    
    def __init__(self, external_system: ExternalSystem):
        super().__init__(external_system)
        self.device_type = external_system.configuration.get('device_type', 'zk')
    
    def fetch_attendance_records(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """جلب سجلات الحضور من الجهاز"""
        try:
            if self.device_type == 'zk':
                return self._fetch_zk_records(start_date, end_date)
            elif self.device_type == 'suprema':
                return self._fetch_suprema_records(start_date, end_date)
            else:
                return {'success': False, 'error': 'نوع جهاز غير مدعوم'}
                
        except Exception as e:
            logger.error(f"Failed to fetch attendance records: {e}")
            return {'success': False, 'error': str(e)}
    
    def _fetch_zk_records(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """جلب سجلات من جهاز ZK"""
        try:
            from zk import ZK  # مكتبة ZK
            
            zk = ZK(self.external_system.host, port=self.external_system.port or 4370)
            conn = zk.connect()
            
            # جلب السجلات
            attendance_records = conn.get_attendance()
            
            # تصفية حسب التاريخ
            filtered_records = []
            for record in attendance_records:
                if start_date and record.timestamp < start_date:
                    continue
                if end_date and record.timestamp > end_date:
                    continue
                
                filtered_records.append({
                    'user_id': record.user_id,
                    'timestamp': record.timestamp,
                    'punch_type': record.punch,
                    'verify_type': record.verify,
                })
            
            conn.disconnect()
            
            return {
                'success': True,
                'records': filtered_records,
                'total_count': len(filtered_records)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _fetch_suprema_records(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """جلب سجلات من جهاز Suprema"""
        # تطبيق API خاص بـ Suprema
        try:
            headers = {
                'Authorization': f'Bearer {self.external_system.api_key}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
            }
            
            response = requests.get(
                f"{self.external_system.endpoint_url}/attendance",
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'records': data.get('records', []),
                    'total_count': len(data.get('records', []))
                }
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_users_to_device(self, employees: List[Any]) -> Dict[str, Any]:
        """مزامنة المستخدمين إلى الجهاز"""
        try:
            if self.device_type == 'zk':
                return self._sync_users_to_zk(employees)
            elif self.device_type == 'suprema':
                return self._sync_users_to_suprema(employees)
            else:
                return {'success': False, 'error': 'نوع جهاز غير مدعوم'}
                
        except Exception as e:
            logger.error(f"Failed to sync users to device: {e}")
            return {'success': False, 'error': str(e)}
    
    def _sync_users_to_zk(self, employees: List[Any]) -> Dict[str, Any]:
        """مزامنة المستخدمين إلى جهاز ZK"""
        try:
            from zk import ZK
            
            zk = ZK(self.external_system.host, port=self.external_system.port or 4370)
            conn = zk.connect()
            
            success_count = 0
            failed_count = 0
            
            for employee in employees:
                try:
                    # إضافة المستخدم
                    conn.set_user(
                        uid=int(employee.employee_number),
                        name=employee.full_name,
                        privilege=0,  # مستخدم عادي
                        password='',
                        group_id='',
                        user_id=employee.employee_number
                    )
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to add user {employee.employee_number}: {e}")
                    failed_count += 1
            
            conn.disconnect()
            
            return {
                'success': True,
                'success_count': success_count,
                'failed_count': failed_count
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _sync_users_to_suprema(self, employees: List[Any]) -> Dict[str, Any]:
        """مزامنة المستخدمين إلى جهاز Suprema"""
        try:
            headers = {
                'Authorization': f'Bearer {self.external_system.api_key}',
                'Content-Type': 'application/json'
            }
            
            users_data = []
            for employee in employees:
                users_data.append({
                    'user_id': employee.employee_number,
                    'name': employee.full_name,
                    'email': employee.email,
                    'department': employee.department.name if employee.department else '',
                })
            
            response = requests.post(
                f"{self.external_system.endpoint_url}/users/bulk",
                headers=headers,
                json={'users': users_data},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'success_count': result.get('success_count', 0),
                    'failed_count': result.get('failed_count', 0)
                }
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


class AccountingSystemService(BaseIntegrationService):
    """خدمة التكامل مع أنظمة المحاسبة"""
    
    def export_payroll_data(self, payroll_entries: List[Any]) -> Dict[str, Any]:
        """تصدير بيانات الرواتب إلى نظام المحاسبة"""
        try:
            accounting_data = []
            
            for entry in payroll_entries:
                # تحويل بيانات كشف الراتب إلى تنسيق المحاسبة
                accounting_entry = {
                    'employee_code': entry.employee.employee_number,
                    'employee_name': entry.employee.full_name,
                    'basic_salary': float(entry.basic_salary),
                    'allowances': float(entry.total_allowances),
                    'deductions': float(entry.total_deductions),
                    'net_salary': float(entry.net_salary),
                    'period': entry.period.strftime('%Y-%m'),
                    'department_code': entry.employee.department.code if entry.employee.department else '',
                    'cost_center': entry.employee.cost_center if hasattr(entry.employee, 'cost_center') else '',
                }
                
                accounting_data.append(accounting_entry)
            
            # إرسال البيانات إلى نظام المحاسبة
            if self.external_system.connection_type == 'api':
                return self._send_payroll_via_api(accounting_data)
            elif self.external_system.connection_type == 'file_transfer':
                return self._export_payroll_to_file(accounting_data)
            else:
                return {'success': False, 'error': 'نوع اتصال غير مدعوم'}
                
        except Exception as e:
            logger.error(f"Failed to export payroll data: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_payroll_via_api(self, accounting_data: List[Dict]) -> Dict[str, Any]:
        """إرسال بيانات الرواتب عبر API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.external_system.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.external_system.endpoint_url}/payroll",
                headers=headers,
                json={'entries': accounting_data},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'transaction_id': result.get('transaction_id'),
                    'processed_count': len(accounting_data)
                }
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _export_payroll_to_file(self, accounting_data: List[Dict]) -> Dict[str, Any]:
        """تصدير بيانات الرواتب إلى ملف"""
        try:
            import csv
            import os
            from django.conf import settings
            
            # إنشاء ملف CSV
            filename = f"payroll_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
            
            # التأكد من وجود المجلد
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if accounting_data:
                    fieldnames = accounting_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(accounting_data)
            
            return {
                'success': True,
                'file_path': filepath,
                'filename': filename,
                'processed_count': len(accounting_data)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


class EmailService:
    """خدمة البريد الإلكتروني المتقدمة"""
    
    def __init__(self):
        self.smtp_settings = getattr(settings, 'EMAIL_SETTINGS', {})
    
    def send_templated_email(
        self,
        template: EmailTemplate,
        recipients: List[str],
        context: Dict[str, Any],
        attachments: List[str] = None
    ) -> Dict[str, Any]:
        """إرسال بريد إلكتروني باستخدام قالب"""
        try:
            # تحويل القالب
            subject = self._render_template(template.subject_template, context)
            html_content = self._render_template(template.html_content, context)
            text_content = self._render_template(template.text_content, context) if template.text_content else None
            
            # إنشاء رسالة البريد
            from_email = template.from_email or settings.DEFAULT_FROM_EMAIL
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content or html_content,
                from_email=from_email,
                to=recipients,
                reply_to=[template.reply_to] if template.reply_to else None
            )
            
            # إضافة المحتوى HTML
            if html_content and text_content:
                msg.attach_alternative(html_content, "text/html")
            
            # إضافة المرفقات
            if attachments:
                for attachment_path in attachments:
                    msg.attach_file(attachment_path)
            
            # إضافة المرفقات الافتراضية
            for attachment_info in template.default_attachments:
                if attachment_info.get('path'):
                    msg.attach_file(attachment_info['path'])
            
            # إرسال البريد
            msg.send()
            
            return {
                'success': True,
                'recipients_count': len(recipients),
                'message': 'تم إرسال البريد بنجاح'
            }
            
        except Exception as e:
            logger.error(f"Failed to send templated email: {e}")
            return {'success': False, 'error': str(e)}
    
    def _render_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """تحويل قالب البريد"""
        try:
            template = Template(template_content)
            django_context = Context(context)
            return template.render(django_context)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return template_content
    
    def send_bulk_email(
        self,
        template: EmailTemplate,
        recipients_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """إرسال بريد جماعي مخصص"""
        try:
            success_count = 0
            failed_count = 0
            
            for recipient_data in recipients_data:
                try:
                    email = recipient_data.get('email')
                    context = recipient_data.get('context', {})
                    
                    if email:
                        result = self.send_templated_email(
                            template=template,
                            recipients=[email],
                            context=context
                        )
                        
                        if result['success']:
                            success_count += 1
                        else:
                            failed_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to send email to recipient: {e}")
                    failed_count += 1
            
            return {
                'success': True,
                'success_count': success_count,
                'failed_count': failed_count,
                'total_count': len(recipients_data)
            }
            
        except Exception as e:
            logger.error(f"Bulk email sending failed: {e}")
            return {'success': False, 'error': str(e)}حوي
ل\n                        transformed_value = self._apply_transformation_rules(\n                            local_value,\n                            mapping.transformation_rules\n                        )\n                        \n                        # تعيين القيمة في المسار المحدد\n                        self._set_nested_value(external_record, mapping.external_field, transformed_value)\n                        \n                except Exception as e:\n                    logger.error(f'خطأ في تحويل الحقل {mapping.external_field}: {str(e)}')\n            \n            transformed_data.append(external_record)\n        \n        return transformed_data\n    \n    def _get_nested_value(self, data: Dict, path: str) -> Any:\n        \"\"\"الحصول على قيمة من مسار متداخل\"\"\"\n        \n        keys = path.split('.')\n        value = data\n        \n        for key in keys:\n            if isinstance(value, dict) and key in value:\n                value = value[key]\n            else:\n                return None\n        \n        return value\n    \n    def _set_nested_value(self, data: Dict, path: str, value: Any):\n        \"\"\"تعيين قيمة في مسار متداخل\"\"\"\n        \n        keys = path.split('.')\n        current = data\n        \n        for key in keys[:-1]:\n            if key not in current:\n                current[key] = {}\n            current = current[key]\n        \n        current[keys[-1]] = value\n    \n    def _apply_transformation_rules(self, value: Any, rules: Dict) -> Any:\n        \"\"\"تطبيق قواعد التحويل\"\"\"\n        \n        if not rules:\n            return value\n        \n        # قواعد التحويل المختلفة\n        if 'type_conversion' in rules:\n            target_type = rules['type_conversion']\n            if target_type == 'string':\n                value = str(value)\n            elif target_type == 'integer':\n                value = int(value) if value else 0\n            elif target_type == 'float':\n                value = float(value) if value else 0.0\n            elif target_type == 'boolean':\n                value = bool(value)\n        \n        if 'format' in rules:\n            format_rule = rules['format']\n            if format_rule == 'date' and isinstance(value, str):\n                from datetime import datetime\n                try:\n                    value = datetime.fromisoformat(value.replace('Z', '+00:00')).date()\n                except:\n                    pass\n            elif format_rule == 'datetime' and isinstance(value, str):\n                from datetime import datetime\n                try:\n                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))\n                except:\n                    pass\n        \n        if 'mapping' in rules:\n            mapping_dict = rules['mapping']\n            value = mapping_dict.get(str(value), value)\n        \n        if 'prefix' in rules:\n            value = f\"{rules['prefix']}{value}\"\n        \n        if 'suffix' in rules:\n            value = f\"{value}{rules['suffix']}\"\n        \n        return value\n    \n    def _validate_data(self, value: Any, rules: Dict) -> bool:\n        \"\"\"التحقق من صحة البيانات\"\"\"\n        \n        if not rules:\n            return True\n        \n        # قواعد التحقق المختلفة\n        if 'required' in rules and rules['required'] and not value:\n            return False\n        \n        if 'min_length' in rules and isinstance(value, str):\n            if len(value) < rules['min_length']:\n                return False\n        \n        if 'max_length' in rules and isinstance(value, str):\n            if len(value) > rules['max_length']:\n                return False\n        \n        if 'pattern' in rules and isinstance(value, str):\n            import re\n            if not re.match(rules['pattern'], value):\n                return False\n        \n        if 'allowed_values' in rules:\n            if value not in rules['allowed_values']:\n                return False\n        \n        return True\n    \n    def _get_model_class(self, model_name: str):\n        \"\"\"الحصول على فئة النموذج\"\"\"\n        \n        model_mapping = {\n            'employee': Employee,\n            'department': Department,\n            'company': Company,\n        }\n        \n        return model_mapping.get(model_name)\n    \n    def _get_unique_fields(self, model_name: str) -> List[str]:\n        \"\"\"الحصول على الحقول الفريدة للنموذج\"\"\"\n        \n        unique_fields_mapping = {\n            'employee': ['employee_id', 'email'],\n            'department': ['code'],\n            'company': ['code'],\n        }\n        \n        return unique_fields_mapping.get(model_name, ['id'])\n    \n    def _get_local_data(self, model_name: str, filters: Dict = None) -> List[Dict]:\n        \"\"\"الحصول على البيانات المحلية\"\"\"\n        \n        model_class = self._get_model_class(model_name)\n        if not model_class:\n            return []\n        \n        queryset = model_class.objects.all()\n        \n        # تطبيق الفلاتر\n        if filters:\n            queryset = queryset.filter(**filters)\n        \n        # تحويل إلى قاموس\n        data = []\n        for obj in queryset:\n            obj_dict = {}\n            for field in obj._meta.fields:\n                value = getattr(obj, field.name)\n                if hasattr(value, 'isoformat'):\n                    value = value.isoformat()\n                elif hasattr(value, '__str__'):\n                    value = str(value)\n                obj_dict[field.name] = value\n            data.append(obj_dict)\n        \n        return data\n    \n    def _apply_webhook_filters(self, data: Dict, filters: Dict) -> bool:\n        \"\"\"تطبيق فلاتر الـ webhook\"\"\"\n        \n        for field, condition in filters.items():\n            field_value = self._get_nested_value(data, field)\n            \n            if isinstance(condition, dict):\n                # شروط معقدة\n                if 'equals' in condition and field_value != condition['equals']:\n                    return False\n                if 'contains' in condition and condition['contains'] not in str(field_value):\n                    return False\n                if 'in' in condition and field_value not in condition['in']:\n                    return False\n            else:\n                # شرط بسيط\n                if field_value != condition:\n                    return False\n        \n        return True\n    \n    def _generate_webhook_signature(self, payload: str, secret: str) -> str:\n        \"\"\"إنتاج توقيع الـ webhook\"\"\"\n        \n        signature = hmac.new(\n            secret.encode('utf-8'),\n            payload.encode('utf-8'),\n            hashlib.sha256\n        ).hexdigest()\n        \n        return f'sha256={signature}'\n\n\nclass APIKeyService:\n    \"\"\"خدمة إدارة مفاتيح API\"\"\"\n    \n    @staticmethod\n    def create_api_key(name: str, description: str = '', permission_level: str = 'read',\n                      allowed_models: List[str] = None, expires_days: int = None,\n                      created_by: 'User' = None) -> Tuple[str, 'APIKey']:\n        \"\"\"إنشاء مفتاح API جديد\"\"\"\n        \n        # إنتاج المفتاح\n        key, key_hash, key_prefix = APIKey.generate_key()\n        \n        # تحديد تاريخ الانتهاء\n        expires_at = None\n        if expires_days:\n            expires_at = timezone.now() + timedelta(days=expires_days)\n        \n        # إنشاء السجل\n        api_key = APIKey.objects.create(\n            name=name,\n            description=description,\n            key_hash=key_hash,\n            key_prefix=key_prefix,\n            permission_level=permission_level,\n            allowed_models=allowed_models or [],\n            expires_at=expires_at,\n            created_by=created_by\n        )\n        \n        return key, api_key\n    \n    @staticmethod\n    def validate_api_key(key: str) -> Optional['APIKey']:\n        \"\"\"التحقق من صحة مفتاح API\"\"\"\n        \n        if not key or not key.startswith('hr_'):\n            return None\n        \n        # إنشاء هاش المفتاح\n        key_hash = hashlib.sha256(key.encode()).hexdigest()\n        \n        try:\n            api_key = APIKey.objects.get(key_hash=key_hash)\n            \n            if api_key.is_valid():\n                return api_key\n            \n        except APIKey.DoesNotExist:\n            pass\n        \n        return None\n    \n    @staticmethod\n    def check_permissions(api_key: 'APIKey', model_name: str, operation: str) -> bool:\n        \"\"\"التحقق من صلاحيات المفتاح\"\"\"\n        \n        # التحقق من النماذج المسموحة\n        if api_key.allowed_models and model_name not in api_key.allowed_models:\n            return False\n        \n        # التحقق من العمليات المسموحة\n        if api_key.allowed_operations and operation not in api_key.allowed_operations:\n            return False\n        \n        # التحقق من مستوى الصلاحية\n        if api_key.permission_level == 'read' and operation not in ['GET']:\n            return False\n        elif api_key.permission_level == 'write' and operation not in ['POST', 'PUT', 'PATCH']:\n            return False\n        elif api_key.permission_level == 'read_write' and operation not in ['GET', 'POST', 'PUT', 'PATCH']:\n            return False\n        \n        return True\n    \n    @staticmethod\n    def check_rate_limit(api_key: 'APIKey') -> bool:\n        \"\"\"التحقق من حد المعدل\"\"\"\n        \n        cache_key = f'api_rate_limit_{api_key.id}'\n        current_count = cache.get(cache_key, 0)\n        \n        if current_count >= api_key.rate_limit:\n            return False\n        \n        # زيادة العداد\n        cache.set(cache_key, current_count + 1, 3600)  # ساعة واحدة\n        return True\n\n\n# مهام Celery للمزامنة التلقائية\n@shared_task\ndef sync_external_system(system_id: str, job_type: str = 'incremental_sync'):\n    \"\"\"مهمة مزامنة نظام خارجي\"\"\"\n    \n    try:\n        system = ExternalSystem.objects.get(id=system_id)\n        \n        if system.status != 'active':\n            return {'success': False, 'error': 'النظام غير نشط'}\n        \n        # إنشاء مهمة مزامنة\n        job = SyncJob.objects.create(\n            external_system=system,\n            name=f'مزامنة تلقائية - {system.name}',\n            job_type=job_type,\n            models_to_sync=['employee', 'department']\n        )\n        \n        # تشغيل المزامنة\n        service = IntegrationService()\n        result = service.sync_data(system, job)\n        \n        return result\n        \n    except ExternalSystem.DoesNotExist:\n        return {'success': False, 'error': 'النظام غير موجود'}\n    except Exception as e:\n        return {'success': False, 'error': str(e)}\n\n\n@shared_task\ndef send_webhook_notification(webhook_id: str, event_type: str, data: Dict):\n    \"\"\"مهمة إرسال webhook\"\"\"\n    \n    try:\n        webhook = WebhookEndpoint.objects.get(id=webhook_id)\n        \n        service = IntegrationService()\n        result = service.send_webhook(webhook, event_type, data)\n        \n        return result\n        \n    except WebhookEndpoint.DoesNotExist:\n        return {'success': False, 'error': 'Webhook غير موجود'}\n    except Exception as e:\n        return {'success': False, 'error': str(e)}\n\n\n@shared_task\ndef cleanup_expired_api_keys():\n    \"\"\"تنظيف مفاتيح API المنتهية الصلاحية\"\"\"\n    \n    try:\n        expired_keys = APIKey.objects.filter(\n            expires_at__lt=timezone.now(),\n            status='active'\n        )\n        \n        count = expired_keys.update(status='expired')\n        \n        return {'success': True, 'expired_keys': count}\n        \n    except Exception as e:\n        return {'success': False, 'error': str(e)}\n\n\n@shared_task\ndef auto_sync_systems():\n    \"\"\"مزامنة تلقائية للأنظمة المفعلة\"\"\"\n    \n    try:\n        systems = ExternalSystem.objects.filter(\n            status='active',\n            auto_sync_enabled=True\n        )\n        \n        results = []\n        \n        for system in systems:\n            # التحقق من وقت آخر مزامنة\n            if system.last_sync_at:\n                time_diff = timezone.now() - system.last_sync_at\n                if time_diff.total_seconds() < (system.sync_interval * 60):\n                    continue\n            \n            # تشغيل المزامنة\n            result = sync_external_system.delay(str(system.id))\n            results.append({\n                'system': system.name,\n                'task_id': result.id\n            })\n        \n        return {'success': True, 'synced_systems': results}\n        \n    except Exception as e:\n        return {'success': False, 'error': str(e)}\n