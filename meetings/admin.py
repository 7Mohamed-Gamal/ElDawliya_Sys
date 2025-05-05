from django.contrib import admin
from .models import Meeting, Attendee

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'created_by', 'get_attendees_count']
    list_filter = ['date', 'created_by']
    search_fields = ['title', 'topic']
    date_hierarchy = 'date'

    def get_attendees_count(self, obj):
        return obj.attendees.count()
    get_attendees_count.short_description = 'عدد الحضور'

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'meeting']
    list_filter = ['meeting']



def has_add_permission(self, request):
        """
        السماح بإضافة اجتماع فقط للأدمن أو المستخدمين المحددين
        """
        return request.user.Role == 'admin'  # أو أي شرط آخر

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