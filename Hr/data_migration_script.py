#!/usr/bin/env python
"""
Data Migration Script for HR System
Migrates data from old models to new enhanced models
"""

import os
import sys
import django
from django.db import transaction
from django.core.management.base import BaseCommand

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from Hr.models import *

class DataMigrator:
    """Class to handle data migration"""
    
    def __init__(self):
        self.stats = {
            'companies': 0,
            'branches': 0,
            'departments': 0,
            'job_positions': 0,
            'employees': 0,
            'errors': []
        }
    
    def log_error(self, message):
        """Log error message"""
        print(f"ERROR: {message}")
        self.stats['errors'].append(message)
    
    def log_success(self, message):
        """Log success message"""
        print(f"SUCCESS: {message}")
    
    def migrate_companies(self):
        """Migrate company data"""
        print("Migrating companies...")
        
        try:
            # Check if we have any companies to migrate
            # This would typically involve migrating from old company model
            # For now, we'll create a default company if none exists
            
            if not Company.objects.exists():
                company = Company.objects.create(
                    name="الشركة الدولية",
                    name_english="International Company",
                    code="INTL",
                    commercial_register="123456789",
                    tax_number="987654321",
                    address="العنوان الرئيسي",
                    city="القاهرة",
                    state="القاهرة",
                    country="مصر",
                    phone="+201234567890",
                    email="info@company.com",
                    business_type="llc",
                    industry="تكنولوجيا المعلومات",
                    default_currency="EGP"
                )
                self.stats['companies'] += 1
                self.log_success(f"Created default company: {company.name}")
            
        except Exception as e:
            self.log_error(f"Error migrating companies: {e}")
    
    def migrate_branches(self):
        """Migrate branch data"""
        print("Migrating branches...")
        
        try:
            company = Company.objects.first()
            if not company:
                self.log_error("No company found for branch migration")
                return
            
            # Create default branch if none exists
            if not Branch.objects.filter(company=company).exists():
                branch = Branch.objects.create(
                    company=company,
                    name="الفرع الرئيسي",
                    code="MAIN",
                    address="عنوان الفرع الرئيسي",
                    city="القاهرة",
                    state="القاهرة",
                    country="مصر",
                    is_headquarters=True
                )
                self.stats['branches'] += 1
                self.log_success(f"Created default branch: {branch.name}")
            
        except Exception as e:
            self.log_error(f"Error migrating branches: {e}")
    
    def migrate_departments(self):
        """Migrate department data"""
        print("Migrating departments...")
        
        try:
            branch = Branch.objects.first()
            if not branch:
                self.log_error("No branch found for department migration")
                return
            
            # Create default departments if none exist
            default_departments = [
                {"name": "الموارد البشرية", "code": "HR", "department_type": "hr"},
                {"name": "المالية", "code": "FIN", "department_type": "finance"},
                {"name": "تكنولوجيا المعلومات", "code": "IT", "department_type": "it"},
                {"name": "الإدارة العامة", "code": "ADMIN", "department_type": "administrative"},
            ]
            
            for dept_data in default_departments:
                if not Department.objects.filter(branch=branch, code=dept_data["code"]).exists():
                    department = Department.objects.create(
                        branch=branch,
                        name=dept_data["name"],
                        code=dept_data["code"],
                        department_type=dept_data["department_type"]
                    )
                    self.stats['departments'] += 1
                    self.log_success(f"Created department: {department.name}")
            
        except Exception as e:
            self.log_error(f"Error migrating departments: {e}")
    
    def migrate_job_positions(self):
        """Migrate job position data"""
        print("Migrating job positions...")
        
        try:
            departments = Department.objects.all()
            
            for department in departments:
                # Create default job positions for each department
                default_positions = []
                
                if department.department_type == "hr":
                    default_positions = [
                        {"title": "مدير الموارد البشرية", "level": 5},
                        {"title": "أخصائي موارد بشرية", "level": 3},
                        {"title": "منسق موارد بشرية", "level": 2},
                    ]
                elif department.department_type == "finance":
                    default_positions = [
                        {"title": "مدير مالي", "level": 5},
                        {"title": "محاسب أول", "level": 3},
                        {"title": "محاسب", "level": 2},
                    ]
                elif department.department_type == "it":
                    default_positions = [
                        {"title": "مدير تكنولوجيا المعلومات", "level": 5},
                        {"title": "مطور برمجيات أول", "level": 4},
                        {"title": "مطور برمجيات", "level": 3},
                    ]
                else:
                    default_positions = [
                        {"title": "مدير القسم", "level": 5},
                        {"title": "موظف أول", "level": 3},
                        {"title": "موظف", "level": 2},
                    ]
                
                for pos_data in default_positions:
                    if not JobPosition.objects.filter(department=department, title=pos_data["title"]).exists():
                        position = JobPosition.objects.create(
                            department=department,
                            title=pos_data["title"],
                            level=pos_data["level"],
                            description=f"وصف وظيفة {pos_data['title']}",
                            requirements=f"متطلبات وظيفة {pos_data['title']}",
                            responsibilities=f"مسؤوليات وظيفة {pos_data['title']}"
                        )
                        self.stats['job_positions'] += 1
                        self.log_success(f"Created job position: {position.title}")
            
        except Exception as e:
            self.log_error(f"Error migrating job positions: {e}")
    
    def migrate_employees(self):
        """Migrate employee data"""
        print("Migrating employees...")
        
        try:
            # This would typically migrate from old employee models
            # For now, we'll just ensure the structure is ready
            
            company = Company.objects.first()
            branch = Branch.objects.first()
            department = Department.objects.first()
            job_position = JobPosition.objects.first()
            
            if not all([company, branch, department, job_position]):
                self.log_error("Missing required organizational structure for employee migration")
                return
            
            # Check if we have employees to migrate
            existing_employees = Employee.objects.count()
            self.log_success(f"Found {existing_employees} existing employees")
            
        except Exception as e:
            self.log_error(f"Error migrating employees: {e}")
    
    def create_sample_data(self):
        """Create sample data for testing"""
        print("Creating sample data...")
        
        try:
            company = Company.objects.first()
            branch = Branch.objects.first()
            hr_dept = Department.objects.filter(department_type="hr").first()
            hr_manager_pos = JobPosition.objects.filter(department=hr_dept, level=5).first()
            
            if all([company, branch, hr_dept, hr_manager_pos]):
                # Create sample employee if none exists
                if not Employee.objects.exists():
                    from django.utils import timezone
                    
                    employee = Employee.objects.create(
                        company=company,
                        branch=branch,
                        department=hr_dept,
                        job_position=hr_manager_pos,
                        first_name="أحمد",
                        middle_name="محمد",
                        last_name="علي",
                        email="ahmed.ali@company.com",
                        phone="+201234567890",
                        hire_date=timezone.now().date(),
                        employment_type="full_time",
                        status="active",
                        basic_salary=15000.00,
                        nationality="مصري",
                        gender="male",
                        marital_status="married"
                    )
                    self.stats['employees'] += 1
                    self.log_success(f"Created sample employee: {employee.full_name}")
            
        except Exception as e:
            self.log_error(f"Error creating sample data: {e}")
    
    def run_migration(self):
        """Run the complete migration process"""
        print("Starting HR Data Migration")
        print("=" * 50)
        
        with transaction.atomic():
            try:
                self.migrate_companies()
                self.migrate_branches()
                self.migrate_departments()
                self.migrate_job_positions()
                self.migrate_employees()
                self.create_sample_data()
                
                print("\nMigration completed successfully!")
                print("=" * 50)
                print("Migration Statistics:")
                print(f"Companies: {self.stats['companies']}")
                print(f"Branches: {self.stats['branches']}")
                print(f"Departments: {self.stats['departments']}")
                print(f"Job Positions: {self.stats['job_positions']}")
                print(f"Employees: {self.stats['employees']}")
                print(f"Errors: {len(self.stats['errors'])}")
                
                if self.stats['errors']:
                    print("\nErrors encountered:")
                    for error in self.stats['errors']:
                        print(f"- {error}")
                
            except Exception as e:
                print(f"Migration failed: {e}")
                raise

def main():
    """Main function"""
    migrator = DataMigrator()
    migrator.run_migration()

if __name__ == '__main__':
    main()