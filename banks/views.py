from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Bank


@login_required
def bank_list(request):
    """عرض قائمة البنوك"""
    search_query = request.GET.get('search', '')

    banks = Bank.objects.all().select_related()  # TODO: Add appropriate select_related fields

    if search_query:
        banks = banks.filter(
            Q(bank_name__icontains=search_query) |
            Q(swift_code__icontains=search_query)
        )

    banks = banks.order_by('bank_name')

    # التصفح
    paginator = Paginator(banks, 25)  # 25 بنك في الصفحة
    page_number = request.GET.get('page')
    banks_page = paginator.get_page(page_number)

    context = {
        'banks': banks_page,
        'search_query': search_query,
        'total_banks': banks.count(),
    }

    return render(request, 'banks/bank_list.html', context)


@login_required
def bank_detail(request, bank_id):
    """عرض تفاصيل البنك"""
    bank = get_object_or_404(Bank, bank_id=bank_id)

    context = {
        'bank': bank,
    }

    return render(request, 'banks/bank_detail.html', context)


@login_required
def add_bank(request):
    """إضافة بنك جديد"""
    if request.method == 'POST':
        bank_name = request.POST.get('bank_name')
        swift_code = request.POST.get('swift_code', '')

        if not bank_name:
            messages.error(request, 'اسم البنك مطلوب')
        else:
            # التحقق من عدم وجود بنك بنفس الاسم
            if Bank.objects.filter(bank_name=bank_name).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exists():
                messages.error(request, 'يوجد بنك بهذا الاسم مسبقاً')
            else:
                Bank.objects.create(
                    bank_name=bank_name,
                    swift_code=swift_code
                )
                messages.success(request, f'تم إضافة البنك {bank_name} بنجاح')
                return redirect('banks:list')

    return render(request, 'banks/add_bank.html')


@login_required
def edit_bank(request, bank_id):
    """تعديل بنك"""
    bank = get_object_or_404(Bank, bank_id=bank_id)

    if request.method == 'POST':
        bank_name = request.POST.get('bank_name')
        swift_code = request.POST.get('swift_code', '')

        if not bank_name:
            messages.error(request, 'اسم البنك مطلوب')
        else:
            # التحقق من عدم وجود بنك آخر بنفس الاسم
            existing_bank = Bank.objects.filter(bank_name=bank_name).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exclude(bank_id=bank_id)
            if existing_bank.exists():
                messages.error(request, 'يوجد بنك آخر بهذا الاسم')
            else:
                bank.bank_name = bank_name
                bank.swift_code = swift_code
                bank.save()

                messages.success(request, f'تم تحديث بيانات البنك {bank_name} بنجاح')
                return redirect('banks:detail', bank_id=bank.bank_id)

    context = {
        'bank': bank,
    }

    return render(request, 'banks/edit_bank.html', context)


@login_required
def delete_bank(request, bank_id):
    """حذف بنك"""
    bank = get_object_or_404(Bank, bank_id=bank_id)

    if request.method == 'POST':
        bank_name = bank.bank_name
        bank.delete()
        messages.success(request, f'تم حذف البنك {bank_name} بنجاح')
        return redirect('banks:list')

    context = {
        'bank': bank,
    }

    return render(request, 'banks/delete_bank.html', context)


@login_required
def bank_branches(request, bank_id):
    """إدارة فروع البنك"""
    bank = get_object_or_404(Bank, bank_id=bank_id)

    # ملاحظة: هذه وظيفة مؤقتة - يمكن توسيعها لاحقاً لإدارة الفروع
    context = {
        'bank': bank,
        'branches': [],  # سيتم إضافة نموذج الفروع لاحقاً
    }

    return render(request, 'banks/bank_branches.html', context)


# API Views
@csrf_exempt
@require_http_methods(["GET"])
def banks_api(request):
    """API لجلب قائمة البنوك"""
    try:
        banks = Bank.objects.all().select_related()  # TODO: Add appropriate select_related fields.order_by('bank_name')

        banks_data = []
        for bank in banks:
            banks_data.append({
                'bank_id': bank.bank_id,
                'bank_name': bank.bank_name,
                'swift_code': bank.swift_code or '',
            })

        return JsonResponse({
            'success': True,
            'banks': banks_data,
            'total': len(banks_data)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def bank_api(request, bank_id):
    """API لجلب تفاصيل بنك محدد"""
    try:
        bank = get_object_or_404(Bank, bank_id=bank_id)

        bank_data = {
            'bank_id': bank.bank_id,
            'bank_name': bank.bank_name,
            'swift_code': bank.swift_code or '',
        }

        return JsonResponse({
            'success': True,
            'bank': bank_data
        })

    except Http404:
        return JsonResponse({
            'success': False,
            'error': 'البنك غير موجود'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
