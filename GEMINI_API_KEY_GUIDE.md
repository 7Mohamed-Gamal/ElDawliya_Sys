# دليل الحصول على مفتاح API صحيح لخدمة Google Gemini AI

## المشكلة 

تلقيت رسالة الخطأ التالية:

```
Error generating Gemini response: 400 API key not valid. Please pass a valid API key. [reason: "API_KEY_INVALID" domain: "googleapis.com" metadata { key: "service" value: "generativelanguage.googleapis.com" }
```

هذا يعني أن مفتاح API المستخدم حالياً غير صالح أو منتهي الصلاحية أو غير مخول للوصول إلى خدمة Gemini AI.

## الحل: الحصول على مفتاح API جديد

للحصول على مفتاح API جديد وصحيح لـ Google Gemini AI، اتبع الخطوات التالية:

### 1. إنشاء حساب Google AI Studio

1. انتقل إلى [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. قم بتسجيل الدخول بحساب Google الخاص بك
3. اقبل الشروط والأحكام إذا طُلب منك ذلك

### 2. إنشاء مفتاح API جديد

1. في صفحة Google AI Studio، انقر على زر "**Create API Key**" أو "**إنشاء مفتاح API**"
2. قم بتسمية المفتاح (اختياري) مثل "Eldawliya System API Key"
3. انسخ مفتاح API الجديد على الفور (سيبدأ بـ "AIza...")

### 3. تكوين المفتاح في النظام

1. افتح ملف `.env` في المجلد الرئيسي للمشروع
2. استبدل قيمة `GEMINI_API_KEY` بالمفتاح الجديد:

```
GEMINI_API_KEY=AIza...your-new-key-here
```

3. قم بتشغيل سكربت إعداد AI لتحديث قاعدة البيانات بالمفتاح الجديد:

```bash
python setup_ai_configuration.py
```

4. أعد تشغيل الخادم:

```bash
python manage.py runserver
```

### 4. التحقق من صحة المفتاح

يمكنك التحقق من صحة المفتاح باستخدام الأمر التالي من سطر الأوامر:

```bash
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent" \
     -d '{"contents": [{"parts": [{"text": "Hello, world!"}]}]}'
```

استبدل `YOUR_API_KEY` بمفتاح API الخاص بك.

## ملاحظات هامة

1. **حدود الاستخدام**: يأتي مفتاح API لـ Gemini مع حصص استخدام شهرية. تأكد من مراجعة سياسة الاستخدام في [لوحة تحكم Google AI](https://ai.google.dev/).

2. **عدم مشاركة المفاتيح**: لا تقم أبداً بمشاركة مفتاح API الخاص بك أو نشره في أماكن عامة.

3. **فترة الصلاحية**: قد تنتهي صلاحية بعض مفاتيح API بعد فترة زمنية محددة. إذا توقف عملها، كرر عملية إنشاء مفتاح جديد.

4. **تأكد من المنطقة الجغرافية**: بعض خدمات AI قد تكون مقيدة في بعض المناطق الجغرافية. تأكد من أن خدمة Gemini متاحة في منطقتك.

## بدائل أخرى

إذا استمرت المشكلة مع API الخاص بـ Gemini، يمكنك تجربة خدمات AI بديلة:

1. **OpenAI API**: [https://platform.openai.com/](https://platform.openai.com/)
2. **Claude API**: [https://console.anthropic.com/](https://console.anthropic.com/)
3. **Cohere API**: [https://dashboard.cohere.ai/](https://dashboard.cohere.ai/)

كل من هذه الخدمات تتطلب تسجيل منفصل والحصول على مفتاح API خاص بها.

## الخطوات التالية

بعد تكوين مفتاح API الصحيح، حاول استخدام ميزة محادثة الذكاء الاصطناعي مرة أخرى. يجب أن تكون قادراً الآن على إجراء محادثات والاستعلام عن بيانات النظام.
