#!/usr/bin/env python
"""
Create tables for attendance app
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.db import connection
from django.core.management.color import no_style

def create_attendance_tables():
    """Create tables for attendance app"""
    
    # Import models
    from apps.hr.attendance.models import (
        AttendanceRule, WorkSchedule, WeeklyHoliday, LeaveType,
        EmployeeAttendanceProfile, LeaveBalance, AttendanceRecord,
        AttendanceRules, EmployeeAttendance, ZKDevice, ZKAttendanceRaw,
        AttendanceProcessingLog, EmployeeDeviceMapping, AttendanceSummary
    )
    
    models_to_create = [
        AttendanceRule, WorkSchedule, WeeklyHoliday, LeaveType,
        EmployeeAttendanceProfile, LeaveBalance, AttendanceRecord,
        AttendanceRules, EmployeeAttendance, ZKDevice, ZKAttendanceRaw,
        AttendanceProcessingLog, EmployeeDeviceMapping, AttendanceSummary
    ]
    
    # Get SQL statements for creating tables
    with connection.schema_editor() as schema_editor:
        try:
            for model in models_to_create:
                print(f"Creating {model._meta.db_table} table...")
                schema_editor.create_model(model)
                print(f"✅ {model._meta.db_table} table created")
            
            print("\n✅ All attendance tables created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_attendance_tables()