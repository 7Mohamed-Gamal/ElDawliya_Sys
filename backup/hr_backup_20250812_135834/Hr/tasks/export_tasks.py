"""
مهام Celery للتصدير المجدول
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging

try:
    from celery import shared_task
except ImportError:
    # إذا لم يكن Celery مثبتاً، استخدم دالة وهمية
    def shared_task(func):
        return func

from ..models_reports import ScheduledReport, ReportInstance
from ..services.report_service import report_service
from ..services.export_service import export_service

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3)
def execute_scheduled_report(self, scheduled_report_id):
    """تنفيذ تقرير مجدول"""
    try:
        scheduled_report = ScheduledReport.objects.get(id=scheduled_report_id, is_active=True)
        
        logger.info(f"بدء تنفيذ التقرير المجدول: {scheduled_report.name}")
        
        # إنتاج التقرير
        instance = report_service.generate_report(
            template_id=scheduled_report.template.id,
            user=scheduled_report.created_by,
            parameters=scheduled_report.parameters,
            output_format=scheduled_report.output_format
        )
        
        # إرسال التقرير عبر البريد الإلكتروني إذا كان مطلوباً
        if scheduled_report.email_recipients:
            export_service.send_report_email(
                report_instance=instance,
                recipients=scheduled_report.email_recipients,
                subject=scheduled_report.email_subject,
                body=scheduled_report.email_body
            )
        
        # تحديث معلومات التشغيل
        scheduled_report.last_run = timezone.now()
        scheduled_report.run_count += 1
        scheduled_report.next_run = calculate_next_run(scheduled_report)
        scheduled_report.save()
        
        logger.info(f"تم تنفيذ التقرير المجدول بنجاح: {scheduled_report.name}")
        
        return {
            'success': True,
            'instance_id': str(instance.id),
            'message': 'تم تنفيذ التقرير المجدول بنجاح'
        }
        
    except ScheduledReport.DoesNotExist:
        logger.error(f"التقرير المجدول غير موجود: {scheduled_report_id}")
        return {
            'success': False,
            'message': 'التقرير المجدول غير موجود'
        }
    except Exception as e:
        logger.error(f"خطأ في تنفيذ التقرير المجدول {scheduled_report_id}: {e}")
        
        # إعادة المحاولة
        if self.request.retries < self.max_retries:
            logger.info(f"إعادة محاولة تنفيذ التقرير المجدول: {scheduled_report_id}")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return {
            'success': False,
            'message': f'فشل في تنفيذ التقرير المجدول: {str(e)}'
        }


@shared_task
def process_scheduled_reports():
    """معالجة جميع التقارير المجدولة المستحقة"""
    try:
        now = timezone.now()
        
        # الحصول على التقارير المستحقة للتنفيذ
        due_reports = ScheduledReport.objects.filter(
            is_active=True,
            next_run__lte=now
        )
        
        logger.info(f"وُجد {due_reports.count()} تقرير مجدول مستحق للتنفيذ")
        
        results = []
        for scheduled_report in due_reports:
            try:
                # تنفيذ التقرير بشكل غير متزامن
                task = execute_scheduled_report.delay(scheduled_report.id)
                results.append({
                    'scheduled_report_id': str(scheduled_report.id),
                    'task_id': task.id,
                    'status': 'queued'
                })
                
                logger.info(f"تم إضافة التقرير المجدول للطابور: {scheduled_report.name}")
                
            except Exception as e:
                logger.error(f"خطأ في إضافة التقرير المجدول للطابور {scheduled_report.id}: {e}")
                results.append({
                    'scheduled_report_id': str(scheduled_report.id),
                    'status': 'error',
                    'message': str(e)
                })
        
        return {
            'success': True,
            'processed_count': len(results),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"خطأ في معالجة التقارير المجدولة: {e}")
        return {
            'success': False,
            'message': str(e)
        }


@shared_task
def cleanup_old_reports():
    """تنظيف التقارير القديمة"""
    try:
        # حذف التقارير الأقدم من 30 يوماً
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_instances = ReportInstance.objects.filter(
            created_at__lt=cutoff_date,
            status='completed'
        )
        
        deleted_count = 0
        for instance in old_instances:
            try:
                # حذف الملف إذا كان موجوداً
                if instance.file_path:
                    from django.core.files.storage import default_storage
                    if default_storage.exists(instance.file_path):
                        default_storage.delete(instance.file_path)
                
                # حذف السجل
                instance.delete()
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"خطأ في حذف التقرير {instance.id}: {e}")
        
        logger.info(f"تم حذف {deleted_count} تقرير قديم")
        
        return {
            'success': True,
            'deleted_count': deleted_count
        }
        
    except Exception as e:
        logger.error(f"خطأ في تنظيف التقارير القديمة: {e}")
        return {
            'success': False,
            'message': str(e)
        }


@shared_task
def generate_bulk_reports(template_ids, parameters_list, user_id, output_format='excel'):
    """إنتاج تقارير متعددة بشكل مجمع"""
    try:
        user = User.objects.get(id=user_id)
        results = []
        
        for i, template_id in enumerate(template_ids):
            try:
                parameters = parameters_list[i] if i < len(parameters_list) else {}
                
                instance = report_service.generate_report(
                    template_id=template_id,
                    user=user,
                    parameters=parameters,
                    output_format=output_format
                )
                
                results.append({
                    'template_id': str(template_id),
                    'instance_id': str(instance.id),
                    'status': 'success'
                })
                
            except Exception as e:
                logger.error(f"خطأ في إنتاج التقرير {template_id}: {e}")
                results.append({
                    'template_id': str(template_id),
                    'status': 'error',
                    'message': str(e)
                })
        
        return {
            'success': True,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"خطأ في الإنتاج المجمع للتقارير: {e}")
        return {
            'success': False,
            'message': str(e)
        }


@shared_task
def export_report_to_multiple_formats(instance_id, formats):
    """تصدير تقرير بصيغ متعددة"""
    try:
        instance = ReportInstance.objects.get(id=instance_id)
        results = []
        
        for format_type in formats:
            try:
                # إنشاء نسخة جديدة بالصيغة المطلوبة
                new_instance = ReportInstance.objects.create(
                    template=instance.template,
                    name=f"{instance.name} - {format_type.upper()}",
                    parameters=instance.parameters,
                    filters_applied=instance.filters_applied,
                    output_format=format_type,
                    created_by=instance.created_by
                )
                
                # إنتاج التقرير بالصيغة الجديدة
                new_instance.mark_as_processing()
                
                # استخدام نفس البيانات
                data = instance.result_data
                
                # تصدير بالصيغة المطلوبة
                file_content, content_type = export_service.export_data(
                    data=data,
                    format_type=format_type,
                    template_name=instance.template.name,
                    metadata={
                        'title': instance.template.name,
                        'record_count': len(data) if isinstance(data, list) else 0
                    }
                )
                
                # حفظ الملف
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile
                
                filename = f"report_{new_instance.id}.{format_type}"
                file_path = f"reports/{filename}"
                
                saved_path = default_storage.save(file_path, ContentFile(file_content))
                file_size = len(file_content)
                
                new_instance.mark_as_completed(
                    file_path=saved_path,
                    record_count=len(data) if isinstance(data, list) else 0,
                    file_size=file_size
                )
                
                results.append({
                    'format': format_type,
                    'instance_id': str(new_instance.id),
                    'status': 'success'
                })
                
            except Exception as e:
                logger.error(f"خطأ في تصدير التقرير بصيغة {format_type}: {e}")
                results.append({
                    'format': format_type,
                    'status': 'error',
                    'message': str(e)
                })
        
        return {
            'success': True,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"خطأ في التصدير متعدد الصيغ: {e}")
        return {
            'success': False,
            'message': str(e)
        }


def calculate_next_run(scheduled_report):
    """حساب موعد التشغيل التالي للتقرير المجدول"""
    try:
        now = timezone.now()
        frequency = scheduled_report.frequency
        
        if frequency == 'daily':
            return now + timedelta(days=1)
        elif frequency == 'weekly':
            return now + timedelta(weeks=1)
        elif frequency == 'monthly':
            # الشهر التالي في نفس اليوم
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1)
            else:
                next_month = now.replace(month=now.month + 1)
            return next_month
        elif frequency == 'quarterly':
            return now + timedelta(days=90)
        elif frequency == 'yearly':
            return now.replace(year=now.year + 1)
        elif frequency == 'custom' and scheduled_report.cron_expression:
            # TODO: تنفيذ تحليل تعبير Cron
            return now + timedelta(days=1)
        else:
            return now + timedelta(days=1)
            
    except Exception as e:
        logger.error(f"خطأ في حساب موعد التشغيل التالي: {e}")
        return timezone.now() + timedelta(days=1)