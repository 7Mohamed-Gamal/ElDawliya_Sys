"""
سكريبت اختبار نظام التنبيهات
يستخدم هذا السكريبت لاختبار إنشاء التنبيهات لمختلف التطبيقات
"""

import os
import django
import sys

# إعداد بيئة Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from Hr.models.employee_model import Employee
from Hr.models.task_models import EmployeeTask
from meetings.models import Meeting, Attendee
from tasks.models import Task
from inventory.models import TblProducts
from Purchase_orders.models import PurchaseRequest, PurchaseRequestItem

from notifications.utils import (
    create_hr_notification,
    create_meeting_notification,
    create_inventory_notification,
    create_purchase_notification,
    create_system_notification,
    get_unread_notifications_count,
    get_notifications_by_type
)

User = get_user_model()

def test_hr_notifications():
    """اختبار تنبيهات الموارد البشرية"""
    print("اختبار تنبيهات الموارد البشرية...")
    
    # الحصول على مستخدم للاختبار
    user = User.objects.first()
    if not user:
        print("لا يوجد مستخدمين في النظام!")
        return
    
    # إنشاء تنبيه مباشر
    notification = create_hr_notification(
        user=user,
        title="تنبيه اختبار للموارد البشرية",
        message="هذا تنبيه اختبار للموارد البشرية",
        priority="medium",
        url="/Hr/"
    )
    
    print(f"تم إنشاء تنبيه: {notification.title}")
    
    # اختبار إنشاء مهمة موظف (يجب أن ينشئ تنبيه تلقائيًا)
    try:
        employee = Employee.objects.first()
        if employee:
            with transaction.atomic():
                task = EmployeeTask.objects.create(
                    title="مهمة اختبار",
                    description="وصف مهمة الاختبار",
                    start_date=timezone.now(),
                    end_date=timezone.now() + timezone.timedelta(days=1),
                    employee=employee,
                    assigned_by=user,
                    status="pending"
                )
            print(f"تم إنشاء مهمة موظف: {task.title}")
        else:
            print("لا يوجد موظفين في النظام!")
    except Exception as e:
        print(f"خطأ في إنشاء مهمة موظف: {e}")


def test_meeting_notifications():
    """اختبار تنبيهات الاجتماعات"""
    print("اختبار تنبيهات الاجتماعات...")
    
    # الحصول على مستخدم للاختبار
    user = User.objects.first()
    if not user:
        print("لا يوجد مستخدمين في النظام!")
        return
    
    # إنشاء تنبيه مباشر
    notification = create_meeting_notification(
        user=user,
        title="تنبيه اختبار للاجتماعات",
        message="هذا تنبيه اختبار للاجتماعات",
        priority="medium",
        url="/meetings/"
    )
    
    print(f"تم إنشاء تنبيه: {notification.title}")
    
    # اختبار إنشاء اجتماع (يجب أن ينشئ تنبيه تلقائيًا)
    try:
        with transaction.atomic():
            meeting = Meeting.objects.create(
                title="اجتماع اختبار",
                date=timezone.now() + timezone.timedelta(days=1),
                topic="موضوع اجتماع الاختبار",
                created_by=user,
                status="pending"
            )
            
            # إضافة الحضور
            attendee = Attendee.objects.create(
                meeting=meeting,
                user=user
            )
            
        print(f"تم إنشاء اجتماع: {meeting.title}")
    except Exception as e:
        print(f"خطأ في إنشاء اجتماع: {e}")


def test_task_notifications():
    """اختبار تنبيهات المهام"""
    print("اختبار تنبيهات المهام...")
    
    # الحصول على مستخدمين للاختبار
    users = User.objects.all()[:2]
    if len(users) < 2:
        print("يجب توفر مستخدمين على الأقل للاختبار!")
        return
    
    creator = users[0]
    assignee = users[1]
    
    # إنشاء تنبيه مباشر
    notification = create_meeting_notification(
        user=assignee,
        title="تنبيه اختبار للمهام",
        message="هذا تنبيه اختبار للمهام",
        priority="medium",
        url="/tasks/"
    )
    
    print(f"تم إنشاء تنبيه: {notification.title}")
    
    # اختبار إنشاء مهمة (يجب أن ينشئ تنبيه تلقائيًا)
    try:
        with transaction.atomic():
            task = Task.objects.create(
                description="مهمة اختبار",
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=1),
                assigned_to=assignee,
                created_by=creator,
                status="pending"
            )
            
        print(f"تم إنشاء مهمة: {task.description}")
    except Exception as e:
        print(f"خطأ في إنشاء مهمة: {e}")


def test_inventory_notifications():
    """اختبار تنبيهات المخزن"""
    print("اختبار تنبيهات المخزن...")
    
    # الحصول على مستخدم للاختبار
    user = User.objects.first()
    if not user:
        print("لا يوجد مستخدمين في النظام!")
        return
    
    # إنشاء تنبيه مباشر
    notification = create_inventory_notification(
        user=user,
        title="تنبيه اختبار للمخزن",
        message="هذا تنبيه اختبار للمخزن",
        priority="medium",
        url="/inventory/"
    )
    
    print(f"تم إنشاء تنبيه: {notification.title}")


def test_purchase_notifications():
    """اختبار تنبيهات طلبات الشراء"""
    print("اختبار تنبيهات طلبات الشراء...")
    
    # الحصول على مستخدم للاختبار
    user = User.objects.first()
    if not user:
        print("لا يوجد مستخدمين في النظام!")
        return
    
    # إنشاء تنبيه مباشر
    notification = create_purchase_notification(
        user=user,
        title="تنبيه اختبار لطلبات الشراء",
        message="هذا تنبيه اختبار لطلبات الشراء",
        priority="medium",
        url="/purchase/"
    )
    
    print(f"تم إنشاء تنبيه: {notification.title}")
    
    # اختبار إنشاء طلب شراء (يجب أن ينشئ تنبيه تلقائيًا)
    try:
        with transaction.atomic():
            purchase_request = PurchaseRequest.objects.create(
                request_number=f"TEST-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                requested_by=user,
                status="pending"
            )
            
        print(f"تم إنشاء طلب شراء: {purchase_request.request_number}")
    except Exception as e:
        print(f"خطأ في إنشاء طلب شراء: {e}")


def test_system_notifications():
    """اختبار تنبيهات النظام"""
    print("اختبار تنبيهات النظام...")
    
    # الحصول على مستخدم للاختبار
    user = User.objects.first()
    if not user:
        print("لا يوجد مستخدمين في النظام!")
        return
    
    # إنشاء تنبيه مباشر
    notification = create_system_notification(
        user=user,
        title="تنبيه اختبار للنظام",
        message="هذا تنبيه اختبار للنظام",
        priority="medium",
        url="/"
    )
    
    print(f"تم إنشاء تنبيه: {notification.title}")


def check_notifications():
    """التحقق من التنبيهات"""
    print("التحقق من التنبيهات...")
    
    # الحصول على مستخدم للاختبار
    user = User.objects.first()
    if not user:
        print("لا يوجد مستخدمين في النظام!")
        return
    
    # الحصول على عدد التنبيهات غير المقروءة
    unread_count = get_unread_notifications_count(user)
    print(f"عدد التنبيهات غير المقروءة: {unread_count}")
    
    # الحصول على التنبيهات حسب النوع
    hr_notifications = get_notifications_by_type(user, notification_type='hr', limit=5)
    print(f"تنبيهات الموارد البشرية: {hr_notifications.count()}")
    
    meeting_notifications = get_notifications_by_type(user, notification_type='meetings', limit=5)
    print(f"تنبيهات الاجتماعات: {meeting_notifications.count()}")
    
    inventory_notifications = get_notifications_by_type(user, notification_type='inventory', limit=5)
    print(f"تنبيهات المخزن: {inventory_notifications.count()}")
    
    purchase_notifications = get_notifications_by_type(user, notification_type='purchase', limit=5)
    print(f"تنبيهات طلبات الشراء: {purchase_notifications.count()}")
    
    system_notifications = get_notifications_by_type(user, notification_type='system', limit=5)
    print(f"تنبيهات النظام: {system_notifications.count()}")


if __name__ == "__main__":
    print("بدء اختبار نظام التنبيهات...")
    
    # اختبار التنبيهات لكل تطبيق
    test_hr_notifications()
    test_meeting_notifications()
    test_task_notifications()
    test_inventory_notifications()
    test_purchase_notifications()
    test_system_notifications()
    
    # التحقق من التنبيهات
    check_notifications()
    
    print("انتهى اختبار نظام التنبيهات.")