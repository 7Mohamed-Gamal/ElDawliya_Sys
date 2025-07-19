from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from datetime import date, timedelta
from calendar import monthrange

from Hr.models import (
    Employee, Department, AttendanceRecord, LeaveRequest, 
    PayrollEntry, Company, Branch
)
from Hr.services import ReportService

class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for HR analytics and KPIs"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard_kpis(self, request):
        """Get main dashboard KPIs"""
        company_id = request.query_params.get('company_id')
        
        # Base queryset filters
        employee_filters = {'status': 'active'}
        if company_id:
            employee_filters['company_id'] = company_id
        
        # Employee statistics
        total_employees = Employee.objects.filter(**employee_filters).count()
        new_employees_this_month = Employee.objects.filter(
            **employee_filters,
            hire_date__month=timezone.now().month,
            hire_date__year=timezone.now().year
        ).count()
        
        # Attendance statistics (last 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        attendance_records = AttendanceRecord.objects.filter(
            date__gte=thirty_days_ago,
            employee__status='active'
        )
        
        if company_id:
            attendance_records = attendance_records.filter(employee__company_id=company_id)
        
        total_attendance_records = attendance_records.count()
        late_arrivals = attendance_records.filter(is_late=True).count()
        early_departures = attendance_records.filter(is_early_departure=True).count()
        
        # Leave statistics (current month)
        current_month_leaves = LeaveRequest.objects.filter(
            start_date__month=timezone.now().month,
            start_date__year=timezone.now().year,
            status='approved'
        )
        
        if company_id:
            current_month_leaves = current_month_leaves.filter(employee__company_id=company_id)
        
        employees_on_leave_today = LeaveRequest.objects.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date(),
            status='approved'
        )
        
        if company_id:
            employees_on_leave_today = employees_on_leave_today.filter(employee__company_id=company_id)
        
        # Department distribution
        department_stats = Employee.objects.filter(**employee_filters).values(
            'department__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return Response({
            'employees': {
                'total': total_employees,
                'new_this_month': new_employees_this_month,
                'on_leave_today': employees_on_leave_today.count()
            },
            'attendance': {
                'total_records_30_days': total_attendance_records,
                'late_arrivals_30_days': late_arrivals,
                'early_departures_30_days': early_departures,
                'punctuality_rate': ((total_attendance_records - late_arrivals) / total_attendance_records * 100) if total_attendance_records > 0 else 0
            },
            'leaves': {
                'approved_this_month': current_month_leaves.count(),
                'employees_on_leave_today': employees_on_leave_today.count()
            },
            'departments': {
                'top_departments': list(department_stats)
            }
        })
    
    @action(detail=False, methods=['get'])
    def employee_analytics(self, request):
        """Get employee analytics"""
        company_id = request.query_params.get('company_id')
        department_id = request.query_params.get('department_id')
        
        filters = {'status': 'active'}
        if company_id:
            filters['company_id'] = company_id
        if department_id:
            filters['department_id'] = department_id
        
        employees = Employee.objects.filter(**filters)
        
        # Age distribution
        age_ranges = {
            '20-30': employees.filter(birth_date__lte=date.today() - timedelta(days=20*365), 
                                    birth_date__gt=date.today() - timedelta(days=30*365)).count(),
            '31-40': employees.filter(birth_date__lte=date.today() - timedelta(days=30*365), 
                                    birth_date__gt=date.today() - timedelta(days=40*365)).count(),
            '41-50': employees.filter(birth_date__lte=date.today() - timedelta(days=40*365), 
                                    birth_date__gt=date.today() - timedelta(days=50*365)).count(),
            '50+': employees.filter(birth_date__lte=date.today() - timedelta(days=50*365)).count()
        }
        
        # Gender distribution
        gender_distribution = employees.values('gender').annotate(count=Count('id'))
        
        # Employment type distribution
        employment_type_distribution = employees.values('employment_type').annotate(count=Count('id'))
        
        # Years of service distribution
        service_ranges = {
            '0-1': 0, '2-5': 0, '6-10': 0, '11-15': 0, '15+': 0
        }
        
        for employee in employees:
            years = employee.years_of_service or 0
            if years <= 1:
                service_ranges['0-1'] += 1
            elif years <= 5:
                service_ranges['2-5'] += 1
            elif years <= 10:
                service_ranges['6-10'] += 1
            elif years <= 15:
                service_ranges['11-15'] += 1
            else:
                service_ranges['15+'] += 1
        
        # Department distribution
        department_distribution = employees.values(
            'department__name'
        ).annotate(count=Count('id')).order_by('-count')
        
        return Response({
            'total_employees': employees.count(),
            'age_distribution': age_ranges,
            'gender_distribution': {item['gender']: item['count'] for item in gender_distribution},
            'employment_type_distribution': {item['employment_type']: item['count'] for item in employment_type_distribution},
            'service_years_distribution': service_ranges,
            'department_distribution': list(department_distribution)
        })
    
    @action(detail=False, methods=['get'])
    def attendance_analytics(self, request):
        """Get attendance analytics"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        department_id = request.query_params.get('department_id')
        
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = (timezone.now().date() - timedelta(days=30)).isoformat()
        if not end_date:
            end_date = timezone.now().date().isoformat()
        
        filters = {
            'date__range': [start_date, end_date]
        }
        
        if department_id:
            filters['employee__department_id'] = department_id
        
        attendance_records = AttendanceRecord.objects.filter(**filters)
        
        # Overall statistics
        total_records = attendance_records.count()
        late_arrivals = attendance_records.filter(is_late=True).count()
        early_departures = attendance_records.filter(is_early_departure=True).count()
        
        # Daily attendance trend
        daily_stats = attendance_records.values('date').annotate(
            total_attendance=Count('id'),
            late_count=Count('id', filter=Q(is_late=True)),
            early_departure_count=Count('id', filter=Q(is_early_departure=True)),
            avg_hours=Avg('total_hours')
        ).order_by('date')
        
        # Department-wise statistics
        dept_stats = attendance_records.values(
            'employee__department__name'
        ).annotate(
            total_records=Count('id'),
            late_arrivals=Count('id', filter=Q(is_late=True)),
            early_departures=Count('id', filter=Q(is_early_departure=True)),
            avg_hours=Avg('total_hours')
        ).order_by('-total_records')
        
        # Top performers (least late arrivals)
        top_performers = attendance_records.values(
            'employee__full_name',
            'employee__employee_number'
        ).annotate(
            total_days=Count('id'),
            late_days=Count('id', filter=Q(is_late=True)),
            punctuality_rate=Count('id', filter=Q(is_late=False)) * 100.0 / Count('id')
        ).order_by('-punctuality_rate')[:10]
        
        return Response({
            'period': {'start_date': start_date, 'end_date': end_date},
            'summary': {
                'total_records': total_records,
                'late_arrivals': late_arrivals,
                'early_departures': early_departures,
                'punctuality_rate': ((total_records - late_arrivals) / total_records * 100) if total_records > 0 else 0,
                'avg_working_hours': attendance_records.aggregate(avg=Avg('total_hours'))['avg'] or 0
            },
            'daily_trend': list(daily_stats),
            'department_stats': list(dept_stats),
            'top_performers': list(top_performers)
        })
    
    @action(detail=False, methods=['get'])
    def leave_analytics(self, request):
        """Get leave analytics"""
        year = int(request.query_params.get('year', timezone.now().year))
        department_id = request.query_params.get('department_id')
        
        filters = {
            'start_date__year': year
        }
        
        if department_id:
            filters['employee__department_id'] = department_id
        
        leave_requests = LeaveRequest.objects.filter(**filters)
        
        # Overall statistics
        total_requests = leave_requests.count()
        approved_requests = leave_requests.filter(status='approved').count()
        pending_requests = leave_requests.filter(status='pending').count()
        rejected_requests = leave_requests.filter(status='rejected').count()
        
        # Leave type distribution
        leave_type_stats = leave_requests.values(
            'leave_type__name'
        ).annotate(
            total_requests=Count('id'),
            approved_requests=Count('id', filter=Q(status='approved')),
            total_days=Sum('days', filter=Q(status='approved'))
        ).order_by('-total_requests')
        
        # Monthly trend
        monthly_stats = leave_requests.values(
            'start_date__month'
        ).annotate(
            total_requests=Count('id'),
            approved_requests=Count('id', filter=Q(status='approved')),
            total_days=Sum('days', filter=Q(status='approved'))
        ).order_by('start_date__month')
        
        # Department-wise statistics
        dept_stats = leave_requests.values(
            'employee__department__name'
        ).annotate(
            total_requests=Count('id'),
            approved_requests=Count('id', filter=Q(status='approved')),
            total_days=Sum('days', filter=Q(status='approved')),
            avg_days_per_employee=Avg('days', filter=Q(status='approved'))
        ).order_by('-total_requests')
        
        # Most frequent leave takers
        frequent_leave_takers = leave_requests.filter(
            status='approved'
        ).values(
            'employee__full_name',
            'employee__employee_number'
        ).annotate(
            total_requests=Count('id'),
            total_days=Sum('days')
        ).order_by('-total_days')[:10]
        
        return Response({
            'year': year,
            'summary': {
                'total_requests': total_requests,
                'approved_requests': approved_requests,
                'pending_requests': pending_requests,
                'rejected_requests': rejected_requests,
                'approval_rate': (approved_requests / total_requests * 100) if total_requests > 0 else 0,
                'total_approved_days': leave_requests.filter(status='approved').aggregate(total=Sum('days'))['total'] or 0
            },
            'leave_type_distribution': list(leave_type_stats),
            'monthly_trend': list(monthly_stats),
            'department_stats': list(dept_stats),
            'frequent_leave_takers': list(frequent_leave_takers)
        })
    
    @action(detail=False, methods=['get'])
    def payroll_analytics(self, request):
        """Get payroll analytics"""
        year = int(request.query_params.get('year', timezone.now().year))
        month = request.query_params.get('month')
        department_id = request.query_params.get('department_id')
        
        filters = {
            'payroll_period__start_date__year': year
        }
        
        if month:
            filters['payroll_period__start_date__month'] = int(month)
        
        if department_id:
            filters['employee__department_id'] = department_id
        
        payroll_entries = PayrollEntry.objects.filter(**filters)
        
        # Overall statistics
        total_entries = payroll_entries.count()
        total_gross_salary = payroll_entries.aggregate(total=Sum('gross_salary'))['total'] or 0
        total_deductions = payroll_entries.aggregate(total=Sum('total_deductions'))['total'] or 0
        total_net_salary = payroll_entries.aggregate(total=Sum('net_salary'))['total'] or 0
        avg_salary = payroll_entries.aggregate(avg=Avg('net_salary'))['avg'] or 0
        
        # Department-wise salary distribution
        dept_salary_stats = payroll_entries.values(
            'employee__department__name'
        ).annotate(
            employee_count=Count('employee', distinct=True),
            total_gross=Sum('gross_salary'),
            total_net=Sum('net_salary'),
            avg_salary=Avg('net_salary')
        ).order_by('-total_net')
        
        # Salary ranges distribution
        salary_ranges = {
            '0-5000': payroll_entries.filter(net_salary__lt=5000).count(),
            '5000-10000': payroll_entries.filter(net_salary__gte=5000, net_salary__lt=10000).count(),
            '10000-15000': payroll_entries.filter(net_salary__gte=10000, net_salary__lt=15000).count(),
            '15000-20000': payroll_entries.filter(net_salary__gte=15000, net_salary__lt=20000).count(),
            '20000+': payroll_entries.filter(net_salary__gte=20000).count()
        }
        
        # Monthly payroll trend (if not filtered by month)
        monthly_trend = []
        if not month:
            monthly_trend = payroll_entries.values(
                'payroll_period__start_date__month'
            ).annotate(
                total_gross=Sum('gross_salary'),
                total_net=Sum('net_salary'),
                employee_count=Count('employee', distinct=True)
            ).order_by('payroll_period__start_date__month')
        
        # Top earners
        top_earners = payroll_entries.values(
            'employee__full_name',
            'employee__employee_number'
        ).annotate(
            avg_net_salary=Avg('net_salary'),
            total_paid=Sum('net_salary')
        ).order_by('-avg_net_salary')[:10]
        
        return Response({
            'period': {'year': year, 'month': month},
            'summary': {
                'total_entries': total_entries,
                'total_gross_salary': float(total_gross_salary),
                'total_deductions': float(total_deductions),
                'total_net_salary': float(total_net_salary),
                'average_salary': float(avg_salary),
                'deduction_rate': (total_deductions / total_gross_salary * 100) if total_gross_salary > 0 else 0
            },
            'department_distribution': [
                {
                    'department': item['employee__department__name'],
                    'employee_count': item['employee_count'],
                    'total_gross': float(item['total_gross'] or 0),
                    'total_net': float(item['total_net'] or 0),
                    'avg_salary': float(item['avg_salary'] or 0)
                }
                for item in dept_salary_stats
            ],
            'salary_ranges': salary_ranges,
            'monthly_trend': [
                {
                    'month': item['payroll_period__start_date__month'],
                    'total_gross': float(item['total_gross'] or 0),
                    'total_net': float(item['total_net'] or 0),
                    'employee_count': item['employee_count']
                }
                for item in monthly_trend
            ],
            'top_earners': [
                {
                    'employee_name': item['employee__full_name'],
                    'employee_number': item['employee__employee_number'],
                    'avg_net_salary': float(item['avg_net_salary'] or 0),
                    'total_paid': float(item['total_paid'] or 0)
                }
                for item in top_earners
            ]
        })
    
    @action(detail=False, methods=['get'])
    def department_analytics(self, request):
        """Get department-wise analytics"""
        company_id = request.query_params.get('company_id')
        
        filters = {}
        if company_id:
            filters['branch__company_id'] = company_id
        
        departments = Department.objects.filter(**filters, is_active=True)
        
        dept_analytics = []
        for dept in departments:
            employees = Employee.objects.filter(department=dept, status='active')
            
            # Attendance statistics (last 30 days)
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            attendance_records = AttendanceRecord.objects.filter(
                employee__department=dept,
                date__gte=thirty_days_ago
            )
            
            # Leave statistics (current year)
            leave_requests = LeaveRequest.objects.filter(
                employee__department=dept,
                start_date__year=timezone.now().year
            )
            
            dept_analytics.append({
                'department': {
                    'id': str(dept.id),
                    'name': dept.name,
                    'manager': dept.manager.full_name if dept.manager else None
                },
                'employees': {
                    'total': employees.count(),
                    'by_employment_type': dict(employees.values_list('employment_type').annotate(Count('id')))
                },
                'attendance': {
                    'total_records_30_days': attendance_records.count(),
                    'late_arrivals_30_days': attendance_records.filter(is_late=True).count(),
                    'punctuality_rate': ((attendance_records.count() - attendance_records.filter(is_late=True).count()) / attendance_records.count() * 100) if attendance_records.count() > 0 else 0
                },
                'leaves': {
                    'total_requests_this_year': leave_requests.count(),
                    'approved_requests': leave_requests.filter(status='approved').count(),
                    'pending_requests': leave_requests.filter(status='pending').count()
                }
            })
        
        return Response({
            'departments': dept_analytics,
            'summary': {
                'total_departments': len(dept_analytics),
                'total_employees': sum(d['employees']['total'] for d in dept_analytics),
                'avg_employees_per_dept': sum(d['employees']['total'] for d in dept_analytics) / len(dept_analytics) if dept_analytics else 0
            }
        })
    
    @action(detail=False, methods=['get'])
    def custom_report(self, request):
        """Generate custom analytics report"""
        report_type = request.query_params.get('type')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        filters = request.query_params.dict()
        
        # Remove non-filter parameters
        filters.pop('type', None)
        filters.pop('start_date', None)
        filters.pop('end_date', None)
        
        try:
            report_service = ReportService()
            
            if report_type == 'employee_summary':
                data = report_service.generate_employee_report(
                    format='json',
                    **filters
                )
            elif report_type == 'attendance_summary':
                data = report_service.generate_attendance_summary(
                    start_date=start_date,
                    end_date=end_date,
                    **filters
                )
            elif report_type == 'leave_summary':
                data = report_service.generate_leave_report(
                    start_date=start_date,
                    end_date=end_date,
                    format='json',
                    **filters
                )
            else:
                return Response({'status': 'error', 'message': 'نوع التقرير غير مدعوم'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'status': 'success',
                'report_type': report_type,
                'data': data
            })
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get trend analysis for various HR metrics"""
        months = int(request.query_params.get('months', 12))  # Default to 12 months
        company_id = request.query_params.get('company_id')
        
        # Calculate date range
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1) - timedelta(days=months*30)  # Approximate
        
        trends = {}
        
        # Employee count trend
        employee_trend = []
        current_date = start_date
        while current_date <= end_date:
            filters = {'hire_date__lte': current_date, 'status': 'active'}
            if company_id:
                filters['company_id'] = company_id
            
            count = Employee.objects.filter(**filters).count()
            employee_trend.append({
                'date': current_date.isoformat(),
                'count': count
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        trends['employee_count'] = employee_trend
        
        # Attendance trend (monthly averages)
        attendance_trend = AttendanceRecord.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).extra(
            select={'month': 'EXTRACT(month FROM date)', 'year': 'EXTRACT(year FROM date)'}
        ).values('month', 'year').annotate(
            total_records=Count('id'),
            late_arrivals=Count('id', filter=Q(is_late=True)),
            avg_hours=Avg('total_hours')
        ).order_by('year', 'month')
        
        trends['attendance'] = list(attendance_trend)
        
        # Leave requests trend
        leave_trend = LeaveRequest.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).extra(
            select={'month': 'EXTRACT(month FROM created_at)', 'year': 'EXTRACT(year FROM created_at)'}
        ).values('month', 'year').annotate(
            total_requests=Count('id'),
            approved_requests=Count('id', filter=Q(status='approved'))
        ).order_by('year', 'month')
        
        trends['leave_requests'] = list(leave_trend)
        
        return Response({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'months': months
            },
            'trends': trends
        })