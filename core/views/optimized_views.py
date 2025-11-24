"""
Optimized Views with Advanced Caching and Query Optimization
==========================================================

This module provides optimized views that demonstrate the use of:
- Advanced caching strategies
- Query optimization techniques
- Performance monitoring
- Database index optimization
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q, Prefetch
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from datetime import date, timedelta
import json

from core.services.cache_service import cache_result, cache_queryset, cache_service
from core.services.query_optimizer import (
    optimize_query, 
    monitor_query_performance,
    get_optimized_employees,
    get_optimized_attendance,
    get_optimized_inventory,
    get_dashboard_stats_cached
)

# Import models with error handling
try:
    from employees.models import Employee, Department, JobPosition
    from attendance.models import EmployeeAttendance
    from leaves.models import EmployeeLeave
    from payrolls.models import PayrollRun, EmployeeSalary
    from inventory.models import TblProducts, TblCategories
except ImportError as e:
    # Handle missing models gracefully
    Employee = None
    Department = None
    JobPosition = None
    EmployeeAttendance = None
    EmployeeLeave = None
    PayrollRun = None
    EmployeeSalary = None
    TblProducts = None
    TblCategories = None


@login_required
@cache_page(300)  # Cache for 5 minutes
@vary_on_headers('User-Agent')
def optimized_dashboard(request):
    """لوحة تحكم محسنة مع تخزين مؤقت متقدم"""
    
    context = {
        'title': 'لوحة التحكم المحسنة',
        'today': date.today(),
        'now': timezone.now(),
    }
    
    # Get cached dashboard stats
    stats = get_dashboard_stats_cached()
    context.update(stats)
    
    # Get recent activities with caching
    context['recent_activities'] = get_recent_activities_cached()
    
    # Get chart data with caching
    context['chart_data'] = get_chart_data_cached()
    
    return render(request, 'core/optimized_dashboard.html', context)


@cache_result(timeout='medium', key_prefix='recent_activities')
def get_recent_activities_cached():
    """الحصول على الأنشطة الأخيرة مع التخزين المؤقت"""
    
    activities = []
    
    try:
        if Employee:
            # Recent new employees
            recent_employees = Employee.objects.filter(
                hire_date__gte=date.today() - timedelta(days=7)
            ).select_related('dept', 'job')[:5]
            
            for emp in recent_employees:
                activities.append({
                    'title': f'موظف جديد: {emp.first_name} {emp.last_name}',
                    'time': emp.hire_date,
                    'icon': 'fas fa-user-plus',
                    'color': '#10b981',
                    'type': 'employee'
                })
    except Exception as e:
        pass
    
    try:
        if EmployeeLeave:
            # Recent leave requests
            recent_leaves = EmployeeLeave.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=3),
                status='Pending'
            ).select_related('employee')[:5]
            
            for leave in recent_leaves:
                activities.append({
                    'title': f'طلب إجازة: {leave.employee.first_name} {leave.employee.last_name}',
                    'time': leave.created_at,
                    'icon': 'fas fa-calendar-alt',
                    'color': '#f59e0b',
                    'type': 'leave'
                })
    except Exception as e:
        pass
    
    # Sort by time (most recent first)
    activities.sort(key=lambda x: x['time'], reverse=True)
    
    return activities[:10]


@cache_result(timeout='short', key_prefix='chart_data')
def get_chart_data_cached():
    """الحصول على بيانات الرسوم البيانية مع التخزين المؤقت"""
    
    chart_data = {
        'attendance_trend': {
            'labels': [],
            'present_data': [],
            'absent_data': []
        },
        'department_distribution': {
            'labels': [],
            'data': []
        }
    }
    
    try:
        if EmployeeAttendance:
            # Attendance trend for last 7 days
            for i in range(7):
                date_check = date.today() - timedelta(days=i)
                chart_data['attendance_trend']['labels'].append(
                    date_check.strftime('%m/%d')
                )
                
                day_attendance = EmployeeAttendance.objects.filter(att_date=date_check)
                present_count = day_attendance.filter(
                    status__in=['Present', 'Late']
                ).count()
                absent_count = day_attendance.filter(status='Absent').count()
                
                chart_data['attendance_trend']['present_data'].append(present_count)
                chart_data['attendance_trend']['absent_data'].append(absent_count)
            
            # Reverse to show chronological order
            chart_data['attendance_trend']['labels'].reverse()
            chart_data['attendance_trend']['present_data'].reverse()
            chart_data['attendance_trend']['absent_data'].reverse()
    except Exception as e:
        pass
    
    try:
        if Employee and Department:
            # Department distribution
            dept_stats = Employee.objects.filter(
                emp_status='Active'
            ).values('dept__dept_name').annotate(
                count=Count('emp_id')
            ).order_by('-count')[:10]
            
            for stat in dept_stats:
                chart_data['department_distribution']['labels'].append(
                    stat['dept__dept_name'] or 'غير محدد'
                )
                chart_data['department_distribution']['data'].append(stat['count'])
    except Exception as e:
        pass
    
    return chart_data


@login_required
@monitor_query_performance
def optimized_employee_list(request):
    """قائمة الموظفين المحسنة"""
    
    # Get filters from request
    department_id = request.GET.get('department')
    job_id = request.GET.get('job')
    status = request.GET.get('status', 'Active')
    search = request.GET.get('search', '').strip()
    
    # Build cache key based on filters
    cache_key = f"employee_list_{department_id}_{job_id}_{status}_{search}"
    
    def get_employees():
        if not Employee:
            return []
        
        # Start with optimized queryset
        queryset = get_optimized_employees()
        
        # Apply filters
        if status:
            queryset = queryset.filter(emp_status=status)
        
        if department_id:
            queryset = queryset.filter(dept_id=department_id)
        
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(emp_code__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('first_name', 'last_name')
    
    # Get cached results
    employees = cache_service.get_or_set(cache_key, get_employees, 'medium')
    
    # Pagination
    paginator = Paginator(employees, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options with caching
    departments = get_departments_cached()
    job_positions = get_job_positions_cached()
    
    context = {
        'title': 'قائمة الموظفين المحسنة',
        'page_obj': page_obj,
        'departments': departments,
        'job_positions': job_positions,
        'current_filters': {
            'department': department_id,
            'job': job_id,
            'status': status,
            'search': search,
        }
    }
    
    return render(request, 'core/optimized_employee_list.html', context)


@cache_result(timeout='daily', key_prefix='departments')
def get_departments_cached():
    """الحصول على الأقسام مع التخزين المؤقت"""
    if not Department:
        return []
    
    return list(Department.objects.filter(
        is_active=True
    ).values('dept_id', 'dept_name').order_by('dept_name'))


@cache_result(timeout='daily', key_prefix='job_positions')
def get_job_positions_cached():
    """الحصول على المناصب مع التخزين المؤقت"""
    if not JobPosition:
        return []
    
    return list(JobPosition.objects.filter(
        is_active=True
    ).values('job_id', 'job_title').order_by('job_title'))


@login_required
@monitor_query_performance
def optimized_attendance_report(request):
    """تقرير الحضور المحسن"""
    
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    department_id = request.GET.get('department')
    
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    else:
        start_date = date.fromisoformat(start_date)
    
    if not end_date:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(end_date)
    
    # Build cache key
    cache_key = f"attendance_report_{start_date}_{end_date}_{department_id}"
    
    def get_attendance_data():
        if not EmployeeAttendance:
            return {
                'summary': {},
                'daily_stats': [],
                'employee_stats': []
            }
        
        # Get optimized attendance queryset
        queryset = get_optimized_attendance(start_date, end_date)
        
        if department_id:
            queryset = queryset.filter(employee__dept_id=department_id)
        
        # Calculate summary statistics
        summary = queryset.aggregate(
            total_records=Count('id'),
            present_days=Count('id', filter=Q(status__in=['Present', 'Late'])),
            absent_days=Count('id', filter=Q(status='Absent')),
            late_days=Count('id', filter=Q(status='Late'))
        )
        
        # Calculate attendance rate
        if summary['total_records'] > 0:
            summary['attendance_rate'] = (
                summary['present_days'] / summary['total_records'] * 100
            )
        else:
            summary['attendance_rate'] = 0
        
        # Daily statistics
        daily_stats = queryset.values('att_date').annotate(
            present=Count('id', filter=Q(status__in=['Present', 'Late'])),
            absent=Count('id', filter=Q(status='Absent')),
            late=Count('id', filter=Q(status='Late'))
        ).order_by('att_date')
        
        # Employee statistics
        employee_stats = queryset.values(
            'employee__first_name',
            'employee__last_name',
            'employee__dept__dept_name'
        ).annotate(
            present_days=Count('id', filter=Q(status__in=['Present', 'Late'])),
            absent_days=Count('id', filter=Q(status='Absent')),
            late_days=Count('id', filter=Q(status='Late')),
            total_days=Count('id')
        ).order_by('employee__first_name')
        
        return {
            'summary': summary,
            'daily_stats': list(daily_stats),
            'employee_stats': list(employee_stats)
        }
    
    # Get cached data
    attendance_data = cache_service.get_or_set(cache_key, get_attendance_data, 'medium')
    
    context = {
        'title': 'تقرير الحضور المحسن',
        'start_date': start_date,
        'end_date': end_date,
        'department_id': department_id,
        'departments': get_departments_cached(),
        'attendance_data': attendance_data,
    }
    
    return render(request, 'core/optimized_attendance_report.html', context)


@login_required
@monitor_query_performance
def optimized_inventory_dashboard(request):
    """لوحة تحكم المخزون المحسنة"""
    
    cache_key = 'inventory_dashboard_stats'
    
    def get_inventory_stats():
        if not TblProducts:
            return {}
        
        # Get optimized inventory queryset
        products = get_optimized_inventory()
        
        # Calculate statistics
        stats = products.aggregate(
            total_products=Count('product_id'),
            total_value=Sum('unit_price'),
            low_stock_items=Count(
                'product_id',
                filter=Q(qte_in_stock__lte=models.F('minimum_threshold'))
            ),
            out_of_stock=Count('product_id', filter=Q(qte_in_stock=0))
        )
        
        # Category distribution
        if TblCategories:
            category_stats = products.values(
                'cat__cat_name'
            ).annotate(
                count=Count('product_id'),
                total_stock=Sum('qte_in_stock')
            ).order_by('-count')[:10]
            
            stats['category_distribution'] = list(category_stats)
        
        # Top products by value
        top_products = products.filter(
            unit_price__isnull=False,
            qte_in_stock__gt=0
        ).annotate(
            total_value=models.F('unit_price') * models.F('qte_in_stock')
        ).order_by('-total_value')[:10]
        
        stats['top_products'] = list(top_products.values(
            'product_name', 'qte_in_stock', 'unit_price', 'total_value'
        ))
        
        # Low stock alerts
        low_stock = products.filter(
            qte_in_stock__lte=models.F('minimum_threshold'),
            minimum_threshold__gt=0
        ).order_by('qte_in_stock')[:20]
        
        stats['low_stock_alerts'] = list(low_stock.values(
            'product_name', 'qte_in_stock', 'minimum_threshold', 'cat__cat_name'
        ))
        
        return stats
    
    # Get cached inventory stats
    inventory_stats = cache_service.get_or_set(cache_key, get_inventory_stats, 'short')
    
    context = {
        'title': 'لوحة تحكم المخزون المحسنة',
        'inventory_stats': inventory_stats,
    }
    
    return render(request, 'core/optimized_inventory_dashboard.html', context)


@login_required
def cache_invalidation_api(request):
    """API لإبطال التخزين المؤقت"""
    
    if request.method == 'POST':
        cache_type = request.POST.get('cache_type')
        object_id = request.POST.get('object_id')
        
        try:
            from core.services.cache_service import cache_invalidation_service
            
            if cache_type == 'employee' and object_id:
                cache_invalidation_service.invalidate_employee_cache(int(object_id))
                message = f'تم إبطال تخزين الموظف {object_id} مؤقتاً'
            
            elif cache_type == 'department' and object_id:
                cache_invalidation_service.invalidate_department_cache(int(object_id))
                message = f'تم إبطال تخزين القسم {object_id} مؤقتاً'
            
            elif cache_type == 'attendance':
                cache_invalidation_service.invalidate_attendance_cache()
                message = 'تم إبطال تخزين الحضور مؤقتاً'
            
            elif cache_type == 'inventory':
                cache_invalidation_service.invalidate_inventory_cache()
                message = 'تم إبطال تخزين المخزون مؤقتاً'
            
            elif cache_type == 'dashboard':
                cache_service.delete_pattern('dashboard_*')
                cache_service.delete_pattern('dash_*')
                message = 'تم إبطال تخزين لوحة التحكم مؤقتاً'
            
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'نوع التخزين المؤقت غير مدعوم'
                })
            
            return JsonResponse({
                'success': True,
                'message': message
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطأ في إبطال التخزين المؤقت: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'طريقة غير مدعومة'
    })


@login_required
def performance_metrics_api(request):
    """API لمقاييس الأداء"""
    
    try:
        from core.services.query_optimizer import performance_monitor
        from core.services.cache_service import cache_performance_monitor
        
        # Get query performance stats
        query_stats = performance_monitor.get_query_stats()
        
        # Get cache performance stats
        cache_stats = cache_performance_monitor.get_performance_stats()
        
        # Get slow queries
        slow_queries = performance_monitor.get_slow_queries(limit=10)
        
        data = {
            'query_performance': query_stats,
            'cache_performance': cache_stats,
            'slow_queries': slow_queries,
            'timestamp': timezone.now().isoformat(),
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)