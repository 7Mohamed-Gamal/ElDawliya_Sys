# 🚀 ElDawliya ERP - Migration Guide

**Created:** April 29, 2026  
**Version:** 1.0  
**Purpose:** Step-by-step guide for migrating apps from Bootstrap to Tailwind CSS

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Migration Strategy](#migration-strategy)
4. [Step-by-Step Migration](#step-by-step-migration)
5. [Component Reference](#component-reference)
6. [Common Patterns](#common-patterns)
7. [Testing Checklist](#testing-checklist)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides a systematic approach to migrate Django app templates from Bootstrap 5 to the unified Tailwind CSS design system. The migration is designed to be **incremental and safe**, allowing you to migrate one app at a time without breaking the system.

### Migration Goals

- ✅ Replace Bootstrap with Tailwind CSS
- ✅ Use shared component library
- ✅ Maintain existing functionality
- ✅ Improve responsiveness
- ✅ Add dark mode support
- ✅ Ensure RTL compliance

---

## Prerequisites

Before starting migration, ensure:

1. ✅ Global `base.html` is enhanced (Task 1 complete)
2. ✅ Component library is created (Task 2 complete)
3. ✅ You have a Git branch for the app being migrated
4. ✅ Database backup is created
5. ✅ Development server is running

---

## Migration Strategy

### The Migration Wrapper Pattern

Instead of directly changing all templates to extend `base.html`, we use a **migration wrapper** pattern:

```
Old Pattern:
template.html → extends app/base_app.html ❌

Migration Pattern:
template.html → extends app/base_app_migration.html → extends base.html ✅

Final Pattern (after 2 weeks):
template.html → extends base.html ✅
```

This allows:
- Safe rollback if issues occur
- Gradual testing
- No disruption to other apps

---

## Step-by-Step Migration

### Step 1: Create Migration Wrapper

Create a new file: `app_name/templates/app_name/base_migration.html`

```django
{% comment %}
  Migration Wrapper for [App Name]
  Created: YYYY-MM-DD
  Status: In Migration
{% endcomment %}
{% extends 'base.html' %}

{% block title %}
  {% block app_title %}App Name{% endblock %}
{% endblock %}

{% block sidebar %}
  {# Include app-specific sidebar if needed #}
  {% include 'components/navigation/sidebar.html' with menu_items=app_menu_items %}
{% endblock %}

{% block extra_css %}
  {# Add app-specific CSS if absolutely necessary #}
  {% block app_css %}{% endblock %}
{% endblock %}

{% block content %}{% endblock %}

{% block extra_js %}
  {# Add app-specific JavaScript #}
  {% block app_js %}{% endblock %}
{% endblock %}
```

### Step 2: Update Template Extensions

Find all templates in the app that extend the old base:

```bash
# Search for old base template usage
grep -r "extends 'app_name/base" app_name/templates/
```

Update each template:

```diff
- {% extends 'app_name/base_old.html' %}
+ {% extends 'app_name/base_migration.html' %}
```

### Step 3: Replace Bootstrap Components

#### 3.1 Buttons

**Before (Bootstrap):**
```html
<button class="btn btn-primary">حفظ</button>
<button class="btn btn-secondary">إلغاء</button>
<button class="btn btn-danger">حذف</button>
```

**After (Tailwind):**
```django
{% include 'components/buttons/btn_primary.html' with text="حفظ" icon="fas fa-save" %}
{% include 'components/buttons/btn_secondary.html' with text="إلغاء" %}
{% include 'components/buttons/btn_danger.html' with text="حذف" icon="fas fa-trash" %}
```

#### 3.2 Cards

**Before (Bootstrap):**
```html
<div class="card">
  <div class="card-header">
    <h5 class="card-title">عنوان البطاقة</h5>
  </div>
  <div class="card-body">
    <p>المحتوى</p>
  </div>
</div>
```

**After (Tailwind):**
```django
{% include 'components/cards/card_basic.html' with title="عنوان البطاقة" %}
  <p>المحتوى</p>
{% endinclude %}
```

Or manually:
```html
<div class="bg-white dark:bg-neutral-800 rounded-lg shadow-md">
  <div class="p-6 border-b border-neutral-200 dark:border-neutral-700">
    <h5 class="text-lg font-semibold">عنوان البطاقة</h5>
  </div>
  <div class="p-6">
    <p>المحتوى</p>
  </div>
</div>
```

#### 3.3 Forms

**Before (Bootstrap):**
```html
<div class="form-group">
  <label for="username">اسم المستخدم</label>
  <input type="text" class="form-control" id="username" placeholder="أدخل اسم المستخدم">
  <small class="form-text text-muted">اسم المستخدم يجب أن يكون فريداً</small>
</div>
```

**After (Tailwind):**
```django
{% include 'components/forms/input.html' with 
  name="username" 
  label="اسم المستخدم" 
  placeholder="أدخل اسم المستخدم"
  help_text="اسم المستخدم يجب أن يكون فريداً" %}
```

Or manually:
```html
<div class="mb-4">
  <label for="username" class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
    اسم المستخدم
  </label>
  <input type="text" 
         id="username" 
         name="username"
         placeholder="أدخل اسم المستخدم"
         class="w-full px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 
                bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100
                focus:ring-2 focus:ring-primary-500 focus:border-transparent
                transition-colors duration-200">
  <p class="mt-1 text-sm text-neutral-500 dark:text-neutral-400">اسم المستخدم يجب أن يكون فريداً</p>
</div>
```

#### 3.4 Tables

**Before (Bootstrap):**
```html
<table class="table table-striped">
  <thead>
    <tr>
      <th>الاسم</th>
      <th>القسم</th>
      <th>الإجراءات</th>
    </tr>
  </thead>
  <tbody>
    {% for item in items %}
    <tr>
      <td>{{ item.name }}</td>
      <td>{{ item.department }}</td>
      <td>
        <a href="#" class="btn btn-sm btn-primary">عرض</a>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
```

**After (Tailwind):**
```django
{% include 'components/tables/table_responsive.html' with 
  headers=["الاسم", "القسم", "الإجراءات"]
  rows=items %}
```

Or manually:
```html
<div class="overflow-x-auto rounded-lg border border-neutral-200 dark:border-neutral-700">
  <table class="min-w-full divide-y divide-neutral-200 dark:divide-neutral-700">
    <thead class="bg-neutral-50 dark:bg-neutral-800">
      <tr>
        <th class="px-6 py-3 text-start text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
          الاسم
        </th>
        <th class="px-6 py-3 text-start text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
          القسم
        </th>
        <th class="px-6 py-3 text-start text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
          الإجراءات
        </th>
      </tr>
    </thead>
    <tbody class="bg-white dark:bg-neutral-900 divide-y divide-neutral-200 dark:divide-neutral-700">
      {% for item in items %}
      <tr class="hover:bg-neutral-50 dark:hover:bg-neutral-800/50">
        <td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-900 dark:text-neutral-100">
          {{ item.name }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-600 dark:text-neutral-400">
          {{ item.department }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm">
          <a href="#" class="text-primary-600 dark:text-primary-400 hover:text-primary-700">عرض</a>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
```

#### 3.5 Alerts

**Before (Bootstrap):**
```html
<div class="alert alert-success alert-dismissible fade show">
  تم الحفظ بنجاح
  <button type="button" class="close" data-dismiss="alert">&times;</button>
</div>
```

**After (Tailwind):**
```django
{% include 'components/feedback/alert.html' with 
  type="success" 
  message="تم الحفظ بنجاح" 
  dismissible=True %}
```

### Step 4: Remove Custom CSS

1. **Identify custom CSS** in `<style>` tags
2. **Convert to Tailwind classes**
3. **Move truly custom styles** to app-specific CSS file (if needed)
4. **Remove the `<style>` tag**

**Example:**

**Before:**
```html
<style>
  .custom-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 20px;
  }
</style>

<div class="custom-card">
  Content
</div>
```

**After:**
```html
<div class="bg-white rounded-lg shadow-md p-5">
  Content
</div>
```

### Step 5: Test Thoroughly

Use the [Testing Checklist](#testing-checklist) below.

### Step 6: Deploy and Monitor

1. Deploy to staging environment
2. User acceptance testing
3. Monitor for 1 week
4. Fix any issues
5. Deploy to production

### Step 7: Cleanup (After 2 Weeks)

After the migration is stable for 2 weeks:

1. **Delete old base template:**
   ```bash
   rm app_name/templates/app_name/base_old.html
   ```

2. **Remove migration wrapper:**
   - Rename `base_migration.html` to `base.html` (if app needs custom base)
   - OR update all templates to extend global `base.html` directly

3. **Update template extensions:**
   ```diff
   - {% extends 'app_name/base_migration.html' %}
   + {% extends 'base.html' %}
   ```

4. **Remove deprecated CSS files**

---

## Component Reference

### Buttons

| Component | Usage |
|-----------|-------|
| `btn_primary.html` | Main actions (Save, Submit, Create) |
| `btn_secondary.html` | Alternative actions (Cancel, Back) |
| `btn_outline.html` | Less prominent actions |
| `btn_ghost.html` | Minimal emphasis |
| `btn_danger.html` | Destructive actions (Delete) |
| `btn_icon.html` | Icon-only buttons |

### Forms

| Component | Usage |
|-----------|-------|
| `input.html` | Text inputs, email, password |
| `select.html` | Dropdown selects |
| `textarea.html` | Multi-line text |
| `form_group.html` | Form field wrapper |
| `checkbox.html` | Checkbox inputs |
| `radio.html` | Radio inputs |

### Cards

| Component | Usage |
|-----------|-------|
| `card_basic.html` | Standard content card |
| `card_stat.html` | Statistics/metrics card |
| `card_action.html` | Quick actions card |
| `card_profile.html` | User profile card |

### Feedback

| Component | Usage |
|-----------|-------|
| `alert.html` | Success, error, warning, info messages |
| `badge.html` | Status indicators |
| `modal.html` | Dialog modals |
| `toast.html` | Toast notifications |
| `spinner.html` | Loading indicators |

### Tables

| Component | Usage |
|-----------|-------|
| `table_responsive.html` | Responsive data tables |
| `table_actions.html` | Table with action buttons |
| `table_empty.html` | Empty state message |

---

## Common Patterns

### Pattern 1: List Page with Actions

```django
{% extends 'base.html' %}

{% block content %}
<!-- Page Header -->
{% include 'components/layout/page_header.html' with 
  title="قائمة الموظفين"
  breadcrumbs=breadcrumbs
  actions='<a href="/create/" class="btn btn-primary">إضافة موظف</a>' %}

<!-- Stats Cards -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
  {% include 'components/cards/card_stat.html' with 
    title="إجمالي الموظفين" value=total_count icon="fas fa-users" color="primary" %}
  {% include 'components/cards/card_stat.html' with 
    title="نشط" value=active_count icon="fas fa-check-circle" color="success" %}
  {% include 'components/cards/card_stat.html' with 
    title="غير نشط" value=inactive_count icon="fas fa-times-circle" color="error" %}
</div>

<!-- Data Table -->
{% include 'components/tables/table_responsive.html' with 
  headers=["الاسم", "القسم", "المنصب", "الإجراءات"]
  rows=employees
  actions=["view", "edit", "delete"] %}
{% endblock %}
```

### Pattern 2: Form Page

```django
{% extends 'base.html' %}

{% block content %}
<!-- Page Header -->
{% include 'components/layout/page_header.html' with 
  title="إضافة موظف جديد"
  breadcrumbs=breadcrumbs %}

<!-- Form Card -->
<div class="bg-white dark:bg-neutral-800 rounded-lg shadow-md">
  <form method="post" class="p-6">
    {% csrf_token %}
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      {% include 'components/forms/input.html' with 
        name="first_name" label="الاسم الأول" required=True %}
      {% include 'components/forms/input.html' with 
        name="last_name" label="اسم العائلة" required=True %}
      {% include 'components/forms/select.html' with 
        name="department" label="القسم" options=departments %}
      {% include 'components/forms/input.html' with 
        name="email" label="البريد الإلكتروني" type="email" %}
    </div>
    
    <!-- Form Actions -->
    <div class="flex items-center justify-end gap-3 mt-6 pt-6 border-t border-neutral-200 dark:border-neutral-700">
      {% include 'components/buttons/btn_secondary.html' with text="إلغاء" onclick="history.back()" %}
      {% include 'components/buttons/btn_primary.html' with text="حفظ" icon="fas fa-save" type="submit" %}
    </div>
  </form>
</div>
{% endblock %}
```

### Pattern 3: Detail Page

```django
{% extends 'base.html' %}

{% block content %}
<!-- Page Header -->
{% include 'components/layout/page_header.html' with 
  title=employee.name
  breadcrumbs=breadcrumbs
  actions='
    <a href="/edit/" class="btn btn-outline">تعديل</a>
    <a href="/delete/" class="btn btn-danger">حذف</a>
  ' %}

<!-- Profile Card -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <!-- Main Info -->
  <div class="lg:col-span-2 bg-white dark:bg-neutral-800 rounded-lg shadow-md p-6">
    <h2 class="text-xl font-semibold mb-4">المعلومات الأساسية</h2>
    <dl class="grid grid-cols-2 gap-4">
      <div>
        <dt class="text-sm text-neutral-500 dark:text-neutral-400">الاسم</dt>
        <dd class="text-base font-medium">{{ employee.name }}</dd>
      </div>
      <div>
        <dt class="text-sm text-neutral-500 dark:text-neutral-400">القسم</dt>
        <dd class="text-base font-medium">{{ employee.department }}</dd>
      </div>
    </dl>
  </div>
  
  <!-- Sidebar Info -->
  <div class="bg-white dark:bg-neutral-800 rounded-lg shadow-md p-6">
    <h2 class="text-xl font-semibold mb-4">معلومات إضافية</h2>
    <!-- Additional info -->
  </div>
</div>
{% endblock %}
```

---

## Testing Checklist

### Visual Testing

- [ ] Light mode renders correctly
- [ ] Dark mode renders correctly
- [ ] Mobile responsive (< 640px)
- [ ] Tablet responsive (768px - 1024px)
- [ ] Desktop responsive (> 1024px)
- [ ] RTL layout correct
- [ ] All icons display properly
- [ ] Colors match design system

### Functional Testing

- [ ] All links work
- [ ] Forms submit correctly
- [ ] Form validation works
- [ ] Modals open/close properly
- [ ] Dropdowns work
- [ ] Sidebar toggle works (mobile)
- [ ] Theme toggle works
- [ ] Search works (if applicable)
- [ ] Pagination works (if applicable)
- [ ] File uploads work (if applicable)

### Accessibility Testing

- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] ARIA labels present
- [ ] Screen reader compatible
- [ ] Color contrast passes WCAG AA
- [ ] Semantic HTML used

### Performance Testing

- [ ] Page load time < 2 seconds
- [ ] No console errors
- [ ] No 404 errors for static files
- [ ] CSS file size reasonable
- [ ] JavaScript loads efficiently

---

## Troubleshooting

### Issue: Styles not applying

**Solution:**
1. Check if Tailwind CSS is loaded:
   ```html
   <link rel="stylesheet" href="{% static 'css/output.css' %}">
   ```
2. Rebuild Tailwind CSS:
   ```bash
   npm run build:css
   ```
3. Clear browser cache
4. Run `collectstatic`:
   ```bash
   python manage.py collectstatic --noinput
   ```

### Issue: Dark mode not working

**Solution:**
1. Check if `dark` class is on `<html>` element
2. Verify `darkMode: 'class'` in `tailwind.config.js`
3. Check localStorage for `theme` key
4. Ensure all components have `dark:` variants

### Issue: RTL layout broken

**Solution:**
1. Verify `<html dir="rtl">` is set
2. Use logical properties (`ms-`, `me-`, `ps-`, `pe-`)
3. Avoid `margin-left`, `margin-right`, etc.
4. Test with `dir="ltr"` to identify issues

### Issue: Components not rendering

**Solution:**
1. Check component path is correct
2. Verify all required parameters are passed
3. Check Django template syntax
4. Look for typos in variable names

### Issue: JavaScript errors

**Solution:**
1. Open browser console (F12)
2. Check for missing Alpine.js
3. Verify all JS files are loaded
4. Check for syntax errors in inline scripts

---

## Quick Reference Card

### Bootstrap → Tailwind Mapping

| Bootstrap | Tailwind Component |
|-----------|-------------------|
| `.btn.btn-primary` | `btn_primary.html` |
| `.btn.btn-secondary` | `btn_secondary.html` |
| `.btn.btn-danger` | `btn_danger.html` |
| `.card` | `card_basic.html` |
| `.form-control` | `input.html` |
| `.form-select` | `select.html` |
| `.table` | `table_responsive.html` |
| `.alert` | `alert.html` |
| `.badge` | `badge.html` |
| `.modal` | `modal.html` |
| `.navbar` | `navbar.html` |

### Color Mapping

| Bootstrap | Tailwind |
|-----------|----------|
| `.primary` | `primary-500` |
| `.secondary` | `secondary-500` |
| `.success` | `success-500` |
| `.danger` | `error-500` |
| `.warning` | `warning-500` |
| `.info` | `info-500` |
| `.light` | `neutral-100` |
| `.dark` | `neutral-900` |

---

**Guide Status:** Complete ✅  
**Last Updated:** April 29, 2026  
**Version:** 1.0
