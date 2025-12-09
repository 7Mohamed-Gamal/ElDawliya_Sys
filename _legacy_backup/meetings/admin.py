from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Meeting, Attendee, MeetingTask, MeetingTaskStep

class MeetingTaskStepInline(admin.TabularInline):
    """MeetingTaskStepInline class"""
    model = MeetingTaskStep
    extra = 0
    fields = ['description', 'completed', 'notes', 'created_by']
    readonly_fields = ['created_by']

class MeetingTaskInline(admin.TabularInline):
    """MeetingTaskInline class"""
    model = MeetingTask
    extra = 1
    fields = ['description', 'assigned_to']

class AttendeeInline(admin.TabularInline):
    """AttendeeInline class"""
    model = Attendee
    extra = 1
    fields = ['user']

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    """MeetingAdmin class"""
    list_display = ['title', 'date', 'created_by', 'get_attendees_count', 'status']
    list_filter = ['date', 'created_by', 'status']
    search_fields = ['title', 'topic']
    date_hierarchy = 'date'
    inlines = [AttendeeInline, MeetingTaskInline]
    fieldsets = (
        (_('معلومات الاجتماع'), {
            'fields': ('title', 'topic')
        }),
        (_('الزمان والمكان'), {
            'fields': ('date',)
        }),
        (_('الحالة'), {
            'fields': ('status', 'created_by')
        }),
    )
    readonly_fields = ['created_by']

    def get_attendees_count(self, obj):
        """get_attendees_count function"""
        return obj.attendees.count()
    get_attendees_count.short_description = 'عدد الحضور'

    def save_model(self, request, obj, form, change):
        """save_model function"""
        if not change:  # إذا كان إنشاء جديد
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        """
        السماح بإضافة اجتماع فقط للأدمن أو المستخدمين المحددين
        """
        return request.user.is_superuser or request.user.Role == 'admin' or request.user.has_perm('meetings.add_meeting')

    def has_change_permission(self, request, obj=None):
        """has_change_permission function"""
        # السماح للمستخدم بتعديل الاجتماعات التي أنشأها
        if obj is not None and (obj.created_by == request.user or request.user.is_superuser or request.user.Role == 'admin'):
            return True
        return super().has_change_permission(request, obj)

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    """AttendeeAdmin class"""
    list_display = ['user', 'meeting']
    list_filter = ['meeting']
    search_fields = ['user__username', 'meeting__title']

    def has_change_permission(self, request, obj=None):
        """has_change_permission function"""
        # السماح للمستخدم بتعديل حضور الاجتماعات التي أنشأها
        if obj is not None and (obj.meeting.created_by == request.user or request.user.is_superuser or request.user.Role == 'admin'):
            return True
        return super().has_change_permission(request, obj)

def has_change_permission(self, request, obj=None):
        """
        السماح بتعديل الاجتماع فقط للأدمن أو منشئ الاجتماع
        """
        if obj is None:
            return request.user.Role == 'admin'
        return request.user.Role == 'admin' or obj.created_by == request.user

def has_delete_permission(self, request, obj=None):
        """
        السماح بحذف الاجتماع فقط للأدمن أو منشئ الاجتماع
        """
        if obj is None:
            return request.user.Role == 'admin'
        return request.user.Role == 'admin' or obj.created_by == request.user

@admin.register(MeetingTask)
class MeetingTaskAdmin(admin.ModelAdmin):
    """MeetingTaskAdmin class"""
    list_display = ['description', 'meeting', 'assigned_to', 'status', 'created_at']
    list_filter = ['meeting', 'assigned_to', 'status']
    search_fields = ['description', 'meeting__title', 'assigned_to__username']
    inlines = [MeetingTaskStepInline]

    def has_change_permission(self, request, obj=None):
        """has_change_permission function"""
        # السماح بتعديل مهام الاجتماع فقط للأدمن أو منشئ الاجتماع
        if obj is None:
            return True
        return (request.user.is_superuser or request.user.Role == 'admin' or
                obj.meeting.created_by == request.user)


@admin.register(MeetingTaskStep)
class MeetingTaskStepAdmin(admin.ModelAdmin):
    """MeetingTaskStepAdmin class"""
    list_display = ['description', 'meeting_task', 'completed', 'created_by', 'created_at']
    list_filter = ['completed', 'created_at', 'meeting_task__meeting']
    search_fields = ['description', 'meeting_task__description', 'notes']
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'completion_date']

    fieldsets = [
        (_('معلومات الخطوة'), {
            'fields': ['meeting_task', 'description', 'notes', 'completed', 'completion_date']
        }),
        (_('معلومات النظام'), {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

    def has_change_permission(self, request, obj=None):
        """has_change_permission function"""
        # السماح بتعديل خطوات المهام فقط للأدمن أو المكلف بالمهمة أو منشئ الاجتماع
        if obj is None:
            return True
        return (request.user.is_superuser or request.user.Role == 'admin' or
                obj.meeting_task.assigned_to == request.user or
                obj.meeting_task.meeting.created_by == request.user)
