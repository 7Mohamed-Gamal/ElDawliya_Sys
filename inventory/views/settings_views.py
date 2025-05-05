"""
Settings views for the inventory application.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from inventory.decorators import inventory_module_permission_required
from inventory.models_local import LocalSystemSettings
from inventory.forms import LocalSystemSettingsForm

@login_required
@inventory_module_permission_required('settings', 'view')
def settings_view(request):
    """عرض وتعديل إعدادات المخزن"""
    # الحصول على الإعدادات الحالية أو إنشاء إعدادات جديدة إذا لم تكن موجودة
    settings, created = LocalSystemSettings.objects.get_or_create(pk=1)

    if request.method == 'POST':
        form = LocalSystemSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ الإعدادات بنجاح')
            return redirect('inventory:settings')
    else:
        form = LocalSystemSettingsForm(instance=settings)

    context = {
        'form': form,
        'page_title': 'إعدادات المخزن',
        'settings': settings,
    }

    return render(request, 'inventory/settings.html', context)

# للتوافق مع الروابط القديمة
@login_required
@inventory_module_permission_required('settings', 'view')
def system_settings(request):
    """
    Alias for settings_view for backward compatibility.
    """
    return settings_view(request)
