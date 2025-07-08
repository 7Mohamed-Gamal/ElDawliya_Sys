# HRMS Navigation Structure & URL Configuration
## ElDawliya International - Complete Navigation Guide

### Overview
This document outlines the comprehensive navigation structure for the HRMS system, including all URL patterns, view functions, and sidebar navigation organization.

## 🗂️ **Sidebar Navigation Structure**

### **1. Dashboard**
- **Main Dashboard** - `Hr:dashboard`
  - Overview of all HR metrics and quick access to key functions

### **2. Organizational Structure** 🏢

#### **Company Management**
- **Company List** - `Hr:companies:list`
- **Add Company** - `Hr:companies:create`
- **Company Details** - `Hr:companies:detail`
- **Edit Company** - `Hr:companies:edit`
- **Company Dashboard** - `Hr:companies:dashboard`

#### **Branch Management**
- **Branch List** - `Hr:branches:list`
- **Add Branch** - `Hr:branches:create`
- **Branch Details** - `Hr:branches:detail`
- **Edit Branch** - `Hr:branches:edit`
- **Branches by Company** - `Hr:branches:by_company`

#### **Department Management (Enhanced)**
- **Department List** - `Hr:departments_new:list`
- **Add Department** - `Hr:departments_new:create`
- **Department Details** - `Hr:departments_new:detail`
- **Department Hierarchy** - `Hr:departments_new:hierarchy`
- **Departments by Branch** - `Hr:departments_new:by_branch`
- **Legacy Departments** - `Hr:departments:department_list`

#### **Job Position Management**
- **Job Position List** - `Hr:job_positions:list`
- **Add Job Position** - `Hr:job_positions:create`
- **Position Details** - `Hr:job_positions:detail`
- **Positions by Department** - `Hr:job_positions:by_department`
- **Legacy Jobs** - `Hr:jobs:job_list`

### **3. Employee Management** 👥

#### **Core Employee Management**
- **Employee List** - `Hr:employees:list`
- **Add Employee** - `Hr:employees:create`
- **Employee Details** - `Hr:employees:detail`
- **Advanced Search** - `Hr:employees:employee_search`

#### **Employee Documents**
- **All Documents** - `Hr:employee_documents:list`
- **Add Document** - `Hr:employee_documents:create`
- **Expiring Documents** - `Hr:employee_documents:expiring`
- **Document Verification** - `Hr:employee_documents:verify`
- **Documents by Employee** - `Hr:employee_documents:by_employee`

#### **Emergency Contacts**
- **All Emergency Contacts** - `Hr:emergency_contacts:list`
- **Add Emergency Contact** - `Hr:emergency_contacts:create`
- **Contacts by Employee** - `Hr:emergency_contacts:by_employee`

#### **Training & Development**
- **All Training Records** - `Hr:employee_training:list`
- **Add Training** - `Hr:employee_training:create`
- **Training Calendar** - `Hr:employee_training:calendar`
- **Complete Training** - `Hr:employee_training:complete`
- **Training Certificate** - `Hr:employee_training:certificate`

### **4. Leave Management** 📅

#### **Leave Configuration**
- **Leave Types** - `Hr:leave_types:list`
- **Leave Policies** - `Hr:leave_policies:list`
- **Policy Applicable Employees** - `Hr:leave_policies:applicable_employees`

#### **Leave Requests**
- **All Leave Requests** - `Hr:leave_requests:list`
- **Pending Requests** - `Hr:leave_requests:pending`
- **Leave Calendar** - `Hr:leave_requests:calendar`
- **Approve/Reject Requests** - `Hr:leave_requests:approve/reject`

#### **Leave Balance Management**
- **Leave Balances** - `Hr:leave_balances:list`
- **Employee Balance** - `Hr:leave_balances:employee_balance`
- **Adjust Balance** - `Hr:leave_balances:adjust`
- **Encash Balance** - `Hr:leave_balances:encash`
- **Balance Report** - `Hr:leave_balances:report`

### **5. Attendance & Time Tracking** ⏰

#### **Work Shift Management**
- **Work Shifts List** - `Hr:work_shifts:list`
- **Add Work Shift** - `Hr:work_shifts:create`
- **Shift Employees** - `Hr:work_shifts:employees`

#### **Attendance Machines (Enhanced)**
- **Machine List** - `Hr:attendance_machines_new:list`
- **Add Machine** - `Hr:attendance_machines_new:create`
- **Test Connection** - `Hr:attendance_machines_new:test_connection`
- **Sync Users** - `Hr:attendance_machines_new:sync_users`
- **Fetch Records** - `Hr:attendance_machines_new:fetch_records`

#### **Attendance Records**
- **Attendance Records** - `Hr:attendance:attendance_record_list`
- **Attendance Summary** - `Hr:attendance:attendance_summary_list`
- **Legacy ZK Devices** - `Hr:attendance:zk_device_connection`
- **Attendance Rules** - `Hr:attendance:attendance_rule_list`

### **6. Payroll Management** 💰

#### **Salary Components**
- **Salary Components** - `Hr:salary_components:list`
- **Add Component** - `Hr:salary_components:create`
- **Component Details** - `Hr:salary_components:detail`
- **Toggle Component Status** - `Hr:salary_components:toggle_status`

#### **Payroll Processing**
- **Calculate Payroll** - `Hr:salaries:payroll_calculate`
- **Payroll Periods** - `Hr:salaries:payroll_period_list`
- **Salary Items** - `Hr:salaries:salary_item_list`

### **7. Reports & Analytics** 📊

#### **Reports**
- **All Reports** - `Hr:reports:report_list`
- **Monthly Salary Report** - `Hr:reports:monthly_salary_report`
- **Employee Report** - `Hr:reports:employee_report`
- **Leave Balance Report** - `Hr:leave_balances:report`

#### **Analytics**
- **Analytics Dashboard** - `Hr:analytics:analytics_dashboard`

### **8. System Management** ⚙️

#### **Organization Tools**
- **Organization Chart** - `Hr:org_chart:org_chart`
- **Notes** - `Hr:notes:employee_notes_dashboard`
- **Alerts** - `Hr:alerts:alert_list`

## 🔗 **URL Pattern Structure**

### **Core Patterns**
```python
# Company Management
company_patterns = [
    path('', company_views.company_list, name='list'),
    path('create/', company_views.company_create, name='create'),
    path('<int:company_id>/', company_views.company_detail, name='detail'),
    path('<int:company_id>/edit/', company_views.company_edit, name='edit'),
    path('<int:company_id>/delete/', company_views.company_delete, name='delete'),
    path('<int:company_id>/toggle-status/', company_views.company_toggle_status, name='toggle_status'),
    path('<int:company_id>/dashboard/', company_views.company_dashboard, name='dashboard'),
    path('export/', company_views.company_export, name='export'),
    path('ajax/search/', company_views.company_search_ajax, name='search_ajax'),
    path('<int:company_id>/ajax/stats/', company_views.company_stats_ajax, name='stats_ajax'),
]
```

### **Leave Management Patterns**
```python
# Leave Request Management
leave_request_patterns = [
    path('', leave_request_views.leave_request_list, name='list'),
    path('create/', leave_request_views.leave_request_create, name='create'),
    path('<int:request_id>/', leave_request_views.leave_request_detail, name='detail'),
    path('<int:request_id>/approve/', leave_request_views.leave_request_approve, name='approve'),
    path('<int:request_id>/reject/', leave_request_views.leave_request_reject, name='reject'),
    path('pending/', leave_request_views.pending_leave_requests, name='pending'),
    path('calendar/', leave_request_views.leave_calendar, name='calendar'),
]
```

### **Attendance Patterns**
```python
# Work Shift Management
work_shift_patterns = [
    path('', work_shift_views.work_shift_list, name='list'),
    path('create/', work_shift_views.work_shift_create, name='create'),
    path('<int:shift_id>/', work_shift_views.work_shift_detail, name='detail'),
    path('<int:shift_id>/employees/', work_shift_views.shift_employees, name='employees'),
]
```

## 📁 **View Structure Organization**

### **Directory Structure**
```
Hr/views/
├── core/                    # Organizational structure views
│   ├── company_views.py     # Company management
│   ├── branch_views.py      # Branch management
│   ├── department_views_new.py # Enhanced departments
│   └── job_position_views.py # Job positions
├── employee/                # Employee management views
│   ├── employee_views_new.py # Enhanced employee management
│   ├── employee_document_views.py # Document management
│   ├── employee_emergency_contact_views.py # Emergency contacts
│   └── employee_training_views.py # Training management
├── leave/                   # Leave management views
│   ├── leave_type_views.py  # Leave types
│   ├── leave_policy_views.py # Leave policies
│   ├── leave_request_views.py # Leave requests
│   └── leave_balance_views.py # Leave balances
├── attendance/              # Attendance views
│   ├── work_shift_views.py  # Work shifts
│   ├── attendance_machine_views_new.py # Enhanced machines
│   ├── attendance_record_views_new.py # Records
│   └── attendance_summary_views_new.py # Summaries
└── payroll/                 # Payroll views
    ├── salary_component_views.py # Salary components
    ├── employee_salary_structure_views.py # Salary structures
    └── payroll_entry_views_new.py # Payroll entries
```

## 🎯 **Key Features Accessible**

### **✅ Fully Accessible Features**
1. **Company Management** - Complete CRUD operations
2. **Branch Management** - Multi-location support
3. **Department Hierarchy** - Enhanced department structure
4. **Job Position Management** - Detailed job descriptions
5. **Employee Documents** - Document lifecycle management
6. **Emergency Contacts** - Comprehensive contact management
7. **Training Management** - Training lifecycle and certificates
8. **Leave Types & Policies** - Flexible leave configuration
9. **Leave Requests** - Complete approval workflow
10. **Leave Balance** - Real-time balance tracking
11. **Work Shifts** - Flexible shift management
12. **Attendance Machines** - ZK device integration
13. **Salary Components** - Advanced payroll components

### **🔄 Legacy Features (Backward Compatible)**
1. **Employee Management** - Original employee views
2. **Department Management** - Original department views
3. **Job Management** - Original job views
4. **Attendance System** - Original attendance views
5. **Payroll System** - Original payroll views

## 🚀 **Navigation Benefits**

### **User Experience**
- **Logical Organization** - Features grouped by business function
- **Intuitive Icons** - Clear visual indicators for each section
- **Breadcrumb Navigation** - Easy navigation tracking
- **Quick Access** - Direct links to most-used features

### **Administrative Efficiency**
- **Comprehensive Coverage** - All 25+ models accessible
- **Workflow Support** - End-to-end process navigation
- **Reporting Integration** - Easy access to reports and analytics
- **System Management** - Administrative tools readily available

### **Technical Architecture**
- **Modular Structure** - Organized by business domain
- **Scalable Design** - Easy to add new modules
- **Backward Compatibility** - Legacy features preserved
- **RESTful URLs** - Clean, predictable URL patterns

---
*Last Updated: 2025-01-08*
*Navigation Structure: Complete - All HRMS modules accessible*
