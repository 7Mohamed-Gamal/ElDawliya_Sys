# نظام التنبيهات

## نظرة عامة
نظام التنبيهات مصمم للتكامل مع جميع تطبيقات المشروع، ويوفر آلية موحدة لإنشاء وإدارة التنبيهات للمستخدمين. يستخدم النظام إشارات Django (signals) للاستجابة للأحداث في مختلف التطبيقات وإنشاء التنبيهات المناسبة.

## هيكل النظام
- **models.py**: يحتوي على نموذج `Notification` الذي يخزن جميع التنبيهات.
- **utils.py**: يحتوي على وظائف مساعدة لإنشاء وإدارة التنبيهات.
- **signals.py**: الملف الرئيسي الذي يستورد جميع ملفات الإشارات الأخرى.
- **signals_meetings.py**: يحتوي على إشارات خاصة بتطبيق الاجتماعات.
- **signals_tasks.py**: يحتوي على إشارات خاصة بتطبيق المهام.
- **signals_inventory.py**: يحتوي على إشارات خاصة بتطبيق المخزن.
- **signals_purchase.py**: يحتوي على إشارات خاصة بتطبيق طلبات الشراء.

## أنواع التنبيهات
النظام يدعم الأنواع التالية من التنبيهات:
- **hr**: تنبيهات الموارد البشرية
- **meetings**: تنبيهات الاجتماعات
- **inventory**: تنبيهات المخزن
- **purchase**: تنبيهات المشتريات
- **system**: تنبيهات النظام

## مستويات الأولوية
يمكن تعيين مستويات الأولوية التالية للتنبيهات:
- **low**: منخفضة
- **medium**: متوسطة
- **high**: عالية
- **urgent**: عاجلة

## التنبيهات حسب التطبيق

### تطبيق الموارد البشرية (Hr)
- تنبيهات المهام المسندة للموظفين
- تنبيهات إكمال المهام
- تنبيهات طلبات الإجازات وحالتها
- تنبيهات انتهاء البطاقة الصحية للموظفين
- تنبيهات انتهاء عقود العمل
- تنبيهات انتهاء رخص السيارات والسائقين

### تطبيق الاجتماعات (meetings)
- تنبيهات الاجتماعات الجديدة
- تنبيهات إضافة مستخدم إلى اجتماع
- تنبيهات إكمال أو إلغاء الاجتماعات

### تطبيق المهام (tasks)
- تنبيهات المهام الجديدة
- تنبيهات تغيير حالة المهام
- تنبيهات إضافة خطوات جديدة للمهام

### تطبيق المخزن (inventory)
- تنبيهات المنتجات التي وصلت للحد الأدنى
- تنبيهات المنتجات التي نفدت من المخزن
- تنبيهات حركات المخزن الجديدة

### تطبيق طلبات الشراء (Purchase_orders)
- تنبيهات طلبات الشراء الجديدة
- تنبيهات الموافقة على طلبات الشراء
- تنبيهات رفض طلبات الشراء
- تنبيهات تغيير حالة عناصر طلبات الشراء

## كيفية استخدام النظام

### إنشاء تنبيه جديد
يمكن إنشاء تنبيه جديد باستخدام الوظائف المساعدة في ملف `utils.py`:

```python
from notifications.utils import create_hr_notification, create_meeting_notification, create_inventory_notification, create_purchase_notification, create_system_notification

# مثال لإنشاء تنبيه للموارد البشرية
create_hr_notification(
    user=user_instance,
    title='عنوان التنبيه',
    message='نص التنبيه',
    priority='medium',
    content_object=related_object,  # اختياري
    url='/path/to/related/page/'  # اختياري
)
```

### الحصول على التنبيهات غير المقروءة
```python
from notifications.utils import get_unread_notifications_count, get_notifications_by_type

# الحصول على عدد التنبيهات غير المقروءة للمستخدم
count = get_unread_notifications_count(user_instance)

# الحصول على التنبيهات غير المقروءة للمستخدم
notifications = get_notifications_by_type(user_instance, include_read=False)

# الحصول على التنبيهات غير المقروءة للمستخدم من نوع معين
hr_notifications = get_notifications_by_type(user_instance, notification_type='hr', include_read=False)
```

### تعليم التنبيهات كمقروءة
```python
from notifications.utils import mark_all_as_read

# تعليم جميع التنبيهات غير المقروءة للمستخدم كمقروءة
mark_all_as_read(user_instance)

# تعليم جميع التنبيهات غير المقروءة للمستخدم من نوع معين كمقروءة
mark_all_as_read(user_instance, notification_type='hr')

# تعليم تنبيه واحد كمقروء
notification_instance.mark_as_read()
```

## إضافة تنبيهات جديدة
لإضافة نوع جديد من التنبيهات، يجب اتباع الخطوات التالية:

1. تحديد الأحداث التي ستؤدي إلى إنشاء التنبيهات
2. إضافة إشارات (signals) جديدة في الملف المناسب أو إنشاء ملف جديد
3. استيراد الملف الجديد في `signals.py` الرئيسي

مثال لإضافة إشارة جديدة:
```python
@receiver(post_save, sender=YourModel)
def your_model_notification(sender, instance, created, **kwargs):
    """وصف الإشارة"""
    if created:
        # إنشاء تنبيه عند إنشاء كائن جديد
        create_notification(
            user=instance.user,
            title=_('عنوان التنبيه'),
            message=_(f'نص التنبيه: {instance.some_field}'),
            notification_type='your_type',
            priority='medium',
            content_object=instance,
            url=f'/your/url/{instance.pk}/'
        )
```