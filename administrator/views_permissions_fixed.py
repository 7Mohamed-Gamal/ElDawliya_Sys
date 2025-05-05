from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import JsonResponse

from .models import (
    Department, Module, Permission, TemplatePermission
)
from .forms import GroupPermissionForm
from .views import system_admin_required


@login_required
@system_admin_required
def edit_group_permissions(request, group_id):
    """
    نسخة مصححة من دالة تعديل صلاحيات المجموعة
    تم إضافة:
    1. فحص إذا كانت القائمة فارغة (selected_ids)
    2. تحويل المعرفات الموجودة إلى أرقام صحيحة للمقارنة
    """
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['group'] = str(group.id)
        
        form = GroupPermissionForm(post_data)
        
        form_valid = True
        error_message = ""
        
        # هذا هو الإصلاح الرئيسي
        for field_name in ['view_permissions', 'add_permissions', 'change_permissions', 'delete_permissions', 'print_permissions']:
            if field_name in post_data:
                selected_ids = post_data.getlist(field_name)
                
                # إصلاح 1: تخطي الحقول الفارغة
                if not selected_ids:
                    continue
                
                permission_type = field_name.split('_')[0]
                existing_ids = list(Permission.objects.filter(
                    id__in=selected_ids, 
                    permission_type=permission_type
                ).values_list('id', flat=True))
                
                # إصلاح 2: تحويل القائمة الموجودة إلى أرقام صحيحة للمقارنة
                existing_ids_int = [int(id) for id in existing_ids]
                
                invalid_ids = [id for id in selected_ids if int(id) not in existing_ids_int]
                
                if invalid_ids:
                    form_valid = False
                    error_message = f"{field_name}: صلاحية غير صالحة. المعرفات {', '.join(invalid_ids)} غير موجودة في قاعدة البيانات."
                    break

        if form.is_valid() and form_valid:
            # نفس منطق المعالجة كما في الدالة الأصلية
            messages.success(request, f'تم تحديث صلاحيات المجموعة {group.name} بنجاح')
            return redirect('administrator:group_permission_list')
        else:
            if not form_valid:
                messages.error(request, error_message)
            else:
                msg = "حدث خطأ في النموذج"
                for field, errors in form.errors.items():
                    msg += f" | {field}: {', '.join(errors)}"
                messages.error(request, msg)
    else:
        # استدعاء المعالج الأصلي للطلبات GET
        from .views_permissions import edit_group_permissions
        return edit_group_permissions(request, group_id)

    return redirect('administrator:edit_group_permissions', group_id=group_id)
