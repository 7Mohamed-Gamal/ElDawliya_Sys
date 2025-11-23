"""
خدمة إدارة الاجتماعات والمحاضر
Meeting Management Service
"""
from django.db import transaction
from django.utils import timezone
from core.services.base import BaseService
from core.models.projects import Meeting, MeetingAttendee, MeetingMinutes, MeetingAction


class MeetingService(BaseService):
    """
    خدمة إدارة الاجتماعات والمحاضر
    Meeting management and minutes service
    """
    
    def create_meeting(self, data):
        """إنشاء اجتماع جديد"""
        self.check_permission('projects.add_meeting')
        
        required_fields = ['title', 'meeting_date', 'start_time']
        self.validate_required_fields(data, required_fields)
        
        try:
            with transaction.atomic():
                meeting = Meeting.objects.create(
                    title=data['title'],
                    description=data.get('description', ''),
                    meeting_date=data['meeting_date'],
                    start_time=data['start_time'],
                    end_time=data.get('end_time'),
                    location=data.get('location', ''),
                    meeting_type=data.get('meeting_type', 'regular'),
                    project_id=data.get('project_id'),
                    organizer=self.user,
                    status='scheduled',
                    created_by=self.user,
                    updated_by=self.user
                )
                
                # Add attendees
                if data.get('attendees'):
                    self._add_meeting_attendees(meeting, data['attendees'])
                
                self.log_action(
                    action='create',
                    resource='meeting',
                    content_object=meeting,
                    message=f'تم إنشاء اجتماع جديد: {meeting.title}'
                )
                
                return self.format_response(
                    data={'meeting_id': meeting.id},
                    message='تم إنشاء الاجتماع بنجاح'
                )
                
        except Exception as e:
            return self.handle_exception(e, 'create_meeting', 'meeting', data)
    
    def record_meeting_minutes(self, meeting_id, minutes_data):
        """تسجيل محضر الاجتماع"""
        self.check_permission('projects.add_meetingminutes')
        
        try:
            meeting = Meeting.objects.get(id=meeting_id)
            
            minutes = MeetingMinutes.objects.create(
                meeting=meeting,
                agenda_items=minutes_data.get('agenda_items', ''),
                discussions=minutes_data.get('discussions', ''),
                decisions=minutes_data.get('decisions', ''),
                action_items=minutes_data.get('action_items', ''),
                next_meeting_date=minutes_data.get('next_meeting_date'),
                recorded_by=self.user,
                created_by=self.user,
                updated_by=self.user
            )
            
            # Add action items
            if minutes_data.get('actions'):
                self._add_meeting_actions(meeting, minutes_data['actions'])
            
            # Update meeting status
            meeting.status = 'completed'
            meeting.save()
            
            self.log_action(
                action='record_minutes',
                resource='meeting_minutes',
                content_object=minutes,
                message=f'تم تسجيل محضر الاجتماع: {meeting.title}'
            )
            
            return self.format_response(
                data={'minutes_id': minutes.id},
                message='تم تسجيل محضر الاجتماع بنجاح'
            )
            
        except Meeting.DoesNotExist:
            return self.format_response(
                success=False,
                message='الاجتماع غير موجود'
            )
        except Exception as e:
            return self.handle_exception(e, 'record_meeting_minutes', f'meeting_minutes/{meeting_id}')
    
    def _add_meeting_attendees(self, meeting, attendees_data):
        """إضافة حضور الاجتماع"""
        from core.models.hr import Employee
        
        for attendee_data in attendees_data:
            try:
                employee = Employee.objects.get(id=attendee_data['employee_id'])
                MeetingAttendee.objects.create(
                    meeting=meeting,
                    employee=employee,
                    attendance_status=attendee_data.get('attendance_status', 'invited'),
                    role=attendee_data.get('role', 'attendee'),
                    created_by=self.user,
                    updated_by=self.user
                )
            except Employee.DoesNotExist:
                self.logger.warning(f"Employee {attendee_data['employee_id']} not found")
    
    def _add_meeting_actions(self, meeting, actions_data):
        """إضافة إجراءات الاجتماع"""
        from core.models.hr import Employee
        
        for action_data in actions_data:
            try:
                assigned_to = Employee.objects.get(id=action_data['assigned_to_id'])
                MeetingAction.objects.create(
                    meeting=meeting,
                    action_description=action_data['description'],
                    assigned_to=assigned_to,
                    due_date=action_data.get('due_date'),
                    priority=action_data.get('priority', 'medium'),
                    status='pending',
                    created_by=self.user,
                    updated_by=self.user
                )
            except Employee.DoesNotExist:
                self.logger.warning(f"Employee {action_data['assigned_to_id']} not found")