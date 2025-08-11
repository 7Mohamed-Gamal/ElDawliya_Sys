from django.contrib import admin
from .models import TrainingProvider, TrainingCourse, EmployeeTraining

@admin.register(TrainingProvider)
class TrainingProviderAdmin(admin.ModelAdmin):
    list_display = ('provider_id', 'provider_name', 'phone', 'email')
    search_fields = ('provider_name', 'phone')

@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_name', 'provider', 'start_date', 'end_date')
    search_fields = ('course_name',)
    list_filter = ('provider',)

@admin.register(EmployeeTraining)
class EmployeeTrainingAdmin(admin.ModelAdmin):
    list_display = ('emp_training_id', 'emp', 'course', 'status', 'enrollment_date')
    search_fields = ('emp__emp_code',)
    list_filter = ('status',)
