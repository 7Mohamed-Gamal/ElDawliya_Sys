"""
خدمة حساب الرواتب الشاملة
Comprehensive Payroll Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count, Q
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from core.services.base import BaseService
from core.models.payroll import (
    PayrollRun, PayrollDetail, PayrollBonus, PayrollDeduction
)


class PayrollService(BaseService):
    """
    خدمة حساب الرواتب الشاملة
    Comprehensive payroll calculation and management service
    """

    def create_salary_structure(self, employee_id, data):
        """
        إنشاء هيكل راتب للموظف
        Create salary structure for employee
        """
        self.check_permission('payroll.add_salarystructure')

        required_fields = ['basic_salary', 'effective_date']
        self.validate_required_fields(data, required_fields)

        try:
            from core.models.hr import Employee

            employee = Employee.objects.get(id=employee_id)

            with transaction.atomic():
                # Deactivate previous salary structure
                SalaryStructure.objects.filter(
                    employee=employee,
                    is_active=True
                ).update(is_active=False, updated_by=self.user)

                # Create new salary structure
                salary_structure = SalaryStructure.objects.create(
                    employee=employee,
                    basic_salary=data['basic_salary'],
                    effective_date=data['effective_date'],
                    currency=data.get('currency', 'SAR'),
                    payment_frequency=data.get('payment_frequency', 'monthly'),
                    created_by=self.user,
                    updated_by=self.user
                )

                # Add salary components
                if data.get('components'):
                    self._add_salary_components(salary_structure, data['components'])

                # Log the action
                self.log_action(
                    action='create',
                    resource='salary_structure',
                    content_object=salary_structure,
                    new_values=data,
                    message=f'تم إنشاء هيكل راتب للموظف: {employee.get_full_name()}'
                )

                return self.format_response(
                    data={'salary_structure_id': salary_structure.id},
                    message='تم إنشاء هيكل الراتب بنجاح'
                )

        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'create_salary_structure', f'salary_structure/{employee_id}', data)

    def calculate_employee_salary(self, employee_id, payroll_period_id, include_overtime=True):
        """
        حساب راتب الموظف لفترة معينة
        Calculate employee salary for specific period
        """
        self.check_permission('payroll.view_payrollrecord')

        try:
            from core.models.hr import Employee

            employee = Employee.objects.get(id=employee_id)
            payroll_period = PayrollPeriod.objects.get(id=payroll_period_id)

            # Get active salary structure
            salary_structure = SalaryStructure.objects.filter(
                employee=employee,
                is_active=True,
                effective_date__lte=payroll_period.end_date
            ).order_by('-effective_date').first()

            if not salary_structure:
                return self.format_response(
                    success=False,
                    message='لا يوجد هيكل راتب مفعل للموظف'
                )

            # Calculate salary components
            calculation_result = self._perform_salary_calculation(
                employee, salary_structure, payroll_period, include_overtime
            )

            return self.format_response(
                data=calculation_result,
                message='تم حساب الراتب بنجاح'
            )

        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except PayrollPeriod.DoesNotExist:
            return self.format_response(
                success=False,
                message='فترة الراتب غير موجودة'
            )
        except Exception as e:
            return self.handle_exception(e, 'calculate_employee_salary', f'salary_calc/{employee_id}')

    def process_payroll(self, payroll_period_id, employee_ids=None, auto_approve=False):
        """
        معالجة الرواتب لفترة معينة
        Process payroll for specific period
        """
        self.check_permission('payroll.add_payrollrecord')

        try:
            payroll_period = PayrollPeriod.objects.get(id=payroll_period_id)

            if payroll_period.status != 'open':
                return self.format_response(
                    success=False,
                    message='فترة الراتب غير مفتوحة للمعالجة'
                )

            # Get employees to process
            from core.models.hr import Employee

            if employee_ids:
                employees = Employee.objects.filter(
                    id__in=employee_ids,
                    is_active=True
                )
            else:
                employees = Employee.objects.filter(is_active=True)

            processed_count = 0
            error_count = 0
            errors = []

            with transaction.atomic():
                for employee in employees:
                    try:
                        # Check if payroll already processed for this employee
                        existing_record = PayrollRecord.objects.filter(
                            employee=employee,
                            payroll_period=payroll_period
                        ).first()

                        if existing_record:
                            continue

                        # Calculate salary
                        calculation_result = self._perform_salary_calculation(
                            employee, None, payroll_period, True
                        )

                        if not calculation_result:
                            error_count += 1
                            errors.append(f'فشل في حساب راتب الموظف: {employee.get_full_name()}')
                            continue

                        # Create payroll record
                        payroll_record = PayrollRecord.objects.create(
                            employee=employee,
                            payroll_period=payroll_period,
                            basic_salary=calculation_result['basic_salary'],
                            total_allowances=calculation_result['total_allowances'],
                            total_deductions=calculation_result['total_deductions'],
                            overtime_amount=calculation_result['overtime_amount'],
                            gross_salary=calculation_result['gross_salary'],
                            net_salary=calculation_result['net_salary'],
                            tax_amount=calculation_result.get('tax_amount', 0),
                            insurance_amount=calculation_result.get('insurance_amount', 0),
                            status='calculated' if not auto_approve else 'approved',
                            calculation_details=calculation_result.get('details', {}),
                            created_by=self.user,
                            updated_by=self.user
                        )

                        processed_count += 1

                    except Exception as e:
                        error_count += 1
                        errors.append(f'خطأ في معالجة راتب {employee.get_full_name()}: {str(e)}')
                        self.logger.error(f"Payroll processing error for employee {employee.id}: {e}")

            # Update payroll period status if all processed successfully
            if error_count == 0 and processed_count > 0:
                payroll_period.status = 'calculated' if not auto_approve else 'approved'
                payroll_period.processed_by = self.user
                payroll_period.processed_at = timezone.now()
                payroll_period.save()

            # Log the action
            self.log_action(
                action='process',
                resource='payroll',
                content_object=payroll_period,
                details={
                    'processed_count': processed_count,
                    'error_count': error_count,
                    'auto_approve': auto_approve
                },
                message=f'تم معالجة {processed_count} راتب لفترة {payroll_period.name}'
            )

            return self.format_response(
                data={
                    'processed_count': processed_count,
                    'error_count': error_count,
                    'errors': errors
                },
                message=f'تم معالجة {processed_count} راتب بنجاح'
            )

        except PayrollPeriod.DoesNotExist:
            return self.format_response(
                success=False,
                message='فترة الراتب غير موجودة'
            )
        except Exception as e:
            return self.handle_exception(e, 'process_payroll', f'payroll_process/{payroll_period_id}')

    def approve_payroll_record(self, payroll_record_id, notes=None):
        """
        اعتماد سجل الراتب
        Approve payroll record
        """
        self.check_permission('payroll.change_payrollrecord')

        try:
            payroll_record = PayrollRecord.objects.get(id=payroll_record_id)

            if payroll_record.status == 'approved':
                return self.format_response(
                    success=False,
                    message='سجل الراتب معتمد بالفعل'
                )

            payroll_record.status = 'approved'
            payroll_record.approved_by = self.user
            payroll_record.approved_at = timezone.now()
            payroll_record.approval_notes = notes
            payroll_record.updated_by = self.user
            payroll_record.save()

            # Log the action
            self.log_action(
                action='approve',
                resource='payroll_record',
                content_object=payroll_record,
                details={'notes': notes},
                message=f'تم اعتماد راتب الموظف: {payroll_record.employee.get_full_name()}'
            )

            return self.format_response(
                message='تم اعتماد سجل الراتب بنجاح'
            )

        except PayrollRecord.DoesNotExist:
            return self.format_response(
                success=False,
                message='سجل الراتب غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'approve_payroll_record', f'payroll_approve/{payroll_record_id}')

    def generate_payslip(self, payroll_record_id, format='pdf'):
        """
        إنشاء قسيمة الراتب
        Generate payslip document
        """
        self.check_permission('payroll.view_payrollrecord')

        try:
            payroll_record = PayrollRecord.objects.select_related(
                'employee', 'payroll_period', 'employee__department', 'employee__job_position'
            ).get(id=payroll_record_id)

            # Check object-level permission
            self.check_object_permission('payroll.view_payrollrecord', payroll_record)

            # Prepare payslip data
            payslip_data = {
                'employee': {
                    'name': payroll_record.employee.get_full_name(),
                    'emp_code': payroll_record.employee.emp_code,
                    'department': payroll_record.employee.department.name_ar if payroll_record.employee.department else '',
                    'job_position': payroll_record.employee.job_position.title_ar if payroll_record.employee.job_position else '',
                },
                'period': {
                    'name': payroll_record.payroll_period.name,
                    'start_date': payroll_record.payroll_period.start_date,
                    'end_date': payroll_record.payroll_period.end_date,
                },
                'salary_details': {
                    'basic_salary': payroll_record.basic_salary,
                    'total_allowances': payroll_record.total_allowances,
                    'total_deductions': payroll_record.total_deductions,
                    'overtime_amount': payroll_record.overtime_amount,
                    'gross_salary': payroll_record.gross_salary,
                    'tax_amount': payroll_record.tax_amount,
                    'insurance_amount': payroll_record.insurance_amount,
                    'net_salary': payroll_record.net_salary,
                },
                'breakdown': payroll_record.calculation_details,
                'generated_at': timezone.now(),
                'generated_by': self.user.get_full_name(),
            }

            if format == 'pdf':
                # Generate PDF payslip
                pdf_content = self._generate_pdf_payslip(payslip_data)
                return self.format_response(
                    data={'pdf_content': pdf_content},
                    message='تم إنشاء قسيمة الراتب بصيغة PDF'
                )
            else:
                # Return JSON data
                return self.format_response(
                    data=payslip_data,
                    message='تم إنشاء بيانات قسيمة الراتب'
                )

        except PayrollRecord.DoesNotExist:
            return self.format_response(
                success=False,
                message='سجل الراتب غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'generate_payslip', f'payslip/{payroll_record_id}')

    def get_payroll_summary(self, payroll_period_id):
        """
        الحصول على ملخص الرواتب
        Get payroll summary for period
        """
        self.check_permission('payroll.view_payrollrecord')

        try:
            payroll_period = PayrollPeriod.objects.get(id=payroll_period_id)

            # Get payroll records for the period
            payroll_records = PayrollRecord.objects.filter(
                payroll_period=payroll_period
            ).select_related('employee', 'employee__department')

            # Calculate summary statistics
            summary = payroll_records.aggregate(
                total_employees=Count('id'),
                total_basic_salary=Sum('basic_salary'),
                total_allowances=Sum('total_allowances'),
                total_deductions=Sum('total_deductions'),
                total_overtime=Sum('overtime_amount'),
                total_gross_salary=Sum('gross_salary'),
                total_tax=Sum('tax_amount'),
                total_insurance=Sum('insurance_amount'),
                total_net_salary=Sum('net_salary'),
            )

            # Get status breakdown
            status_breakdown = payroll_records.values('status').annotate(
                count=Count('id'),
                total_amount=Sum('net_salary')
            ).order_by('status')

            # Get department breakdown
            department_breakdown = payroll_records.values(
                'employee__department__name_ar'
            ).annotate(
                count=Count('id'),
                total_amount=Sum('net_salary')
            ).order_by('employee__department__name_ar')

            summary_data = {
                'period': {
                    'id': payroll_period.id,
                    'name': payroll_period.name,
                    'start_date': payroll_period.start_date,
                    'end_date': payroll_period.end_date,
                    'status': payroll_period.status,
                },
                'totals': summary,
                'status_breakdown': list(status_breakdown),
                'department_breakdown': list(department_breakdown),
            }

            return self.format_response(
                data=summary_data,
                message='تم الحصول على ملخص الرواتب بنجاح'
            )

        except PayrollPeriod.DoesNotExist:
            return self.format_response(
                success=False,
                message='فترة الراتب غير موجودة'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_payroll_summary', f'payroll_summary/{payroll_period_id}')

    def _perform_salary_calculation(self, employee, salary_structure, payroll_period, include_overtime):
        """تنفيذ حساب الراتب"""
        try:
            # Get salary structure if not provided
            if not salary_structure:
                salary_structure = SalaryStructure.objects.filter(
                    employee=employee,
                    is_active=True,
                    effective_date__lte=payroll_period.end_date
                ).order_by('-effective_date').first()

                if not salary_structure:
                    return None

            # Calculate basic salary (pro-rated if needed)
            basic_salary = self._calculate_prorated_salary(
                salary_structure.basic_salary,
                payroll_period.start_date,
                payroll_period.end_date,
                employee.hire_date
            )

            # Calculate allowances
            total_allowances = self._calculate_allowances(employee, payroll_period)

            # Calculate deductions
            total_deductions = self._calculate_deductions(employee, payroll_period)

            # Calculate overtime
            overtime_amount = Decimal('0')
            if include_overtime:
                overtime_amount = self._calculate_overtime_amount(employee, payroll_period)

            # Calculate gross salary
            gross_salary = basic_salary + total_allowances + overtime_amount

            # Calculate tax and insurance
            tax_amount = self._calculate_tax(gross_salary, employee)
            insurance_amount = self._calculate_insurance(gross_salary, employee)

            # Calculate net salary
            net_salary = gross_salary - total_deductions - tax_amount - insurance_amount

            return {
                'basic_salary': basic_salary,
                'total_allowances': total_allowances,
                'total_deductions': total_deductions,
                'overtime_amount': overtime_amount,
                'gross_salary': gross_salary,
                'tax_amount': tax_amount,
                'insurance_amount': insurance_amount,
                'net_salary': net_salary,
                'details': {
                    'calculation_date': timezone.now().isoformat(),
                    'salary_structure_id': salary_structure.id,
                    'period_days': (payroll_period.end_date - payroll_period.start_date).days + 1,
                }
            }

        except Exception as e:
            self.logger.error(f"Salary calculation error for employee {employee.id}: {e}")
            return None

    def _calculate_prorated_salary(self, basic_salary, period_start, period_end, hire_date):
        """حساب الراتب الأساسي المتناسب"""
        # If hired during the period, calculate pro-rated salary
        if hire_date and hire_date > period_start:
            actual_start = max(hire_date, period_start)
            total_days = (period_end - period_start).days + 1
            worked_days = (period_end - actual_start).days + 1
            return basic_salary * (worked_days / total_days)

        return basic_salary

    def _calculate_allowances(self, employee, payroll_period):
        """حساب البدلات"""
        allowances = Allowance.objects.filter(
            employee=employee,
            is_active=True,
            effective_date__lte=payroll_period.end_date
        )

        total = Decimal('0')
        for allowance in allowances:
            if allowance.allowance_type == 'fixed':
                total += allowance.amount
            elif allowance.allowance_type == 'percentage':
                # Calculate percentage of basic salary
                salary_structure = SalaryStructure.objects.filter(
                    employee=employee,
                    is_active=True
                ).first()
                if salary_structure:
                    total += salary_structure.basic_salary * (allowance.percentage / 100)

        return total

    def _calculate_deductions(self, employee, payroll_period):
        """حساب الخصومات"""
        deductions = Deduction.objects.filter(
            employee=employee,
            is_active=True,
            effective_date__lte=payroll_period.end_date
        )

        total = Decimal('0')
        for deduction in deductions:
            if deduction.deduction_type == 'fixed':
                total += deduction.amount
            elif deduction.deduction_type == 'percentage':
                # Calculate percentage of basic salary
                salary_structure = SalaryStructure.objects.filter(
                    employee=employee,
                    is_active=True
                ).first()
                if salary_structure:
                    total += salary_structure.basic_salary * (deduction.percentage / 100)

        return total

    def _calculate_overtime_amount(self, employee, payroll_period):
        """حساب مبلغ الساعات الإضافية"""
        from core.models.attendance import OvertimeRecord

        overtime_records = OvertimeRecord.objects.filter(
            employee=employee,
            overtime_date__range=[payroll_period.start_date, payroll_period.end_date],
            status='approved'
        )

        total_amount = Decimal('0')
        salary_structure = SalaryStructure.objects.filter(
            employee=employee,
            is_active=True
        ).first()

        if salary_structure:
            # Calculate hourly rate (assuming 8 hours per day, 22 working days per month)
            hourly_rate = salary_structure.basic_salary / (22 * 8)

            for overtime in overtime_records:
                overtime_amount = hourly_rate * overtime.overtime_hours * overtime.overtime_rate
                total_amount += overtime_amount

        return total_amount

    def _calculate_tax(self, gross_salary, employee):
        """حساب الضريبة"""
        # This is a simplified tax calculation
        # In real implementation, this would follow the country's tax rules

        # Example: No tax for salaries below 3000, 5% for above
        if gross_salary <= 3000:
            return Decimal('0')
        else:
            return (gross_salary - 3000) * Decimal('0.05')

    def _calculate_insurance(self, gross_salary, employee):
        """حساب التأمين الاجتماعي"""
        # Example: 9% employee contribution for social insurance
        return gross_salary * Decimal('0.09')

    def _add_salary_components(self, salary_structure, components):
        """إضافة مكونات الراتب"""
        for component_data in components:
            SalaryComponent.objects.create(
                salary_structure=salary_structure,
                component_type=component_data['component_type'],
                component_name=component_data['component_name'],
                amount=component_data.get('amount', 0),
                percentage=component_data.get('percentage', 0),
                is_taxable=component_data.get('is_taxable', True),
                created_by=self.user,
                updated_by=self.user
            )

    def _generate_pdf_payslip(self, payslip_data):
        """إنشاء قسيمة راتب بصيغة PDF"""
        # This would use a PDF generation library like ReportLab
        # For now, return a placeholder
        return "PDF content would be generated here"
