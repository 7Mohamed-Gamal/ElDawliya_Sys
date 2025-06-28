# ElDawliya Design System - Component Library

## Overview
This document provides comprehensive documentation for the ElDawliya Design System component library. All components are built with modern CSS, support RTL (Arabic) layout, and follow accessibility best practices.

## Design Tokens
All components use CSS custom properties (design tokens) for consistent styling:

```css
/* Colors */
--primary-500, --primary-600, --primary-700
--success-500, --warning-500, --error-500
--gray-50, --gray-100, --gray-200, etc.

/* Spacing */
--space-1 through --space-8 (0.25rem to 2rem)

/* Typography */
--text-xs through --text-3xl
--font-normal, --font-medium, --font-semibold, --font-bold

/* Borders & Shadows */
--radius-sm, --radius-md, --radius-lg, --radius-full
--shadow-xs, --shadow-sm, --shadow-md, --shadow-lg, --shadow-xl
```

## Button Components

### Basic Buttons
```html
<!-- Primary Button -->
<button class="btn btn-primary">
    <i class="fas fa-save"></i>
    <span>حفظ</span>
</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">إلغاء</button>

<!-- Outline Button -->
<button class="btn btn-outline-primary">تحرير</button>

<!-- Ghost Button -->
<button class="btn btn-ghost">عرض التفاصيل</button>
```

### Button Sizes
```html
<button class="btn btn-primary btn-xs">صغير جداً</button>
<button class="btn btn-primary btn-sm">صغير</button>
<button class="btn btn-primary">عادي</button>
<button class="btn btn-primary btn-lg">كبير</button>
<button class="btn btn-primary btn-xl">كبير جداً</button>
```

### Button States
```html
<!-- Loading State -->
<button class="btn btn-primary btn-loading">جاري التحميل...</button>

<!-- Disabled State -->
<button class="btn btn-primary" disabled>معطل</button>

<!-- Icon Only -->
<button class="btn btn-primary btn-icon-only">
    <i class="fas fa-edit"></i>
</button>
```

### Button Groups
```html
<div class="btn-group">
    <button class="btn btn-outline-primary">الكل</button>
    <button class="btn btn-outline-primary">نشط</button>
    <button class="btn btn-outline-primary">مكتمل</button>
</div>
```

## Form Components

### Form Groups
```html
<div class="form-group">
    <label class="form-label required" for="name">الاسم</label>
    <input type="text" class="form-control" id="name" placeholder="أدخل الاسم">
    <div class="form-text">يجب أن يكون الاسم باللغة العربية</div>
</div>
```

### Input Sizes
```html
<input type="text" class="form-control form-control-sm" placeholder="صغير">
<input type="text" class="form-control" placeholder="عادي">
<input type="text" class="form-control form-control-lg" placeholder="كبير">
```

### Input Groups
```html
<div class="input-group">
    <span class="input-group-text">
        <i class="fas fa-search"></i>
    </span>
    <input type="text" class="form-control" placeholder="البحث...">
</div>
```

### Form Validation
```html
<!-- Valid Input -->
<input type="email" class="form-control is-valid" value="user@example.com">
<div class="valid-feedback">البريد الإلكتروني صحيح</div>

<!-- Invalid Input -->
<input type="email" class="form-control is-invalid" value="invalid-email">
<div class="invalid-feedback">يرجى إدخال بريد إلكتروني صحيح</div>
```

### Checkboxes and Radios
```html
<!-- Checkbox -->
<div class="form-check">
    <input class="form-check-input" type="checkbox" id="agree">
    <label class="form-check-label" for="agree">
        أوافق على الشروط والأحكام
    </label>
</div>

<!-- Radio Buttons -->
<div class="form-check">
    <input class="form-check-input" type="radio" name="status" id="active">
    <label class="form-check-label" for="active">نشط</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="radio" name="status" id="inactive">
    <label class="form-check-label" for="inactive">غير نشط</label>
</div>

<!-- Switch -->
<div class="form-check form-switch">
    <input class="form-check-input" type="checkbox" id="notifications">
    <label class="form-check-label" for="notifications">تفعيل التنبيهات</label>
</div>
```

## Card Components

### Basic Card
```html
<div class="card">
    <div class="card-header">
        <h3 class="card-title">عنوان البطاقة</h3>
    </div>
    <div class="card-body">
        <p class="card-text">محتوى البطاقة هنا...</p>
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">إجراء</button>
    </div>
</div>
```

### Feature Card
```html
<div class="feature-card">
    <div class="feature-card-icon">
        <i class="fas fa-users"></i>
    </div>
    <h3 class="feature-card-title">إدارة الموظفين</h3>
    <p class="feature-card-description">إدارة شاملة لبيانات الموظفين والحضور</p>
</div>
```

### Stats Card
```html
<div class="stats-card">
    <div class="stats-card-icon">
        <i class="fas fa-chart-line"></i>
    </div>
    <div class="stats-card-content">
        <div class="stats-card-value">1,234</div>
        <div class="stats-card-label">إجمالي المبيعات</div>
    </div>
</div>
```

## Table Components

### Enhanced Table
```html
<div class="table-container">
    <table class="table table-hover">
        <thead>
            <tr>
                <th>الاسم</th>
                <th>البريد الإلكتروني</th>
                <th>الحالة</th>
                <th>الإجراءات</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>أحمد محمد</td>
                <td>ahmed@example.com</td>
                <td><span class="badge badge-success">نشط</span></td>
                <td>
                    <div class="table-actions">
                        <button class="btn btn-sm btn-outline-primary">تحرير</button>
                        <button class="btn btn-sm btn-outline-error">حذف</button>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

## Modal Components

### Basic Modal
```html
<div class="modal" id="exampleModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">عنوان النافذة</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>محتوى النافذة المنبثقة...</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                <button type="button" class="btn btn-primary">حفظ</button>
            </div>
        </div>
    </div>
</div>
```

### Modal Sizes
```html
<!-- Small Modal -->
<div class="modal modal-sm">...</div>

<!-- Large Modal -->
<div class="modal modal-lg">...</div>

<!-- Extra Large Modal -->
<div class="modal modal-xl">...</div>

<!-- Fullscreen Modal -->
<div class="modal modal-fullscreen">...</div>
```

## Badge Components

### Basic Badges
```html
<span class="badge badge-primary">أساسي</span>
<span class="badge badge-success">نجح</span>
<span class="badge badge-warning">تحذير</span>
<span class="badge badge-error">خطأ</span>
<span class="badge badge-secondary">ثانوي</span>
```

### Outline Badges
```html
<span class="badge badge-outline-primary">أساسي</span>
<span class="badge badge-outline-success">نجح</span>
```

### Badge Sizes
```html
<span class="badge badge-primary badge-sm">صغير</span>
<span class="badge badge-primary">عادي</span>
<span class="badge badge-primary badge-lg">كبير</span>
```

### Badge with Icons
```html
<span class="badge badge-primary badge-icon">
    <i class="fas fa-check"></i>
    <span>مكتمل</span>
</span>
```

## Progress Components

### Basic Progress
```html
<div class="progress">
    <div class="progress-bar" style="width: 75%">75%</div>
</div>
```

### Progress Variants
```html
<div class="progress">
    <div class="progress-bar progress-bar-success" style="width: 60%"></div>
</div>

<div class="progress">
    <div class="progress-bar progress-bar-warning" style="width: 40%"></div>
</div>

<div class="progress">
    <div class="progress-bar progress-bar-error" style="width: 20%"></div>
</div>
```

### Progress Sizes
```html
<div class="progress progress-sm">
    <div class="progress-bar" style="width: 50%"></div>
</div>

<div class="progress progress-lg">
    <div class="progress-bar" style="width: 75%"></div>
</div>
```

## Loading Components

### Spinners
```html
<!-- Border Spinner -->
<div class="spinner"></div>
<div class="spinner spinner-sm"></div>
<div class="spinner spinner-lg"></div>

<!-- Grow Spinner -->
<div class="spinner-grow"></div>
<div class="spinner-grow spinner-grow-sm"></div>
<div class="spinner-grow spinner-grow-lg"></div>
```

## Utility Components

### Avatar
```html
<div class="avatar">
    <img src="user-avatar.jpg" alt="صورة المستخدم">
</div>

<!-- Avatar Sizes -->
<div class="avatar avatar-sm">...</div>
<div class="avatar avatar-lg">...</div>
<div class="avatar avatar-xl">...</div>

<!-- Avatar Group -->
<div class="avatar-group">
    <div class="avatar"><img src="user1.jpg" alt="مستخدم 1"></div>
    <div class="avatar"><img src="user2.jpg" alt="مستخدم 2"></div>
    <div class="avatar"><img src="user3.jpg" alt="مستخدم 3"></div>
</div>
```

### Dividers
```html
<!-- Horizontal Divider -->
<hr class="divider">

<!-- Vertical Divider -->
<div class="divider-vertical"></div>
```

## Accessibility Guidelines

1. **Semantic HTML**: Use proper HTML elements and ARIA attributes
2. **Keyboard Navigation**: All interactive elements support keyboard navigation
3. **Screen Readers**: Proper labels and descriptions for assistive technology
4. **Color Contrast**: All text meets WCAG 2.1 AA contrast requirements
5. **Focus Management**: Clear focus indicators and logical tab order

## RTL Support

All components automatically support RTL layout for Arabic text:
- Text alignment is automatically adjusted
- Icons and spacing are mirrored appropriately
- Form controls maintain proper RTL behavior
- Navigation and layout elements respect text direction

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers with modern CSS support
