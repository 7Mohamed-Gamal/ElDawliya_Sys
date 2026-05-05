# Design System Strategy

This document defines the target UI architecture for the Django refactor. It is a planning document only; it does not modify templates or static files.

## Target Principle

The system should have one visual language, one template inheritance model, one compiled Tailwind output, and one shared component library.

Target state:

- One global application base: `templates/base.html`
- One Tailwind configuration: `tailwind.config.js`
- One Tailwind entrypoint: `static/css/tailwind.css`
- One compiled output: `static/css/output.css`
- One component namespace: `templates/components/`
- App templates contain business content only, not layout shells
- App-specific CSS/JS exists only for truly app-specific interactions

## Current Problems To Solve

1. The project has multiple competing layout roots:
   - `templates/base.html`
   - `frontend/templates/base/base_enhanced.html`
   - `administrator/base_admin.html`
   - `inventory/base_inventory.html`
   - `tasks/base_tasks.html`
   - `meetings/base_meetings.html`
   - HR app-specific bases
   - Notifications and procurement-specific bases

2. Styling is fragmented:
   - Tailwind is compiled globally.
   - Bootstrap is imported in several base templates.
   - Many base templates include large inline `<style>` blocks.
   - App-local CSS files override layout, buttons, cards, forms, and tables independently.

3. Navigation is duplicated:
   - Sidebar and navbar exist in global `templates/base.html`.
   - Administrator, inventory, frontend, tasks, meetings, notifications, and procurement define their own shell.

4. Responsiveness is inconsistent:
   - Sidebar breakpoints differ by app.
   - Mobile overlays and collapsed-sidebar behavior are implemented several times.
   - Tables and forms use different responsive wrappers.

5. Design tokens are not enforced:
   - Tailwind tokens exist, but Bootstrap/inline CSS define alternative colors, radii, shadows, and spacing.

## Global Template Strategy

### Canonical Base

Use `templates/base.html` as the only runtime base for authenticated application pages.

Required base contract:

- Loads `static/css/output.css`
- Sets `html lang="ar" dir="rtl"` by default
- Supports dark mode through the existing `dark` class strategy
- Includes global sidebar and navbar through shared components
- Renders Django messages through shared alert components
- Provides stable extension blocks:
  - `title`
  - `meta`
  - `extra_css`
  - `body_class`
  - `sidebar`
  - `navbar`
  - `breadcrumb`
  - `page_header`
  - `content`
  - `modals`
  - `extra_js`

### Compatibility Adapters

Do not remove app-local bases immediately. Convert them gradually into adapters:

```django
{% extends "base.html" %}
{% block sidebar %}
  {% include "components/navigation/sidebar.html" with section="inventory" %}
{% endblock %}
{% block content %}
  {% block app_content %}{% endblock %}
{% endblock %}
```

This prevents a high-risk big-bang rewrite. Child templates can then be migrated from `content` to `app_content` or directly to the global block contract one app at a time.

### Public/Auth Pages

Login and access-denied pages should use a controlled layout mode:

- `show_sidebar=False`
- `show_navbar=False` for login
- `show_footer=False` if a full-screen auth layout is required
- Reuse global typography, color, form, and alert components

## Tailwind Strategy

### Keep One Config

Keep `tailwind.config.js` as the only Tailwind config. It already scans global templates, app templates, Python files, and JS assets.

Required cleanup:

- Remove duplicated nested `extend` keys in the Tailwind config during implementation.
- Freeze new Bootstrap imports.
- Move design tokens currently embedded in inline CSS into Tailwind theme tokens or `@layer components`.
- Keep `darkMode: "class"`.
- Keep Arabic-first font support.

### Build Pipeline

Standardize on:

- `npm run build:css` for production CSS
- `npm run watch:css` for development
- Output: `static/css/output.css`

No app should compile its own Tailwind CSS.

### CSS Ownership

Allowed global CSS:

- `static/css/tailwind.css`
- `static/css/output.css`
- Small, documented compatibility stylesheet during migration if needed

Allowed app CSS:

- Only for non-generic behavior that cannot be expressed as components, e.g. attendance device status visualization or special report print layouts.

Disallowed after migration:

- App-local `.card`, `.btn`, `.table`, `.sidebar`, `.navbar`, `.form-control` redefinitions
- Large inline `<style>` blocks in templates
- Bootstrap utility classes in newly migrated templates

## Color System

Use a professional operational dashboard palette. Avoid a one-note blue-only system by using semantic colors intentionally.

### Core Tokens

- Primary: `primary-600 #2563eb`
- Primary hover: `primary-700 #1d4ed8`
- Secondary: `secondary-600 #4f46e5`
- Accent: `accent-500 #f59e0b`
- Neutral background: `neutral-50 #fafafa`
- Surface: white / `neutral-800` in dark mode
- Border: `neutral-200` / `neutral-700`
- Text primary: `neutral-900` / `neutral-50`
- Text secondary: `neutral-600` / `neutral-400`

### Semantic Tokens

- Success: `success-600`
- Warning: `warning-500`
- Error: `error-600`
- Info: `info-600`

### Domain Accent Usage

Domain colors should only appear as small accents, icons, badges, or active navigation markers:

- HR: primary blue
- Inventory: success green
- Procurement: accent amber
- Projects: secondary indigo
- Finance: info cyan
- Administration: neutral/dark
- Audit/security: error red only for risk states

No app should redefine the full color palette.

## Typography

Primary font:

- `Cairo`, with `system-ui` fallback

Allowed alternatives only through system settings:

- `Tajawal`
- `Almarai`
- `IBM Plex Sans Arabic`
- `Noto Sans Arabic`

Typography scale:

- Page title: `text-2xl font-semibold`
- Section title: `text-xl font-semibold`
- Card title: `text-base font-semibold`
- Body: `text-sm` or `text-base`
- Table text: `text-sm`
- Help text: `text-xs text-neutral-500`

Rules:

- No viewport-based font scaling.
- No negative letter spacing.
- Do not use oversized hero-style typography inside dashboards.
- Keep Arabic line-height comfortable: `leading-6` for body, `leading-7` for dense panels.

## Layout Grid

### Page Shell

Desktop:

- Fixed logical sidebar: `lg:w-64`
- Main content offset: `lg:pe-64`
- Top navbar inside content area
- Main content max width controlled by container, not arbitrary app wrappers

Mobile:

- Sidebar becomes off-canvas
- Navbar contains menu trigger
- Content uses `px-4 py-4`
- Tables become horizontally scrollable or card-list views for narrow screens

### Content Grid

Dashboard:

- Stats: `grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4`
- Main analytics: `grid grid-cols-1 xl:grid-cols-3 gap-6`
- Forms: single column on mobile, two columns from `lg`
- Dense admin lists: full-width table inside a responsive table component

### Spacing

- Page padding: `px-4 py-6 lg:py-8`
- Section gap: `space-y-6`
- Card padding: `p-4` or `p-6`
- Form gap: `gap-4`
- Button gap: `gap-2`

## Sidebar Strategy

Use one shared sidebar component:

- `templates/components/navigation/sidebar.html`

It should receive navigation data from a context processor or a simple include context:

- `active_app`
- `active_section`
- `menu_items`
- `user`
- `permissions`

Sidebar behavior:

- Collapsible on desktop
- Off-canvas on mobile
- Permission-aware menu rendering
- Active states based on resolver namespace or `active_app`
- Domain grouping:
  - Main
  - HR
  - Inventory and Procurement
  - Projects
  - Finance
  - Reports
  - Administration

Migration rule:

- App-local sidebars become data/config only; they should not own layout CSS.

## Navbar Strategy

Use one shared navbar component:

- `templates/components/navigation/navbar.html`

Required features:

- Mobile sidebar trigger
- Breadcrumb slot
- Global search slot
- Notification menu
- User menu
- Theme toggle
- Language indicator or future language switcher

Navbar must not hard-code app URLs that may not exist. It should rely on safe navigation config or conditionally loaded menu items.

## Component System

Canonical component namespace:

- `templates/components/`

Existing components to keep and standardize:

- Buttons: `components/buttons/*`
- Cards: `components/cards/*`
- Feedback: alerts, badges, modal, spinner, toast
- Forms: input, select, textarea, form group
- Layout: page header, sidebar item
- Navigation: navbar, sidebar
- Tables: responsive table
- Breadcrumb

Required new components:

- `components/layout/app_shell.html` if base needs shell composition
- `components/layout/page_toolbar.html`
- `components/forms/form_actions.html`
- `components/tables/empty_state.html`
- `components/tables/pagination.html`
- `components/tables/table_actions.html`
- `components/feedback/confirm_delete.html`
- `components/feedback/status_badge.html`
- `components/data/stat_grid.html`
- `components/data/chart_panel.html`
- `components/navigation/module_tabs.html`

Component rules:

- Components must be dumb templates with explicit inputs.
- Components should not fetch data.
- Components should avoid app-specific URL names unless passed in.
- Components must be RTL-safe using logical spacing where possible.
- Components should not depend on Bootstrap classes.

## Forms Strategy

Use `widget_tweaks` or explicit component includes to standardize form rendering.

Required form patterns:

- Label above field
- Required marker
- Help text
- Error list
- Consistent input height
- Consistent focus ring
- Sticky form action row for large edit screens where useful

Migration rule:

- Remove JavaScript that auto-adds Bootstrap classes to form elements.
- Replace with explicit Django form widgets or shared form components.

## Tables Strategy

Tables are critical for this system. Standardize them early.

Required table behavior:

- Responsive wrapper
- Sticky header where useful
- Empty state
- Pagination component
- Compact density option
- Action-button component
- Status-badge component
- Safe horizontal scroll on mobile

Apps most affected:

- Inventory
- Purchase orders
- Employees
- Administrator
- Attendance
- Leaves
- Payroll
- Audit

## JavaScript Strategy

Global JS ownership:

- `static/js/main.js` for initialization only
- `static/js/navigation.js` for sidebar/navbar behavior
- `static/js/components.js` for component behavior
- App-specific JS only for complex app workflows

Rules:

- No duplicate sidebar toggle implementation per app.
- No global mutation of all inputs/buttons to Bootstrap classes.
- Use `data-*` attributes for component initialization.
- Keep Alpine.js only if used intentionally by shared components.
- Avoid jQuery in newly migrated screens.

## Migration Guardrails

1. Do not rewrite all apps at once.
2. Create a compatibility period where app bases extend global `base.html`.
3. Migrate highest-dependency layouts first.
4. Keep URL names and view context unchanged unless a backend issue blocks UI migration.
5. After each app migration, run:
   - Django template rendering smoke tests
   - CSS build
   - Manual responsive check for desktop/tablet/mobile
6. Remove old CSS only after no templates reference its classes.

## Acceptance Criteria

A screen is considered migrated when:

- It extends `base.html` directly or through a documented temporary adapter.
- It uses shared navbar/sidebar.
- It loads only global Tailwind output plus approved app JS.
- It does not import Bootstrap.
- It does not define layout-level inline CSS.
- Buttons, cards, forms, tables, alerts, badges, and modals use shared components.
- It behaves correctly at mobile, tablet, and desktop widths.
- It respects RTL layout.

## Final Target Structure

```text
templates/
  base.html
  components/
    buttons/
    cards/
    data/
    feedback/
    forms/
    layout/
    navigation/
    tables/
  errors/
  admin/

static/
  css/
    tailwind.css
    output.css
  js/
    main.js
    navigation.js
    components.js
  inventory/
    js/
      voucher_form.js
      product_form.js
```

App templates should remain inside their apps where possible:

```text
apps/hr/employees/templates/employees/
apps/inventory/templates/inventory/
apps/procurement/purchase_orders/templates/purchase_orders/
```

Global domain templates currently under `templates/hr`, `templates/leaves`, `templates/org`, and similar folders should be migrated or explicitly documented as legacy routes.
