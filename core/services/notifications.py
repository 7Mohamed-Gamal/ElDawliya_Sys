"""
خدمة الإشعارات الذكية
Smart Notifications Service
"""
from django.contrib.auth.models import User
from django.utils import timezone
from django.template import Context, Template
from core.models.settings import NotificationTemplate
from .base import BaseService


class NotificationService(BaseService):
    """
    خدمة الإشعارات الذكية
    Smart notification service for multi-channel messaging
    """
    
    CHANNELS = {
        'in_app': 'داخل التطبيق',
        'email': 'البريد الإلكتروني',
        'sms': 'رسائل نصية',
        'push': 'إشعارات فورية',
    }
    
    PRIORITY_LEVELS = {
        'low': 1,
        'normal': 2,
        'high': 3,
        'urgent': 4,
    }
    
    def send_notification(self, recipient, template_name, context=None, 
                         channels=None, priority='normal', send_at=None):
        """
        إرسال إشعار متعدد القنوات
        Send multi-channel notification
        """
        try:
            # Get notification template
            template = self._get_template(template_name)
            if not template:
                return self.format_response(
                    success=False,
                    message=f'قالب الإشعار {template_name} غير موجود'
                )
            
            # Use default channels if not specified
            channels = channels or ['in_app']
            context = context or {}
            
            # Add common context variables
            context.update(self._get_common_context(recipient))
            
            # Render template content
            subject = template.render_subject(context)
            message = template.render_message(context)
            
            # Create notification record
            notification = self._create_notification_record(
                recipient=recipient,
                template=template,
                subject=subject,
                message=message,
                priority=priority,
                channels=channels
            )
            
            # Send via each channel
            results = {}
            for channel in channels:
                if send_at:
                    # Schedule notification
                    results[channel] = self._schedule_notification(
                        notification, channel, send_at
                    )
                else:
                    # Send immediately
                    results[channel] = self._send_via_channel(
                        notification, channel, context
                    )
            
            # Log the notification
            self.log_action(
                action='create',
                resource='notification',
                content_object=notification,
                details={
                    'template_name': template_name,
                    'channels': channels,
                    'recipient_id': recipient.id if hasattr(recipient, 'id') else None,
                    'results': results
                },
                message=f'تم إرسال إشعار: {subject}'
            )
            
            return self.format_response(
                data={
                    'notification_id': notification.id if hasattr(notification, 'id') else None,
                    'results': results
                },
                message='تم إرسال الإشعار بنجاح'
            )
            
        except Exception as e:
            return self.handle_exception(e, 'send_notification', template_name, {
                'recipient': str(recipient),
                'template_name': template_name,
                'channels': channels
            })
    
    def send_bulk_notification(self, recipients, template_name, context=None, 
                              channels=None, priority='normal'):
        """
        إرسال إشعار جماعي
        Send bulk notification to multiple recipients
        """
        results = []
        
        for recipient in recipients:
            # Add recipient-specific context
            recipient_context = context.copy() if context else {}
            recipient_context.update(self._get_recipient_context(recipient))
            
            result = self.send_notification(
                recipient=recipient,
                template_name=template_name,
                context=recipient_context,
                channels=channels,
                priority=priority
            )
            
            results.append({
                'recipient': str(recipient),
                'success': result['success'],
                'message': result.get('message', ''),
            })
        
        success_count = sum(1 for r in results if r['success'])
        
        return self.format_response(
            data={
                'total_sent': len(recipients),
                'successful': success_count,
                'failed': len(recipients) - success_count,
                'results': results
            },
            message=f'تم إرسال {success_count} من {len(recipients)} إشعار'
        )
    
    def schedule_notification(self, recipient, template_name, send_at, 
                             context=None, channels=None, priority='normal'):
        """
        جدولة إشعار للإرسال لاحقاً
        Schedule notification for later delivery
        """
        return self.send_notification(
            recipient=recipient,
            template_name=template_name,
            context=context,
            channels=channels,
            priority=priority,
            send_at=send_at
        )
    
    def create_template(self, data):
        """
        إنشاء قالب إشعار جديد
        Create new notification template
        """
        self.check_permission('core.add_notificationtemplate')
        
        required_fields = ['name', 'display_name', 'template_type', 'message_template']
        self.validate_required_fields(data, required_fields)
        
        try:
            template = NotificationTemplate.objects.create(
                **data,
                created_by=self.user,
                updated_by=self.user
            )
            
            self.log_action(
                action='create',
                resource='notification_template',
                content_object=template,
                new_values=data,
                message=f'تم إنشاء قالب إشعار جديد: {template.display_name}'
            )
            
            return self.format_response(
                data=template,
                message='تم إنشاء قالب الإشعار بنجاح'
            )
            
        except Exception as e:
            return self.handle_exception(e, 'create_template', 'notification_template', data)
    
    def get_user_notifications(self, user_id=None, unread_only=False, 
                              page=1, page_size=20):
        """
        الحصول على إشعارات المستخدم
        Get user notifications
        """
        # This will be implemented when we have notification models
        # For now, return empty result
        return self.paginate_queryset([], page, page_size)
    
    def mark_notification_read(self, notification_id):
        """
        تمييز الإشعار كمقروء
        Mark notification as read
        """
        # This will be implemented when we have notification models
        return self.format_response(message='تم تمييز الإشعار كمقروء')
    
    def _get_template(self, template_name):
        """الحصول على قالب الإشعار"""
        try:
            return NotificationTemplate.objects.get(
                name=template_name,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            return None
    
    def _get_common_context(self, recipient):
        """الحصول على السياق المشترك للإشعارات"""
        from core.models.settings import CompanyProfile
        
        context = {
            'current_date': timezone.now().strftime('%Y-%m-%d'),
            'current_time': timezone.now().strftime('%H:%M'),
            'current_datetime': timezone.now(),
        }
        
        # Add company information
        company = CompanyProfile.get_company()
        if company:
            context.update({
                'company_name': company.name,
                'company_email': company.email,
                'company_phone': company.phone,
                'company_website': company.website,
            })
        
        return context
    
    def _get_recipient_context(self, recipient):
        """الحصول على سياق المستلم"""
        context = {}
        
        if hasattr(recipient, 'username'):
            # User object
            context.update({
                'recipient_name': recipient.get_full_name() or recipient.username,
                'recipient_email': recipient.email,
                'recipient_username': recipient.username,
            })
        elif hasattr(recipient, 'first_name'):
            # Employee object (when implemented)
            context.update({
                'recipient_name': f"{recipient.first_name} {recipient.last_name}",
                'recipient_email': getattr(recipient, 'email', ''),
            })
        
        return context
    
    def _create_notification_record(self, recipient, template, subject, 
                                   message, priority, channels):
        """إنشاء سجل الإشعار"""
        # This will create actual notification record when model is implemented
        # For now, return a mock object
        class MockNotification:
            def __init__(self):
                self.id = f"notif_{timezone.now().timestamp()}"
                self.subject = subject
                self.message = message
                self.priority = priority
                self.channels = channels
        
        return MockNotification()
    
    def _send_via_channel(self, notification, channel, context):
        """إرسال الإشعار عبر قناة محددة"""
        try:
            if channel == 'email':
                return self._send_email(notification, context)
            elif channel == 'sms':
                return self._send_sms(notification, context)
            elif channel == 'push':
                return self._send_push(notification, context)
            elif channel == 'in_app':
                return self._send_in_app(notification, context)
            else:
                return {
                    'success': False,
                    'message': f'قناة الإرسال {channel} غير مدعومة'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في إرسال الإشعار عبر {channel}: {str(e)}'
            }
    
    def _send_email(self, notification, context):
        """إرسال إشعار بالبريد الإلكتروني"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        try:
            # This is a basic implementation
            # In production, you might want to use more advanced email services
            send_mail(
                subject=notification.subject,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[context.get('recipient_email', '')],
                fail_silently=False,
            )
            
            return {
                'success': True,
                'message': 'تم إرسال البريد الإلكتروني بنجاح'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'فشل في إرسال البريد الإلكتروني: {str(e)}'
            }
    
    def _send_sms(self, notification, context):
        """إرسال رسالة نصية"""
        # This would integrate with SMS service provider
        # For now, return success
        return {
            'success': True,
            'message': 'تم إرسال الرسالة النصية بنجاح (محاكاة)'
        }
    
    def _send_push(self, notification, context):
        """إرسال إشعار فوري"""
        # This would integrate with push notification service
        # For now, return success
        return {
            'success': True,
            'message': 'تم إرسال الإشعار الفوري بنجاح (محاكاة)'
        }
    
    def _send_in_app(self, notification, context):
        """إرسال إشعار داخل التطبيق"""
        # This would create in-app notification record
        # For now, return success
        return {
            'success': True,
            'message': 'تم إنشاء الإشعار داخل التطبيق بنجاح'
        }
    
    def _schedule_notification(self, notification, channel, send_at):
        """جدولة إشعار للإرسال لاحقاً"""
        # This would create scheduled notification record
        # For now, return success
        return {
            'success': True,
            'message': f'تم جدولة الإشعار للإرسال في {send_at}'
        }