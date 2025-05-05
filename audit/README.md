# نظام تسجيل الأحداث (Audit Logging System)

تم تصميم هذا التطبيق لتسجيل و تتبع أنشطة المستخدمين والأحداث المهمة في النظام، مما يساعد في الرقابة والامتثال وتحديد المشكلات الأمنية.

## المميزات الرئيسية

- تسجيل تلقائي للأحداث (إنشاء، تحديث، حذف، عرض)
- تسجيل عمليات تسجيل الدخول والخروج
- تخزين معلومات تفصيلية عن كل حدث (المستخدم، الوقت، IP، المتصفح، البيانات المتغيرة)
- واجهة رسومية لاستعراض وتصفية وتصدير السجلات
- تكامل مع نظام المستخدمين وإدارة الصلاحيات
- مرونة في التخصيص والتوسعة

## المكونات الرئيسية

1. **نموذج AuditLog**: لتخزين بيانات السجلات
2. **Middleware**: للتقاط الأحداث تلقائيًا
3. **Signals**: لتسجيل عمليات الدخول والخروج
4. **وظائف مساعدة**: للتسجيل اليدوي
5. **واجهة إدارة**: لعرض وتصفية السجلات

## كيفية الاستخدام

### التسجيل التلقائي

تم تكوين middleware لتسجيل معظم العمليات تلقائيًا (GET، POST، PUT، DELETE)، لا يحتاج المطورون إلى أي تعديل للاستفادة من هذه الميزة.

### التسجيل اليدوي

يمكن استخدام الوظائف المساعدة لتسجيل الأحداث المحددة يدويًا، على سبيل المثال:

```python
from audit.utils import log_action, log_create, log_update, log_delete

# تسجيل عملية إنشاء
log_create(request.user, object_instance, action_details="إنشاء عنصر جديد")

# تسجيل عملية تحديث
log_update(request.user, object_instance, 
          original_data=old_data, new_data=new_data, 
          action_details="تحديث بيانات العنصر")

# تسجيل عملية حذف
log_delete(request.user, object_instance, action_details="حذف العنصر")

# تسجيل حدث مخصص
log_action(request.user, AuditLog.OTHER, 
          action_details="عملية مخصصة", 
          app_name="my_app",
          change_data={"key": "value"})
```

### الوصول إلى السجلات

يمكن الوصول إلى واجهة تسجيل الأحداث من خلال:
- واجهة المستخدم: `/audit/`
- لوحة الإدارة: قسم "سجلات التدقيق"

يمكن تصفية السجلات حسب:
- المستخدم
- نوع الإجراء
- التطبيق
- التاريخ
- البحث النصي

## الصلاحيات

يتطلب الوصول إلى سجلات التدقيق أحد الصلاحيات التالية:
- مدير (is_superuser)
- طاقم إداري (is_staff)
- صلاحية خاصة: 'audit.view_auditlog'

## التخصيص

يمكن تخصيص نظام التسجيل من خلال:

1. **تعديل EXCLUDED_URLS في middleware.py**: لاستبعاد مسارات URL من التسجيل
2. **تخصيص قوالب العرض**: في مجلد templates/audit
3. **إضافة سجلات مخصصة**: باستخدام وظائف log_*

## الأداء

نظرًا لأن نظام التسجيل يقوم بعمليات كتابة مع كل طلب، فهناك بعض النصائح للأداء:
- استخدم EXCLUDED_URLS لاستبعاد المسارات عالية الحجم
- ضع في اعتبارك جدولة مهمة دورية لأرشفة السجلات القديمة
- راقب حجم الجدول مع نمو البيانات

## مثال على تسجيل إجراء مخصص

```python
from django.views import View
from django.http import HttpResponse
from audit.utils import log_action
from audit.models import AuditLog

class CustomActionView(View):
    def post(self, request, *args, **kwargs):
        # قم بالعملية المطلوبة
        result = some_operation()
        
        # سجل الإجراء
        log_action(
            user=request.user,
            action=AuditLog.OTHER,
            action_details="عملية مخصصة: " + str(result),
            app_name="my_app",
            change_data={"result": result},
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return HttpResponse("تمت العملية بنجاح")
