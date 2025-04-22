# Ejemplos de uso del sistema de permisos en vistas

# 1. Ejemplo de uso del decorador module_permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from administrator.decorators import module_permission_required
from Hr.models import Employee  # Import the Employee model

# Ejemplo en una vista basada en función
@module_permission_required(department_name="الموارد البشرية", module_name="إدارة الموظفين", permission_type="view")
def employee_list(request):
    """Vista para listar empleados"""
    # Código para listar empleados
    employees = Employee.objects.all()  # Assuming Employee is the model for employees
    return render(request, 'Hr/employee_list.html', {'employees': employees})

from Hr.forms import EmployeeForm  # Import the EmployeeForm class

@module_permission_required(department_name="الموارد البشرية", module_name="إدارة الموظفين", permission_type="add")
def employee_create(request):
    """Vista para crear un nuevo empleado"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado creado exitosamente.')
            return redirect('Hr:employee_list')  # Replace with the actual name of your employee list URL
    else:
        form = EmployeeForm()
    return render(request, 'Hr/employee_form.html', {'form': form})

# 2. Ejemplo de uso en vistas basadas en clases
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from inventory.models import Product  # Import the Product model
from inventory.forms import ProductForm  # Import the ProductForm class

@method_decorator(module_permission_required(department_name="المخزن", module_name="قطع الغيار", permission_type="view"), name='dispatch')
class ProductListView(ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'

@method_decorator(module_permission_required(department_name="المخزن", module_name="قطع الغيار", permission_type="add"), name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')

# 3. Ejemplo de verificación de permisos dentro de una vista
from administrator.decorators import has_module_permission

def dashboard(request):
    """Vista del dashboard que muestra diferentes secciones según los permisos"""
    context = {
        'can_view_employees': has_module_permission(request, "الموارد البشرية", "إدارة الموظفين", "view"),
        'can_view_inventory': has_module_permission(request, "المخزن", "قطع الغيار", "view"),
        'can_view_maintenance': has_module_permission(request, "الصيانة", "الأعطال", "view"),
    }
    return render(request, 'dashboard.html', context)

# 4. Ejemplo de verificación de permisos para acciones específicas
def employee_detail(request, pk):
    """Vista de detalle de empleado con acciones condicionadas por permisos"""
    employee = get_object_or_404(Employee, pk=pk)
    
    context = {
        'employee': employee,
        'can_edit': has_module_permission(request, "الموارد البشرية", "إدارة الموظفين", "edit"),
        'can_delete': has_module_permission(request, "الموارد البشرية", "إدارة الموظفين", "delete"),
        'can_print': has_module_permission(request, "الموارد البشرية", "إدارة الموظفين", "print"),
    }
    
    return render(request, 'Hr/employee_detail.html', context)
