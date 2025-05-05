from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json

from Hr.models.employee_model import Employee

@login_required
def org_chart(request):
    """عرض الهيكل التنظيمي للشركة"""
    # Get all employees
    employees = Employee.objects.filter(working_condition='سارى').select_related('department')
    
    # Build the organizational chart data
    org_data = build_org_chart(employees)
    
    context = {
        'org_data': json.dumps(org_data),
        'title': 'الهيكل التنظيمي للشركة'
    }
    
    return render(request, 'Hr/org_chart/index.html', context)

def build_org_chart(employees):
    """بناء بيانات الهيكل التنظيمي"""
    # Create a dictionary of employees by ID for quick lookup
    employees_dict = {emp.emp_id: emp for emp in employees}
    
    # Find the root nodes (employees without a direct manager or with a manager not in the company)
    root_employees = [emp for emp in employees if not emp.direct_manager_id or emp.direct_manager_id not in employees_dict]
    
    # Build the chart recursively
    org_data = []
    
    for emp in root_employees:
        org_data.append(build_employee_node(emp, employees_dict))
    
    return org_data

def build_employee_node(employee, employees_dict):
    """بناء عقدة موظف في الهيكل التنظيمي"""
    # Create the employee node
    node = {
        'id': employee.emp_id,
        'name': employee.emp_full_name or f'موظف {employee.emp_id}',
        'title': employee.jop_name or 'غير محدد',
        'department': employee.department.dept_name if employee.department else 'غير محدد',
        'img': employee.emp_image.url if employee.emp_image else None,
        'children': []
    }
    
    # Find all subordinates (employees who have this employee as their direct manager)
    subordinates = [emp for emp_id, emp in employees_dict.items() if emp.direct_manager_id == employee.emp_id]
    
    # Add subordinates recursively
    for sub in subordinates:
        node['children'].append(build_employee_node(sub, employees_dict))
    
    return node
