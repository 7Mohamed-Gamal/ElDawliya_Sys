# نظام التصميم الموحد - ElDawliya Design System

## نظرة عامة

نظام التصميم الموحد لنظام الدولية هو مجموعة شاملة من المكونات والأنماط والإرشادات التي تضمن تجربة مستخدم متسقة وحديثة عبر جميع أجزاء النظام.

## الميزات الرئيسية

### 🎨 نظام الألوان المتقدم
- لوحة ألوان شاملة مع 10 درجات لكل لون
- دعم الثيم الفاتح والداكن
- ألوان دلالية (نجاح، تحذير، خطأ، معلومات)
- متغيرات CSS للتخصيص السهل

### 🔤 نظام الطباعة العربي
- خط Cairo المحسن للنصوص العربية
- أحجام خطوط متدرجة ومتجاوبة
- أوزان خطوط متعددة
- دعم كامل لـ RTL

### 📱 نظام الشبكة المتجاوبة
- نظام شبكة CSS Grid حديث
- نظام Flexbox مرن
- نقاط توقف متجاوبة
- دعم جميع أحجام الشاشات

### 🌙 نظام الثيمات
- تبديل سلس بين الوضع الفاتح والداكن
- حفظ تفضيلات المستخدم
- دعم تفضيلات النظام
- انتقالات سلسة

## هيكل الملفات

```
frontend/static/css/
├── design-system.css      # النظام الأساسي والمتغيرات
├── theme-system.css       # نظام الثيمات
├── components.css         # مكتبة المكونات
├── grid-system.css        # نظام الشبكة المتجاوبة
└── utilities.css          # الفئات المساعدة
```

## استخدام النظام

### 1. تضمين الملفات

```html
<!-- النظام الأساسي -->
<link rel="stylesheet" href="{% static 'css/design-system.css' %}">

<!-- نظام الثيمات -->
<link rel="stylesheet" href="{% static 'css/theme-system.css' %}">

<!-- المكونات -->
<link rel="stylesheet" href="{% static 'css/components.css' %}">

<!-- نظام الشبكة -->
<link rel="stylesheet" href="{% static 'css/grid-system.css' %}">

<!-- JavaScript للثيمات -->
<script src="{% static 'js/theme-system.js' %}"></script>
```

### 2. المتغيرات الأساسية

```css
:root {
    /* الألوان الأساسية */
    --primary-600: #2563eb;
    --secondary-600: #64748b;
    --success-600: #16a34a;
    --warning-600: #d97706;
    --error-600: #dc2626;
    --info-600: #0891b2;
    
    /* الخطوط */
    --font-family-arabic: 'Cairo', sans-serif;
    --font-size-base: 1rem;
    --font-weight-normal: 400;
    
    /* المسافات */
    --spacing-4: 1rem;
    --spacing-6: 1.5rem;
    
    /* الظلال */
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    
    /* الانتقالات */
    --transition-normal: 300ms ease-in-out;
}
```

## المكونات الأساسية

### الأزرار (Buttons)

```html
<!-- أزرار أساسية -->
<button class="btn btn-primary">زر أساسي</button>
<button class="btn btn-secondary">زر ثانوي</button>
<button class="btn btn-success">زر نجاح</button>
<button class="btn btn-warning">زر تحذير</button>
<button class="btn btn-error">زر خطأ</button>

<!-- أحجام مختلفة -->
<button class="btn btn-primary btn-sm">صغير</button>
<button class="btn btn-primary">عادي</button>
<button class="btn btn-primary btn-lg">كبير</button>

<!-- أزرار محددة -->
<button class="btn btn-outline-primary">محدد أساسي</button>
<button class="btn btn-ghost">شفاف</button>

<!-- زر أيقونة -->
<button class="btn-icon btn-primary">
    <i class="fas fa-plus"></i>
</button>
```

### البطاقات (Cards)

```html
<!-- بطاقة أساسية -->
<div class="card">
    <div class="card-header">
        <h3 class="card-title">عنوان البطاقة</h3>
    </div>
    <div class="card-body">
        <p class="card-text">محتوى البطاقة</p>
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">إجراء</button>
    </div>
</div>

<!-- بطاقة محسنة -->
<div class="card-enhanced card-primary">
    <div class="card-header-enhanced">
        <h3 class="card-title-enhanced">
            <i class="card-title-icon fas fa-chart-bar"></i>
            الإحصائيات
        </h3>
        <div class="card-actions">
            <button class="btn btn-sm btn-ghost">
                <i class="fas fa-ellipsis-v"></i>
            </button>
        </div>
    </div>
    <div class="card-body-enhanced">
        <p>محتوى البطاقة المحسنة</p>
    </div>
</div>

<!-- بطاقة إحصائيات -->
<div class="stats-card">
    <div class="stats-header">
        <h4 class="stats-title">إجمالي الموظفين</h4>
        <div class="stats-icon">
            <i class="fas fa-users"></i>
        </div>
    </div>
    <p class="stats-value">1,234</p>
    <div class="stats-change positive">
        <i class="fas fa-arrow-up"></i>
        <span>+12% من الشهر الماضي</span>
    </div>
</div>
```

### النماذج (Forms)

```html
<!-- مجموعة نموذج أساسية -->
<div class="form-group">
    <label class="form-label required">الاسم الكامل</label>
    <input type="text" class="form-control" placeholder="أدخل الاسم الكامل">
    <div class="form-text">يرجى إدخال الاسم الكامل</div>
</div>

<!-- مجموعة نموذج محسنة -->
<div class="form-group-enhanced">
    <label class="form-label-enhanced required">
        <i class="form-label-icon fas fa-user"></i>
        الاسم الكامل
    </label>
    <input type="text" class="form-control-enhanced" placeholder="أدخل الاسم الكامل">
    <div class="invalid-feedback">هذا الحقل مطلوب</div>
</div>

<!-- مجموعة إدخال -->
<div class="input-group-enhanced">
    <input type="text" class="form-control-enhanced" placeholder="البحث">
    <span class="input-group-text">
        <i class="fas fa-search"></i>
    </span>
</div>

<!-- تسمية عائمة -->
<div class="form-floating-enhanced">
    <input type="email" class="form-control-enhanced" id="email" placeholder="البريد الإلكتروني">
    <label class="form-label-enhanced" for="email">البريد الإلكتروني</label>
</div>
```

### الجداول (Tables)

```html
<!-- جدول محسن -->
<div class="table-responsive">
    <table class="table-enhanced">
        <thead>
            <tr>
                <th class="sortable">الاسم</th>
                <th class="sortable">القسم</th>
                <th class="sortable">التاريخ</th>
                <th>الإجراءات</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>أحمد محمد</td>
                <td>الموارد البشرية</td>
                <td>2024-01-15</td>
                <td>
                    <div class="table-actions">
                        <button class="table-action-btn btn-view" title="عرض">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="table-action-btn btn-edit" title="تعديل">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="table-action-btn btn-delete" title="حذف">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

### التنبيهات (Alerts)

```html
<!-- تنبيه أساسي -->
<div class="alert alert-primary">
    هذا تنبيه أساسي
</div>

<!-- تنبيه محسن -->
<div class="alert-enhanced alert-success">
    <i class="alert-icon fas fa-check-circle"></i>
    <div class="alert-content">
        <h4 class="alert-title">نجح!</h4>
        <p class="alert-message">تم حفظ البيانات بنجاح</p>
    </div>
</div>
```

### الشارات (Badges)

```html
<span class="badge badge-primary">أساسي</span>
<span class="badge badge-success">نجح</span>
<span class="badge badge-warning">تحذير</span>
<span class="badge badge-error">خطأ</span>
```

## نظام الشبكة

### CSS Grid

```html
<!-- شبكة أساسية -->
<div class="grid-system grid-cols-3 gap-4">
    <div>عنصر 1</div>
    <div>عنصر 2</div>
    <div>عنصر 3</div>
</div>

<!-- شبكة متجاوبة -->
<div class="grid-system grid-cols-1 grid-cols-md-2 grid-cols-lg-3 gap-4">
    <div class="col-span-full col-span-lg-1">عنصر 1</div>
    <div class="col-span-1 col-span-lg-2">عنصر 2</div>
</div>

<!-- شبكة تلقائية -->
<div class="grid-system grid-auto-fit gap-4">
    <div>عنصر 1</div>
    <div>عنصر 2</div>
    <div>عنصر 3</div>
</div>
```

### Flexbox Grid

```html
<div class="flex-grid">
    <div class="flex-col-12 flex-col-md-6 flex-col-lg-4">
        <div class="card">محتوى</div>
    </div>
    <div class="flex-col-12 flex-col-md-6 flex-col-lg-8">
        <div class="card">محتوى</div>
    </div>
</div>
```

## نظام الثيمات

### تفعيل نظام الثيمات

```javascript
// تهيئة نظام الثيمات
const themeSystem = new ThemeSystem();

// تبديل الثيم
themeSystem.toggleTheme();

// تعيين ثيم محدد
themeSystem.setTheme('dark');

// الحصول على الثيم الحالي
const currentTheme = themeSystem.getCurrentTheme();

// الاستماع لتغييرات الثيم
document.addEventListener('themechange', (e) => {
    console.log('تم تغيير الثيم إلى:', e.detail.theme);
});
```

### استخدام الألوان المتجاوبة للثيم

```css
.my-component {
    background-color: var(--gray-100);
    color: var(--gray-900);
    border: 1px solid var(--gray-300);
}

/* سيتم تطبيق الألوان المناسبة تلقائياً حسب الثيم */
```

## الفئات المساعدة

### المسافات

```html
<!-- الهوامش -->
<div class="m-4">هامش من جميع الجهات</div>
<div class="mt-4 mb-2">هامش علوي وسفلي</div>
<div class="mx-auto">توسيط أفقي</div>

<!-- الحشو -->
<div class="p-6">حشو من جميع الجهات</div>
<div class="px-4 py-2">حشو أفقي وعمودي</div>
```

### الألوان

```html
<div class="bg-primary text-white">خلفية أساسية</div>
<div class="text-success">نص أخضر</div>
<div class="bg-gray-100">خلفية رمادية فاتحة</div>
```

### الظلال

```html
<div class="shadow-sm">ظل خفيف</div>
<div class="shadow-md">ظل متوسط</div>
<div class="shadow-lg">ظل كبير</div>
```

### الحدود المدورة

```html
<div class="rounded-md">حدود مدورة متوسطة</div>
<div class="rounded-lg">حدود مدورة كبيرة</div>
<div class="rounded-full">حدود دائرية</div>
```

## التخصيص

### تخصيص الألوان

```css
:root {
    /* تخصيص الألوان الأساسية */
    --primary-600: #your-color;
    --secondary-600: #your-color;
    
    /* تخصيص ألوان الثيم الداكن */
}

[data-theme="dark"] {
    --primary-600: #your-dark-color;
}
```

### تخصيص الخطوط

```css
:root {
    --font-family-arabic: 'YourFont', 'Cairo', sans-serif;
    --font-size-base: 1.125rem; /* 18px */
}
```

### تخصيص المسافات

```css
:root {
    --spacing-4: 1.25rem; /* 20px بدلاً من 16px */
}
```

## أفضل الممارسات

### 1. استخدام المتغيرات
```css
/* جيد */
.my-component {
    color: var(--primary-600);
    padding: var(--spacing-4);
}

/* تجنب */
.my-component {
    color: #2563eb;
    padding: 16px;
}
```

### 2. استخدام الفئات المساعدة
```html
<!-- جيد -->
<div class="bg-white p-6 rounded-lg shadow-md">

<!-- تجنب -->
<div style="background: white; padding: 24px; border-radius: 8px; box-shadow: ...">
```

### 3. التجاوب
```html
<!-- جيد -->
<div class="grid-cols-1 grid-cols-md-2 grid-cols-lg-3">

<!-- تجنب -->
<div class="grid-cols-3">
```

### 4. إمكانية الوصول
```html
<!-- جيد -->
<button class="btn btn-primary" aria-label="حفظ البيانات">
    <i class="fas fa-save" aria-hidden="true"></i>
    حفظ
</button>
```

## الدعم والمساعدة

للحصول على المساعدة أو الإبلاغ عن مشاكل:

1. راجع هذا الدليل أولاً
2. تحقق من أمثلة الكود
3. تأكد من تضمين جميع الملفات المطلوبة
4. استخدم أدوات المطور في المتصفح لفحص العناصر

## التحديثات المستقبلية

- إضافة المزيد من المكونات
- تحسين الأداء
- دعم المزيد من الثيمات
- إضافة الرسوم المتحركة المتقدمة
- تحسين إمكانية الوصول