# 🎨 ElDawliya ERP - Design System Strategy

**Created:** April 29, 2026  
**Version:** 2.0 (Unified)  
**Status:** Implementation Ready

---

## 1. Vision & Goals

### 1.1 Vision
Create a **unified, scalable, and accessible** design system for the ElDawliya ERP that provides:
- Consistent user experience across all modules
- Mobile-first responsive design
- Full RTL (Arabic) support
- Dark mode by default
- WCAG 2.1 AA accessibility compliance

### 1.2 Goals
- Reduce 26 base templates to **1 global base**
- Eliminate Bootstrap dependency (currently 58% usage)
- Achieve 100% Tailwind CSS adoption
- Increase component reusability from 25% to 80%+
- Reduce custom CSS files from 11 to <5

---

## 2. Architecture Overview

### 2.1 Template Hierarchy

```
base.html (Global Enhanced Base)
│
├── {% block extra_css %}          ← App-specific CSS (if needed)
├── {% block sidebar %}            ← App-specific sidebar
├── {% block navbar %}             ← Global navbar (override if needed)
├── {% block breadcrumbs %}        ← Page breadcrumbs
├── {% block content %}            ← Main page content
├── {% block modals %}             ← Page modals
└── {% block extra_js %}           ← App-specific JavaScript
```

### 2.2 Component Architecture

**Three-Tier System:**

```
Atomic Components (Buttons, Inputs, Badges)
    ↓
Molecular Components (Cards, Forms, Tables)
    ↓
Organism Components (Header, Sidebar, Page Layout)
```

### 2.3 File Structure

```
templates/
├── base.html                          ← Single global base
├── components/
│   ├── layout/                        ← Layout organisms
│   │   ├── header.html                ← Page header
│   │   ├── sidebar.html               ← Global sidebar
│   │   ├── sidebar_item.html          ← Sidebar menu item
│   │   ├── footer.html                ← Page footer
│   │   └── page_wrapper.html          ← Content wrapper
│   │
│   ├── navigation/                    ← Navigation components
│   │   ├── navbar.html                ← Top navbar
│   │   ├── navbar_user_menu.html      ← User dropdown
│   │   ├── navbar_notifications.html  ← Notifications dropdown
│   │   └── breadcrumbs.html           ← Breadcrumb navigation
│   │
│   ├── buttons/                       ← Button atoms
│   │   ├── btn_primary.html
│   │   ├── btn_secondary.html
│   │   ├── btn_outline.html
│   │   ├── btn_ghost.html
│   │   ├── btn_danger.html            ← NEW
│   │   └── btn_icon.html              ← NEW
│   │
│   ├── forms/                         ← Form molecules
│   │   ├── input.html
│   │   ├── select.html
│   │   ├── textarea.html
│   │   ├── form_group.html
│   │   ├── checkbox.html              ← NEW
│   │   ├── radio.html                 ← NEW
│   │   └── form_errors.html           ← NEW
│   │
│   ├── cards/                         ← Card molecules
│   │   ├── card_basic.html
│   │   ├── card_stat.html
│   │   ├── card_action.html           ← NEW
│   │   └── card_profile.html          ← NEW
│   │
│   ├── tables/                        ← Table molecules
│   │   ├── table_responsive.html
│   │   ├── table_actions.html         ← NEW
│   │   └── table_empty.html           ← NEW
│   │
│   ├── feedback/                      ← Feedback atoms
│   │   ├── alert.html
│   │   ├── badge.html
│   │   ├── modal.html
│   │   ├── toast.html                 ← NEW
│   │   ├── spinner.html               ← NEW
│   │   └── progress_bar.html          ← NEW
│   │
│   └── data/                          ← Data display (NEW)
│       ├── avatar.html
│       ├── timeline.html
│       ├── tabs.html
│       └── pagination.html
│
└── pages/
    ├── dashboard.html                 ← Dashboard template
    ├── login.html                     ← Login page
    └── error/
        ├── 404.html
        ├── 500.html
        └── 403.html
```

---

## 3. Design Tokens

### 3.1 Color System

**Already defined in `tailwind.config.js` - MUST ENFORCE USAGE**

#### Primary Colors (Blue)
```javascript
primary: {
  50: '#eff6ff',   // Light backgrounds
  100: '#dbeafe',  // Hover states (light)
  500: '#3b82f6',  // Main primary (buttons, links)
  600: '#2563eb',  // Active states
  700: '#1d4ed8',  // Dark mode primary
  900: '#1e3a8a',  // Text on light bg
}
```

#### Secondary Colors (Indigo)
```javascript
secondary: {
  500: '#6366f1',  // Main secondary
  600: '#4f46e5',  // Alternative actions
}
```

#### Accent Colors (Amber)
```javascript
accent: {
  500: '#f59e0b',  // Highlights, warnings
  600: '#d97706',  // Active accent
}
```

#### Semantic Colors
```javascript
success: { 500: '#22c55e' }  // Success states
warning: { 500: '#f59e0b' }  // Warning states
error:   { 500: '#ef4444' }  // Error states
info:    { 500: '#0ea5e9' }  // Information states
```

#### Neutral Colors
```javascript
neutral: {
  50: '#fafafa',   // Page background (light)
  100: '#f5f5f5',  // Card backgrounds
  200: '#e5e5e5',  // Borders
  500: '#737373',  // Secondary text
  700: '#404040',  // Primary text (light mode)
  800: '#262626',  // Page background (dark)
  900: '#171717',  // Text (dark mode)
}
```

### 3.2 Typography

#### Font Families
```javascript
fontFamily: {
  sans: ['Cairo', 'system-ui', '-apple-system', 'sans-serif'],
  display: ['Cairo', 'system-ui', 'sans-serif'],
  body: ['Cairo', 'system-ui', 'sans-serif'],
  tajawal: ['Tajawal', 'system-ui', 'sans-serif'],
  almarai: ['Almarai', 'system-ui', 'sans-serif'],
  'ibm-plex': ['IBM Plex Sans Arabic', 'system-ui', 'sans-serif'],
  'noto-sans': ['Noto Sans Arabic', 'system-ui', 'sans-serif'],
}
```

#### Font Scale
| Token | REM | PX | Usage |
|-------|-----|----|-------|
| xs | 0.75rem | 12px | Captions, hints |
| sm | 0.875rem | 14px | Small text, labels |
| base | 1rem | 16px | Body text (default) |
| lg | 1.125rem | 18px | Subheadings |
| xl | 1.25rem | 20px | Section titles |
| 2xl | 1.5rem | 24px | Page titles |
| 3xl | 1.875rem | 30px | Hero titles |

#### Font Weights
- **300** (light) - Rarely used
- **400** (normal) - Body text
- **500** (medium) - Labels, metadata
- **600** (semibold) - Headings, buttons
- **700** (bold) - Important text

### 3.3 Spacing System

**4px Grid System:**

| Token | REM | PX | Usage |
|-------|-----|----|-------|
| 1 | 0.25rem | 4px | Tight spacing |
| 2 | 0.5rem | 8px | Small gaps |
| 3 | 0.75rem | 12px | Form elements |
| 4 | 1rem | 16px | Standard spacing |
| 6 | 1.5rem | 24px | Section spacing |
| 8 | 2rem | 32px | Large gaps |
| 12 | 3rem | 48px | Page sections |
| 16 | 4rem | 64px | Major sections |

### 3.4 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| sm | 0.125rem (2px) | Small elements |
| md | 0.375rem (6px) | Buttons, inputs |
| lg | 0.5rem (8px) | Cards |
| xl | 0.75rem (12px) | Large cards |
| 2xl | 1rem (16px) | Modals |
| full | 9999px | Avatars, badges |

### 3.5 Shadows

| Token | Usage |
|-------|-------|
| sm | Subtle elevation (dropdowns) |
| md | Cards, panels |
| lg | Modals, popovers |
| xl | Floating elements |
| card | Component-specific (0 2px 8px) |
| dropdown | Dropdown menus (0 4px 12px) |
| modal | Modal dialogs (0 20px 60px) |

---

## 4. Layout System

### 4.1 Global Layout Structure

```
┌────────────────────────────────────────────────────┐
│  HEADER (64px height)                              │
│  ┌──────────────────────────────────────────────┐  │
│  │ Logo | Search | Notifications | User Menu    │  │
│  └──────────────────────────────────────────────┘  │
├──────────┬─────────────────────────────────────────┤
│          │                                         │
│ SIDEBAR  │  MAIN CONTENT AREA                     │
│ (280px)  │  ┌───────────────────────────────────┐  │
│          │  │ Breadcrumbs                       │  │
│          │  ├───────────────────────────────────┤  │
│          │  │ Page Title                        │  │
│          │  ├───────────────────────────────────┤  │
│          │  │                                   │  │
│          │  │ Content                           │  │
│          │  │                                   │  │
│          │  └───────────────────────────────────┘  │
│          │                                         │
├──────────┴─────────────────────────────────────────┤
│  FOOTER (optional, 48px)                           │
└────────────────────────────────────────────────────┘
```

### 4.2 Responsive Breakpoints

| Breakpoint | Width | Layout Behavior |
|------------|-------|-----------------|
| Mobile | < 640px | Single column, sidebar hidden |
| sm | 640px | 2 columns possible |
| md | 768px | Sidebar collapsible |
| lg | 1024px | Full sidebar + content |
| xl | 1280px | Maximum content width |
| 2xl | 1536px | Extra-wide layouts |

### 4.3 Grid System

**Dashboard Grid:**
```html
<!-- Mobile: 1 col, Tablet: 2 cols, Desktop: 4 cols -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <!-- Stat cards -->
</div>
```

**Form Grid:**
```html
<!-- Mobile: 1 col, Desktop: 2 cols -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
  <!-- Form fields -->
</div>
```

**Content Layout:**
```html
<!-- Sidebar + Main content -->
<div class="flex flex-col lg:flex-row gap-6">
  <aside class="w-full lg:w-80">...</aside>
  <main class="flex-1">...</main>
</div>
```

---

## 5. Component Guidelines

### 5.1 Buttons

#### Usage Rules
- **Primary:** Main action (Save, Submit, Create) - ONE per page
- **Secondary:** Alternative actions (Cancel, Back)
- **Outline:** Less prominent actions (View Details, Export)
- **Ghost:** Minimal emphasis (links, toggles)
- **Danger:** Destructive actions (Delete, Remove)

#### Example
```django
{% include 'components/buttons/btn_primary.html' with 
  text="حفظ" 
  icon="fas fa-save" 
  href="/save/" %}

{% include 'components/buttons/btn_secondary.html' with 
  text="إلغاء" 
  onclick="history.back()" %}

{% include 'components/buttons/btn_danger.html' with 
  text="حذف" 
  icon="fas fa-trash" 
  href="/delete/" %}
```

#### Sizes
- `sm` - Compact (28px height)
- default - Medium (36px height)
- `lg` - Large (44px height)
- `xl` - Extra large (52px height)

### 5.2 Forms

#### Input Fields
```django
{% include 'components/forms/input.html' with 
  name="username" 
  label="اسم المستخدم" 
  placeholder="أدخل اسم المستخدم"
  required=True 
  icon="fas fa-user"
  help_text="اسم المستخدم يجب أن يكون فريداً" %}
```

#### States
- Default
- Focus (ring-2 ring-primary-500)
- Error (border-error-500 + error message)
- Disabled (opacity-50 cursor-not-allowed)
- Loading (spinner icon)

#### Validation
- Client-side: HTML5 validation attributes
- Server-side: Django form validation
- Display: Inline error messages below fields

### 5.3 Cards

#### Stat Card
```django
{% include 'components/cards/card_stat.html' with 
  title="إجمالي الموظفين" 
  value="150" 
  icon="fas fa-users" 
  color="primary" 
  trend="+5%" 
  trend_type="increase" %}
```

#### Basic Card
```django
<div class="bg-white dark:bg-neutral-800 rounded-lg shadow-md p-6">
  <h3 class="text-xl font-semibold mb-4">عنوان البطاقة</h3>
  <div class="content">
    {% block card_content %}{% endblock %}
  </div>
</div>
```

### 5.4 Tables

#### Responsive Table
```django
{% include 'components/tables/table_responsive.html' with 
  title="قائمة الموظفين"
  headers=["الاسم", "القسم", "المنصب", "الإجراءات"]
  rows=employee_data
  sortable=True
  empty_message="لا توجد بيانات"
  actions=["view", "edit", "delete"] %}
```

#### Mobile Behavior
- Horizontal scroll on small screens
- Sticky first column (optional)
- Condensed row height

### 5.5 Feedback

#### Alerts
```django
{% include 'components/feedback/alert.html' with 
  type="success" 
  message="تم الحفظ بنجاح" 
  dismissible=True 
  icon="fas fa-check-circle" %}
```

**Types:**
- `info` - Blue (informational)
- `success` - Green (success)
- `warning` - Amber (warning)
- `error` - Red (error)

#### Badges
```django
{% include 'components/feedback/badge.html' with 
  text="نشط" 
  color="success" 
  size="sm" %}
```

**Colors:** primary, secondary, success, warning, error, info, neutral

---

## 6. Navigation System

### 6.1 Sidebar Structure

```django
<aside class="sidebar">
  <!-- Logo -->
  <div class="sidebar-header">
    <a href="/" class="sidebar-logo">
      <i class="fas fa-building"></i>
      <span>نظام الدولية</span>
    </a>
  </div>

  <!-- Menu Items -->
  <nav class="sidebar-nav">
    {% for item in menu_items %}
      {% include 'components/layout/sidebar_item.html' with 
        item=item 
        active=request.path == item.url %}
    {% endfor %}
  </nav>

  <!-- User Profile (bottom) -->
  <div class="sidebar-footer">
    {% include 'components/navigation/user_profile_mini.html' %}
  </div>
</aside>
```

### 6.2 Navbar Structure

```django
<header class="navbar">
  <!-- Mobile menu toggle -->
  <button class="mobile-menu-toggle">
    <i class="fas fa-bars"></i>
  </button>

  <!-- Global search -->
  <div class="navbar-search">
    <input type="search" placeholder="بحث...">
  </div>

  <!-- Right side -->
  <div class="navbar-actions">
    <!-- Theme toggle -->
    <button class="theme-toggle">
      <i class="fas fa-moon"></i>
    </button>

    <!-- Notifications -->
    {% include 'components/navigation/navbar_notifications.html' %}

    <!-- User menu -->
    {% include 'components/navigation/navbar_user_menu.html' %}
  </div>
</header>
```

### 6.3 Breadcrumbs

```django
{% include 'components/navigation/breadcrumbs.html' with 
  items=[
    {"url": "/", "label": "الرئيسية"},
    {"url": "/employees/", "label": "الموظفين"},
    {"label": "قائمة الموظفين"}
  ] %}
```

---

## 7. Dark Mode Strategy

### 7.1 Implementation

**Class-based dark mode:**
```html
<html class="dark">  <!-- Dark mode -->
<html>               <!-- Light mode -->
```

### 7.2 Usage Pattern

```html
<!-- Background -->
<div class="bg-white dark:bg-neutral-800">

<!-- Text -->
<p class="text-neutral-900 dark:text-neutral-100">

<!-- Borders -->
<div class="border-neutral-200 dark:border-neutral-700">

<!-- Hover states -->
<button class="hover:bg-primary-50 dark:hover:bg-primary-900">
```

### 7.3 Toggle Function

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

### 7.4 Persistence

```javascript
// On page load
(function() {
  const theme = localStorage.getItem('theme');
  if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
  }
})();
```

---

## 8. RTL (Right-to-Left) Support

### 8.1 HTML Setup

```html
<html lang="ar" dir="rtl">
```

### 8.2 Tailwind RTL

**Use logical properties:**
```html
<!-- Instead of margin-left/margin-right -->
<div class="ms-4 me-2">  <!-- margin-start, margin-end -->

<!-- Instead of padding-left/padding-right -->
<div class="ps-6 pe-4">  <!-- padding-start, padding-end -->

<!-- Text alignment -->
<p class="text-start">   <!-- Aligns right in RTL, left in LTR -->
```

### 8.3 Flexbox RTL

```html
<!-- Automatically reverses in RTL -->
<div class="flex gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

### 8.4 Icons in RTL

```html
<!-- Arrow icons should flip -->
<i class="fas fa-arrow-{% if LANGUAGE_CODE == 'ar' %}left{% else %}right{% endif %}"></i>

<!-- Or use logical CSS -->
<i class="fas fa-arrow-right rtl:rotate-180"></i>
```

---

## 9. Accessibility (WCAG 2.1 AA)

### 9.1 Required Features

- ✅ Semantic HTML5 elements
- ✅ ARIA labels and roles
- ✅ Focus visible indicators
- ✅ Keyboard navigation
- ✅ Color contrast (minimum 4.5:1)
- ✅ Screen reader text (`.sr-only`)
- ✅ Skip to main content link
- ✅ Form labels and error messages
- ✅ Alt text for images
- ✅ Descriptive link text

### 9.2 Focus Styles

```css
*:focus-visible {
  @apply outline-none ring-2 ring-primary-500 ring-offset-2;
  @apply dark:ring-offset-neutral-900;
}
```

### 9.3 Color Contrast

**Test all combinations:**
- Primary text on white: ✅ Pass (ratio > 4.5:1)
- Secondary text on white: ✅ Pass
- White text on primary-500: ✅ Pass
- White text on error-500: ✅ Pass

---

## 10. Migration Strategy

### 10.1 Phase 1: Foundation (Week 1-2)

1. **Enhance global base.html**
   - Add sidebar component
   - Add navbar component
   - Add breadcrumb system
   - Add toast notifications
   - Add loading states

2. **Create layout components**
   - `/templates/components/layout/header.html`
   - `/templates/components/layout/sidebar.html`
   - `/templates/components/layout/footer.html`

3. **Document migration process**
   - Create migration guide
   - Create component usage examples
   - Create before/after comparisons

### 10.2 Phase 2: Migration Wrappers (Week 3-4)

For each app:
```django
{# app_name/base_migration.html #}
{% extends 'base.html' %}

{% block sidebar %}
  {% include 'components/navigation/sidebar_app_name.html' %}
{% endblock %}

{% block title %}{% endblock %}
{% block extra_css %}{% endblock %}
{% block content %}{% endblock %}
{% block extra_js %}{% endblock %}
```

### 10.3 Phase 3: Bootstrap → Tailwind (Week 5-12)

**Replace Bootstrap components:**

| Bootstrap | Tailwind Equivalent |
|-----------|---------------------|
| `.btn.btn-primary` | `{% include 'components/buttons/btn_primary.html' %}` |
| `.card` | `{% include 'components/cards/card_basic.html' %}` |
| `.form-control` | `{% include 'components/forms/input.html' %}` |
| `.table` | `{% include 'components/tables/table_responsive.html' %}` |
| `.alert` | `{% include 'components/feedback/alert.html' %}` |
| `.modal` | `{% include 'components/feedback/modal.html' %}` |
| `.navbar` | `{% include 'components/navigation/navbar.html' %}` |

### 10.4 Phase 4: Cleanup (Week 13-14)

1. Remove old base templates
2. Remove migration wrappers
3. Delete deprecated CSS files
4. Update documentation
5. Run performance tests

---

## 11. Component Development Workflow

### 11.1 Creating New Components

1. **Identify need:** Is this component reusable?
2. **Design:** Follow design tokens (colors, spacing, typography)
3. **Create:** Add to appropriate `/templates/components/` subdirectory
4. **Document:** Add usage examples in comments
5. **Test:** Light mode, dark mode, mobile, RTL
6. **Review:** Code review before merging

### 11.2 Component Template Structure

```django
{# components/category/component_name.html #}
{# 
  Usage:
  {% include 'components/category/component_name.html' with 
    param1="value1"
    param2="value2"
  %}
  
  Parameters:
  - param1: Description (required)
  - param2: Description (optional, default: "value")
#}

<div class="component-class">
  {{ content }}
</div>
```

### 11.3 Naming Conventions

- **Files:** `snake_case.html` (e.g., `btn_primary.html`)
- **Classes:** `kebab-case` (e.g., `.sidebar-nav-item`)
- **IDs:** `camelCase` (e.g., `#mainContent`)
- **Variables:** `snake_case` (e.g., `menu_items`)

---

## 12. Performance Guidelines

### 12.1 CSS Optimization

- ✅ Use Tailwind purge in production
- ✅ Minimize custom CSS
- ✅ Avoid `!important`
- ✅ Use utility classes over custom CSS
- ✅ Combine duplicate styles

### 12.2 JavaScript Optimization

- ✅ Defer non-critical JS
- ✅ Use async for external scripts
- ✅ Minimize inline scripts
- ✅ Use event delegation
- ✅ Lazy load modals and heavy components

### 12.3 Template Optimization

- ✅ Use `{% include %}` for reusable parts
- ✅ Avoid deep nesting (max 3 levels)
- ✅ Cache expensive computations
- ✅ Use `{% if %}` to conditionally load heavy components
- ✅ Minimize template variables

### 12.4 Image Optimization

- ✅ Use WebP format
- ✅ Lazy load images (`loading="lazy"`)
- ✅ Specify dimensions (`width`, `height`)
- ✅ Use responsive images (`srcset`)
- ✅ Compress images before upload

---

## 13. Testing Strategy

### 13.1 Visual Testing

- [ ] Light mode
- [ ] Dark mode
- [ ] Mobile (< 640px)
- [ ] Tablet (768px - 1024px)
- [ ] Desktop (> 1024px)
- [ ] RTL layout
- [ ] LTR layout (if multi-language)

### 13.2 Functional Testing

- [ ] All links work
- [ ] Forms submit correctly
- [ ] Modals open/close
- [ ] Dropdowns work
- [ ] Sidebar toggle works
- [ ] Theme toggle works
- [ ] Search works

### 13.3 Accessibility Testing

- [ ] Keyboard navigation
- [ ] Screen reader compatibility
- [ ] Focus management
- [ ] Color contrast
- [ ] ARIA attributes
- [ ] Semantic HTML

### 13.4 Performance Testing

- [ ] Page load < 2 seconds
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] CSS size < 50KB
- [ ] JS size < 100KB

---

## 14. Success Metrics

### 14.1 Technical Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Base templates | 26 | 1 | Count files |
| Bootstrap usage | 58% | 0% | Grep for `.btn.btn-` |
| Component reuse | 25% | 80% | {% include %} count |
| Custom CSS files | 11 | <5 | Count files |
| Avg template size | 312 lines | <200 lines | Line count |

### 14.2 User Experience Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Mobile responsive | 100% | Browser dev tools |
| Dark mode support | 100% | Visual inspection |
| RTL compliance | 100% | Visual inspection |
| WCAG AA score | Pass | axe DevTools |
| Page load time | < 2s | Lighthouse |

### 14.3 Developer Experience Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Onboarding time | < 1 day | Developer feedback |
| Component docs | 100% | Documentation coverage |
| Migration guide | Complete | User testing |
| Production bugs | 0 | Bug tracker |

---

## 15. Next Steps

1. ✅ Review and approve this strategy
2. 🔄 Enhance global base.html (Task 1)
3. 🔄 Create layout components (Task 2)
4. 🔄 Create migration documentation (Task 3)
5. ⏳ Start app-by-app migration (Tasks 4-11)

---

**Strategy Status:** Ready for Implementation ✅  
**Last Updated:** April 29, 2026  
**Version:** 2.0  
**Approved By:** Pending
