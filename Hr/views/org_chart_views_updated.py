from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

from Hr.models.department_models import Department
from Hr.models.employee_model import Employee


@login_required
def org_chart(request):
    """الهيكل التنظيمي للشركة"""
    # الحصول على جميع الأقسام
    departments = Department.objects.all()
    
    # إعداد سياق العرض
    context = {
        'departments': departments,
        'title': 'الهيكل التنظيمي للشركة'
    }
    
    return render(request, 'Hr/org_chart/org_chart.html', context)


@login_required
def org_chart_data(request):
    """بيانات الهيكل التنظيمي بتنسيق JSON للعرض التفاعلي"""
    # تصفية حسب القسم إذا تم تحديده
    dept_code = request.GET.get('dept_code')
    if dept_code:
        departments = Department.objects.filter(dept_code=dept_code)
    else:
        departments = Department.objects.all()
    
    # إعداد بيانات الهيكل
    org_data = {
        'id': 'company',
        'name': 'الشركة',
        'title': 'المدير العام',
        'children': []
    }
    
    # إضافة الأقسام
    for dept in departments:
        dept_data = {
            'id': f'dept_{dept.dept_code}',
            'name': dept.dept_name,
            'title': 'مدير القسم',
            'className': 'department',
            'children': []
        }
        
        # إضافة مدير القسم إذا كان موجوداً
        if dept.manager:
            dept_data['manager'] = {
                'id': f'emp_{dept.manager.emp_id}',
                'name': dept.manager.emp_full_name,
                'title': dept.manager.jop_name,
                'imageUrl': dept.manager.emp_image.url if dept.manager.emp_image else None
            }
        
        # إضافة الموظفين في القسم، مع مراعاة التسلسل الهرمي
        # تجميع الموظفين حسب الرئيس المباشر
        employees_by_supervisor = {}
        
        # الحصول على جميع الموظفين في القسم
        employees = Employee.objects.filter(department=dept)
        
        for emp in employees:
            if emp != dept.manager:  # استبعاد المدير لتجنب التكرار
                if emp.direct_supervisor:
                    supervisor_id = emp.direct_supervisor.emp_id
                    if supervisor_id not in employees_by_supervisor:
                        employees_by_supervisor[supervisor_id] = []
                    
                    employees_by_supervisor[supervisor_id].append(emp)
                else:
                    # الموظفون بدون رئيس مباشر يتبعون مباشرة للقسم
                    emp_data = {
                        'id': f'emp_{emp.emp_id}',
                        'name': emp.emp_full_name,
                        'title': emp.jop_name,
                        'className': 'employee',
                        'imageUrl': emp.emp_image.url if emp.emp_image else None
                    }
                    dept_data['children'].append(emp_data)
        
        # إضافة الموظفين في التسلسل الهرمي
        add_subordinates(dept_data, employees_by_supervisor, dept.manager.emp_id if dept.manager else None)
        
        # إضافة القسم إلى الهيكل الرئيسي
        org_data['children'].append(dept_data)
    
    return JsonResponse(org_data)


@login_required
def department_org_chart(request, dept_code):
    """الهيكل التنظيمي لقسم محدد"""
    department = get_object_or_404(Department, dept_code=dept_code)
    
    context = {
        'department': department,
        'title': f'الهيكل التنظيمي لقسم {department.dept_name}'
    }
    
    return render(request, 'Hr/org_chart/department_org_chart.html', context)


@login_required
def employee_hierarchy(request, emp_id):
    """عرض التسلسل الهرمي للموظف"""
    employee = get_object_or_404(Employee, emp_id=emp_id)
    
    # إعداد البيانات الأولية
    hierarchy_data = {
        'employee': employee,
        'supervisors': [],
        'colleagues': [],
        'subordinates': []
    }
    
    # الحصول على المشرفين (التسلسل الهرمي للأعلى)
    current_supervisor = employee.direct_supervisor
    while current_supervisor:
        hierarchy_data['supervisors'].append(current_supervisor)
        current_supervisor = current_supervisor.direct_supervisor
    
    # عكس قائمة المشرفين لتكون من الأعلى للأسفل
    hierarchy_data['supervisors'].reverse()
    
    # الحصول على الزملاء (الموظفين تحت نفس المشرف)
    if employee.direct_supervisor:
        colleagues = Employee.objects.filter(direct_supervisor=employee.direct_supervisor).exclude(emp_id=employee.emp_id)
        hierarchy_data['colleagues'] = colleagues
    
    # الحصول على المرؤوسين المباشرين
    subordinates = Employee.objects.filter(direct_supervisor=employee)
    hierarchy_data['subordinates'] = subordinates
    
    context = {
        'hierarchy': hierarchy_data,
        'title': f'التسلسل الهرمي للموظف: {employee.emp_full_name}'
    }
    
    return render(request, 'Hr/org_chart/employee_hierarchy.html', context)


# وظائف مساعدة
def add_subordinates(node, employees_by_supervisor, supervisor_id):
    """إضافة المرؤوسين بشكل متكرر"""
    if supervisor_id in employees_by_supervisor:
        for emp in employees_by_supervisor[supervisor_id]:
            emp_data = {
                'id': f'emp_{emp.emp_id}',
                'name': emp.emp_full_name,
                'title': emp.jop_name,
                'className': 'employee',
                'imageUrl': emp.emp_image.url if emp.emp_image else None,
                'children': []
            }
            
            # إضافة المرؤوسين بشكل متكرر
            add_subordinates(emp_data, employees_by_supervisor, emp.emp_id)
            
            # إضافة الموظف إلى الشجرة
            node['children'].append(emp_data)
