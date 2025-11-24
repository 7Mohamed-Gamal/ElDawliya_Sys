"""
خدمة نظام التقييمات
Employee Evaluation System Service
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import date, timedelta
from core.services.base import BaseService
from core.models.evaluations import (
    EvaluationTemplate, EvaluationCriteria, EvaluationPeriod,
    EmployeeEvaluation, EvaluationScore, EvaluationGoal,
    PerformanceReview, TrainingRecommendation
)


class EvaluationService(BaseService):
    """
    خدمة نظام التقييمات الشاملة
    Comprehensive employee evaluation system service
    """

    def create_evaluation_template(self, data):
        """
        إنشاء قالب تقييم جديد
        Create new evaluation template
        """
        self.check_permission('evaluations.add_evaluationtemplate')

        required_fields = ['name', 'description', 'evaluation_type']
        self.validate_required_fields(data, required_fields)

        try:
            with transaction.atomic():
                # Create evaluation template
                template = EvaluationTemplate.objects.create(
                    name=data['name'],
                    description=data['description'],
                    evaluation_type=data['evaluation_type'],
                    max_score=data.get('max_score', 100),
                    passing_score=data.get('passing_score', 60),
                    is_active=data.get('is_active', True),
                    created_by=self.user,
                    updated_by=self.user
                )

                # Add evaluation criteria
                if data.get('criteria'):
                    self._add_evaluation_criteria(template, data['criteria'])

                # Log the action
                self.log_action(
                    action='create',
                    resource='evaluation_template',
                    content_object=template,
                    new_values=data,
                    message=f'تم إنشاء قالب تقييم جديد: {template.name}'
                )

                return self.format_response(
                    data={'template_id': template.id},
                    message='تم إنشاء قالب التقييم بنجاح'
                )

        except Exception as e:
            return self.handle_exception(e, 'create_evaluation_template', 'evaluation_template', data)

    def start_evaluation_period(self, data):
        """
        بدء فترة تقييم جديدة
        Start new evaluation period
        """
        self.check_permission('evaluations.add_evaluationperiod')

        required_fields = ['name', 'start_date', 'end_date', 'template_id']
        self.validate_required_fields(data, required_fields)

        try:
            template = EvaluationTemplate.objects.get(id=data['template_id'])

            # Check for overlapping periods
            overlapping = EvaluationPeriod.objects.filter(
                template=template,
                start_date__lte=data['end_date'],
                end_date__gte=data['start_date'],
                status__in=['active', 'pending']
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exists()

            if overlapping:
                return self.format_response(
                    success=False,
                    message='يوجد فترة تقييم متداخلة مع هذه الفترة'
                )

            with transaction.atomic():
                # Create evaluation period
                period = EvaluationPeriod.objects.create(
                    name=data['name'],
                    description=data.get('description', ''),
                    template=template,
                    start_date=data['start_date'],
                    end_date=data['end_date'],
                    status='active',
                    created_by=self.user,
                    updated_by=self.user
                )

                # Create evaluations for eligible employees
                if data.get('auto_create_evaluations', True):
                    created_count = self._create_employee_evaluations(period, data.get('department_ids'))
                else:
                    created_count = 0

                # Log the action
                self.log_action(
                    action='create',
                    resource='evaluation_period',
                    content_object=period,
                    details={
                        'template_id': template.id,
                        'evaluations_created': created_count
                    },
                    message=f'تم بدء فترة تقييم جديدة: {period.name}'
                )

                return self.format_response(
                    data={
                        'period_id': period.id,
                        'evaluations_created': created_count
                    },
                    message=f'تم بدء فترة التقييم وإنشاء {created_count} تقييم'
                )

        except EvaluationTemplate.DoesNotExist:
            return self.format_response(
                success=False,
                message='قالب التقييم غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'start_evaluation_period', 'evaluation_period', data)

    def submit_evaluation(self, evaluation_id, scores_data, comments=None):
        """
        تقديم التقييم
        Submit evaluation scores
        """
        self.check_permission('evaluations.change_employeeevaluation')

        try:
            evaluation = EmployeeEvaluation.objects.select_related(
                'employee', 'evaluator', 'period', 'period__template'
            ).get(id=evaluation_id)

            # Check if user can submit this evaluation
            if evaluation.evaluator != self.user and not self.user.has_perm('evaluations.manage_all_evaluations'):
                return self.format_response(
                    success=False,
                    message='ليس لديك صلاحية تقديم هذا التقييم'
                )

            if evaluation.status != 'pending':
                return self.format_response(
                    success=False,
                    message='لا يمكن تعديل تقييم مقدم بالفعل'
                )

            with transaction.atomic():
                # Delete existing scores
                EvaluationScore.objects.filter(evaluation=evaluation).prefetch_related()  # TODO: Add appropriate prefetch_related fields.delete()

                # Add new scores
                total_score = 0
                max_possible_score = 0

                for score_data in scores_data:
                    criteria = EvaluationCriteria.objects.get(
                        id=score_data['criteria_id'],
                        template=evaluation.period.template
                    )

                    score = EvaluationScore.objects.create(
                        evaluation=evaluation,
                        criteria=criteria,
                        score=score_data['score'],
                        comments=score_data.get('comments', ''),
                        created_by=self.user,
                        updated_by=self.user
                    )

                    # Calculate weighted score
                    weighted_score = (score_data['score'] * criteria.weight) / 100
                    total_score += weighted_score
                    max_possible_score += (criteria.max_score * criteria.weight) / 100

                # Calculate final score percentage
                final_score = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0

                # Update evaluation
                evaluation.total_score = final_score
                evaluation.status = 'submitted'
                evaluation.submitted_at = timezone.now()
                evaluation.comments = comments
                evaluation.updated_by = self.user
                evaluation.save()

                # Determine performance rating
                rating = self._calculate_performance_rating(final_score, evaluation.period.template)
                evaluation.performance_rating = rating
                evaluation.save()

                # Log the action
                self.log_action(
                    action='submit',
                    resource='employee_evaluation',
                    content_object=evaluation,
                    details={
                        'total_score': final_score,
                        'performance_rating': rating,
                        'scores_count': len(scores_data)
                    },
                    message=f'تم تقديم تقييم الموظف: {evaluation.employee.get_full_name()}'
                )

                # Send notification to employee
                self._send_evaluation_notification(evaluation, 'submitted')

                return self.format_response(
                    data={
                        'evaluation_id': evaluation.id,
                        'total_score': final_score,
                        'performance_rating': rating
                    },
                    message='تم تقديم التقييم بنجاح'
                )

        except EmployeeEvaluation.DoesNotExist:
            return self.format_response(
                success=False,
                message='التقييم غير موجود'
            )
        except EvaluationCriteria.DoesNotExist:
            return self.format_response(
                success=False,
                message='معيار التقييم غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'submit_evaluation', f'evaluation/{evaluation_id}')

    def approve_evaluation(self, evaluation_id, action, feedback=None):
        """
        اعتماد أو رفض التقييم
        Approve or reject evaluation
        """
        self.check_permission('evaluations.approve_evaluation')

        if action not in ['approve', 'reject', 'request_revision']:
            return self.format_response(
                success=False,
                message='الإجراء غير صحيح'
            )

        try:
            evaluation = EmployeeEvaluation.objects.select_related(
                'employee', 'evaluator', 'period'
            ).get(id=evaluation_id)

            if evaluation.status != 'submitted':
                return self.format_response(
                    success=False,
                    message='لا يمكن اعتماد تقييم غير مقدم'
                )

            with transaction.atomic():
                if action == 'approve':
                    evaluation.status = 'approved'
                    evaluation.approved_by = self.user
                    evaluation.approved_at = timezone.now()

                    # Create performance review record
                    self._create_performance_review(evaluation)

                elif action == 'reject':
                    evaluation.status = 'rejected'
                    evaluation.rejected_by = self.user
                    evaluation.rejected_at = timezone.now()

                elif action == 'request_revision':
                    evaluation.status = 'revision_requested'

                evaluation.reviewer_feedback = feedback
                evaluation.updated_by = self.user
                evaluation.save()

                # Log the action
                self.log_action(
                    action=action,
                    resource='evaluation_approval',
                    content_object=evaluation,
                    details={
                        'action': action,
                        'feedback': feedback
                    },
                    message=f'تم {action} تقييم الموظف: {evaluation.employee.get_full_name()}'
                )

                # Send notification
                self._send_evaluation_notification(evaluation, action)

                return self.format_response(
                    data={'new_status': evaluation.status},
                    message=f'تم {action} التقييم بنجاح'
                )

        except EmployeeEvaluation.DoesNotExist:
            return self.format_response(
                success=False,
                message='التقييم غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'approve_evaluation', f'evaluation_approval/{evaluation_id}')

    def get_employee_evaluations(self, employee_id, year=None, page=1, page_size=20):
        """
        الحصول على تقييمات الموظف
        Get employee evaluations
        """
        self.check_permission('evaluations.view_employeeevaluation')

        try:
            from core.models.hr import Employee

            employee = Employee.objects.get(id=employee_id)

            # Check object-level permission
            self.check_object_permission('evaluations.view_employeeevaluation', employee)

            queryset = EmployeeEvaluation.objects.filter(employee=employee).prefetch_related()  # TODO: Add appropriate prefetch_related fields

            if year:
                queryset = queryset.filter(period__start_date__year=year)

            queryset = queryset.select_related(
                'period', 'period__template', 'evaluator', 'approved_by'
            ).order_by('-period__start_date')

            # Paginate results
            paginated_data = self.paginate_queryset(queryset, page, page_size)

            # Format evaluation data
            evaluations = []
            for evaluation in paginated_data['results']:
                evaluations.append({
                    'id': evaluation.id,
                    'period_name': evaluation.period.name,
                    'template_name': evaluation.period.template.name,
                    'evaluation_type': evaluation.period.template.evaluation_type,
                    'start_date': evaluation.period.start_date,
                    'end_date': evaluation.period.end_date,
                    'evaluator_name': evaluation.evaluator.get_full_name() if evaluation.evaluator else '',
                    'total_score': evaluation.total_score,
                    'performance_rating': evaluation.performance_rating,
                    'status': evaluation.status,
                    'submitted_at': evaluation.submitted_at,
                    'approved_at': evaluation.approved_at,
                })

            paginated_data['results'] = evaluations

            return self.format_response(
                data=paginated_data,
                message='تم الحصول على تقييمات الموظف بنجاح'
            )

        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'get_employee_evaluations', f'evaluations/{employee_id}')

    def get_evaluation_analytics(self, period_id=None, department_id=None):
        """
        الحصول على تحليلات التقييم
        Get evaluation analytics
        """
        self.check_permission('evaluations.view_evaluation_analytics')

        try:
            queryset = EmployeeEvaluation.objects.filter(status='approved').prefetch_related()  # TODO: Add appropriate prefetch_related fields

            if period_id:
                queryset = queryset.filter(period_id=period_id)

            if department_id:
                queryset = queryset.filter(employee__department_id=department_id)

            # Calculate analytics
            analytics = queryset.aggregate(
                total_evaluations=Count('id'),
                avg_score=Avg('total_score'),
                excellent_count=Count('id', filter=Q(performance_rating='excellent')),
                good_count=Count('id', filter=Q(performance_rating='good')),
                satisfactory_count=Count('id', filter=Q(performance_rating='satisfactory')),
                needs_improvement_count=Count('id', filter=Q(performance_rating='needs_improvement')),
                unsatisfactory_count=Count('id', filter=Q(performance_rating='unsatisfactory')),
            )

            # Calculate percentages
            total = analytics['total_evaluations'] or 1
            analytics.update({
                'excellent_percentage': round((analytics['excellent_count'] / total) * 100, 2),
                'good_percentage': round((analytics['good_count'] / total) * 100, 2),
                'satisfactory_percentage': round((analytics['satisfactory_count'] / total) * 100, 2),
                'needs_improvement_percentage': round((analytics['needs_improvement_count'] / total) * 100, 2),
                'unsatisfactory_percentage': round((analytics['unsatisfactory_count'] / total) * 100, 2),
            })

            # Get department breakdown if not filtered by department
            if not department_id:
                department_breakdown = queryset.values(
                    'employee__department__name_ar'
                ).annotate(
                    count=Count('id'),
                    avg_score=Avg('total_score')
                ).order_by('employee__department__name_ar')

                analytics['department_breakdown'] = list(department_breakdown)

            return self.format_response(
                data=analytics,
                message='تم الحصول على تحليلات التقييم بنجاح'
            )

        except Exception as e:
            return self.handle_exception(e, 'get_evaluation_analytics', 'evaluation_analytics')

    def set_evaluation_goals(self, employee_id, period_id, goals_data):
        """
        تحديد أهداف التقييم
        Set evaluation goals for employee
        """
        self.check_permission('evaluations.add_evaluationgoal')

        try:
            from core.models.hr import Employee

            employee = Employee.objects.get(id=employee_id)
            period = EvaluationPeriod.objects.get(id=period_id)

            with transaction.atomic():
                # Delete existing goals
                EvaluationGoal.objects.filter(
                    employee=employee,
                    period=period
                ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.delete()

                # Create new goals
                goals_created = 0
                for goal_data in goals_data:
                    EvaluationGoal.objects.create(
                        employee=employee,
                        period=period,
                        goal_title=goal_data['title'],
                        goal_description=goal_data['description'],
                        target_value=goal_data.get('target_value'),
                        measurement_unit=goal_data.get('measurement_unit'),
                        weight=goal_data.get('weight', 0),
                        due_date=goal_data.get('due_date'),
                        status='active',
                        created_by=self.user,
                        updated_by=self.user
                    )
                    goals_created += 1

                # Log the action
                self.log_action(
                    action='create',
                    resource='evaluation_goals',
                    details={
                        'employee_id': employee_id,
                        'period_id': period_id,
                        'goals_count': goals_created
                    },
                    message=f'تم تحديد {goals_created} هدف للموظف: {employee.get_full_name()}'
                )

                return self.format_response(
                    data={'goals_created': goals_created},
                    message=f'تم تحديد {goals_created} هدف بنجاح'
                )

        except Employee.DoesNotExist:
            return self.format_response(
                success=False,
                message='الموظف غير موجود'
            )
        except EvaluationPeriod.DoesNotExist:
            return self.format_response(
                success=False,
                message='فترة التقييم غير موجودة'
            )
        except Exception as e:
            return self.handle_exception(e, 'set_evaluation_goals', f'goals/{employee_id}')

    def _add_evaluation_criteria(self, template, criteria_data):
        """إضافة معايير التقييم"""
        for criteria in criteria_data:
            EvaluationCriteria.objects.create(
                template=template,
                name=criteria['name'],
                description=criteria.get('description', ''),
                max_score=criteria.get('max_score', 10),
                weight=criteria.get('weight', 10),
                criteria_type=criteria.get('criteria_type', 'numeric'),
                is_required=criteria.get('is_required', True),
                created_by=self.user,
                updated_by=self.user
            )

    def _create_employee_evaluations(self, period, department_ids=None):
        """إنشاء تقييمات للموظفين"""
        from core.models.hr import Employee

        queryset = Employee.objects.filter(is_active=True).prefetch_related()  # TODO: Add appropriate prefetch_related fields

        if department_ids:
            queryset = queryset.filter(department_id__in=department_ids)

        created_count = 0
        for employee in queryset:
            # Check if evaluation already exists
            if not EmployeeEvaluation.objects.filter(
                employee=employee,
                period=period
            ).prefetch_related()  # TODO: Add appropriate prefetch_related fields.exists():
                # Assign evaluator (manager or HR)
                evaluator = employee.manager.user if employee.manager and employee.manager.user else self.user

                EmployeeEvaluation.objects.create(
                    employee=employee,
                    period=period,
                    evaluator=evaluator,
                    status='pending',
                    created_by=self.user,
                    updated_by=self.user
                )
                created_count += 1

        return created_count

    def _calculate_performance_rating(self, score, template):
        """حساب تقدير الأداء"""
        if score >= 90:
            return 'excellent'
        elif score >= 80:
            return 'good'
        elif score >= template.passing_score:
            return 'satisfactory'
        elif score >= 40:
            return 'needs_improvement'
        else:
            return 'unsatisfactory'

    def _create_performance_review(self, evaluation):
        """إنشاء مراجعة الأداء"""
        PerformanceReview.objects.create(
            employee=evaluation.employee,
            evaluation=evaluation,
            review_period_start=evaluation.period.start_date,
            review_period_end=evaluation.period.end_date,
            overall_rating=evaluation.performance_rating,
            strengths=evaluation.comments,
            areas_for_improvement='',
            development_plan='',
            reviewer=evaluation.approved_by,
            created_by=self.user,
            updated_by=self.user
        )

    def _send_evaluation_notification(self, evaluation, action):
        """إرسال إشعار التقييم"""
        try:
            template_name = f'evaluation_{action}'

            if action in ['submitted', 'approved', 'rejected']:
                recipient = evaluation.employee.user if evaluation.employee.user else evaluation.employee
            else:
                recipient = evaluation.evaluator

            self.send_notification(
                recipient=recipient,
                template_name=template_name,
                context={'evaluation': evaluation},
                channels=['in_app', 'email']
            )
        except Exception as e:
            self.logger.warning(f"Failed to send evaluation notification: {e}")
