# App-by-App UI Refactor Plan

This document defines a step-by-step UI refactor roadmap for each Django app. It is planning-only and intentionally avoids code changes.

## Global Execution Rules

1. Stabilize the global design-system contract before migrating business screens.
2. Keep every app URL and view context stable during UI migration.
3. Convert app-local base templates into temporary adapters before changing child templates.
4. Remove Bootstrap and inline layout CSS only after the matching templates no longer depend on them.
5. Validate template inheritance after each app migration.
6. Do not delete legacy global templates until routing confirms they are unused.

## Phase 0 - Foundation Work

Required before app-specific work:

- Finalize `templates/base.html` block contract.
- Finalize shared sidebar and navbar behavior.
- Normalize Tailwind config and rebuild `static/css/output.css`.
- Create or finalize shared components for buttons, cards, alerts, badges, forms, tables, page headers, breadcrumbs, modals, empty states, pagination, and action buttons.
- Add a navigation data strategy using either a context processor or explicit include data.
- Create a template smoke-test checklist for each migrated app.

Priority: High

Estimated complexity: معقد

## App: frontend

### Current Problems

- Contains a second enhanced base template that competes with `templates/base.html`.
- Uses Bootstrap, custom CSS, custom grid system, custom theme system, and PWA/service-worker behavior in one large shell.
- Hard-codes many URL names that may not exist or may not belong to this app.
- Duplicates component ideas already present in global `templates/components/`.

### Required Changes

- Treat `frontend/templates/base/base_enhanced.html` as a source of patterns, not as a runtime app base.
- Extract useful pieces into global components:
  - Enhanced sidebar patterns
  - Page header
  - Stat cards
  - Form field
  - Data table
  - Modal
  - Help system, if still needed
- Retire or freeze `frontend/static/css/*` after equivalent Tailwind components exist.
- Move service-worker/PWA behavior into a separate documented decision; do not keep it inside the base template by default.

### Dependencies

- Global `base.html`
- Global component library
- Global navigation config
- Tailwind output

### Backend Impact

- Possible context processor cleanup for notifications, search, user menu, and dashboard counters.

### Refactor Priority

High

### Estimated Complexity

معقد

## App: accounts

### Current Problems

- Has two account base templates: `base_accounts.html` and `base_accounts_migration.html`.
- Login and access-denied pages may not follow the same shell contract as authenticated screens.
- Account home/dashboard is a high-traffic entry point, so inconsistency here affects the whole product.

### Required Changes

- Make `base_accounts_migration.html` a thin adapter over global `base.html`, then migrate children to global blocks.
- Keep login in an auth layout mode using global form, alert, button, and card components.
- Refactor:
  - `home.html`
  - `dashboard.html`
  - `edit_permissions.html`
  - `access_denied.html`
  - `login.html`
- Remove `base_accounts.html` only after confirming no template extends it.

### Dependencies

- Auth layout mode in `base.html`
- Shared form components
- Shared permission/status badges

### Backend Impact

- Low. May need explicit context variables: `show_sidebar`, `show_navbar`, `show_footer`, `active_app`.

### Refactor Priority

High

### Estimated Complexity

متوسط

## App: administrator

### Current Problems

- Owns a full Bootstrap-based admin shell with sidebar, navbar, inline CSS, jQuery, and automatic form class mutation.
- Audit templates depend on `administrator/base_admin.html`, increasing coupling.
- Permission and user-management screens likely contain dense tables/forms that need consistent design-system components.

### Required Changes

- Convert `administrator/base_admin.html` into an adapter over global `base.html`.
- Replace admin sidebar with shared sidebar section configured for administration.
- Migrate pages in batches:
  1. Dashboard and system settings
  2. Users and groups
  3. Permissions and modules
  4. Departments
  5. Database settings/setup
  6. Helper pages
- Replace Bootstrap form mutation script with shared form rendering.
- Move database setup JS to explicit page-level initialization.

### Dependencies

- Shared admin navigation section
- Shared table, form, badge, confirm-delete, and page-header components
- Audit app migration coordination

### Backend Impact

- Medium. Permission screens may need standardized context for active modules, breadcrumbs, and action buttons.

### Refactor Priority

High

### Estimated Complexity

معقد

## App: audit

### Current Problems

- Audit screens extend `administrator/base_admin.html`, so audit UI is blocked by administrator layout migration.
- Audit list/detail screens are security-sensitive and must remain readable and dense.

### Required Changes

- After administrator adapter exists, migrate `auditlog_list.html` and `auditlog_detail.html` to global `base.html`.
- Use shared table component with compact density.
- Use semantic badges for action type, severity, user, timestamp, and object.
- Add a clear filter/search toolbar if backend supports it.

### Dependencies

- Administrator adapter or completed administrator shell migration
- Shared table and badge components

### Backend Impact

- Low unless filters/pagination are standardized.

### Refactor Priority

Medium

### Estimated Complexity

Simple

## App: core

### Current Problems

- Uses both global `base.html` and `base/base_enhanced.html`.
- Monitoring and cache dashboards likely use custom dashboard card patterns.
- `core/base.html` creates another app-local base layer.

### Required Changes

- Convert `core/base.html` to a temporary adapter or remove if unused.
- Migrate cache and monitoring dashboards away from `base/base_enhanced.html`.
- Use shared stat cards, chart panels, and status badges.
- Standardize permissions dashboard with administrator permission components.

### Dependencies

- Frontend base deprecation
- Shared dashboard components
- Shared status badge component

### Backend Impact

- Low to medium depending on dashboard context shape.

### Refactor Priority

High

### Estimated Complexity

متوسط

## App: api

### Current Problems

- `base_api.html` exists but most API UI screens extend global `base.html`.
- API management screens need a consistent admin/security look.
- AI chat/data-analysis screens may have unique interactive layouts.

### Required Changes

- Remove or convert `base_api.html` into a thin adapter.
- Standardize key creation, provider forms, usage stats, and settings pages using shared form/table components.
- Use semantic risk/status components for API keys and provider health.
- Create a specialized chat panel component only if the AI chat page requires it.

### Dependencies

- Shared form/table/status components
- Admin/security navigation section

### Backend Impact

- Low. Usage stats may benefit from standardized pagination/filter context.

### Refactor Priority

Medium

### Estimated Complexity

متوسط

## App: notifications

### Current Problems

- Owns `base_notifications.html`.
- Notification styling likely differs from global alerts/toasts and navbar notification menu.
- Dashboard/list/detail/user notification pages duplicate notification UI concepts.

### Required Changes

- Convert `base_notifications.html` into an adapter over `base.html`.
- Align notification list and detail screens with shared notification item/status components.
- Integrate unread/read status badges with navbar notification count.
- Standardize empty states and pagination.

### Dependencies

- Global navbar notification menu
- Shared status badge, list item, empty state, and pagination components

### Backend Impact

- Medium if notification counts are centralized in a context processor.

### Refactor Priority

Medium

### Estimated Complexity

متوسط

## App: companies

### Current Problems

- Templates live globally under `templates/companies/` instead of app-local `companies/templates/companies/`.
- Uses global base but likely has inconsistent form/table/card markup.
- CRUD pages are straightforward but need shared action patterns.

### Required Changes

- Decide whether to keep global templates temporarily or move to app-local templates during a separate cleanup phase.
- Refactor company list/detail/form/add/delete to use shared page header, table, form, card, and confirm-delete components.
- Standardize action buttons and breadcrumbs.

### Dependencies

- Shared CRUD components
- Navigation section for companies/customers

### Backend Impact

- Low if template paths remain stable. Medium if moving templates requires view `template_name` updates.

### Refactor Priority

Low

### Estimated Complexity

Simple

## App: org

### Current Problems

- Templates live globally under `templates/org/` instead of app-local `org/templates/org/`.
- Branch, department, and job screens likely use basic but inconsistent CRUD markup.

### Required Changes

- Standardize branches, departments, and jobs using shared CRUD components.
- Use a single org navigation/breadcrumb pattern.
- Keep template paths stable until view template names are audited.

### Dependencies

- Shared CRUD components
- Administrator/org navigation relationship

### Backend Impact

- Low unless templates are moved into the app.

### Refactor Priority

Low

### Estimated Complexity

Simple

## App: apps.hr.employees

### Current Problems

- Mixed inheritance between global `base.html` and `employees/base.html`.
- Multiple list variants exist: `employee_list.html`, `modern_list.html`, `index.html`.
- Employee profile/detail/form screens likely use separate visual patterns.

### Required Changes

- Convert `employees/base.html` into an adapter, then migrate all children to global blocks.
- Choose one canonical employee list UI and mark other list templates as legacy.
- Standardize:
  - Employee list table/cards
  - Employee profile/detail page
  - Comprehensive edit form
  - Pickup points
  - Vehicles
  - Social insurance job titles
  - Reports
- Use shared avatars, status badges, table actions, and form sections.

### Dependencies

- HR navigation section
- Shared table, form, profile header, stat card, and action button components

### Backend Impact

- Medium. Duplicate list views/templates may require route-level decisions.

### Refactor Priority

High

### Estimated Complexity

معقد

## App: apps.hr.attendance

### Current Problems

- Mixed inheritance: `base.html`, `attendance/base_attendance.html`, and references to missing/ambiguous `attendance/base.html`.
- Has app-local CSS/JS.
- ZK device, attendance rules, reports, and attendance records are visually and behaviorally different surfaces.

### Required Changes

- Resolve missing `attendance/base.html` references before migration.
- Convert `base_attendance.html` into an adapter over global `base.html`.
- Migrate in batches:
  1. Dashboard/enhanced dashboard
  2. Attendance records and forms
  3. Rules
  4. Leave balance/mark attendance/profile
  5. ZK device screens
  6. Reports
- Keep app-specific JS only for device workflows and attendance interactions.
- Replace app CSS layout classes with shared components.

### Dependencies

- HR navigation
- Shared table, form, status badge, report filter, and device-status components

### Backend Impact

- Medium. Device screens may require explicit UI state context.

### Refactor Priority

High

### Estimated Complexity

معقد

## App: apps.hr.leaves

### Current Problems

- Mixed inheritance between `leaves/base.html` and global `base.html`.
- Global legacy templates also exist under `templates/leaves/`.
- Leave request/list/type/holiday/balance screens need consistent workflows.

### Required Changes

- Convert `leaves/base.html` into adapter.
- Audit global `templates/leaves/*` and decide whether they are active legacy routes.
- Standardize leave dashboard, request form, leave list, leave types, holidays, and balance report.
- Use shared status badges for pending/approved/rejected and shared date/filter components.

### Dependencies

- HR navigation
- Shared status badge, table, form, calendar/date input, and report components

### Backend Impact

- Low to medium if global legacy templates are still referenced by views.

### Refactor Priority

High

### Estimated Complexity

متوسط

## App: apps.hr.payroll

### Current Problems

- Mixed inheritance between `payrolls/base.html` and global `base.html`.
- Global legacy payroll dashboard also exists.
- Payroll screens need high readability and strong table/form consistency.

### Required Changes

- Convert `payrolls/base.html` into adapter.
- Standardize dashboard, payroll runs, payslips, salary list, reports, and payslip detail.
- Use shared financial amount formatting components where possible.
- Ensure print/export screens are not broken by global shell changes.

### Dependencies

- HR/finance navigation relationship
- Shared table, amount display, status badge, print layout, and report components

### Backend Impact

- Medium. Print/export flows may require layout mode flags.

### Refactor Priority

High

### Estimated Complexity

معقد

## App: apps.hr.evaluations

### Current Problems

- Mixed inheritance between `evaluations/base.html` and global `base.html`.
- Has app-local CSS/JS.
- Dashboard and modern dashboard coexist.

### Required Changes

- Convert `evaluations/base.html` into adapter.
- Choose canonical dashboard template.
- Standardize evaluation list, periods, reports, and performance comparison using shared chart/table/card components.
- Keep app JS only for charts or evaluation-specific interactions.

### Dependencies

- HR navigation
- Shared stat card, chart panel, table, and report filter components

### Backend Impact

- Low to medium depending on chart data format.

### Refactor Priority

Medium

### Estimated Complexity

متوسط

## App: apps.hr.training

### Current Problems

- Only `modern_dashboard.html` was found.
- UI likely bypasses a domain-specific base and extends global base directly.

### Required Changes

- Align dashboard with HR dashboard components.
- Add clear empty states/placeholders if module is incomplete.
- Ensure navigation exposes training only when routes are ready.

### Dependencies

- HR navigation
- Shared dashboard/stat components

### Backend Impact

- Low.

### Refactor Priority

Low

### Estimated Complexity

Simple

## App: apps.hr.insurance

### Current Problems

- Has templates but is not currently installed in `LOCAL_APPS`.
- Mixed inheritance between `insurance/base.html` and global `base.html`.

### Required Changes

- Confirm whether insurance is active before refactoring.
- If active, convert base to adapter and standardize dashboard screens.
- If inactive, document as dormant and avoid migration effort.

### Dependencies

- HR navigation
- Shared dashboard components

### Backend Impact

- Depends on whether app is activated.

### Refactor Priority

Low

### Estimated Complexity

Simple

## App: apps.hr.loans

### Current Problems

- Has one dashboard template but is not installed in `LOCAL_APPS`.

### Required Changes

- Confirm active/inactive status.
- If active, align dashboard with HR financial components.
- If inactive, leave untouched until module activation.

### Dependencies

- HR navigation

### Backend Impact

- Low unless activated.

### Refactor Priority

Low

### Estimated Complexity

Simple

## App: apps.inventory

### Current Problems

- Owns a large Bootstrap-based `base_inventory.html` with sidebar, inline CSS, Bootstrap imports, and custom JS.
- Has many CRUD/report screens and both app-local and global inventory JS.
- One supplier delete template extends global `base.html`, while most extend `base_inventory.html`.
- Inventory is a core operational module with high regression risk.

### Required Changes

- Convert `base_inventory.html` into a compatibility adapter over global `base.html`.
- Preserve inventory-specific sidebar items as navigation config, not custom layout.
- Migrate in batches:
  1. Dashboard and settings
  2. Products, categories, units
  3. Suppliers, customers, departments
  4. Invoices and invoice items
  5. Vouchers
  6. Product movements
  7. Reports
  8. Purchase request bridge screen
- Consolidate duplicate JS:
  - Keep `product_form.js` and `voucher_form.js` only if still required.
  - Review global `static/inventory/js/*` and remove obsolete filter loaders after migration.
- Replace inventory-specific `.card`, `.btn`, `.table`, `.sidebar` styles with shared components.

### Dependencies

- Shared dense table component
- Shared form sections
- Shared report filters
- Shared status badges
- Shared action buttons
- Inventory navigation config

### Backend Impact

- Medium. Some screens may need normalized context for filters, pagination, low-stock count, and active menu.

### Refactor Priority

High

### Estimated Complexity

معقد

## App: apps.procurement.purchase_orders

### Current Problems

- Owns `base_purchase_orders.html` and `base_purchase.html`.
- Template folder is capitalized as `Purchase_orders`, which is fragile across platforms and inconsistent with Django conventions.
- Uses global purchase-orders CSS/JS.
- Approval workflows need consistent state visualization.

### Required Changes

- Convert `base_purchase_orders.html` into adapter over global `base.html`.
- Decide whether to rename template namespace to lowercase `purchase_orders` in a separate compatibility-safe phase.
- Migrate:
  1. Dashboard
  2. Purchase request list/detail/form/item form/delete
  3. Approval form
  4. Pending/approved/rejected lists
  5. Vendors
  6. Reports
- Replace global `purchase_orders.css` with Tailwind components.
- Keep JS only for workflow-specific interactions.

### Dependencies

- Shared workflow/status badge component
- Shared table/action buttons
- Shared form components
- Inventory integration points

### Backend Impact

- Medium. Approval status, permissions, and inventory links may require stable context.

### Refactor Priority

High

### Estimated Complexity

معقد

## App: apps.projects.tasks

### Current Problems

- Owns `base_tasks.html`.
- Has both legacy and unified templates: `dashboard.html`, `unified_dashboard.html`, `task_list.html`, `unified_task_list.html`, etc.
- Task state, priority, owner, and due-date UI likely differs from meetings/project pages.

### Required Changes

- Convert `base_tasks.html` into adapter.
- Choose unified templates as canonical if routes support them.
- Standardize task list/detail/form/my tasks/completed tasks/analytics/reports.
- Use shared status badges, priority indicators, user chips, date badges, and action menus.

### Dependencies

- Projects navigation
- Shared table/list, badge, form, analytics card, and report components

### Backend Impact

- Medium because duplicate templates may map to different views.

### Refactor Priority

Medium

### Estimated Complexity

متوسط

## App: apps.projects.meetings

### Current Problems

- Owns `base_meetings.html`.
- Calendar, meeting detail, and meeting task pages likely have custom patterns.
- Needs consistency with tasks because both are projects-domain apps.

### Required Changes

- Convert `base_meetings.html` into adapter.
- Standardize meeting dashboard, list, detail, form, task detail, reports, and calendar.
- Use shared page header, cards, action buttons, and status badges.
- Keep calendar-specific styling isolated if required.

### Dependencies

- Projects navigation
- Shared calendar/list/form components or approved app-specific calendar CSS

### Backend Impact

- Low to medium for calendar data/context.

### Refactor Priority

Medium

### Estimated Complexity

متوسط

## App: apps.finance.banks

### Current Problems

- Only `bank_list.html` was found.
- Extends global `base.html`, so layout risk is low.
- Finance domain is underdeveloped in UI compared with other modules.

### Required Changes

- Standardize bank list with shared table and empty state.
- Add finance navigation only for confirmed active routes.
- Avoid creating a finance-specific base template.

### Dependencies

- Shared table and page-header components

### Backend Impact

- Low.

### Refactor Priority

Low

### Estimated Complexity

Simple

## App: apps.reports

### Current Problems

- Single enhanced dashboard extends global `base.html`.
- Reporting dashboards may duplicate cards/charts used elsewhere.

### Required Changes

- Standardize dashboard with shared stat grid, chart panel, filters, and empty states.
- Ensure report pages use a print/export layout mode if needed.

### Dependencies

- Shared dashboard/chart/report filter components

### Backend Impact

- Low to medium depending on chart/report data context.

### Refactor Priority

Medium

### Estimated Complexity

متوسط

## App: apps/administration/cars

### Current Problems

- Not installed in `LOCAL_APPS`, but has a substantial UI.
- Uses `cars/base.html`, `templates/base.html`, and mixed Windows-style template extends such as `cars\base.html`.
- Has app-local custom CSS.

### Required Changes

- Confirm whether this app is active or legacy before investing effort.
- Replace backslash template paths with forward slashes during implementation if active.
- Convert `cars/base.html` into adapter.
- Standardize car, employee, supplier, trip, route point, settings, reports, and average price screens.

### Dependencies

- Administration or fleet navigation section
- Shared CRUD/table/report components

### Backend Impact

- Medium if the app is activated because template path cleanup may expose hidden route issues.

### Refactor Priority

Low until activated; High if production-active outside `LOCAL_APPS`

### Estimated Complexity

متوسط

## App: apps/administration/assets

### Current Problems

- Discovered but not installed.
- No templates or static files found.

### Required Changes

- No UI refactor now.
- Add to future roadmap only after routes/templates exist.

### Dependencies

- None.

### Backend Impact

- None.

### Refactor Priority

Low

### Estimated Complexity

Simple

## App: apps/administration/tickets

### Current Problems

- Discovered but not installed.
- No templates or static files found.

### Required Changes

- No UI refactor now.
- If activated later, build from global base and shared components from day one.

### Dependencies

- None.

### Backend Impact

- None.

### Refactor Priority

Low

### Estimated Complexity

Simple

## App: apps.hr.disciplinary

### Current Problems

- Discovered but not installed.
- No templates/static files found.

### Required Changes

- No UI refactor now.
- Future implementation should use global HR navigation and shared CRUD components.

### Dependencies

- HR navigation if activated.

### Backend Impact

- None for UI refactor.

### Refactor Priority

Low

### Estimated Complexity

Simple

## App: apps.rbac

### Current Problems

- Discovered but not installed.
- No templates/static files found.
- Permission UI currently appears split across administrator, accounts, and core.

### Required Changes

- Do not create UI until architecture decision is made.
- If RBAC becomes the canonical permission app, migrate permission screens from administrator/accounts/core later.

### Dependencies

- Permission architecture decision

### Backend Impact

- Potentially high in future, but none for current UI plan.

### Refactor Priority

Low

### Estimated Complexity

معقد if activated

## App: apps.syssettings

### Current Problems

- Discovered but not installed.
- System settings UI currently lives in administrator and inventory.

### Required Changes

- Decide whether system settings should be centralized here.
- No UI refactor until that ownership decision is made.

### Dependencies

- Settings ownership decision

### Backend Impact

- Potentially high in future.

### Refactor Priority

Low

### Estimated Complexity

معقد if activated

## App: apps.workflow

### Current Problems

- Discovered but not installed.
- No templates/static files found.
- Workflow concepts appear in purchase approvals and tasks but are not centralized.

### Required Changes

- No UI refactor now.
- Future workflow screens should reuse shared status, timeline, approval-step, and action components.

### Dependencies

- Workflow architecture decision

### Backend Impact

- None for current UI plan.

### Refactor Priority

Low

### Estimated Complexity

متوسط if activated

## Safe Execution Order

### 1. Foundation and Design System

Refactor first:

- `templates/base.html`
- `templates/components/*`
- `tailwind.config.js`
- `static/css/tailwind.css`
- Global navigation/sidebar/navbar JS

Why:

- Every app migration depends on a stable shell and component contract.
- Without this, each app will continue inventing local fixes.

Risk:

- High, because the global base is widely used.

Mitigation:

- Preserve existing block names.
- Add new blocks without removing old ones.
- Smoke-test high-traffic pages after base changes.

### 2. Frontend Design System Consolidation

Refactor second:

- `frontend/templates/base/base_enhanced.html`
- `frontend/templates/components/*`
- `frontend/static/css/*`
- `frontend/static/js/*`

Why:

- It currently represents a parallel design system.
- Its useful parts should be merged before app migrations begin.

Risk:

- Medium to high because it hard-codes routes and layout behavior.

Mitigation:

- Extract components first.
- Do not switch app templates to `base_enhanced.html`.

### 3. Accounts

Why first app:

- It is the entry point after login.
- It already has a migration base extending global `base.html`.
- It validates auth layout, sidebar visibility flags, messages, and user menu.

### 4. Core

Why:

- It depends on both global and enhanced bases.
- Monitoring/cache dashboards validate dashboard components before business modules.

### 5. Administrator

Why:

- It is a dependency for audit and permission management.
- It contains many reusable admin patterns needed elsewhere.

### 6. Audit

Why:

- It currently depends on administrator base.
- It is small and can validate the migrated admin/security visual language.

### 7. Notifications

Why:

- Navbar notification behavior and notification pages should align before broad app rollout.

### 8. HR Core Apps

Recommended order:

1. Employees
2. Attendance
3. Leaves
4. Payroll
5. Evaluations
6. Training
7. Insurance/Loans only if active

Why:

- Employees is a foundational HR entity used by attendance, leaves, payroll, evaluations, and training.
- Attendance and payroll are complex and should benefit from components hardened during employees/leaves migration.

### 9. Inventory

Why:

- It is large and operationally critical.
- It should be migrated after table/form/report components are proven in HR and admin.

### 10. Procurement Purchase Orders

Why:

- It depends conceptually on inventory and approval workflow components.
- Status/approval UI should reuse components proven in inventory and tasks.

### 11. Projects

Recommended order:

1. Tasks
2. Meetings

Why:

- Tasks define shared project status and action patterns.
- Meetings can reuse those patterns for meeting tasks and reports.

### 12. Finance, Reports, Companies, Org

Recommended order:

1. Reports
2. Finance banks
3. Companies
4. Org

Why:

- These are smaller or already closer to global base inheritance.
- They are suitable after the main component system is stable.

### 13. Dormant Apps

Only refactor after activation decision:

- `apps/administration/cars`
- `apps/administration/assets`
- `apps/administration/tickets`
- `apps/hr/disciplinary`
- `apps/hr/insurance`
- `apps/hr/loans`
- `apps/rbac`
- `apps/syssettings`
- `apps/workflow`

## Final Migration Checklist Per App

Before marking any app complete:

- All active templates render without `TemplateDoesNotExist`.
- No active screen imports Bootstrap unless explicitly approved as a temporary exception.
- No active screen owns a full sidebar/navbar layout.
- App-local base is removed or documented as a temporary adapter.
- Tables use shared responsive table patterns.
- Forms use shared form rendering.
- Delete/confirm flows use shared confirm-delete pattern.
- Empty states exist for list screens.
- Mobile width works without overlapping sidebar/content.
- RTL layout is preserved.
- Tailwind build includes the migrated templates.
- App-specific CSS/JS is reduced to necessary behavior only.
