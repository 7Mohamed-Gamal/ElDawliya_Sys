## نطاق العمل
- تنفيذ طبقة توافق للإجازات تربط Attendance بـ Leaves دون كسر الواجهات.
- تحضير توحيد قواعد الحضور عبر واجهة خدمة موحّدة.
- ضبط أمن وإعدادات البيئة (CSRF/CORS) من `.env`.
- إضافة اختبارات أساسية لصفحات HR والحضور لضمان الاستقرار وCI.

## المهام التنفيذية
- إنشاء `attendance/leave_service.py` يتضمن:
  - `get_leave_types()` لجلب `leaves.models.LeaveType`.
  - `get_employee_leaves(emp, range?)` و`get_balance(emp, leave_type)` بالربط مع `leaves.EmployeeLeave` و`attendance.LeaveBalance`.
- تحديث `attendance/forms.py` لتنظيف الاستيراد من `LeaveType` في الحضور إذا لم يُستخدم فعليًا، والاعتماد على الخدمة عند الحاجة للأنواع.
- إنشاء `attendance/rules_service.py` بواجهات `list_rules()`, `create_rule(data)`, `update_rule(id, data)`, `delete_rule(id)` مع دعم كلٍ من `AttendanceRule` و`AttendanceRules`.
- ضبط `ElDawliya_sys/settings.py` لإضافة:
  - `CSRF_TRUSTED_ORIGINS` و`CORS_ALLOWED_ORIGINS` و`CORS_ALLOW_CREDENTIALS` قراءةً من `.env` بقيم افتراضية آمنة.
- إضافة اختبارات:
  - `hr/tests.py`: إنشاء مستخدم عبر `get_user_model()` مع `Role='admin'`, تسجيل الدخول، اختبار `hr:dashboard` و`hr:dashboard_data` ترجع 200/JSON.
  - `attendance/tests.py`: تسجيل الدخول، اختبار `attendance:dashboard` ترجع 200.

## الموارد المطلوبة
- 1 Backend Django لتنفيذ الخدمات والتعديلات.
- 1 QA لإضافة وتنفيذ الاختبارات.
- إمكانية تشغيل بيئة Staging (اختياري) للتأكد من عدم كسر العروض.

## KPIs المستهدفة (Sprint 1)
- تمرير اختبارات Sprint 1 بنسبة ≥ 95%.
- عدم حدوث أخطاء 500/404 في صفحات HR/الحضور.
- تفعيل إعدادات CSRF/CORS بدون أخطاء وصول (0 حوادث رفض غير مبرر).

## المخاطر والطوارئ
- خطر تعارض النماذج عند استخدام الخدمة الجديدة:
  - المعالجة: حقن الخدمة بشكل غير كسري، إبقاء النماذج كما هي مرحليًا.
- خطر فشل اختبارات بسبب نموذج مستخدم مخصص:
  - المعالجة: استخدام `get_user_model()` مع توفير `Role` والحقول الدنيا، وضبط كلمة مرور مؤكدة.

## المتابعة والتقييم
- مراجعة يومية قصيرة لتقدم المهام.
- تشغيل الاختبارات محليًا ثم عبر CI، وتسجيل النتائج.

## التوثيق
- توثيق واجهات الخدمات الجديدة (leave/rules) مختصرًا داخل دليل تقني داخلي.
- تحديث سجل التغييرات للمرحلة.

## الجدول الزمني
- المدة: 3–4 أيام عمل.
- ترتيب التنفيذ: خدمة الإجازات → خدمة القواعد → إعدادات أمن → اختبارات.
