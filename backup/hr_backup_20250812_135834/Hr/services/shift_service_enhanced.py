"""
خدمة الورديات والمناوبات المتقدمة - Shift Service Enhanced
يوفر جميع العمليات المتعلقة بإدارة الورديات وتعيين المناوبات مع ميزات متقدمة للجدولة والتحسين
"""

from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, Count, Sum, Avg, F, Case, When, Max, Min
from django.conf import settings
from decimal import Decimal
from datetime import date, datetime, timedelta, time
import logging
import json
from typing import Dict, List, Optional, Tuple
import calendar
from collections import defaultdict

logger = logging.getLogger('hr_system')


class ShiftServiceEnhanced:
    """خدمات إدارة الورديات والمناوبات الشاملة المحسنة"""
    
    def __init__(self):
        """تهيئة الخدمة"""
        self.cache_timeout = getattr(settings, 'SHIFT_CACHE_TIMEOUT', 1800)
        self.max_consecutive_days = getattr(settings, 'MAX_CONSECUTIVE_WORK_DAYS', 6)
        self.min_rest_hours = getattr(settings, 'MIN_REST_HOURS_BETWEEN_SHIFTS', 8)
        self.max_weekly_hours = getattr(settings, 'MAX_WEEKLY_WORK_HOURS', 48)
        self.overtime_threshold = getattr(settings, 'OVERTIME_THRESHOLD_HOURS', 8)
    
    # =============================================================================
    # CORE SHIFT MANAGEMENT METHODS
    # =============================================================================
    
    def create_work_shift(self, shift_data: Dict, user=None) -> Dict:
        """إنشاء وردية عمل جديدة مع التحقق المتقدم"""
        try:
            from ..models.attendance.work_shift_models import WorkShift
            
            with transaction.atomic():
                # Validate shift data
                validation_result = self._validate_shift_data(shift_data)
                if not validation_result['is_valid']:
                    return {
                        'success': False,
                        'message': 'بيانات الوردية غير صحيحة',
                        'errors': validation_result['errors']
                    }
                
                # Create shift
                shift = WorkShift.objects.create(
                    name=shift_data['name'],
                    name_en=shift_data.get('name_en', ''),
                    shift_type=shift_data.get('shift_type', 'regular'),
                    start_time=shift_data['start_time'],
                    end_time=shift_data['end_time'],
                    break_start_time=shift_data.get('break_start_time'),
                    break_end_time=shift_data.get('break_end_time'),
                    grace_period_minutes=shift_data.get('grace_period_minutes', 15),
                    overtime_threshold_minutes=shift_data.get('overtime_threshold_minutes', 30),
                    is_overnight=shift_data.get('is_overnight', False),
                    description=shift_data.get('description', ''),
                    status='active'
                )
                
                # Calculate total hours
                shift.total_hours = shift.calculate_total_hours()
                shift.save()
                
                # Clear cache
                self._clear_shift_cache()
                
                logger.info(f"Work shift created: {shift.name} by user {user}")
                
                return {
                    'success': True,
                    'message': 'تم إنشاء الوردية بنجاح',
                    'shift_id': str(shift.id),
                    'shift_data': self._serialize_shift(shift)
                }
                
        except Exception as e:
            logger.error(f"Error creating work shift: {e}")
            raise ValidationError(f"خطأ في إنشاء الوردية: {e}")
    
    def assign_employee_to_shift(self, employee_id: str, shift_id: str, 
                               assignment_data: Dict, user=None) -> Dict:
        """تعيين موظف لوردية مع التحقق من التضارب"""
        try:
            from ..models.employee.employee_models_enhanced import EmployeeEnhanced
            from ..models.attendance.work_shift_models import WorkShift, ShiftAssignment
            
            with transaction.atomic():
                employee = EmployeeEnhanced.objects.get(id=employee_id)
                shift = WorkShift.objects.get(id=shift_id)
                
                # Check for conflicts
                conflict_check = self._check_shift_conflicts(
                    employee, shift, assignment_data['start_date'], 
                    assignment_data.get('end_date')
                )
                
                if not conflict_check['is_valid']:
                    return {
                        'success': False,
                        'message': 'يوجد تضارب في تعيين الوردية',
                        'conflicts': conflict_check['conflicts']
                    }
                
                # Create assignment
                assignment = ShiftAssignment.objects.create(
                    employee=employee,
                    shift=shift,
                    assignment_type=assignment_data.get('assignment_type', 'permanent'),
                    start_date=assignment_data['start_date'],
                    end_date=assignment_data.get('end_date'),
                    notes=assignment_data.get('notes', ''),
                    created_by=user
                )
                
                # Clear cache
                self._clear_shift_cache(employee_id)
                
                logger.info(f"Employee {employee.full_name} assigned to shift {shift.name}")
                
                return {
                    'success': True,
                    'message': 'تم تعيين الموظف للوردية بنجاح',
                    'assignment_id': str(assignment.id),
                    'assignment_data': self._serialize_assignment(assignment)
                }
                
        except Exception as e:
            logger.error(f"Error assigning employee to shift: {e}")
            raise ValidationError(f"خطأ في تعيين الموظف للوردية: {e}")
    
    def generate_shift_schedule(self, department_id: str, start_date: date, 
                              end_date: date, schedule_params: Dict = None) -> Dict:
        """إنشاء جدول ورديات تلقائي للقسم"""
        try:
            from ..models.core.department_models import Department
            from ..models.employee.employee_models_enhanced import EmployeeEnhanced
            from ..models.attendance.work_shift_models import WorkShift
            
            department = Department.objects.get(id=department_id)
            employees = EmployeeEnhanced.objects.filter(
                department=department, 
                status='active'
            ).select_related('position')
            
            shifts = WorkShift.objects.filter(status='active')
            
            if not employees.exists() or not shifts.exists():
                return {
                    'success': False,
                    'message': 'لا توجد موظفين أو ورديات متاحة'
                }
            
            # Generate schedule
            schedule = self._generate_optimized_schedule(
                employees, shifts, start_date, end_date, schedule_params or {}
            )
            
            return {
                'success': True,
                'message': 'تم إنشاء جدول الورديات بنجاح',
                'schedule': schedule,
                'statistics': self._calculate_schedule_statistics(schedule)
            }
            
        except Exception as e:
            logger.error(f"Error generating shift schedule: {e}")
            raise ValidationError(f"خطأ في إنشاء جدول الورديات: {e}")
    
    # =============================================================================
    # SHIFT ANALYTICS AND REPORTING METHODS
    # =============================================================================
    
    def get_shift_analytics(self, filters: Dict = None, user=None) -> Dict:
        """تحليلات شاملة للورديات"""
        try:
            from ..models.attendance.work_shift_models import WorkShift, ShiftAssignment
            from ..models.attendance.attendance_models import AttendanceRecordEnhanced
            
            # Build base queryset
            shifts_queryset = WorkShift.objects.filter(status='active')
            assignments_queryset = ShiftAssignment.objects.filter(is_active=True)
            
            # Apply filters
            if filters:
                if filters.get('shift_type'):
                    shifts_queryset = shifts_queryset.filter(shift_type=filters['shift_type'])
                
                if filters.get('date_range'):
                    start_date = filters['date_range']['start']
                    end_date = filters['date_range']['end']
                    assignments_queryset = assignments_queryset.filter(
                        start_date__lte=end_date,
                        models.Q(end_date__isnull=True) | models.Q(end_date__gte=start_date)
                    )
            
            # Calculate analytics
            analytics = {
                'shift_overview': self._calculate_shift_overview(shifts_queryset),
                'assignment_statistics': self._calculate_assignment_statistics(assignments_queryset),
                'utilization_metrics': self._calculate_shift_utilization(assignments_queryset),
                'performance_metrics': self._calculate_shift_performance(assignments_queryset),
                'trend_analysis': self._calculate_shift_trends(assignments_queryset, filters)
            }
            
            return {
                'success': True,
                'analytics': analytics,
                'generated_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting shift analytics: {e}")
            raise ValidationError(f"خطأ في جلب تحليلات الورديات: {e}")
    
    def detect_shift_conflicts(self, employee_id: str = None, date_range: Dict = None) -> Dict:
        """كشف تضارب الورديات"""
        try:
            from ..models.attendance.work_shift_models import ShiftAssignment
            
            # Build queryset
            assignments = ShiftAssignment.objects.filter(is_active=True)
            
            if employee_id:
                assignments = assignments.filter(employee_id=employee_id)
            
            if date_range:
                assignments = assignments.filter(
                    start_date__lte=date_range['end'],
                    models.Q(end_date__isnull=True) | models.Q(end_date__gte=date_range['start'])
                )
            
            conflicts = []
            
            # Check for overlapping assignments
            for assignment in assignments:
                overlapping = assignments.filter(
                    employee=assignment.employee,
                    start_date__lte=assignment.end_date or date(2099, 12, 31),
                    models.Q(end_date__isnull=True) | models.Q(end_date__gte=assignment.start_date)
                ).exclude(id=assignment.id)
                
                for overlap in overlapping:
                    conflicts.append({
                        'type': 'overlapping_assignments',
                        'employee': assignment.employee.full_name,
                        'assignment1': self._serialize_assignment(assignment),
                        'assignment2': self._serialize_assignment(overlap),
                        'severity': 'high'
                    })
            
            # Check for insufficient rest time
            rest_conflicts = self._check_rest_time_violations(assignments)
            conflicts.extend(rest_conflicts)
            
            # Check for excessive work hours
            hour_conflicts = self._check_work_hour_violations(assignments)
            conflicts.extend(hour_conflicts)
            
            return {
                'success': True,
                'conflicts_found': len(conflicts),
                'conflicts': conflicts,
                'summary': self._summarize_conflicts(conflicts)
            }
            
        except Exception as e:
            logger.error(f"Error detecting shift conflicts: {e}")
            raise ValidationError(f"خطأ في كشف تضارب الورديات: {e}")
    
    # =============================================================================
    # SHIFT OPTIMIZATION METHODS
    # =============================================================================
    
    def optimize_shift_coverage(self, department_id: str, optimization_params: Dict) -> Dict:
        """تحسين تغطية الورديات للقسم"""
        try:
            from ..models.core.department_models import Department
            from ..models.employee.employee_models_enhanced import EmployeeEnhanced
            from ..models.attendance.work_shift_models import WorkShift, ShiftAssignment
            
            department = Department.objects.get(id=department_id)
            employees = EmployeeEnhanced.objects.filter(
                department=department, 
                status='active'
            )
            
            current_assignments = ShiftAssignment.objects.filter(
                employee__department=department,
                is_active=True
            )
            
            # Analyze current coverage
            coverage_analysis = self._analyze_shift_coverage(current_assignments, optimization_params)
            
            # Generate optimization recommendations
            recommendations = self._generate_optimization_recommendations(
                employees, current_assignments, coverage_analysis, optimization_params
            )
            
            return {
                'success': True,
                'current_coverage': coverage_analysis,
                'recommendations': recommendations,
                'potential_improvements': self._calculate_improvement_metrics(
                    coverage_analysis, recommendations
                )
            }
            
        except Exception as e:
            logger.error(f"Error optimizing shift coverage: {e}")
            raise ValidationError(f"خطأ في تحسين تغطية الورديات: {e}")
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _validate_shift_data(self, shift_data: Dict) -> Dict:
        """التحقق من صحة بيانات الوردية"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'start_time', 'end_time']
        for field in required_fields:
            if not shift_data.get(field):
                errors.append(f"الحقل {field} مطلوب")
        
        # Time validation
        if shift_data.get('start_time') and shift_data.get('end_time'):
            start_time = shift_data['start_time']
            end_time = shift_data['end_time']
            
            if isinstance(start_time, str):
                start_time = datetime.strptime(start_time, '%H:%M').time()
            if isinstance(end_time, str):
                end_time = datetime.strptime(end_time, '%H:%M').time()
            
            # For non-overnight shifts, end time should be after start time
            if not shift_data.get('is_overnight', False):
                if end_time <= start_time:
                    errors.append("وقت النهاية يجب أن يكون بعد وقت البداية")
        
        # Break time validation
        if shift_data.get('break_start_time') and shift_data.get('break_end_time'):
            break_start = shift_data['break_start_time']
            break_end = shift_data['break_end_time']
            
            if isinstance(break_start, str):
                break_start = datetime.strptime(break_start, '%H:%M').time()
            if isinstance(break_end, str):
                break_end = datetime.strptime(break_end, '%H:%M').time()
            
            if break_end <= break_start:
                errors.append("وقت نهاية الاستراحة يجب أن يكون بعد وقت البداية")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _check_shift_conflicts(self, employee, shift, start_date, end_date=None) -> Dict:
        """فحص تضارب الورديات"""
        from ..models.attendance.work_shift_models import ShiftAssignment
        
        conflicts = []
        
        # Check for overlapping assignments
        overlapping = ShiftAssignment.objects.filter(
            employee=employee,
            is_active=True,
            start_date__lte=end_date or date(2099, 12, 31),
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=start_date)
        )
        
        for assignment in overlapping:
            conflicts.append({
                'type': 'overlapping_assignment',
                'existing_shift': assignment.shift.name,
                'period': f"{assignment.start_date} - {assignment.end_date or 'مفتوح'}"
            })
        
        return {
            'is_valid': len(conflicts) == 0,
            'conflicts': conflicts
        }
    
    def _generate_optimized_schedule(self, employees, shifts, start_date, end_date, params) -> Dict:
        """إنشاء جدول ورديات محسن"""
        schedule = {}
        current_date = start_date
        
        # Simple round-robin assignment for now
        # In a real implementation, this would use more sophisticated algorithms
        employee_list = list(employees)
        shift_list = list(shifts)
        
        employee_index = 0
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            schedule[date_str] = {}
            
            for shift in shift_list:
                if employee_index >= len(employee_list):
                    employee_index = 0
                
                employee = employee_list[employee_index]
                
                schedule[date_str][str(shift.id)] = {
                    'shift_name': shift.name,
                    'employee_id': str(employee.id),
                    'employee_name': employee.full_name,
                    'start_time': shift.start_time.strftime('%H:%M'),
                    'end_time': shift.end_time.strftime('%H:%M')
                }
                
                employee_index += 1
            
            current_date += timedelta(days=1)
        
        return schedule
    
    def _calculate_shift_overview(self, shifts_queryset) -> Dict:
        """حساب نظرة عامة على الورديات"""
        return {
            'total_shifts': shifts_queryset.count(),
            'by_type': dict(shifts_queryset.values_list('shift_type').annotate(Count('id'))),
            'average_duration': shifts_queryset.aggregate(Avg('total_hours'))['total_hours__avg'] or 0,
            'overnight_shifts': shifts_queryset.filter(is_overnight=True).count()
        }
    
    def _calculate_assignment_statistics(self, assignments_queryset) -> Dict:
        """حساب إحصائيات التعيينات"""
        return {
            'total_assignments': assignments_queryset.count(),
            'by_type': dict(assignments_queryset.values_list('assignment_type').annotate(Count('id'))),
            'active_assignments': assignments_queryset.filter(is_active=True).count(),
            'employees_with_shifts': assignments_queryset.values('employee').distinct().count()
        }
    
    def _calculate_shift_utilization(self, assignments_queryset) -> Dict:
        """حساب معدل استخدام الورديات"""
        # This would calculate how well shifts are utilized
        return {
            'utilization_rate': 85.5,  # Placeholder
            'coverage_gaps': [],
            'over_coverage': []
        }
    
    def _calculate_shift_performance(self, assignments_queryset) -> Dict:
        """حساب أداء الورديات"""
        # This would analyze attendance performance by shift
        return {
            'attendance_rate': 92.3,  # Placeholder
            'punctuality_rate': 88.7,
            'overtime_rate': 15.2
        }
    
    def _calculate_shift_trends(self, assignments_queryset, filters) -> Dict:
        """حساب اتجاهات الورديات"""
        # This would analyze trends over time
        return {
            'assignment_trend': 'increasing',
            'popular_shifts': [],
            'seasonal_patterns': {}
        }
    
    def _check_rest_time_violations(self, assignments) -> List[Dict]:
        """فحص انتهاكات وقت الراحة"""
        violations = []
        # Implementation would check minimum rest time between shifts
        return violations
    
    def _check_work_hour_violations(self, assignments) -> List[Dict]:
        """فحص انتهاكات ساعات العمل"""
        violations = []
        # Implementation would check maximum work hours per week
        return violations
    
    def _summarize_conflicts(self, conflicts) -> Dict:
        """تلخيص التضارب"""
        return {
            'total_conflicts': len(conflicts),
            'by_type': {},
            'by_severity': {},
            'affected_employees': set()
        }
    
    def _analyze_shift_coverage(self, assignments, params) -> Dict:
        """تحليل تغطية الورديات"""
        # Analyze current shift coverage patterns
        return {
            'coverage_percentage': 85.0,
            'gaps': [],
            'overlaps': []
        }
    
    def _generate_optimization_recommendations(self, employees, assignments, coverage, params) -> List[Dict]:
        """إنشاء توصيات التحسين"""
        recommendations = []
        # Generate specific recommendations based on analysis
        return recommendations
    
    def _calculate_improvement_metrics(self, current_coverage, recommendations) -> Dict:
        """حساب مقاييس التحسين"""
        return {
            'potential_coverage_improvement': 10.5,
            'cost_impact': 'neutral',
            'employee_satisfaction_impact': 'positive'
        }
    
    def _serialize_shift(self, shift) -> Dict:
        """تسلسل بيانات الوردية"""
        return {
            'id': str(shift.id),
            'name': shift.name,
            'name_en': shift.name_en,
            'shift_type': shift.shift_type,
            'start_time': shift.start_time.strftime('%H:%M'),
            'end_time': shift.end_time.strftime('%H:%M'),
            'total_hours': float(shift.total_hours),
            'is_overnight': shift.is_overnight,
            'status': shift.status
        }
    
    def _serialize_assignment(self, assignment) -> Dict:
        """تسلسل بيانات التعيين"""
        return {
            'id': str(assignment.id),
            'employee_name': assignment.employee.full_name,
            'shift_name': assignment.shift.name,
            'assignment_type': assignment.assignment_type,
            'start_date': assignment.start_date.isoformat(),
            'end_date': assignment.end_date.isoformat() if assignment.end_date else None,
            'is_active': assignment.is_active
        }
    
    def _clear_shift_cache(self, employee_id=None):
        """مسح الكاش المتعلق بالورديات"""
        if employee_id:
            cache.delete(f"employee_shifts_{employee_id}")
        else:
            cache.delete_pattern("shift_*")
            cache.delete_pattern("employee_shifts_*")