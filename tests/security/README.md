# Security Testing Suite - نظام الدولية

## نظرة عامة

هذه مجموعة شاملة من اختبارات الأمان لنظام الدولية، تغطي جميع جوانب الأمان الرئيسية بما في ذلك OWASP Top 10، أمان API، حماية البيانات، واختبارات الاختراق.

## محتويات الاختبارات

### 1. اختبارات OWASP Top 10 (`test_owasp_top10.py`)
- **A01: Broken Access Control** - اختبار التحكم في الوصول
- **A02: Cryptographic Failures** - اختبار فشل التشفير
- **A03: Injection** - اختبار هجمات الحقن (SQL, XSS, Command)
- **A04: Insecure Design** - اختبار التصميم غير الآمن
- **A05: Security Misconfiguration** - اختبار سوء التكوين الأمني
- **A06: Vulnerable Components** - اختبار المكونات المعرضة للخطر
- **A07: Authentication Failures** - اختبار فشل المصادقة
- **A08: Software Integrity Failures** - اختبار فشل سلامة البرمجيات
- **A09: Logging Failures** - اختبار فشل التسجيل والمراقبة
- **A10: Server-Side Request Forgery** - اختبار SSRF

### 2. اختبارات المصادقة والتخويل (`test_authentication.py`)
- قوة كلمات المرور وتشفيرها
- إدارة الجلسات الآمنة
- حماية من هجمات القوة الغاشمة
- نظام الصلاحيات الهرمي
- حماية من تصعيد الامتيازات
- أمان JWT وAPI Keys

### 3. اختبارات أمان API (`test_api_security.py`)
- مصادقة API وتخويلها
- التحقق من صحة المدخلات
- حماية من حقن SQL في API
- حماية من XSS في استجابات API
- تحديد معدل الطلبات (Rate Limiting)
- رؤوس الأمان HTTP
- حماية البيانات الحساسة

### 4. اختبارات حماية البيانات (`test_data_protection.py`)
- تشفير البيانات الحساسة
- أمان قاعدة البيانات
- حماية الخصوصية وGDPR
- أمان رفع الملفات
- منع تسريب البيانات
- أمان النسخ الاحتياطية

### 5. اختبارات الاختراق (`test_penetration.py`)
- محاولات تجاوز المصادقة
- هجمات اختطاف الجلسات
- تجاوز رموز CSRF
- هجمات تصعيد الامتيازات
- هجمات تضمين الملفات (LFI/RFI)
- حقن الأوامر
- هجمات XXE
- هجمات إلغاء التسلسل

## كيفية تشغيل الاختبارات

### تشغيل جميع اختبارات الأمان
```bash
python tests/security/security_test_runner.py
```

### تشغيل فئة محددة من الاختبارات
```bash
# اختبارات OWASP Top 10
python -m pytest tests/security/test_owasp_top10.py -v

# اختبارات المصادقة
python -m pytest tests/security/test_authentication.py -v

# اختبارات API
python -m pytest tests/security/test_api_security.py -v

# اختبارات حماية البيانات
python -m pytest tests/security/test_data_protection.py -v

# اختبارات الاختراق
python -m pytest tests/security/test_penetration.py -v
```

### تشغيل اختبار محدد
```bash
python -m pytest tests/security/test_owasp_top10.py::OWASPTop10SecurityTests::test_a03_injection_attacks -v
```

## التقارير

يتم إنشاء تقارير شاملة بعد تشغيل الاختبارات:

### تقرير JSON
```json
{
  "test_run": {
    "start_time": "2024-01-01T10:00:00",
    "end_time": "2024-01-01T10:05:00",
    "duration": 300
  },
  "summary": {
    "total_tests": 150,
    "passed": 140,
    "failures": 8,
    "errors": 2,
    "success_rate": 93.3
  },
  "categories": {...},
  "recommendations": [...],
  "security_checklist": {...}
}
```

### تقرير HTML
تقرير تفاعلي باللغة العربية يتضمن:
- ملخص النتائج
- تفاصيل كل فئة اختبار
- التوصيات الأمنية
- قائمة التحقق الأمنية

## الثغرات الشائعة المختبرة

### 1. حقن SQL
```python
# أمثلة على الحمولات المختبرة
payloads = [
    "'; DROP TABLE users; --",
    "' OR '1'='1",
    "' UNION SELECT * FROM users --"
]
```

### 2. Cross-Site Scripting (XSS)
```python
# أمثلة على حمولات XSS
payloads = [
    '<script>alert("XSS")</script>',
    '"><script>alert("XSS")</script>',
    '<img src=x onerror=alert("XSS")>'
]
```

### 3. CSRF
```python
# اختبار حماية CSRF
response = client.post('/sensitive-action/', {
    'data': 'malicious'
    # بدون رمز CSRF
})
assert response.status_code == 403
```

### 4. تصعيد الامتيازات
```python
# محاولة تصعيد الامتيازات
response = client.post('/api/users/me/', {
    'is_superuser': True,
    'is_staff': True
})
# يجب أن يفشل
```

## التوصيات الأمنية

### 1. المصادقة والتخويل
- ✅ تطبيق سياسة كلمات مرور قوية
- ✅ تفعيل المصادقة متعددة العوامل (MFA)
- ✅ تطبيق نظام صلاحيات هرمي
- ✅ مراقبة محاولات تسجيل الدخول الفاشلة

### 2. حماية البيانات
- ✅ تشفير البيانات الحساسة
- ✅ استخدام HTTPS لجميع الاتصالات
- ✅ تطبيق سياسات الاحتفاظ بالبيانات
- ✅ إخفاء هوية البيانات في السجلات

### 3. أمان API
- ✅ تطبيق تحديد معدل الطلبات
- ✅ التحقق الشامل من المدخلات
- ✅ استخدام آليات مصادقة آمنة
- ✅ تطبيق رؤوس الأمان HTTP

### 4. مراقبة الأمان
- ✅ تسجيل جميع الأحداث الأمنية
- ✅ مراقبة الأنشطة المشبوهة
- ✅ تطبيق تنبيهات الأمان
- ✅ مراجعة السجلات بانتظام

## قائمة التحقق الأمنية

### المصادقة ✓
- [ ] سياسة كلمات مرور قوية
- [ ] المصادقة متعددة العوامل
- [ ] إدارة جلسات آمنة
- [ ] حماية من القوة الغاشمة
- [ ] أمان إعادة تعيين كلمة المرور

### التخويل ✓
- [ ] نظام صلاحيات قائم على الأدوار
- [ ] مبدأ أقل امتياز
- [ ] صلاحيات على مستوى الكائن
- [ ] تخويل API مناسب

### التحقق من المدخلات ✓
- [ ] التحقق من جميع مدخلات المستخدم
- [ ] حماية من حقن SQL
- [ ] حماية من XSS
- [ ] أمان رفع الملفات
- [ ] حماية CSRF مفعلة

### حماية البيانات ✓
- [ ] تشفير البيانات الحساسة
- [ ] اتصال آمن (HTTPS)
- [ ] أمان قاعدة البيانات
- [ ] أمان النسخ الاحتياطية
- [ ] سياسات الاحتفاظ بالبيانات

### البنية التحتية ✓
- [ ] رؤوس الأمان مطبقة
- [ ] معالجة أخطاء آمنة
- [ ] تسجيل ومراقبة
- [ ] تحديثات أمنية منتظمة
- [ ] مراجعة تكوين الأمان

## استكشاف الأخطاء

### مشاكل شائعة

1. **فشل الاتصال بقاعدة البيانات**
   ```bash
   # تأكد من تشغيل قاعدة البيانات
   python manage.py check --database default
   ```

2. **مشاكل في الاستيراد**
   ```bash
   # تأكد من تثبيت المتطلبات
   pip install -r requirements.txt
   ```

3. **فشل اختبارات CSRF**
   ```python
   # تأكد من تفعيل CSRF middleware
   MIDDLEWARE = [
       'django.middleware.csrf.CsrfViewMiddleware',
       # ...
   ]
   ```

### تشغيل الاختبارات في بيئة آمنة

```bash
# إنشاء بيئة اختبار منفصلة
export DJANGO_SETTINGS_MODULE=ElDawliya_sys.settings.testing
python manage.py migrate --run-syncdb
python tests/security/security_test_runner.py
```

## المساهمة

لإضافة اختبارات أمان جديدة:

1. أنشئ ملف اختبار جديد في `tests/security/`
2. اتبع نمط التسمية: `test_[category].py`
3. استخدم فئات اختبار وصفية
4. أضف توثيق شامل للاختبارات
5. حدث `security_test_runner.py` لتضمين الاختبارات الجديدة

## الموارد الإضافية

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)

---

**ملاحظة**: هذه الاختبارات مصممة للكشف عن الثغرات الأمنية في بيئة آمنة. لا تستخدم هذه الأدوات ضد أنظمة لا تملك إذناً لاختبارها.