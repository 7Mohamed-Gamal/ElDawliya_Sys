# 🚀 Quick Start Guide - Tailwind CSS UI

## 1️⃣ Setup (One Time)

```bash
# Install Node dependencies
npm install
```

---

## 2️⃣ Development Workflow

### Start CSS Watcher
```bash
npm run watch:css
```
This watches for changes in `static/css/tailwind.css` and auto-compiles.

### Start Django Server
```bash
python manage.py runserver
```

### View Demo Page
```
http://localhost:8000/ui-demo/
```

---

## 3️⃣ Using Components

### In Any Template
```django
{% extends 'base.html' %}

{% block content %}
<!-- Your content here -->
{% endblock %}
```

### Buttons
```django
{% include 'components/buttons/btn_primary.html' with text="حفظ" icon="fas fa-save" %}
{% include 'components/buttons/btn_secondary.html' with text="إلغاء" %}
{% include 'components/buttons/btn_outline.html' with text="تفاصيل" color="primary" %}
```

### Forms
```django
{% include 'components/forms/input.html' with name="email" label="البريد" type="email" %}
{% include 'components/forms/select.html' with name="dept" label="القسم" options=departments %}
```

### Cards
```django
{% include 'components/cards/card_basic.html' with title="عنوان" body="محتوى" %}
{% include 'components/cards/card_stat.html' with title="الموظفين" value="150" icon="fas fa-users" %}
```

### Tables
```django
{% include 'components/tables/table_responsive.html' with 
  title="قائمة"
  headers=["الاسم", "القسم"]
  rows=data %}
```

### Alerts
```django
{% include 'components/feedback/alert.html' with type="success" message="تم الحفظ" %}
```

---

## 4️⃣ Dark Mode

Toggle automatically works! Just click the moon/sun icon in navbar.

To manually toggle:
```javascript
toggleTheme()
```

---

## 5️⃣ Common Tailwind Classes

### Colors
```html
<div class="bg-primary-500 text-white">
<div class="bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-300">
```

### Spacing
```html
<div class="p-4 m-2 gap-3 space-y-4">
```

### Typography
```html
<p class="text-sm font-semibold text-neutral-900 dark:text-neutral-100">
```

### Responsive
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

### Flexbox
```html
<div class="flex items-center justify-between gap-3">
```

---

## 6️⃣ Production Build

```bash
# Compile and minify CSS
npm run build:css

# Collect static files
python manage.py collectstatic --noinput
```

---

## 7️⃣ File Locations

| File | Purpose |
|------|---------|
| `tailwind.config.js` | Design system config |
| `static/css/tailwind.css` | Source CSS |
| `static/css/output.css` | Compiled CSS (auto-generated) |
| `templates/base.html` | Main template |
| `templates/components/` | All components |
| `docs/design_system.md` | Full documentation |

---

## 8️️ Common Patterns

### Page with Sidebar
```django
{% extends 'base.html' %}
{% load static %}

{% block title %}Page Title{% endblock %}

{% block content %}
<h1 class="text-3xl font-bold mb-6">Page Title</h1>
<!-- Content -->
{% endblock %}
```

### Dashboard Stats
```django
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
  {% include 'components/cards/card_stat.html' with 
    title="Title" value="100" icon="fas fa-icon" color="primary" %}
</div>
```

### Form Page
```django
<div class="max-w-2xl mx-auto">
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">Form Title</h2>
    </div>
    <div class="card-body">
      <form method="POST" class="space-y-6">
        {% csrf_token %}
        <!-- Form fields -->
      </form>
    </div>
  </div>
</div>
```

---

## 9️⃣ Need Help?

- **Design System**: `/docs/design_system.md`
- **UI Audit**: `/docs/ui_audit_report.md`
- **Tailwind Docs**: https://tailwindcss.com/docs
- **Demo Page**: `http://localhost:8000/ui-demo/`

---

**Last Updated**: April 29, 2026
