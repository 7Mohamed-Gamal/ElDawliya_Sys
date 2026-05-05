# Project Structure UI Analysis

This document captures the UI-related structure of the Django project before any refactor work. It is based on a source scan excluding `venv`, `node_modules`, `staticfiles`, `media`, and `logs`.

## Executive Summary

- Django project root: `ElDawliya_sys`
- Global template directory: `templates/`
- App template discovery: enabled through `APP_DIRS=True`
- Global static directory: `static/`
- Static collection output: `staticfiles/`
- Frontend/design-system app: `frontend`
- Tailwind entrypoint: `static/css/tailwind.css`
- Tailwind build output: `static/css/output.css`
- Tailwind config: `tailwind.config.js`
- UI templates found: 301 HTML files
- CSS/JS source assets found: 63 files
- Django `apps.py` modules found: 34

## Installed Django Apps

The following local apps are registered in `ElDawliya_sys/settings/base.py`.

| App | Installed Path | UI Surface |
| --- | --- | --- |
| API | `api.apps.ApiConfig` | API management screens and AI settings |
| Accounts | `accounts` | Login, home, permissions, account dashboard |
| Administrator | `administrator` | Admin dashboard, users, groups, modules, database settings |
| Notifications | `notifications` | Notification dashboard, list, detail |
| Core | `core.apps.CoreConfig` | Monitoring, cache, permissions dashboard |
| Audit | `audit.apps.AuditConfig` | Audit log list/detail |
| Companies | `companies.apps.CompaniesConfig` | Uses global `templates/companies/` |
| Org | `org.apps.OrgConfig` | Uses global `templates/org/` |
| Frontend | `frontend` | Existing enhanced base and component templates |
| HR | `apps.hr.apps.HrConfig` | Domain namespace only |
| Attendance | `apps.hr.attendance.apps.AttendanceConfig` | Attendance dashboards, devices, rules, reports |
| Employees | `apps.hr.employees.apps.EmployeesConfig` | Employee list/detail/forms/profile |
| Leaves | `apps.hr.leaves.apps.LeavesConfig` | Leave dashboard, requests, holidays, balances |
| Evaluations | `apps.hr.evaluations.apps.EvaluationsConfig` | Evaluation dashboards, reports, periods |
| Payroll | `apps.hr.payroll.apps.PayrollsConfig` | Payroll dashboards, payslips, reports |
| Training | `apps.hr.training.apps.TrainingConfig` | Modern dashboard only |
| Inventory | `apps.inventory.apps.InventoryConfig` | Large CRUD/reporting UI |
| Purchase Orders | `apps.procurement.purchase_orders.apps.PurchaseOrdersConfig` | Procurement requests, approvals, vendors, reports |
| Tasks | `apps.projects.tasks.apps.TasksConfig` | Task dashboards, lists, forms, analytics |
| Meetings | `apps.projects.meetings.apps.MeetingsConfig` | Meeting calendar, CRUD, reports |
| Banks | `apps.finance.banks.apps.BanksConfig` | Bank list |
| Reports | `apps.reports.apps.ReportsConfig` | Enhanced reports dashboard |

## Discovered But Not Installed Apps

These have `apps.py` files but are not currently listed in `LOCAL_APPS`. They should be treated as dormant or future modules until confirmed.

| App | Path | UI Surface |
| --- | --- | --- |
| Assets | `apps/administration/assets` | No templates/static found in source scan |
| Cars | `apps/administration/cars` | Full CRUD/reporting UI, not installed |
| Tickets | `apps/administration/tickets` | No templates/static found |
| Finance namespace | `apps/finance` | Namespace only |
| Disciplinary | `apps/hr/disciplinary` | No templates/static found |
| Insurance | `apps/hr/insurance` | Dashboard templates exist, not installed |
| Loans | `apps/hr/loans` | Dashboard template exists, not installed |
| Procurement namespace | `apps/procurement` | Namespace only |
| Projects namespace | `apps/projects` | Namespace only |
| RBAC | `apps/rbac` | No templates/static found |
| Syssettings | `apps/syssettings` | No templates/static found |
| Workflow | `apps/workflow` | No templates/static found |

## Global Templates

Global templates under `templates/` include:

- `templates/base.html`
- `templates/home_dashboard.html`
- `templates/ui_demo.html`
- `templates/admin/base_site.html`
- `templates/admin/index.html`
- `templates/components/...`
- `templates/errors/403.html`, `404.html`, `500.html`
- Domain folders: `attendance`, `companies`, `employees`, `evaluations`, `hr`, `insurance`, `inventory`, `leaves`, `org`, `payrolls`, `reporting`

Important finding:

- `templates/base.html` is the primary Tailwind-oriented layout and includes sidebar/navbar components.
- The template starts with a comment showing `{% extends 'base.html' %}` as usage guidance. It is inside a Django comment, not an executable self-extension.
- Global component templates already exist and should become the canonical shared component library.

## App Template Inventory

### `accounts`

Templates:

- `accounts/access_denied.html`
- `accounts/base_accounts.html`
- `accounts/base_accounts_migration.html`
- `accounts/dashboard.html`
- `accounts/edit_permissions.html`
- `accounts/home.html`
- `accounts/login.html`

Base usage:

- Most migrated screens extend `accounts/base_accounts_migration.html`.
- `accounts/base_accounts_migration.html` extends global `base.html`.
- `login.html` and `access_denied.html` need manual review because they do not follow the same inheritance pattern in the scan output.

Static files:

- No app-local static files found.

### `administrator`

Templates:

- `administrator/base_admin.html`
- Dashboard, database settings/setup, departments, groups, modules, permissions, users, helper screens.

Base usage:

- All administrator screens extend `administrator/base_admin.html`.
- `audit` also extends `administrator/base_admin.html`.

Static files:

- `administrator/static/administrator/js/db_setup.js`

### `api`

Templates:

- `api/base_api.html`
- `api/dashboard.html`
- `api/create_key.html`
- `api/usage_stats.html`
- `api/ai_settings.html`
- `api/add_ai_config.html`
- `api/edit_ai_config.html`
- `api/ai_chat.html`
- `api/data_analysis.html`

Base usage:

- Most templates extend global `base.html`.
- `base_api.html` exists but appears underused.

Static files:

- No app-local static files found.

### `apps/administration/cars`

Templates:

- `cars/base.html`
- `templates/base.html`
- Cars, employees, suppliers, trips, route points, settings, reports, average price.

Base usage:

- Templates use both `cars/base.html` and mixed slash styles such as `cars\base.html`.
- `cars/base.html` extends global `base.html`.

Static files:

- `apps/administration/cars/static/css/custom.css`

### `apps/finance/banks`

Templates:

- `banks/bank_list.html`

Base usage:

- Extends global `base.html`.

Static files:

- No app-local static files found.

### `apps/hr/attendance`

Templates:

- `attendance/base_attendance.html`
- `attendance/dashboard.html`
- `attendance/enhanced_dashboard.html`
- Attendance records/forms/lists
- Leave balance list
- Rules screens
- ZK device screens
- Reports/profile/mark attendance

Base usage:

- Mixed inheritance: `base.html`, `attendance/base_attendance.html`, and references to `attendance/base.html`.
- `attendance/base.html` was not found in the app template inventory, so those references require validation.

Static files:

- `attendance/css/attendance.css`
- `attendance/js/attendance.js`

### `apps/hr/employees`

Templates:

- `employees/base.html`
- `employees/index.html`
- `employees/modern_list.html`
- Employee list/detail/profile/form/comprehensive edit
- Pickup points, vehicles, social insurance job titles, reports

Base usage:

- Mixed inheritance: direct global `base.html` and `employees/base.html`.
- `employees/base.html` extends global `base.html`.

Static files:

- No app-local static files found.

### `apps/hr/evaluations`

Templates:

- `evaluations/base.html`
- `evaluations/dashboard.html`
- `evaluations/modern_dashboard.html`
- `evaluations/evaluation_list.html`
- `evaluations/performance_comparison.html`
- `evaluations/periods.html`
- `evaluations/reports.html`

Base usage:

- Mixed inheritance: `evaluations/base.html` and global `base.html`.

Static files:

- `evaluations/css/evaluations.css`
- `evaluations/js/evaluations.js`

### `apps/hr/insurance`

Templates:

- `insurance/base.html`
- `insurance/dashboard.html`
- `insurance/modern_dashboard.html`

Base usage:

- Mixed inheritance: `insurance/base.html` and global `base.html`.

Static files:

- No app-local static files found.

### `apps/hr/leaves`

Templates:

- `leaves/base.html`
- `leaves/dashboard.html`
- `leaves/modern_dashboard.html`
- `leaves/leave_list.html`
- `leaves/leave_form.html`
- `leaves/leave_request_form.html`
- `leaves/leave_types.html`
- `leaves/holidays.html`
- `leaves/balance_report.html`

Base usage:

- Mixed inheritance: `leaves/base.html` and global `base.html`.
- Global templates also contain legacy `templates/leaves/*`.

Static files:

- `leaves/css/leaves.css`
- `leaves/js/leaves.js`

### `apps/hr/loans`

Templates:

- `loans/modern_dashboard.html`

Base usage:

- Extends global `base.html`.

Static files:

- No app-local static files found.

### `apps/hr/payroll`

Templates:

- `payrolls/base.html`
- `payrolls/dashboard.html`
- `payrolls/modern_payslip_detail.html`
- `payrolls/payroll_runs.html`
- `payrolls/payslips.html`
- `payrolls/reports.html`
- `payrolls/salary_list.html`

Base usage:

- Mixed inheritance: `payrolls/base.html` and global `base.html`.
- Global templates also contain legacy `templates/payrolls/dashboard.html`.

Static files:

- `payrolls/css/payrolls.css`
- `payrolls/js/payrolls.js`

### `apps/hr/training`

Templates:

- `training/modern_dashboard.html`

Base usage:

- Extends global `base.html`.

Static files:

- No app-local static files found.

### `apps/inventory`

Templates:

- `inventory/base_inventory.html`
- Inventory dashboards
- Product/category/unit/supplier/customer/department CRUD
- Invoice/invoice item CRUD
- Voucher CRUD
- Product movements
- Stock, movement, voucher, daily reports
- Settings/system settings
- Include partials: `action_buttons.html`, `filter_scripts.html`

Base usage:

- Nearly all screens extend `inventory/base_inventory.html`.
- One supplier delete screen extends global `base.html`.
- A legacy global `templates/inventory/product_form.html` also extends `inventory/base_inventory.html`.

Static files:

- `inventory/js/product_form.js`
- `inventory/js/voucher_form.js`
- Additional global inventory scripts exist under `static/inventory/js/`.

### `apps/procurement/purchase_orders`

Templates:

- `Purchase_orders/base_purchase_orders.html`
- `Purchase_orders/base_purchase.html`
- Dashboard, request list/detail/form/delete, approval form, approved/pending/rejected lists, reports, vendors.
- Include partial: `Purchase_orders/includes/action_buttons.html`

Base usage:

- Most screens extend `Purchase_orders/base_purchase_orders.html`.
- Template folder uses capitalized `Purchase_orders`, which increases portability risk.

Static files:

- Global assets: `static/css/purchase_orders.css`, `static/js/purchase_orders.js`

### `apps/projects/meetings`

Templates:

- `meetings/base_meetings.html`
- Dashboard, calendar, meeting list/detail/form, meeting task detail, reports.
- Include partial: `meetings/includes/action_buttons.html`

Base usage:

- All screens extend `meetings/base_meetings.html`.

Static files:

- No app-local static files found.

### `apps/projects/tasks`

Templates:

- `tasks/base_tasks.html`
- Dashboard, unified dashboard, task list/detail/form, unified list/detail, my tasks, completed tasks, analytics, reports.

Base usage:

- All screens extend `tasks/base_tasks.html`.

Static files:

- No app-local static files found.

### `apps/reports`

Templates:

- `reports/enhanced_dashboard.html`

Base usage:

- Extends global `base.html`.

Static files:

- No app-local static files found.

### `audit`

Templates:

- `audit/auditlog_list.html`
- `audit/auditlog_detail.html`

Base usage:

- Extends `administrator/base_admin.html`.

Static files:

- No app-local static files found.

### `companies`

Templates:

- Templates are currently in global `templates/companies/`, not app-local `companies/templates/companies/`.
- Company list/detail/form/add/delete.

Base usage:

- Extends global `base.html`.

Static files:

- No app-local static files found.

### `core`

Templates:

- `core/base.html`
- `core/cache_dashboard.html`
- `core/monitoring_dashboard.html`
- `core/permissions/dashboard.html`

Base usage:

- Mixed inheritance: global `base.html` and `base/base_enhanced.html`.

Static files:

- No app-local static files found.

### `frontend`

Templates:

- `base/base_enhanced.html`
- `components/data_table.html`
- `components/form_field.html`
- `components/help_system.html`
- `components/modal.html`
- `components/stats_card.html`
- `pages/dashboard.html`

Static files:

- Design-system CSS: `base-enhanced.css`, `components.css`, `design-system.css`, `grid-system.css`, `theme-system.css`, `permissions.css`, `help-system.css`, `performance-optimized.css`
- JS: `components.js`, `theme-system.js`, `permissions.js`, `help-system.js`, `image-optimizer.js`, `performance-optimizer.js`, `sw.js`

Important finding:

- This app contains a second, Bootstrap-heavy enhanced design system separate from global `templates/base.html`.

### `notifications`

Templates:

- `notifications/base_notifications.html`
- `notifications/dashboard.html`
- `notifications/list.html`
- `notifications/detail.html`
- `notifications/user_notifications.html`

Base usage:

- All notification screens extend `notifications/base_notifications.html`.

Static files:

- No app-local static files found.

### `org`

Templates:

- Templates are currently in global `templates/org/`, not app-local `org/templates/org/`.
- Branch, department, and job list/detail/add/edit screens.

Base usage:

- Extends global `base.html`.

Static files:

- No app-local static files found.

## Base Templates Found

These templates define or behave like app-level layout roots:

- `templates/base.html`
- `frontend/templates/base/base_enhanced.html`
- `accounts/templates/accounts/base_accounts.html`
- `accounts/templates/accounts/base_accounts_migration.html`
- `administrator/templates/administrator/base_admin.html`
- `api/templates/api/base_api.html`
- `apps/administration/cars/templates/cars/base.html`
- `apps/administration/cars/templates/base.html`
- `apps/hr/attendance/templates/attendance/base_attendance.html`
- `apps/hr/employees/templates/employees/base.html`
- `apps/hr/evaluations/templates/evaluations/base.html`
- `apps/hr/insurance/templates/insurance/base.html`
- `apps/hr/leaves/templates/leaves/base.html`
- `apps/hr/payroll/templates/payrolls/base.html`
- `apps/inventory/templates/inventory/base_inventory.html`
- `apps/procurement/purchase_orders/templates/Purchase_orders/base_purchase_orders.html`
- `apps/procurement/purchase_orders/templates/Purchase_orders/base_purchase.html`
- `apps/projects/meetings/templates/meetings/base_meetings.html`
- `apps/projects/tasks/templates/tasks/base_tasks.html`
- `core/templates/core/base.html`
- `notifications/templates/notifications/base_notifications.html`
- `templates/admin/base_site.html`

## Static Asset Inventory

### Global Static Assets

Major global CSS:

- `static/css/tailwind.css`
- `static/css/output.css`
- `static/css/style.css`
- `static/css/style_updated.css`
- `static/css/style_inventory.css`
- `static/css/purchase_orders.css`
- `static/css/employee_list.css`
- `static/css/modern.css`
- `static/css/rtl.css`
- `static/css/theme-toggle.css`
- `static/css/zk_device_connection.css`
- `static/hr_ui_ux_redesign/style.css`

Major global JS:

- `static/js/main.js`
- `static/js/eldawliya.js`
- `static/js/navigation.js`
- `static/js/components.js`
- `static/js/global-search.js`
- `static/js/enhanced-search.js`
- `static/js/theme-toggle.js`
- `static/js/purchase_orders.js`
- `static/js/script_inventory.js`
- `static/js/employee_list.js`
- `static/js/zk_device_connection.js`

Inventory-specific global JS:

- `static/inventory/js/api_patch.js`
- `static/inventory/js/auto_loader.js`
- `static/inventory/js/direct_filter.js`
- `static/inventory/js/filter_installer.js`
- `static/inventory/js/filter_script_loader.js`
- `static/inventory/js/product_search_enhanced.js`
- `static/inventory/js/standalone_filter.js`
- `static/inventory/js/voucher_filter_loader.js`
- `static/inventory/js/voucher_form.js`
- `static/inventory/js/voucher_form_enhancer.js`

### App-Local Static Assets

- `administrator/static/administrator/js/db_setup.js`
- `apps/administration/cars/static/css/custom.css`
- `apps/hr/attendance/static/attendance/css/attendance.css`
- `apps/hr/attendance/static/attendance/js/attendance.js`
- `apps/hr/evaluations/static/evaluations/css/evaluations.css`
- `apps/hr/evaluations/static/evaluations/js/evaluations.js`
- `apps/hr/leaves/static/leaves/css/leaves.css`
- `apps/hr/leaves/static/leaves/js/leaves.js`
- `apps/hr/payroll/static/payrolls/css/payrolls.css`
- `apps/hr/payroll/static/payrolls/js/payrolls.js`
- `apps/inventory/static/inventory/js/product_form.js`
- `apps/inventory/static/inventory/js/voucher_form.js`
- `frontend/static/css/*`
- `frontend/static/js/*`

## UI Architecture Risks

1. Multiple base templates create inconsistent navigation, spacing, typography, and responsive behavior.
2. Bootstrap, Tailwind, inline CSS, and custom CSS are mixed in the same system.
3. Several app-level base templates define their own sidebar and navbar rather than using shared components.
4. The `frontend` design system duplicates concepts already present in `templates/components/`.
5. Some app template references use Windows backslashes, e.g. `cars\base.html`; Django template paths should use forward slashes.
6. Some templates reference missing or ambiguous bases, e.g. `attendance/base.html`.
7. Global legacy templates duplicate app templates for HR, inventory, companies, org, and payroll.
8. Static files are split across app-local static folders, global static folders, and frontend static folders with overlapping responsibilities.

## Refactor Implications

- The migration should preserve existing URL/view behavior and only change template inheritance after the global layout contract is stable.
- `templates/base.html` should become the only runtime application base.
- App-local base templates should be converted into thin compatibility adapters, then deleted only after all child templates are migrated.
- `frontend/templates/base/base_enhanced.html` should not remain a parallel application base; extract reusable ideas/components into the global component system.
- Tailwind should become the primary styling system for application screens. Bootstrap usage should be frozen, then removed app-by-app.
