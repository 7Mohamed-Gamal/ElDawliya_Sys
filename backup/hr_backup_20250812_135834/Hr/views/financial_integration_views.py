"""
واجهات للتكامل المالي مع نظام الموارد البشرية

هذا الملف يحتوي على واجهات العرض الخاصة بتكامل نظام الموارد البشرية
مع النظام المالي والمحاسبي
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from datetime import date

from Hr.models.payroll.payroll_models import Payroll, PayrollStatus
from Hr.services.financial_integration_service import FinancialIntegrationService


class FinancialIntegrationBaseView(LoginRequiredMixin, PermissionRequiredMixin):
    """
    الصنف الأساسي لواجهات التكامل المالي
    """
    permission_required = 'hr.view_payroll'

    def get_company(self):
        """
        الحصول على الشركة الحالية
        """
        if hasattr(self.request.user, 'employee') and self.request.user.employee:
            return self.request.user.employee.company
        return None


class PayrollJournalEntriesView(FinancialIntegrationBaseView, DetailView):
    """
    واجهة عرض وإنشاء القيود المحاسبية لكشف الراتب
    """
    model = Payroll
    template_name = 'hr/financial_integration/payroll_journal_entries.html'
    context_object_name = 'payroll'
    permission_required = ('hr.view_payroll', 'hr.change_payroll')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payroll = self.object

        # التحقق من وجود قيود محاسبية سابقة
        context['has_journal_entries'] = bool(payroll.accounting_reference)

        # الحصول على قيود المحاسبة إن وجدت
        if context['has_journal_entries']:
            success, result = FinancialIntegrationService.generate_payroll_journal_entries(payroll)
            if success:
                context['journal_entries'] = result['journal_entries']
                context['total_debit'] = result['total_debit']
                context['total_credit'] = result['total_credit']

        return context

    def post(self, request, *args, **kwargs):
        """
        إنشاء القيود المحاسبية لكشف الراتب
        """
        payroll = self.get_object()

        # التأكد من أن كشف الراتب معتمد
        if payroll.status != PayrollStatus.APPROVED:
            messages.error(request, "لا يمكن إنشاء قيود محاسبية لكشف راتب غير معتمد")
            return redirect('hr:payroll_detail', pk=payroll.id)

        # التحقق من عدم وجود قيود سابقة
        if payroll.accounting_reference:
            messages.warning(request, f"توجد قيود محاسبية سابقة لكشف الراتب: {payroll.accounting_reference}")
            return redirect('hr:payroll_journal_entries', pk=payroll.id)

        # إنشاء القيود المحاسبية
        success, result = FinancialIntegrationService.generate_payroll_journal_entries(payroll)

        if success:
            messages.success(request, f"تم إنشاء القيود المحاسبية بنجاح. المرجع: {result['accounting_reference']}")
        else:
            messages.error(request, f"فشل إنشاء القيود المحاسبية: {result}")

        return redirect('hr:payroll_journal_entries', pk=payroll.id)


class PayrollPaymentVouchersView(FinancialIntegrationBaseView, DetailView):
    """
    واجهة عرض وإنشاء سندات صرف الرواتب
    """
    model = Payroll
    template_name = 'hr/financial_integration/payroll_payment_vouchers.html'
    context_object_name = 'payroll'
    permission_required = ('hr.view_payroll', 'hr.change_payroll')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payroll = self.object

        # التحقق من وجود سندات صرف سابقة
        context['has_payment_vouchers'] = bool(payroll.payment_reference)

        # الحصول على سندات الصرف إن وجدت
        if context['has_payment_vouchers']:
            success, result = FinancialIntegrationService.generate_payment_vouchers(payroll)
            if success:
                context['payment_vouchers'] = result['payment_vouchers']
                context['total_amount'] = result['total_amount']

        return context

    def post(self, request, *args, **kwargs):
        """
        إنشاء سندات صرف الرواتب
        """
        payroll = self.get_object()

        # التأكد من أن كشف الراتب معتمد
        if payroll.status != PayrollStatus.APPROVED:
            messages.error(request, "لا يمكن إنشاء سندات صرف لكشف راتب غير معتمد")
            return redirect('hr:payroll_detail', pk=payroll.id)

        # التحقق من عدم وجود سندات سابقة
        if payroll.payment_reference:
            messages.warning(request, f"توجد سندات صرف سابقة لكشف الراتب: {payroll.payment_reference}")
            return redirect('hr:payroll_payment_vouchers', pk=payroll.id)

        # إنشاء سندات الصرف
        success, result = FinancialIntegrationService.generate_payment_vouchers(payroll)

        if success:
            messages.success(request, f"تم إنشاء سندات الصرف بنجاح. المرجع: {result['payment_reference']}")
        else:
            messages.error(request, f"فشل إنشاء سندات الصرف: {result}")

        return redirect('hr:payroll_payment_vouchers', pk=payroll.id)


class BankTransferFileView(FinancialIntegrationBaseView, DetailView):
    """
    واجهة إنشاء ملف التحويلات البنكية
    """
    model = Payroll
    template_name = 'hr/financial_integration/bank_transfer_file.html'
    context_object_name = 'payroll'
    permission_required = ('hr.view_payroll', 'hr.change_payroll')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banks'] = [
            {'code': 'NCB', 'name': 'البنك الأهلي'},
            {'code': 'SABB', 'name': 'بنك ساب'},
            {'code': 'RAJHI', 'name': 'مصرف الراجحي'},
            {'code': 'ALBILAD', 'name': 'بنك البلاد'},
        ]
        return context

    def post(self, request, *args, **kwargs):
        """
        إنشاء ملف التحويلات البنكية
        """
        payroll = self.get_object()
        bank_code = request.POST.get('bank_code')

        # التأكد من أن كشف الراتب معتمد
        if payroll.status != PayrollStatus.APPROVED:
            messages.error(request, "لا يمكن إنشاء ملف تحويلات لكشف راتب غير معتمد")
            return redirect('hr:payroll_detail', pk=payroll.id)

        # إنشاء ملف التحويلات البنكية
        success, result = FinancialIntegrationService.generate_bank_transfer_file(payroll, bank_code)

        if success:
            # إنشاء استجابة لتحميل الملف
            response = HttpResponse(
                result['file_content'],
                content_type='text/csv'
            )
            response['Content-Disposition'] = f'attachment; filename="{result["file_name"]}"'
            messages.success(request, f"تم إنشاء ملف التحويلات البنكية لـ {result['transfer_count']} موظف بإجمالي {result['total_amount']}")
            return response
        else:
            messages.error(request, f"فشل إنشاء ملف التحويلات البنكية: {result}")
            return redirect('hr:bank_transfer_file', pk=payroll.id)


class BudgetComparisonView(FinancialIntegrationBaseView, TemplateView):
    """
    واجهة عرض مقارنة المصروفات الفعلية مع الموازنة
    """
    template_name = 'hr/financial_integration/budget_comparison.html'
    permission_required = ('hr.view_payroll',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_company()

        # الحصول على السنة والشهر من الطلب
        year = int(self.request.GET.get('year', date.today().year))
        month = self.request.GET.get('month', '')

        if month.isdigit():
            month = int(month)
        else:
            month = None

        # الحصول على بيانات الموازنة والمصروفات الفعلية
        success, budget_data = FinancialIntegrationService.get_budget_vs_actual_expenses(company, year, month)

        if success:
            context['budget_data'] = budget_data
        else:
            messages.error(self.request, f"فشل جلب بيانات الموازنة: {budget_data}")
            context['budget_data'] = None

        # إعداد بيانات الفلترة
        context['filter_year'] = year
        context['filter_month'] = month

        # قائمة السنوات للفلتر
        current_year = date.today().year
        context['years'] = list(range(current_year - 3, current_year + 1))

        return context
