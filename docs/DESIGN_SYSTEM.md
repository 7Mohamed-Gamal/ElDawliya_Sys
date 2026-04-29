# 🎨 ElDawliya ERP - Tailwind CSS Design System

## Overview

A comprehensive, modern design system built with Tailwind CSS for the ElDawliya ERP system. Features mobile-first responsive design, full dark mode support, and RTL (Right-to-Left) layout for Arabic.

---

## 🎯 Core Principles

1. **Mobile-First**: All components designed for mobile, then enhanced for larger screens
2. **Dark Mode Native**: Every component supports light and dark themes
3. **RTL Ready**: Full Arabic language support with logical CSS properties
4. **Accessible**: WCAG 2.1 AA compliant with proper ARIA attributes
5. **Reusable**: Component-based architecture for consistency

---

## 🎨 Color Palette

### Primary Colors (Blue)
| Shade | Hex | Usage |
|-------|-----|-------|
| 50 | `#eff6ff` | Light backgrounds |
| 100 | `#dbeafe` | Hover states |
| 500 | `#3b82f6` | **Main primary** |
| 600 | `#2563eb` | Active states |
| 700 | `#1d4ed8` | Dark mode primary |
| 900 | `#1e3a8a` | Text on light bg |

### Secondary Colors (Indigo)
| Shade | Hex | Usage |
|-------|-----|-------|
| 500 | `#6366f1` | **Main secondary** |
| 600 | `#4f46e5` | Alternative actions |

### Semantic Colors
| Color | Usage | Example |
|-------|-------|---------|
| Success | Confirmations, success states | "تم الحفظ بنجاح" |
| Warning | Cautions, warnings | "تنبيه: بيانات غير مكتملة" |
| Error | Errors, deletions | "خطأ في البيانات" |
| Info | Information, help | "معلومات إضافية" |

### Neutral Colors
Used for backgrounds, text, borders throughout the system.

---

## 📝 Typography

### Font Families
- **Primary**: Cairo (Arabic) + system-ui (fallback)
- **Alternative**: Tajawal, Almarai, IBM Plex Sans Arabic, Noto Sans Arabic

### Font Scale
| Size | REM | PX | Usage |
|------|-----|----|-------|
| xs | 0.75rem | 12px | Captions, hints |
| sm | 0.875rem | 14px | Small text, labels |
| base | 1rem | 16px | Body text |
| lg | 1.125rem | 18px | Subheadings |
| xl | 1.25rem | 20px | Section titles |
| 2xl | 1.5rem | 24px | Page titles |
| 3xl | 1.875rem | 30px | Hero titles |

### Font Weights
- **300**: Light (rarely used)
- **400**: Normal (body text)
- **500**: Medium (labels, metadata)
- **600**: Semibold (headings, buttons)
- **700**: Bold (important text)

---

## 📏 Spacing System

Based on 4px grid system (0.25rem = 4px)

| Token | Value | PX |
|-------|-------|----|
| 1 | 0.25rem | 4px |
| 2 | 0.5rem | 8px |
| 3 | 0.75rem | 12px |
| 4 | 1rem | 16px |
| 6 | 1.5rem | 24px |
| 8 | 2rem | 32px |
| 12 | 3rem | 48px |
| 16 | 4rem | 64px |

---

## 🧩 Components

### Buttons

#### Primary Button
```django
{% include 'components/buttons/btn_primary.html' with text="حفظ" icon="fas fa-save" %}
```
- **Use**: Main actions (Save, Submit, Create)
- **Colors**: Blue background, white text
- **States**: Default, Hover, Active, Disabled

#### Secondary Button
```django
{% include 'components/buttons/btn_secondary.html' with text="إلغاء" %}
```
- **Use**: Alternative actions (Cancel, Back)

#### Outline Button
```django
{% include 'components/buttons/btn_outline.html' with text="تفاصيل" color="primary" %}
```
- **Use**: Less prominent actions
- **Colors**: primary, secondary, success, error, warning

#### Ghost Button
```django
{% include 'components/buttons/btn_ghost.html' with text="عرض" %}
```
- **Use**: Minimal emphasis (links, toggles)

#### Sizes
- `sm`: Small (compact)
- `` (default): Medium
- `lg`: Large
- `xl`: Extra large

---

### Form Inputs

#### Text Input
```django
{% include 'components/forms/input.html' with 
  name="username" 
  label="اسم المستخدم" 
  placeholder="أدخل اسم المستخدم"
  required=True 
  icon="fas fa-user" %}
```

#### Select Dropdown
```django
{% include 'components/forms/select.html' with 
  name="department" 
  label="القسم" 
  options=department_list 
  include_empty=True %}
```

#### Textarea
```django
{% include 'components/forms/textarea.html' with 
  name="notes" 
  label="ملاحظات" 
  rows=4 %}
```

#### States
- Default
- Focus (ring)
- Error (red border + error message)
- Disabled
- With icon

---

### Cards

#### Basic Card
```django
{% include 'components/cards/card_basic.html' with 
  title="عنوان البطاقة" 
  body="المحتوى" 
  hover=True %}
```

#### Stat Card (Dashboard)
```django
{% include 'components/cards/card_stat.html' with 
  title="إجمالي الموظفين" 
  value="150" 
  icon="fas fa-users" 
  color="primary" 
  trend="+5%" %}
```

---

### Tables

#### Responsive Table
```django
{% include 'components/tables/table_responsive.html' with 
  title="قائمة الموظفين"
  headers=["الاسم", "القسم", "المنصب"]
  rows=employee_data
  sortable=True
  empty_message="لا توجد بيانات" %}
```

- Mobile: Horizontal scroll
- Desktop: Full width
- Optional: Sortable headers, pagination

---

### Feedback

#### Alerts
```django
{% include 'components/feedback/alert.html' with 
  type="success" 
  message="تم الحفظ بنجاح" 
  dismissible=True %}
```
- **Types**: info, success, warning, error
- **Features**: Dismissible, icons, titles

#### Badges
```django
{% include 'components/feedback/badge.html' with 
  text="نشط" 
  color="success" 
  size="sm" %}
```
- **Colors**: primary, secondary, success, warning, error, info, neutral
- **Sizes**: sm, default, lg

#### Modals
```django
{% include 'components/feedback/modal.html' with 
  id="myModal" 
  title="عنوان النافذة" 
  size="md" %}
  <!-- Content -->
{% endinclude %}
```
- **Sizes**: sm, md, lg, xl
- **Features**: Backdrop close, keyboard dismiss

---

### Navigation

#### Navbar
```django
{% include 'components/navigation/navbar.html' %}
```
- **Features**:
  - Mobile menu toggle
  - Global search
  - Theme toggle (dark/light)
  - Notifications dropdown
  - User menu dropdown

#### Sidebar
```django
{% include 'components/navigation/sidebar.html' %}
```
- **Features**:
  - Logo & branding
  - Menu items with icons
  - Submenus (collapsible)
  - Active state highlighting
  - Badge support

---

## 🌙 Dark Mode

### Implementation
- **Strategy**: Class-based (`dark` class on `<html>`)
- **Toggle**: Sun/Moon icon button in navbar
- **Persistence**: localStorage (`theme` key)
- **Auto-detect**: Respects `prefers-color-scheme` media query

### Usage
```html
<!-- Light mode default -->
<div class="bg-white dark:bg-neutral-800">
  <p class="text-neutral-900 dark:text-neutral-100">Text</p>
</div>
```

### Toggle Function
```javascript
function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.classList.contains('dark');
    
    if (isDark) {
        html.classList.remove('dark');
        localStorage.setItem('theme', 'light');
    } else {
        html.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    }
}
```

---

## 📱 Responsive Design

### Breakpoints (Mobile-First)
| Breakpoint | Width | Device |
|------------|-------|--------|
| sm | 640px | Large phones |
| md | 768px | Tablets |
| lg | 1024px | Laptops |
| xl | 1280px | Desktops |
| 2xl | 1536px | Large screens |

### Usage Example
```html
<!-- Mobile: 1 column, Tablet: 2 columns, Desktop: 4 columns -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  <!-- Cards -->
</div>
```

---

## ♿ Accessibility

### Features
- ✅ Semantic HTML5 elements
- ✅ ARIA labels and roles
- ✅ Focus visible indicators
- ✅ Keyboard navigation
- ✅ Color contrast (WCAG AA)
- ✅ Screen reader text (`.sr-only`)
- ✅ Skip to main content link

### Focus Styles
```css
*:focus-visible {
  @apply outline-none ring-2 ring-primary-500 ring-offset-2;
  @apply dark:ring-offset-neutral-900;
}
```

---

## 🚀 Performance

### Optimizations
1. **PurgeCSS**: Removes unused CSS in production
2. **Minification**: Compressed CSS output
3. **Caching**: Static files cached with versioning
4. **Lazy Loading**: Images and modals load on demand
5. **Code Splitting**: Separate CSS for critical path

### Build Commands
```bash
# Development (watch mode)
npm run watch:css

# Production (minified)
npm run build:css
```

---

## 📦 File Structure

```
ElDawliya_Sys/
├── static/css/
│   ├── tailwind.css          # Source CSS
│   └── output.css            # Compiled CSS (gitignore)
├── templates/
│   ├── base.html             # Main template
│   └── components/
│       ├── buttons/
│       │   ├── btn_primary.html
│       │   ├── btn_secondary.html
│       │   ├── btn_outline.html
│       │   └── btn_ghost.html
│       ├── forms/
│       │   ├── input.html
│       │   ├── select.html
│       │   ├── textarea.html
│       │   └── form_group.html
│       ├── cards/
│       │   ├── card_basic.html
│       │   └── card_stat.html
│       ├── tables/
│       │   └── table_responsive.html
│       ├── feedback/
│       │   ├── alert.html
│       │   ├── badge.html
│       │   └── modal.html
│       └── navigation/
│           ├── navbar.html
│           └── sidebar.html
└── tailwind.config.js         # Design system config
```

---

## 🛠️ Customization

### Adding New Colors
Edit `tailwind.config.js`:
```javascript
colors: {
  custom: {
    50: '#...',
    500: '#...',
    900: '#...',
  }
}
```

### Creating New Components
1. Create HTML file in `/templates/components/[category]/`
2. Use Tailwind utility classes only
3. Add documentation comment at top
4. Include in `static/css/tailwind.css` if needed

### Extending Tailwind
Add plugins in `tailwind.config.js`:
```javascript
plugins: [
  require('@tailwindcss/forms'),
  require('@tailwindcss/typography'),
]
```

---

## 📚 Usage Guidelines

### DO ✅
- Use component includes for consistency
- Follow mobile-first approach
- Test in both light and dark modes
- Use semantic HTML elements
- Add proper ARIA attributes

### DON'T ❌
- Don't use inline styles
- Don't mix Bootstrap with Tailwind
- Don't create custom CSS unless necessary
- Don't skip responsive testing
- Don't hardcode colors (use design tokens)

---

## 🔧 Development Workflow

1. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

2. **Watch CSS for Changes**
   ```bash
   npm run watch:css
   ```

3. **Build for Production**
   ```bash
   npm run build:css
   python manage.py collectstatic --noinput
   ```

---

## 📖 Examples

### Dashboard Page
```django
{% extends 'base.html' %}

{% block content %}
<!-- Stats Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
  {% include 'components/cards/card_stat.html' with 
    title="الموظفين" value="150" icon="fas fa-users" color="primary" %}
  {% include 'components/cards/card_stat.html' with 
    title="المشاريع" value="45" icon="fas fa-project-diagram" color="secondary" %}
  {% include 'components/cards/card_stat.html' with 
    title="المهام" value="230" icon="fas fa-tasks" color="success" %}
  {% include 'components/cards/card_stat.html' with 
    title="التنبيهات" value="12" icon="fas fa-bell" color="warning" %}
</div>

<!-- Action Buttons -->
<div class="flex gap-3 mb-6">
  {% include 'components/buttons/btn_primary.html' with 
    text="إنشاء موظف" icon="fas fa-plus" href="/employees/create/" %}
  {% include 'components/buttons/btn_outline.html' with 
    text="تصدير" icon="fas fa-download" color="secondary" %}
</div>

<!-- Data Table -->
{% include 'components/tables/table_responsive.html' with 
  title="آخر الموظفين"
  headers=["الاسم", "القسم", "تاريخ الإنشاء"]
  rows=employees %}
{% endblock %}
```

---

## 🤝 Contributing

When adding new components:
1. Follow existing naming conventions
2. Add comprehensive documentation
3. Test in light/dark modes
4. Test across all breakpoints
5. Ensure accessibility compliance
6. Update this documentation

---

## 📄 License

Internal use only - ElDawliya ERP System

---

**Last Updated**: April 29, 2026  
**Version**: 1.0.0  
**Tailwind CSS**: 3.4.1
