"""
خدمات الإشعارات الذكية للموارد البشرية
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from django.utils import timezone
from django.contrib.auth.models import User
from django.template import Template, Context
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction
from celery import shared_task

from ..models_notifications import (
    NotificationTemplate, NotificationRule, Notification,
    NotificationDelivery, NotificationPreference, NotificationDigest
)

logger = logging.getLogger('hr_notifications')


class NotificationService:
    """خدمات الإشعارات الذكية"""
    
    def __init__(self):
        self.email_enabled = getattr(settings, 'NOTIFICATIONS_SETTINGS', {}).get('EMAIL_NOTIFICATIONS', True)
        self.sms_enabled = getattr(settings, 'NOTIFICATIONS_SETTINGS', {}).get('SMS_NOTIFICATIONS', False)
        self.push_enabled = getattr(settings, 'NOTIFICATIONS_SETTINGS', {}).get('PUSH_NOTIFICATIONS', True)
    
    def send_document_expiry_notification(self, employee_file):
        """إرسال تنبيه انتهاء صلاحية الوثيقة"""
        try:
            context = {
                'employee': employee_file.employee,
                'document': employee_file,
                'days_until_expiry': employee_file.days_until_expiry,
                'company': employee_file.employee.company,
            }
            
            # Send to employee
            if self.email_enabled:
                self._send_email_notification(
                    recipient=employee_file.employee.email,
                    subject=f'تنبيه: انتهاء صلاحية {employee_file.title}',
                    template_name='document_expiry_employee',
                    context=context
                )
            
            # Send to HR department
            hr_emails = self._get_hr_department_emails(employee_file.employee.company)
            for email in hr_emails:
                if self.email_enabled:
                    self._send_email_notification(
                        recipient=email,
                        subject=f'تنبيه: انتهاء صلاحية وثيقة الموظف {employee_file.employee.full_name}',
                        template_name='document_expiry_hr',
                        context=context
                    )
            
            # Send to direct manager
            if employee_file.employee.direct_manager and self.email_enabled:
                self._send_email_notification(
                    recipient=employee_file.employee.direct_manager.email,
                    subject=f'تنبيه: انتهاء صلاحية وثيقة {employee_file.employee.full_name}',
                    template_name='document_expiry_manager',
                    context=context
                )
            
            logger.info(f"Document expiry notification sent for {employee_file.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending document expiry notification: {e}")
            return False
    
    def send_leave_request_notification(self, leave_request):
        """إرسال إشعار طلب الإجازة"""
        try:
            context = {
                'employee': leave_request.employee,
                'leave_request': leave_request,
                'company': leave_request.employee.company,
            }
            
            # Send to direct manager
            if leave_request.employee.direct_manager and self.email_enabled:
                self._send_email_notification(
                    recipient=leave_request.employee.direct_manager.email,
                    subject=f'طلب إجازة جديد من {leave_request.employee.full_name}',
                    template_name='leave_request_manager',
                    context=context
                )
            
            # Send to HR department
            hr_emails = self._get_hr_department_emails(leave_request.employee.company)
            for email in hr_emails:
                if self.email_enabled:
                    self._send_email_notification(
                        recipient=email,
                        subject=f'طلب إجازة جديد - {leave_request.employee.full_name}',
                        template_name='leave_request_hr',
                        context=context
                    )
            
            logger.info(f"Leave request notification sent for {leave_request.employee.employee_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending leave request notification: {e}")
            return False
    
    def send_leave_approval_notification(self, leave_request):
        """إرسال إشعار موافقة الإجازة"""
        try:
            context = {
                'employee': leave_request.employee,
                'leave_request': leave_request,
                'company': leave_request.employee.company,
            }
            
            # Send to employee
            if self.email_enabled:
                self._send_email_notification(
                    recipient=leave_request.employee.email,
                    subject=f'تم اعتماد طلب الإجازة - {leave_request.leave_type.name}',
                    template_name='leave_approved_employee',
                    context=context
                )
            
            # Send to HR department
            hr_emails = self._get_hr_department_emails(leave_request.employee.company)
            for email in hr_emails:
                if self.email_enabled:
                    self._send_email_notification(
                        recipient=email,
                        subject=f'تم اعتماد إجازة {leave_request.employee.full_name}',
                        template_name='leave_approved_hr',
                        context=context
                    )
            
            logger.info(f"Leave approval notification sent for {leave_request.employee.employee_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending leave approval notification: {e}")
            return False
    
    def send_attendance_late_notification(self, employee, late_minutes):
        """إرسال إشعار تأخير في الحضور"""
        try:
            context = {
                'employee': employee,
                'late_minutes': late_minutes,
                'date': timezone.now().date(),
                'company': employee.company,
            }
            
            # Send to direct manager
            if employee.direct_manager and self.email_enabled:
                self._send_email_notification(
                    recipient=employee.direct_manager.email,
                    subject=f'تأخير في الحضور - {employee.full_name}',
                    template_name='attendance_late_manager',
                    context=context
                )
            
            # Send to HR department if late more than threshold
            threshold_minutes = getattr(settings, 'HR_SETTINGS', {}).get('LATE_THRESHOLD_MINUTES', 15)
            if late_minutes > threshold_minutes:
                hr_emails = self._get_hr_department_emails(employee.company)
                for email in hr_emails:
                    if self.email_enabled:
                        self._send_email_notification(
                            recipient=email,
                            subject=f'تأخير كبير في الحضور - {employee.full_name}',
                            template_name='attendance_late_hr',
                            context=context
                        )
            
            logger.info(f"Late attendance notification sent for {employee.employee_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending late attendance notification: {e}")
            return False
    
    def send_birthday_notification(self, employee):
        """إرسال تهنئة عيد الميلاد"""
        try:
            context = {
                'employee': employee,
                'company': employee.company,
                'age': employee.age,
            }
            
            # Send to employee
            if self.email_enabled:
                self._send_email_notification(
                    recipient=employee.email,
                    subject=f'كل عام وأنت بخير - {employee.full_name}',
                    template_name='birthday_employee',
                    context=context
                )
            
            # Send to direct manager
            if employee.direct_manager and self.email_enabled:
                self._send_email_notification(
                    recipient=employee.direct_manager.email,
                    subject=f'عيد ميلاد {employee.full_name}',
                    template_name='birthday_manager',
                    context=context
                )
            
            # Send to HR department
            hr_emails = self._get_hr_department_emails(employee.company)
            for email in hr_emails:
                if self.email_enabled:
                    self._send_email_notification(
                        recipient=email,
                        subject=f'عيد ميلاد الموظف {employee.full_name}',
                        template_name='birthday_hr',
                        context=context
                    )
            
            logger.info(f"Birthday notification sent for {employee.employee_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending birthday notification: {e}")
            return False
    
    def send_work_anniversary_notification(self, employee):
        """إرسال تهنئة ذكرى التوظيف"""
        try:
            service_details = self._calculate_service_years(employee)
            
            context = {
                'employee': employee,
                'company': employee.company,
                'service_years': service_details['years'],
                'service_details': service_details,
            }
            
            # Send to employee
            if self.email_enabled:
                self._send_email_notification(
                    recipient=employee.email,
                    subject=f'ذكرى التوظيف - {service_details["years"]} سنوات من العطاء',
                    template_name='work_anniversary_employee',
                    context=context
                )
            
            # Send to direct manager
            if employee.direct_manager and self.email_enabled:
                self._send_email_notification(
                    recipient=employee.direct_manager.email,
                    subject=f'ذكرى توظيف {employee.full_name}',
                    template_name='work_anniversary_manager',
                    context=context
                )
            
            logger.info(f"Work anniversary notification sent for {employee.employee_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending work anniversary notification: {e}")
            return False
    
    def send_performance_review_reminder(self, employee, review_due_date):
        """إرسال تذكير تقييم الأداء"""
        try:
            context = {
                'employee': employee,
                'review_due_date': review_due_date,
                'company': employee.company,
            }
            
            # Send to direct manager
            if employee.direct_manager and self.email_enabled:
                self._send_email_notification(
                    recipient=employee.direct_manager.email,
                    subject=f'تذكير: تقييم أداء {employee.full_name}',
                    template_name='performance_review_manager',
                    context=context
                )
            
            # Send to HR department
            hr_emails = self._get_hr_department_emails(employee.company)
            for email in hr_emails:
                if self.email_enabled:
                    self._send_email_notification(
                        recipient=email,
                        subject=f'تذكير: تقييم أداء الموظف {employee.full_name}',
                        template_name='performance_review_hr',
                        context=context
                    )
            
            logger.info(f"Performance review reminder sent for {employee.employee_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending performance review reminder: {e}")
            return False
    
    def _send_email_notification(self, recipient, subject, template_name, context):
        """إرسال إشعار بريد إلكتروني"""
        try:
            # Render email templates
            html_content = render_to_string(f'hr/emails/{template_name}.html', context)
            text_content = render_to_string(f'hr/emails/{template_name}.txt', context)
            
            # Create email message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient]
            )
            msg.attach_alternative(html_content, "text/html")
            
            # Send email
            msg.send()
            
            logger.info(f"Email sent to {recipient}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient}: {e}")
            return False
    
    def _get_hr_department_emails(self, company):
        """الحصول على بريد قسم الموارد البشرية"""
        try:
            from ..models_enhanced import Employee, Department
            
            # Get HR department
            hr_departments = Department.objects.filter(
                company=company,
                name__icontains='موارد بشرية',
                is_active=True
            )
            
            if not hr_departments.exists():
                hr_departments = Department.objects.filter(
                    company=company,
                    name__icontains='HR',
                    is_active=True
                )
            
            emails = []
            for dept in hr_departments:
                # Get department employees
                hr_employees = Employee.objects.filter(
                    department=dept,
                    is_active=True
                ).values_list('email', flat=True)
                emails.extend(hr_employees)
            
            # Remove duplicates
            return list(set(emails))
            
        except Exception as e:
            logger.error(f"Error getting HR department emails: {e}")
            return []
    
    def _calculate_service_years(self, employee):
        """حساب سنوات الخدمة"""
        from datetime import date
        
        today = date.today()
        hire_date = employee.hire_date
        
        years = today.year - hire_date.year
        months = today.month - hire_date.month
        days = today.day - hire_date.day
        
        if days < 0:
            months -= 1
            days += 30  # Approximate
        
        if months < 0:
            years -= 1
            months += 12
        
        return {
            'years': years,
            'months': months,
            'days': days,
            'total_days': (today - hire_date).days
        }

c
lass AdvancedNotificationService:
    """خدمة الإشعارات المتقدمة"""
    
    def __init__(self):
        self.delivery_handlers = {
            'email': self._send_email,
            'sms': self._send_sms,
            'push': self._send_push,
            'in_app': self._send_in_app,
            'slack': self._send_slack,
            'teams': self._send_teams,
        }
    
    def create_notification(
        self,
        recipient: User,
        title: str,
        message: str,
        notification_type: str = 'info',
        priority: str = 'normal',
        template: Optional[NotificationTemplate] = None,
        rule: Optional[NotificationRule] = None,
        content_object: Any = None,
        data: Dict = None,
        delivery_methods: List[str] = None,
        scheduled_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        sender: Optional[User] = None
    ) -> Notification:
        """إنشاء إشعار جديد"""
        
        try:
            # التحقق من تفضيلات المستخدم
            preferences = self._get_user_preferences(recipient)
            
            if not preferences.enabled:
                logger.info(f"Notifications disabled for user {recipient.username}")
                return None
            
            # تحديد طرق التوصيل
            if delivery_methods is None:
                delivery_methods = self._get_default_delivery_methods(recipient, notification_type)
            
            # فلترة طرق التوصيل حسب تفضيلات المستخدم
            delivery_methods = [
                method for method in delivery_methods
                if preferences.is_delivery_method_enabled(method)
            ]
            
            if not delivery_methods:
                logger.info(f"No enabled delivery methods for user {recipient.username}")
                return None
            
            # التحقق من وقت عدم الإزعاج
            if preferences.is_quiet_time() and priority not in ['urgent']:
                # تأجيل الإشعار إلى نهاية وقت عدم الإزعاج
                if not scheduled_at:
                    scheduled_at = self._calculate_next_send_time(preferences)
            
            # إنشاء الإشعار
            with transaction.atomic():
                notification = Notification.objects.create(
                    recipient=recipient,
                    sender=sender,
                    template=template,
                    rule=rule,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    content_object=content_object,
                    data=data or {},
                    delivery_methods=delivery_methods,
                    scheduled_at=scheduled_at or timezone.now(),
                    expires_at=expires_at,
                    status='pending'
                )
                
                # جدولة الإرسال
                if scheduled_at and scheduled_at > timezone.now():
                    self._schedule_notification(notification)
                else:
                    self._send_notification(notification)
                
                return notification
                
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    def create_from_template(
        self,
        template_code: str,
        recipient: User,
        context: Dict,
        sender: Optional[User] = None,
        content_object: Any = None,
        scheduled_at: Optional[datetime] = None
    ) -> Notification:
        """إنشاء إشعار من قالب"""
        
        try:
            template = NotificationTemplate.objects.get(
                code=template_code,
                is_active=True
            )
            
            # تحويل القالب إلى محتوى
            rendered_content = template.render_content(context)
            
            return self.create_notification(
                recipient=recipient,
                title=rendered_content['title'],
                message=rendered_content['message'],
                notification_type=template.notification_type,
                template=template,
                sender=sender,
                content_object=content_object,
                delivery_methods=template.delivery_methods,
                scheduled_at=scheduled_at,
                data={'rendered_content': rendered_content}
            )
            
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Template not found: {template_code}")
            return None
        except Exception as e:
            logger.error(f"Error creating notification from template: {e}")
            return None
    
    def trigger_rule(self, event: str, context: Dict, content_object: Any = None):
        """تفعيل قواعد الإشعارات"""
        
        try:
            rules = NotificationRule.objects.filter(
                trigger_event=event,
                is_active=True
            )
            
            for rule in rules:
                # التحقق من الشروط
                if not self._check_rule_conditions(rule, context):
                    continue
                
                # تحديد المستقبلين
                recipients = self._get_rule_recipients(rule, context, content_object)
                
                for recipient in recipients:
                    # إنشاء الإشعار
                    self.create_from_template(
                        template_code=rule.template.code,
                        recipient=recipient,
                        context=context,
                        content_object=content_object
                    )
                    
        except Exception as e:
            logger.error(f"Error triggering rule for event {event}: {e}")
    
    def send_bulk_notification(
        self,
        recipients: List[User],
        title: str,
        message: str,
        notification_type: str = 'info',
        delivery_methods: List[str] = None,
        sender: Optional[User] = None
    ) -> List[Notification]:
        """إرسال إشعار جماعي"""
        
        notifications = []
        
        for recipient in recipients:
            notification = self.create_notification(
                recipient=recipient,
                title=title,
                message=message,
                notification_type=notification_type,
                delivery_methods=delivery_methods,
                sender=sender
            )
            
            if notification:
                notifications.append(notification)
        
        return notifications
    
    def mark_as_read(self, notification_id: str, user: User) -> bool:
        """تحديد الإشعار كمقروء"""
        
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=user
            )
            
            notification.mark_as_read()
            return True
            
        except Notification.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    def get_user_notifications(
        self,
        user: User,
        status: str = None,
        notification_type: str = None,
        limit: int = 50
    ) -> List[Notification]:
        """الحصول على إشعارات المستخدم"""
        
        queryset = Notification.objects.filter(recipient=user)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        return queryset.order_by('-created_at')[:limit]
    
    def get_unread_count(self, user: User) -> int:
        """عدد الإشعارات غير المقروءة"""
        
        return Notification.objects.filter(
            recipient=user,
            status__in=['sent', 'delivered']
        ).count()
    
    def _send_notification(self, notification: Notification):
        """إرسال الإشعار"""
        
        try:
            for method in notification.delivery_methods:
                if method in self.delivery_handlers:
                    self.delivery_handlers[method](notification)
            
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save(update_fields=['status', 'sent_at', 'updated_at'])
            
        except Exception as e:
            notification.mark_as_failed(str(e))
            logger.error(f"Error sending notification {notification.id}: {e}")
    
    def _send_email(self, notification: Notification):
        """إرسال بريد إلكتروني"""
        
        try:
            recipient_email = notification.recipient.email
            if not recipient_email:
                raise ValueError("No email address for recipient")
            
            # استخدام المحتوى المُحضر من القالب إذا كان متوفراً
            rendered_content = notification.data.get('rendered_content', {})
            
            subject = rendered_content.get('email_subject') or notification.title
            html_content = rendered_content.get('email_body') or notification.message
            text_content = notification.message
            
            # إنشاء رسالة البريد
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )
            
            if html_content != text_content:
                msg.attach_alternative(html_content, "text/html")
            
            # إرسال البريد
            msg.send()
            
            # تسجيل التوصيل
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='email',
                recipient_address=recipient_email,
                status='sent',
                sent_at=timezone.now()
            )
            
            logger.info(f"Email sent for notification {notification.id}")
            
        except Exception as e:
            # تسجيل الفشل
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='email',
                recipient_address=notification.recipient.email or '',
                status='failed',
                error_message=str(e)
            )
            raise e
    
    def _send_sms(self, notification: Notification):
        """إرسال رسالة نصية"""
        
        try:
            # هذا مثال - يحتاج إلى تكامل مع مزود خدمة الرسائل النصية
            phone_number = getattr(notification.recipient, 'phone_number', None)
            if not phone_number:
                raise ValueError("No phone number for recipient")
            
            rendered_content = notification.data.get('rendered_content', {})
            sms_message = rendered_content.get('sms_message') or notification.message[:160]
            
            # هنا يتم التكامل مع مزود خدمة الرسائل النصية
            # مثال: Twilio, AWS SNS, إلخ
            
            # تسجيل التوصيل
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='sms',
                recipient_address=phone_number,
                status='sent',
                sent_at=timezone.now(),
                sent_content={'message': sms_message}
            )
            
            logger.info(f"SMS sent for notification {notification.id}")
            
        except Exception as e:
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='sms',
                recipient_address=getattr(notification.recipient, 'phone_number', ''),
                status='failed',
                error_message=str(e)
            )
            raise e
    
    def _send_push(self, notification: Notification):
        """إرسال إشعار فوري"""
        
        try:
            # هذا مثال - يحتاج إلى تكامل مع خدمة الإشعارات الفورية
            # مثال: Firebase Cloud Messaging, Apple Push Notifications
            
            push_data = {
                'title': notification.title,
                'body': notification.message,
                'data': notification.data
            }
            
            # تسجيل التوصيل
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='push',
                recipient_address=f"user_{notification.recipient.id}",
                status='sent',
                sent_at=timezone.now(),
                sent_content=push_data
            )
            
            logger.info(f"Push notification sent for notification {notification.id}")
            
        except Exception as e:
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='push',
                recipient_address=f"user_{notification.recipient.id}",
                status='failed',
                error_message=str(e)
            )
            raise e
    
    def _send_in_app(self, notification: Notification):
        """إرسال إشعار داخل التطبيق"""
        
        try:
            # الإشعارات داخل التطبيق تُحفظ في قاعدة البيانات فقط
            # ويتم عرضها في واجهة المستخدم
            
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='in_app',
                recipient_address=f"user_{notification.recipient.id}",
                status='delivered',
                sent_at=timezone.now(),
                delivered_at=timezone.now()
            )
            
            logger.info(f"In-app notification created for notification {notification.id}")
            
        except Exception as e:
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='in_app',
                recipient_address=f"user_{notification.recipient.id}",
                status='failed',
                error_message=str(e)
            )
            raise e
    
    def _send_slack(self, notification: Notification):
        """إرسال إشعار عبر سلاك"""
        
        try:
            # هذا مثال - يحتاج إلى تكامل مع Slack API
            slack_user_id = getattr(notification.recipient, 'slack_user_id', None)
            if not slack_user_id:
                raise ValueError("No Slack user ID for recipient")
            
            # تسجيل التوصيل
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='slack',
                recipient_address=slack_user_id,
                status='sent',
                sent_at=timezone.now()
            )
            
            logger.info(f"Slack notification sent for notification {notification.id}")
            
        except Exception as e:
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='slack',
                recipient_address=getattr(notification.recipient, 'slack_user_id', ''),
                status='failed',
                error_message=str(e)
            )
            raise e
    
    def _send_teams(self, notification: Notification):
        """إرسال إشعار عبر مايكروسوفت تيمز"""
        
        try:
            # هذا مثال - يحتاج إلى تكامل مع Microsoft Teams API
            teams_user_id = getattr(notification.recipient, 'teams_user_id', None)
            if not teams_user_id:
                raise ValueError("No Teams user ID for recipient")
            
            # تسجيل التوصيل
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='teams',
                recipient_address=teams_user_id,
                status='sent',
                sent_at=timezone.now()
            )
            
            logger.info(f"Teams notification sent for notification {notification.id}")
            
        except Exception as e:
            NotificationDelivery.objects.create(
                notification=notification,
                delivery_method='teams',
                recipient_address=getattr(notification.recipient, 'teams_user_id', ''),
                status='failed',
                error_message=str(e)
            )
            raise e
    
    def _get_user_preferences(self, user: User) -> NotificationPreference:
        """الحصول على تفضيلات المستخدم"""
        
        preferences, created = NotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'enabled': True,
                'email_enabled': True,
                'in_app_enabled': True,
                'push_enabled': True,
                'sms_enabled': False
            }
        )
        
        return preferences
    
    def _get_default_delivery_methods(self, user: User, notification_type: str) -> List[str]:
        """تحديد طرق التوصيل الافتراضية"""
        
        # طرق التوصيل الافتراضية حسب نوع الإشعار
        default_methods = {
            'urgent': ['email', 'sms', 'push', 'in_app'],
            'error': ['email', 'in_app'],
            'warning': ['email', 'in_app'],
            'success': ['in_app'],
            'info': ['in_app'],
            'reminder': ['email', 'in_app'],
            'approval': ['email', 'in_app'],
        }
        
        return default_methods.get(notification_type, ['in_app'])
    
    def _calculate_next_send_time(self, preferences: NotificationPreference) -> datetime:
        """حساب وقت الإرسال التالي بعد انتهاء وقت عدم الإزعاج"""
        
        now = timezone.now()
        
        if preferences.quiet_hours_end:
            # حساب الوقت التالي بعد انتهاء وقت عدم الإزعاج
            next_send = now.replace(
                hour=preferences.quiet_hours_end.hour,
                minute=preferences.quiet_hours_end.minute,
                second=0,
                microsecond=0
            )
            
            if next_send <= now:
                next_send += timedelta(days=1)
            
            return next_send
        
        return now
    
    def _check_rule_conditions(self, rule: NotificationRule, context: Dict) -> bool:
        """التحقق من شروط القاعدة"""
        
        if not rule.conditions:
            return True
        
        try:
            # تقييم الشروط
            for condition_key, condition_value in rule.conditions.items():
                context_value = context.get(condition_key)
                
                if isinstance(condition_value, dict):
                    # شروط معقدة
                    operator = condition_value.get('operator', 'eq')
                    expected_value = condition_value.get('value')
                    
                    if operator == 'eq' and context_value != expected_value:
                        return False
                    elif operator == 'ne' and context_value == expected_value:
                        return False
                    elif operator == 'gt' and context_value <= expected_value:
                        return False
                    elif operator == 'lt' and context_value >= expected_value:
                        return False
                    elif operator == 'in' and context_value not in expected_value:
                        return False
                    elif operator == 'not_in' and context_value in expected_value:
                        return False
                else:
                    # شرط بسيط
                    if context_value != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rule conditions: {e}")
            return False
    
    def _get_rule_recipients(self, rule: NotificationRule, context: Dict, content_object: Any) -> List[User]:
        """تحديد مستقبلي الإشعار حسب القاعدة"""
        
        recipients = []
        
        # المستخدمون المحددون مباشرة
        recipients.extend(rule.recipient_users.all())
        
        # المستخدمون حسب الأدوار
        if rule.recipient_roles:
            for role in rule.recipient_roles:
                if role == 'employee' and content_object:
                    if hasattr(content_object, 'employee'):
                        recipients.append(content_object.employee.user)
                elif role == 'manager' and content_object:
                    if hasattr(content_object, 'employee') and content_object.employee.direct_manager:
                        recipients.append(content_object.employee.direct_manager.user)
                elif role == 'hr_department':
                    # الحصول على موظفي قسم الموارد البشرية
                    hr_users = self._get_hr_users(context.get('company'))
                    recipients.extend(hr_users)
        
        # إزالة التكرارات
        return list(set(recipients))
    
    def _get_hr_users(self, company) -> List[User]:
        """الحصول على مستخدمي قسم الموارد البشرية"""
        
        try:
            from ..models_enhanced import Employee, Department
            
            hr_departments = Department.objects.filter(
                company=company,
                name__icontains='موارد بشرية',
                is_active=True
            )
            
            if not hr_departments.exists():
                hr_departments = Department.objects.filter(
                    company=company,
                    name__icontains='HR',
                    is_active=True
                )
            
            hr_employees = Employee.objects.filter(
                department__in=hr_departments,
                is_active=True
            )
            
            return [emp.user for emp in hr_employees if emp.user]
            
        except Exception as e:
            logger.error(f"Error getting HR users: {e}")
            return []
    
    def _schedule_notification(self, notification: Notification):
        """جدولة الإشعار للإرسال لاحقاً"""
        
        try:
            # استخدام Celery لجدولة المهام
            send_scheduled_notification.apply_async(
                args=[str(notification.id)],
                eta=notification.scheduled_at
            )
            
            logger.info(f"Notification {notification.id} scheduled for {notification.scheduled_at}")
            
        except Exception as e:
            logger.error(f"Error scheduling notification: {e}")
            # إرسال فوري في حالة فشل الجدولة
            self._send_notification(notification)


@shared_task
def send_scheduled_notification(notification_id: str):
    """مهمة Celery لإرسال الإشعارات المجدولة"""
    
    try:
        notification = Notification.objects.get(id=notification_id)
        
        if notification.status == 'pending' and not notification.is_expired():
            service = AdvancedNotificationService()
            service._send_notification(notification)
        
    except Notification.DoesNotExist:
        logger.error(f"Scheduled notification not found: {notification_id}")
    except Exception as e:
        logger.error(f"Error sending scheduled notification: {e}")


@shared_task
def process_notification_digests():
    """معالجة ملخصات الإشعارات"""
    
    try:
        service = NotificationDigestService()
        service.process_daily_digests()
        service.process_weekly_digests()
        service.process_monthly_digests()
        
    except Exception as e:
        logger.error(f"Error processing notification digests: {e}")


class NotificationDigestService:
    """خدمة ملخصات الإشعارات"""
    
    def process_daily_digests(self):
        """معالجة الملخصات اليومية"""
        
        users_with_daily_digest = NotificationPreference.objects.filter(
            digest_enabled=True,
            digest_frequency='daily'
        )
        
        for preference in users_with_daily_digest:
            self._create_digest(preference.user, 'daily')
    
    def process_weekly_digests(self):
        """معالجة الملخصات الأسبوعية"""
        
        # تشغيل فقط في يوم الأحد
        if timezone.now().weekday() != 6:  # 6 = Sunday
            return
        
        users_with_weekly_digest = NotificationPreference.objects.filter(
            digest_enabled=True,
            digest_frequency='weekly'
        )
        
        for preference in users_with_weekly_digest:
            self._create_digest(preference.user, 'weekly')
    
    def process_monthly_digests(self):
        """معالجة الملخصات الشهرية"""
        
        # تشغيل فقط في اليوم الأول من الشهر
        if timezone.now().day != 1:
            return
        
        users_with_monthly_digest = NotificationPreference.objects.filter(
            digest_enabled=True,
            digest_frequency='monthly'
        )
        
        for preference in users_with_monthly_digest:
            self._create_digest(preference.user, 'monthly')
    
    def _create_digest(self, user: User, frequency: str):
        """إنشاء ملخص الإشعارات"""
        
        try:
            # تحديد فترة الملخص
            now = timezone.now()
            
            if frequency == 'daily':
                period_start = now - timedelta(days=1)
            elif frequency == 'weekly':
                period_start = now - timedelta(weeks=1)
            elif frequency == 'monthly':
                period_start = now - timedelta(days=30)
            else:
                return
            
            period_end = now
            
            # التحقق من وجود ملخص لنفس الفترة
            existing_digest = NotificationDigest.objects.filter(
                user=user,
                frequency=frequency,
                period_start__date=period_start.date()
            ).first()
            
            if existing_digest:
                return
            
            # الحصول على الإشعارات
            notifications = Notification.objects.filter(
                recipient=user,
                created_at__range=[period_start, period_end],
                status__in=['sent', 'delivered', 'read']
            ).order_by('-created_at')
            
            if not notifications.exists():
                return
            
            # إنشاء محتوى الملخص
            title = f"ملخص الإشعارات {self._get_frequency_display(frequency)}"
            content = self._generate_digest_content(notifications, frequency)
            
            # إنشاء الملخص
            digest = NotificationDigest.objects.create(
                user=user,
                frequency=frequency,
                period_start=period_start,
                period_end=period_end,
                title=title,
                content=content,
                status='pending'
            )
            
            # ربط الإشعارات بالملخص
            digest.notifications.set(notifications)
            
            # إرسال الملخص
            self._send_digest(digest)
            
        except Exception as e:
            logger.error(f"Error creating digest for user {user.username}: {e}")
    
    def _generate_digest_content(self, notifications, frequency: str) -> str:
        """توليد محتوى الملخص"""
        
        # تجميع الإشعارات حسب النوع
        notifications_by_type = {}
        for notification in notifications:
            notification_type = notification.get_notification_type_display()
            if notification_type not in notifications_by_type:
                notifications_by_type[notification_type] = []
            notifications_by_type[notification_type].append(notification)
        
        # بناء المحتوى
        content_parts = [
            f"إجمالي الإشعارات: {notifications.count()}",
            ""
        ]
        
        for notification_type, type_notifications in notifications_by_type.items():
            content_parts.append(f"## {notification_type} ({len(type_notifications)})")
            
            for notification in type_notifications[:5]:  # أول 5 إشعارات فقط
                content_parts.append(f"- {notification.title}")
            
            if len(type_notifications) > 5:
                content_parts.append(f"... و {len(type_notifications) - 5} إشعارات أخرى")
            
            content_parts.append("")
        
        return "\n".join(content_parts)
    
    def _send_digest(self, digest: NotificationDigest):
        """إرسال الملخص"""
        
        try:
            # إرسال الملخص كبريد إلكتروني
            subject = digest.title
            message = digest.content
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[digest.user.email]
            )
            
            msg.send()
            
            # تحديث حالة الملخص
            digest.status = 'sent'
            digest.sent_at = timezone.now()
            digest.save(update_fields=['status', 'sent_at', 'updated_at'])
            
            logger.info(f"Digest sent to {digest.user.username}")
            
        except Exception as e:
            digest.status = 'failed'
            digest.save(update_fields=['status', 'updated_at'])
            logger.error(f"Error sending digest: {e}")
    
    def _get_frequency_display(self, frequency: str) -> str:
        """عرض تكرار الملخص"""
        
        frequency_map = {
            'daily': 'اليومي',
            'weekly': 'الأسبوعي',
            'monthly': 'الشهري'
        }
        
        return frequency_map.get(frequency, frequency)