# اختبارات الأداء والتحميل
# Performance and Load Testing

هذا المجلد يحتوي على اختبارات شاملة لأداء نظام الدولية، بما في ذلك اختبارات أوقات الاستجابة، التحميل المتزامن، استهلاك الذاكرة، والتحسينات.

## محتويات المجلد

### ملفات الاختبار

1. **`test_page_response_times.py`** - اختبارات أوقات الاستجابة للصفحات
   - قياس أوقات الاستجابة للصفحات الرئيسية
   - اختبار أداء API endpoints
   - تحليل أداء استعلامات قاعدة البيانات
   - اختبار أداء التخزين المؤقت

2. **`test_load_testing.py`** - اختبارات التحميل المتزامن
   - محاكاة مستخدمين متعددين متزامنين
   - اختبار التحميل الخفيف (5 مستخدمين)
   - اختبار التحميل المتوسط (10 مستخدمين)
   - اختبار التحميل الثقيل (20 مستخدم)
   - اختبار العمليات المتزامنة على قاعدة البيانات

3. **`test_memory_usage.py`** - اختبارات استهلاك الذاكرة
   - مراقبة استهلاك الذاكرة للصفحات
   - كشف تسريب الذاكرة في الطلبات المتكررة
   - اختبار استهلاك الذاكرة مع الطلبات المتزامنة
   - مراقبة استهلاك المعالج وعمليات القرص

4. **`test_optimization.py`** - اختبارات التحسين
   - تحليل وتحسين استعلامات قاعدة البيانات
   - كشف مشكلة N+1 في الاستعلامات
   - اختبار فعالية select_related/prefetch_related
   - تحليل أداء التخزين المؤقت
   - قياس تأثير التحسينات على الأداء

### أدوات التشغيل

5. **`performance_test_runner.py`** - مشغل اختبارات الأداء الشامل
   - تشغيل جميع اختبارات الأداء تلقائياً
   - إنتاج تقارير شاملة
   - تحليل النتائج وإنتاج التوصيات
   - حفظ النتائج في ملفات JSON

## كيفية تشغيل الاختبارات

### تشغيل جميع اختبارات الأداء

```bash
# تشغيل جميع الاختبارات مع تقرير شامل
python tests/performance/performance_test_runner.py

# أو باستخدام Django test runner
python manage.py test tests.performance
```

### تشغيل اختبارات محددة

```bash
# اختبارات أوقات الاستجابة فقط
python manage.py test tests.performance.test_page_response_times

# اختبارات التحميل فقط
python manage.py test tests.performance.test_load_testing

# اختبارات الذاكرة فقط
python manage.py test tests.performance.test_memory_usage

# اختبارات التحسين فقط
python manage.py test tests.performance.test_optimization
```

### تشغيل اختبارات محددة

```bash
# اختبار محدد
python manage.py test tests.performance.test_page_response_times.PageResponseTimeTests.test_homepage_response_time

# مع تفاصيل أكثر
python manage.py test tests.performance.test_load_testing.ConcurrentUserTests.test_light_load_5_users -v 2
```

## متطلبات الاختبارات

### المتطلبات الأساسية

```bash
pip install psutil  # لمراقبة الموارد
```

### إعدادات Django المطلوبة

```python
# في settings.py للاختبارات
DEBUG = True  # لتتبع الاستعلامات
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## معايير الأداء المستهدفة

### أوقات الاستجابة
- الصفحة الرئيسية: < 500ms
- صفحات التطبيقات: < 1000ms
- API endpoints: < 300ms

### التحميل المتزامن
- 5 مستخدمين: معدل نجاح ≥ 95%
- 10 مستخدمين: معدل نجاح ≥ 90%
- 20 مستخدم: معدل نجاح ≥ 80%

### استهلاك الموارد
- استهلاك الذاكرة: < 100MB زيادة لكل 20 طلب
- استعلامات قاعدة البيانات: < 50 استعلام لكل صفحة
- استهلاك المعالج: < 80% تحت الحمولة

### قاعدة البيانات
- وقت الاستعلام المتوسط: < 10ms
- عدد الاستعلامات البطيئة: < 5 لكل صفحة
- عدم وجود مشكلة N+1 حادة

## تفسير النتائج

### رموز الحالة
- ✅ **نجح**: الاختبار مر بنجاح ضمن المعايير المحددة
- ⚠️  **تحذير**: الاختبار مر لكن قريب من الحد الأقصى
- ❌ **فشل**: الاختبار فشل أو تجاوز المعايير المحددة

### مؤشرات الأداء الرئيسية (KPIs)

1. **وقت الاستجابة المتوسط**: متوسط الوقت لمعالجة الطلبات
2. **النسبة المئوية 95**: 95% من الطلبات تكتمل خلال هذا الوقت
3. **معدل النجاح**: نسبة الطلبات الناجحة من إجمالي الطلبات
4. **الطلبات في الثانية**: عدد الطلبات التي يمكن معالجتها في الثانية
5. **استهلاك الذاكرة**: مقدار الذاكرة المستخدمة
6. **عدد الاستعلامات**: عدد استعلامات قاعدة البيانات لكل طلب

## التحسينات المقترحة

### تحسينات قاعدة البيانات
```python
# استخدام select_related للعلاقات الفردية
employees = Employee.objects.select_related('department', 'job_position')

# استخدام prefetch_related للعلاقات المتعددة
employees = Employee.objects.prefetch_related('groups', 'user_permissions')

# إضافة فهارس للحقول المستخدمة في البحث
class Employee(models.Model):
    emp_code = models.CharField(max_length=20, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['department', 'is_active']),
            models.Index(fields=['hire_date']),
        ]
```

### تحسينات التخزين المؤقت
```python
from django.core.cache import cache

# تخزين مؤقت للبيانات الثابتة
def get_departments():
    departments = cache.get('departments_list')
    if departments is None:
        departments = list(Department.objects.filter(is_active=True))
        cache.set('departments_list', departments, 3600)  # ساعة واحدة
    return departments

# تخزين مؤقت للصفحات
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 دقيقة
def employee_list(request):
    # ...
```

### تحسينات الاستعلامات
```python
# تجنب مشكلة N+1
# بدلاً من:
for employee in employees:
    print(employee.department.name)  # استعلام لكل موظف

# استخدم:
employees = Employee.objects.select_related('department')
for employee in employees:
    print(employee.department.name)  # بدون استعلامات إضافية
```

## استكشاف الأخطاء

### مشاكل شائعة

1. **اختبارات بطيئة**: تأكد من وجود بيانات اختبار كافية
2. **فشل الاتصال بقاعدة البيانات**: تحقق من إعدادات قاعدة البيانات
3. **نفاد الذاكرة**: قلل من حجم البيانات المختبرة
4. **فشل التخزين المؤقت**: تأكد من تشغيل Redis

### تشخيص المشاكل

```bash
# فحص استهلاك الموارد
python -c "
import psutil
print(f'الذاكرة المتاحة: {psutil.virtual_memory().available / 1024 / 1024:.2f} MB')
print(f'استهلاك المعالج: {psutil.cpu_percent()}%')
"

# فحص اتصال قاعدة البيانات
python manage.py dbshell

# فحص Redis
redis-cli ping
```

## التقارير والمراقبة

### ملفات النتائج
- النتائج تحفظ في `tests/performance/results/`
- تنسيق JSON مع timestamp
- تحتوي على تفاصيل كل اختبار والتوصيات

### مراقبة مستمرة
```bash
# إضافة إلى CI/CD pipeline
python tests/performance/performance_test_runner.py
if [ $? -ne 0 ]; then
    echo "فشل اختبارات الأداء"
    exit 1
fi
```

## المساهمة

عند إضافة اختبارات أداء جديدة:

1. اتبع نمط التسمية الموجود
2. أضف تعليقات باللغة العربية
3. حدد معايير أداء واضحة
4. اختبر على بيانات واقعية
5. وثق النتائج المتوقعة

## الدعم

للمساعدة في اختبارات الأداء:
- راجع السجلات في `logs/`
- تحقق من إعدادات قاعدة البيانات
- تأكد من توفر الموارد الكافية
- استخدم أدوات المراقبة المناسبة