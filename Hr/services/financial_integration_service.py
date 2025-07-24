"""
خدمة التكامل مع النظام المالي والمحاسبي

هذا الملف يحتوي على خدمات لربط نظام الموارد البشرية
مع النظام المالي والمحاسبي لضمان تكامل البيانات المالية
"""

import logging
from decimal import Decimal
from datetime import datetime, date, timedelta
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Q

# إعداد نظام التسجيل
logger = logging.getLogger(__name__)

class FinancialIntegrationService:
    """
    خدمة التكامل مع النظام المالي

    توفر هذه الخدمة وظائف لربط نظام الموارد البشرية بالنظام المالي والمحاسبي،
    مثل تحويل بيانات الرواتب إلى قيود محاسبية وإنشاء مستندات الصرف
    """

    @staticmethod
    def generate_payroll_journal_entries(payroll):
        """
        إنشاء قيود المحاسبة لكشف الراتب

        تقوم بإنشاء قيود محاسبية لكشف راتب معين لتسجيلها في النظام المالي
        """
        try:
            from Hr.models.payroll.payroll_models import PayrollStatus

            # التأكد من أن كشف الراتب معتمد
            if payroll.status != PayrollStatus.APPROVED:
                logger.warning(f"لا يمكن إنشاء قيود محاسبية لكشف راتب غير معتمد. الحالة: {payroll.status}")
                return False, "لا يمكن إنشاء قيود محاسبية لكشف راتب غير معتمد"

            # التحقق من عدم وجود قيود سابقة
            if payroll.accounting_reference:
                logger.warning(f"توجد قيود محاسبية سابقة لكشف الراتب: {payroll.accounting_reference}")
                return False, "توجد قيود محاسبية سابقة لهذا الكشف"

            # إنشاء مرجع للقيود المحاسبية
            accounting_reference = f"PR-{payroll.id}-{date.today().strftime('%Y%m%d')}"

            # إنشاء القيود المحاسبية
            journal_entries = []

            # 1. قيد إجمالي الرواتب
            total_gross = payroll.total_gross_salary or 0
            if total_gross > 0:
                journal_entries.append({
                    'account_code': '5001',  # رمز حساب الرواتب
                    'account_name': 'مصروف الرواتب',
                    'debit': total_gross,
                    'credit': 0,
                    'description': f"إجمالي الرواتب لشهر {payroll.payroll_month}/{payroll.payroll_year}"
                })

            # 2. قيود الاستقطاعات
            total_deductions = payroll.total_deductions or 0
            if total_deductions > 0:
                # يمكن تفصيل الاستقطاعات حسب نوعها
                journal_entries.append({
                    'account_code': '2002',  # رمز حساب الاستقطاعات
                    'account_name': 'استقطاعات الرواتب',
                    'debit': 0,
                    'credit': total_deductions,
                    'description': f"إجمالي استقطاعات الرواتب لشهر {payroll.payroll_month}/{payroll.payroll_year}"
                })

            # 3. قيد صافي الرواتب المستحقة للدفع
            total_net = payroll.total_net_salary or 0
            if total_net > 0:
                journal_entries.append({
                    'account_code': '2001',  # رمز حساب الرواتب المستحقة
                    'account_name': 'رواتب مستحقة الدفع',
                    'debit': 0,
                    'credit': total_net,
                    'description': f"صافي الرواتب المستحقة لشهر {payroll.payroll_month}/{payroll.payroll_year}"
                })

            # حفظ مرجع القيود المحاسبية في كشف الراتب
            payroll.accounting_reference = accounting_reference
            payroll.accounting_date = date.today()
            payroll.save(update_fields=['accounting_reference', 'accounting_date'])

            # تسجيل العملية
            logger.info(f"تم إنشاء القيود المحاسبية لكشف الراتب {payroll.id} بمرجع {accounting_reference}")

            # إرسال القيود إلى النظام المالي (يحتاج إلى تنفيذ واجهة مخصصة)
            # هنا يمكن استدعاء API النظام المالي أو إنشاء ملف تصدير

            return True, {
                'accounting_reference': accounting_reference,
                'journal_entries': journal_entries,
                'total_debit': total_gross,
                'total_credit': total_deductions + total_net
            }

        except Exception as e:
            logger.error(f"خطأ في إنشاء القيود المحاسبية لكشف الراتب: {str(e)}")
            return False, f"خطأ في إنشاء القيود المحاسبية: {str(e)}"

    @staticmethod
    def generate_payment_vouchers(payroll):
        """
        إنشاء سندات صرف الرواتب

        تقوم بإنشاء سندات صرف لدفع الرواتب للموظفين
        """
        try:
            from Hr.models.payroll.payroll_models import PayrollStatus

            # التأكد من أن كشف الراتب معتمد
            if payroll.status != PayrollStatus.APPROVED:
                logger.warning(f"لا يمكن إنشاء سندات صرف لكشف راتب غير معتمد. الحالة: {payroll.status}")
                return False, "لا يمكن إنشاء سندات صرف لكشف راتب غير معتمد"

            # التحقق من عدم وجود سندات سابقة
            if payroll.payment_reference:
                logger.warning(f"توجد سندات صرف سابقة لكشف الراتب: {payroll.payment_reference}")
                return False, "توجد سندات صرف سابقة لهذا الكشف"

            # إنشاء مرجع لسندات الصرف
            payment_reference = f"PV-{payroll.id}-{date.today().strftime('%Y%m%d')}"

            # الحصول على قائمة الموظفين وصافي الرواتب
            payment_vouchers = []
            for pe in payroll.payroll_employees.filter(status=PayrollStatus.APPROVED):
                payment_vouchers.append({
                    'employee_id': pe.employee.employee_id,
                    'employee_name': pe.employee.full_name,
                    'amount': pe.net_salary,
                    'bank_account': pe.employee.bank_account_number,
                    'bank_name': pe.employee.bank_name,
                    'description': f"راتب شهر {payroll.payroll_month}/{payroll.payroll_year}"
                })

            # حفظ مرجع سندات الصرف في كشف الراتب
            payroll.payment_reference = payment_reference
            payroll.payment_date = date.today()
            payroll.save(update_fields=['payment_reference', 'payment_date'])

            # تسجيل العملية
            logger.info(f"تم إنشاء سندات صرف الرواتب لكشف الراتب {payroll.id} بمرجع {payment_reference}")

            # إرسال سندات الصرف إلى النظام المالي (يحتاج إلى تنفيذ واجهة مخصصة)
            # هنا يمكن استدعاء API النظام المالي أو إنشاء ملف تصدير

            return True, {
                'payment_reference': payment_reference,
                'payment_vouchers': payment_vouchers,
                'total_amount': sum(pv['amount'] for pv in payment_vouchers)
            }

        except Exception as e:
            logger.error(f"خطأ في إنشاء سندات صرف الرواتب: {str(e)}")
            return False, f"خطأ في إنشاء سندات صرف الرواتب: {str(e)}"

    @staticmethod
    def generate_bank_transfer_file(payroll, bank_code):
        """
        إنشاء ملف تحويلات بنكية

        تقوم بإنشاء ملف للتحويلات البنكية بتنسيق معين حسب البنك
        """
        try:
            from Hr.models.payroll.payroll_models import PayrollStatus
            import csv
            import io

            # التأكد من أن كشف الراتب معتمد
            if payroll.status != PayrollStatus.APPROVED:
                logger.warning(f"لا يمكن إنشاء ملف تحويلات لكشف راتب غير معتمد. الحالة: {payroll.status}")
                return False, "لا يمكن إنشاء ملف تحويلات لكشف راتب غير معتمد"

            # إنشاء ملف CSV للتحويلات البنكية
            output = io.StringIO()
            writer = csv.writer(output)

            # إضافة رأس الجدول حسب تنسيق البنك
            if bank_code == 'NCB':
                # تنسيق البنك الأهلي
                writer.writerow(['رقم الحساب', 'اسم المستفيد', 'المبلغ', 'الوصف'])
            elif bank_code == 'SABB':
                # تنسيق بنك ساب
                writer.writerow(['ACCOUNT_NUMBER', 'BENEFICIARY_NAME', 'AMOUNT', 'DESCRIPTION'])
            else:
                # تنسيق افتراضي
                writer.writerow(['account_number', 'beneficiary_name', 'amount', 'description'])

            # إضافة بيانات التحويلات
            total_amount = 0
            transfer_count = 0

            for pe in payroll.payroll_employees.filter(status=PayrollStatus.APPROVED):
                # تخطي الموظفين بدون حسابات بنكية
                if not pe.employee.bank_account_number:
                    continue

                # التأكد من تطابق البنك إذا تم تحديده
                if bank_code and pe.employee.bank_code and pe.employee.bank_code != bank_code:
                    continue

                description = f"راتب {pe.employee.employee_id} - {payroll.payroll_month}/{payroll.payroll_year}"
                writer.writerow([
                    pe.employee.bank_account_number,
                    pe.employee.full_name,
                    pe.net_salary,
                    description
                ])

                total_amount += pe.net_salary
                transfer_count += 1

            # الحصول على محتوى الملف
            output.seek(0)
            file_content = output.read()

            # تسجيل العملية
            logger.info(f"تم إنشاء ملف تحويلات بنكية لكشف الراتب {payroll.id} لـ {transfer_count} موظف بإجمالي {total_amount}")

            return True, {
                'file_name': f"salary_transfer_{bank_code}_{payroll.payroll_month}_{payroll.payroll_year}.csv",
                'file_content': file_content,
                'total_amount': total_amount,
                'transfer_count': transfer_count
            }

        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف التحويلات البنكية: {str(e)}")
            return False, f"خطأ في إنشاء ملف التحويلات البنكية: {str(e)}"

    @staticmethod
    def sync_accounting_master_data():
        """
        مزامنة البيانات الرئيسية مع النظام المحاسبي

        تقوم بمزامنة مراكز التكلفة والحسابات المالية بين النظامين
        """
        try:
            # هنا يتم تنفيذ عملية المزامنة مع النظام المحاسبي
            # عادة تتم من خلال API أو قاعدة بيانات مشتركة

            # تسجيل العملية
            logger.info("تم بدء مزامنة البيانات الرئيسية مع النظام المحاسبي")

            # مثال لهيكل البيانات التي يمكن مزامنتها
            sync_data = {
                'cost_centers': [
                    # مراكز التكلفة من النظام المحاسبي
                    {'code': 'CC001', 'name': 'الإدارة العامة'},
                    {'code': 'CC002', 'name': 'إدارة الموارد البشرية'},
                    {'code': 'CC003', 'name': 'إدارة المبيعات'},
                    {'code': 'CC004', 'name': 'إدارة تقنية المعلومات'}
                ],
                'accounts': [
                    # الحسابات المالية من النظام المحاسبي
                    {'code': '5001', 'name': 'مصروف الرواتب', 'type': 'expense'},
                    {'code': '5002', 'name': 'مصروف البدلات', 'type': 'expense'},
                    {'code': '2001', 'name': 'رواتب مستحقة الدفع', 'type': 'liability'},
                    {'code': '2002', 'name': 'استقطاعات الرواتب', 'type': 'liability'}
                ]
            }

            # هنا يمكن تحديث بيانات النظام بناءً على المعلومات المستلمة

            return True, sync_data

        except Exception as e:
            logger.error(f"خطأ في مزامنة البيانات مع النظام المحاسبي: {str(e)}")
            return False, f"خطأ في المزامنة: {str(e)}"

    @staticmethod
    def get_budget_vs_actual_expenses(company, year, month=None):
        """
        الحصول على مقارنة المصروفات الفعلية مع الموازنة

        تقوم بجلب بيانات المصروفات الفعلية من النظام المالي ومقارنتها بالموازنة
        """
        try:
            # هنا يتم الاتصال بالنظام المالي لجلب البيانات المطلوبة
            # هذه مجرد بيانات افتراضية للتوضيح

            # تحديد الفترة
            if month:
                period = f"{year}-{month:02d}"
                period_name = f"{month}/{year}"
            else:
                period = f"{year}"
                period_name = f"{year}"

            # بيانات افتراضية للعرض
            budget_data = {
                'period': period_name,
                'expenses': [
                    {
                        'category': 'الرواتب الأساسية',
                        'budget': 450000,
                        'actual': 437500,
                        'variance': 12500,
                        'variance_percent': 2.8
                    },
                    {
                        'category': 'البدلات',
                        'budget': 200000,
                        'actual': 210000,
                        'variance': -10000,
                        'variance_percent': -5.0
                    },
                    {
                        'category': 'العمل الإضافي',
                        'budget': 75000,
                        'actual': 68000,
                        'variance': 7000,
                        'variance_percent': 9.3
                    },
                    {
                        'category': 'التأمينات الاجتماعية',
                        'budget': 45000,
                        'actual': 45000,
                        'variance': 0,
                        'variance_percent': 0
                    },
                    {
                        'category': 'التأمين الطبي',
                        'budget': 120000,
                        'actual': 118000,
                        'variance': 2000,
                        'variance_percent': 1.7
                    },
                    {
                        'category': 'المكافآت',
                        'budget': 100000,
                        'actual': 85000,
                        'variance': 15000,
                        'variance_percent': 15.0
                    }
                ],
                'summary': {
                    'total_budget': 990000,
                    'total_actual': 963500,
                    'total_variance': 26500,
                    'total_variance_percent': 2.7
                }
            }

            return True, budget_data

        except Exception as e:
            logger.error(f"خطأ في جلب بيانات الموازنة والمصروفات الفعلية: {str(e)}")
            return False, f"خطأ في جلب البيانات: {str(e)}"
