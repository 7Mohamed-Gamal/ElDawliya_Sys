# نظام الأذونات في المشروع (Permission System Documentation)

## ملفات قوالب الأذونات (Permission Template Tags Files)

هذا المستند يوثق الملفات المختلفة المتعلقة بنظام الأذونات في المشروع وكيفية استخدامها.

### نظرة عامة على هيكل الملفات

#### permissions.py

**الملف الرئيسي الموحد** الذي يجمع جميع وظائف الأذونات في مكان واحد. يجب استخدام هذا الملف للتطوير المستقبلي.

#### الملفات للتوافق مع الإصدارات السابقة

هذه الملفات موجودة للحفاظ على التوافق مع القوالب الحالية التي تستخدمها:

- **permission_filters.py**: يستورد وظائف التصفية من permissions.py
- **permission_tags.py**: يستورد وظائف وسوم الأذونات من permissions.py
- **permission_common.py**: مستخدم سابقًا للوظائف المشتركة، وتم دمجه الآن في permissions.py
- **rbac_tags.py**: يستورد وظائف نظام RBAC من permissions.py

> ملاحظة: يُفضل استخدام `{% load permissions %}` في القوالب الجديدة، ولكن القوالب الحالية التي تستخدم `{% load permission_filters %}` أو `{% load permission_tags %}` أو `{% load rbac_tags %}` ستستمر في العمل.

## نظامي الأذونات في المشروع

المشروع يحتوي على نظامين للأذونات:

1. **نظام الأذونات الأصلي**: يعتمد على نموذج هرمي (قسم > وحدة > صلاحية) ويتم التحكم به من خلال وسوم وفلاتر مثل `has_module_permission`.
2. **نظام RBAC الجديد**: يعتمد على نموذج الأدوار والصلاحيات المباشرة ويتم التحكم به من خلال وسوم وفلاتر مثل `has_rbac_permission`.

### وظائف نظام الأذونات الأصلي

#### وظائف مشتركة
- `get_item`: دالة لاستخراج عنصر من قاموس باستخدام مفتاح معين

#### مرشحات الأذونات (Filters)
- `filter_by_code`: فلتر للبحث عن عملية بكود معين ضمن قائمة من العمليات
- `filter_by_type`: فلتر للبحث عن عملية بنوع إذن معين ضمن قائمة من العمليات
- `get_modules_for_department`: فلتر لاسترجاع الوحدات الخاصة بقسم معين
- `get_form_field`: فلتر للحصول على حقل من نموذج بواسطة اسمه
- `filter_by`: فلتر لتصفية مجموعة استعلام حسب حقل وقيمته
- `hide_if_not_admin`: فلتر لإخفاء المحتوى إذا لم يكن المستخدم مشرفا
- `has_template_permission`: فلتر للتحقق إذا كان المستخدم لديه إذن للوصول إلى قالب معين

#### وسوم الأذونات (Tags)
- `render_department_checkbox`: وسم بسيط لعرض خانة اختيار لقسم معين
- `render_module_checkbox`: وسم بسيط لعرض خانة اختيار لوحدة معينة
- `render_permission_checkbox`: وسم بسيط لعرض خانة اختيار لإذن معين
- `is_admin`: وسم للتحقق إذا كان المستخدم له دور المشرف
- `has_permission`: وسم للتحقق إذا كان المستخدم لديه إذن لنوع إجراء معين
- `render_if_admin`: وسم لعرض محتوى فقط إذا كان المستخدم مشرفا
- `has_module_permission`: وسم للتحقق إذا كان المستخدم لديه إذن لوحدة معينة
- `action_buttons`: وسم لعرض أزرار الإجراءات بناءً على أذونات المستخدم

### وظائف نظام RBAC

#### مرشحات الأذونات (Filters)
- `has_rbac_permission`: فلتر للتحقق إذا كان المستخدم لديه صلاحية RBAC محددة

#### وسوم الأذونات (Tags)
- `check_rbac_permission`: وسم للتحقق إذا كان المستخدم لديه صلاحية RBAC محددة

## ملاحظات التحديث (Update Notes)

- تم دمج جميع الوظائف في ملف موحد `permissions.py` لتسهيل الصيانة
- تم الاحتفاظ بالملفات القديمة للتوافق مع القوالب الحالية
- تم دمج وظائف `rbac_tags.py` في ملف `permissions.py`
- ملف `permission_tags_new.py` غير موجود في المشروع

## كيفية استخدام وسوم الأذونات في القوالب

### تحميل وسوم الأذونات

لاستخدام نظام الأذونات في قوالب HTML، يفضل تحميل الملف الموحد:

```html
{% load permissions %}
```

أو يمكن استخدام الطريقة القديمة للقوالب الحالية:

```html
{% load permission_filters %}
{% load permission_tags %}
```

### أمثلة على استخدام النظام الأصلي

1. التحقق من أذونات الوصول إلى وحدة:

```html
{% has_module_permission "الموارد البشرية" "إدارة الموظفين" "add" as can_add_employee %}
{% if can_add_employee %}
    <a href="{% url 'Hr:employee_create' %}" class="btn btn-primary">إضافة موظف جديد</a>
{% endif %}
```

2. الحصول على عنصر من قاموس:

```html
{{ permissions_dict|get_item:module_id }}
```

3. فلترة العمليات حسب الكود ونوع الإذن:

```html
{% with add_op=operation_permissions|get_item:module.id|filter_by_code:operation.code|filter_by_type:'add' %}
    {% if add_op %}
        <!-- عرض زر الإضافة -->
    {% endif %}
{% endwith %}
```

4. عرض خانات اختيار الأذونات:

```html
{% render_department_checkbox form department.id %}
{% render_module_checkbox form module.id %}
{% render_permission_checkbox form module.id 'view' %}
```

### أمثلة على استخدام نظام RBAC

1. استخدام فلتر `has_rbac_permission`:

```html
{% if user|has_rbac_permission:"edit_articles" %}
    <a href="{% url 'edit_article' article.id %}" class="btn btn-primary">تعديل المقال</a>
{% endif %}
```

2. استخدام وسم `check_rbac_permission`:

```html
{% check_rbac_permission user "publish_content" as can_publish %}
{% if can_publish %}
    <button class="btn btn-success">نشر المحتوى</button>
{% endif %}
