# HR Application File Cleanup Plan

## Files to Remove (Duplicates and Unnecessary)

### Base Templates (Keep only one standardized version)
- `Hr/templates/Hr/base.html` - Remove (older version)
- `Hr/templates/Hr/base_hr_modern.html` - Remove (will be replaced with tasks-style)
- Keep: `Hr/templates/Hr/base_hr.html` - Will be updated to match tasks design

### Dashboard Templates (Consolidate)
- `Hr/templates/Hr/dashboard_simple.html` - Remove (duplicate)
- `Hr/templates/Hr/dashboard_temp.html` - Remove (temporary file)
- Keep: `Hr/templates/Hr/dashboard.html` - Main dashboard

### Employee Templates (Remove duplicates)
- `Hr/templates/Hr/employee_form_new.html` - Remove (duplicate in employees folder)
- `Hr/templates/Hr/employees/employee_form_new.html` - Remove (duplicate)
- `Hr/templates/Hr/employees/employee_detail_view.html` - Remove (duplicate)
- `Hr/templates/Hr/employees/employee_search_demo.html` - Remove (demo file)
- `Hr/templates/Hr/employees/under_construction.html` - Remove (use global one)

### Payroll Templates (Remove duplicates)
- `Hr/templates/Hr/payrolls/` - Entire folder (duplicate of payroll/)
- Keep: `Hr/templates/Hr/payroll/` - Main payroll templates

### New Module Templates (Remove incomplete implementations)
- `Hr/templates/Hr/new_attendance/` - Remove (incomplete)
- `Hr/templates/Hr/new_employee/` - Remove (incomplete)  
- `Hr/templates/Hr/new_leave/` - Remove (incomplete)

### Unused/Placeholder Templates
- `Hr/templates/Hr/simple_list.html` - Remove (generic placeholder)
- `Hr/templates/Hr/update_data.html` - Remove (utility template)

### Static Files (Check for duplicates)
- Review CSS files for consolidation opportunities
- Review JS files for consolidation opportunities

## Files to Keep and Update

### Core Templates
- `Hr/templates/Hr/base_hr.html` - Update to match tasks design
- `Hr/templates/Hr/dashboard.html` - Update styling
- `Hr/templates/Hr/under_construction.html` - Keep for placeholder pages

### Functional Templates
- All templates in working modules (employees, departments, jobs, etc.)
- Report templates
- Form templates that are actively used

## Backup Strategy
1. Create backup of entire Hr/templates folder before cleanup
2. Document all removed files in this plan
3. Test functionality after each cleanup phase

## Cleanup Phases
1. Phase 1: Remove obvious duplicates and temp files
2. Phase 2: Consolidate base templates
3. Phase 3: Update remaining templates to match tasks design
4. Phase 4: Test all functionality

## Risk Assessment
- Low Risk: Removing temp files, demo files, obvious duplicates
- Medium Risk: Consolidating base templates
- High Risk: Removing functional templates (requires testing)

## Testing Required After Cleanup
- Dashboard loads correctly
- Employee management functions work
- Navigation works properly
- All forms render correctly
- Reports generate successfully
