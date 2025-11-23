#!/usr/bin/env python
"""
نص الهجرة النهائي الشامل لنظام الدولية
Final Comprehensive Migration Script for ElDawliya System

هذا النص ينفذ الهجرة الشاملة مع معالجة جميع المشاكل المحددة
This script executes comprehensive migration while handling all identified issues.
"""

import os
import sys
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, date

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

class FinalMigrationScript:
    """منفذ الهجرة النهائية الشاملة"""
    
    def __init__(self):
        self.db_path = project_root / 'db_migration.sqlite3'
        self.backup_path = project_root / 'db_migration_backup.sqlite3'
        self.migration_log = []
        
    def log(self, message):
        """تسجيل رسالة"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.migration_log.append(log_entry)
        
    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        self.log("إنشاء نسخة احتياطية من قاعدة البيانات...")
        
        if self.db_path.exists():
            import shutil
            shutil.copy2(self.db_path, self.backup_path)
            self.log(f"تم إنشاء نسخة احتياطية: {self.backup_path}")
        else:
            self.log("لا توجد قاعدة بيانات موجودة - سيتم إنشاء قاعدة بيانات جديدة")
            
    def create_database_structure(self):
        """إنشاء هيكل قاعدة البيانات الجديد"""
        self.log("إنشاء هيكل قاعدة البيانات الجديد...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create core tables with proper structure
            
            # 1. Departments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_department (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    name TEXT NOT NULL,
                    name_en TEXT,
                    description TEXT,
                    manager_id TEXT,
                    parent_id TEXT,
                    code TEXT UNIQUE,
                    FOREIGN KEY (parent_id) REFERENCES core_department(id)
                )
            """)
            
            # 2. Job Positions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_jobposition (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    title TEXT NOT NULL,
                    title_en TEXT,
                    description TEXT,
                    department_id TEXT,
                    level INTEGER DEFAULT 1,
                    min_salary DECIMAL(10,2),
                    max_salary DECIMAL(10,2),
                    FOREIGN KEY (department_id) REFERENCES core_department(id)
                )
            """)
            
            # 3. Employees table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_employee (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    emp_code TEXT UNIQUE,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    first_name_en TEXT,
                    last_name_en TEXT,
                    email TEXT UNIQUE,
                    phone TEXT,
                    mobile TEXT,
                    national_id TEXT UNIQUE,
                    hire_date DATE,
                    birth_date DATE,
                    gender TEXT CHECK (gender IN ('male', 'female')),
                    marital_status TEXT CHECK (marital_status IN ('single', 'married', 'divorced', 'widowed')),
                    nationality TEXT DEFAULT 'السعودية',
                    department_id TEXT,
                    job_position_id TEXT,
                    manager_id TEXT,
                    emp_status TEXT DEFAULT 'active' CHECK (emp_status IN ('active', 'inactive', 'terminated', 'suspended')),
                    work_location TEXT,
                    contract_type TEXT DEFAULT 'permanent' CHECK (contract_type IN ('permanent', 'temporary', 'contract', 'intern')),
                    FOREIGN KEY (department_id) REFERENCES core_department(id),
                    FOREIGN KEY (job_position_id) REFERENCES core_jobposition(id),
                    FOREIGN KEY (manager_id) REFERENCES core_employee(id)
                )
            """)
            
            # 4. Product Categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_productcategory (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    name TEXT NOT NULL,
                    name_en TEXT,
                    description TEXT,
                    parent_id TEXT,
                    code TEXT UNIQUE,
                    FOREIGN KEY (parent_id) REFERENCES core_productcategory(id)
                )
            """)
            
            # 5. Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_product (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    name TEXT NOT NULL,
                    name_en TEXT,
                    description TEXT,
                    sku TEXT UNIQUE,
                    barcode TEXT,
                    category_id TEXT,
                    unit_price DECIMAL(10,2) DEFAULT 0,
                    cost_price DECIMAL(10,2) DEFAULT 0,
                    min_stock_level INTEGER DEFAULT 0,
                    max_stock_level INTEGER DEFAULT 0,
                    reorder_level INTEGER DEFAULT 0,
                    unit_of_measure TEXT DEFAULT 'piece',
                    FOREIGN KEY (category_id) REFERENCES core_productcategory(id)
                )
            """)
            
            # 6. Projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_project (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    version INTEGER DEFAULT 1,
                    deleted_at TIMESTAMP NULL,
                    name TEXT NOT NULL,
                    code TEXT UNIQUE,
                    description TEXT,
                    status TEXT DEFAULT 'planning' CHECK (status IN ('planning', 'active', 'on_hold', 'completed', 'cancelled', 'archived')),
                    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
                    start_date DATE,
                    end_date DATE,
                    actual_end_date DATE,
                    budget DECIMAL(15,2),
                    actual_cost DECIMAL(15,2) DEFAULT 0,
                    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
                    manager_id TEXT,
                    category_id TEXT,
                    parent_project_id TEXT,
                    FOREIGN KEY (manager_id) REFERENCES core_employee(id),
                    FOREIGN KEY (parent_project_id) REFERENCES core_project(id)
                )
            """)
            
            # 7. Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_task (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    version INTEGER DEFAULT 1,
                    deleted_at TIMESTAMP NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    task_type TEXT DEFAULT 'regular' CHECK (task_type IN ('regular', 'meeting', 'milestone', 'phase')),
                    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled', 'deferred', 'blocked')),
                    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent', 'critical')),
                    start_date TIMESTAMP,
                    due_date TIMESTAMP,
                    completed_date TIMESTAMP,
                    estimated_hours DECIMAL(8,2),
                    actual_hours DECIMAL(8,2) DEFAULT 0,
                    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
                    assigned_to_id TEXT,
                    project_id TEXT,
                    parent_task_id TEXT,
                    is_private BOOLEAN DEFAULT 0,
                    tags TEXT,
                    FOREIGN KEY (assigned_to_id) REFERENCES core_employee(id),
                    FOREIGN KEY (project_id) REFERENCES core_project(id),
                    FOREIGN KEY (parent_task_id) REFERENCES core_task(id)
                )
            """)
            
            # 8. Meetings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_meeting (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    version INTEGER DEFAULT 1,
                    title TEXT NOT NULL,
                    description TEXT,
                    meeting_type TEXT DEFAULT 'team' CHECK (meeting_type IN ('project', 'team', 'client', 'review', 'planning', 'standup', 'other')),
                    start_datetime TIMESTAMP,
                    end_datetime TIMESTAMP,
                    location TEXT,
                    virtual_link TEXT,
                    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'postponed')),
                    agenda TEXT,
                    minutes TEXT,
                    organizer_id TEXT,
                    project_id TEXT,
                    FOREIGN KEY (organizer_id) REFERENCES core_employee(id),
                    FOREIGN KEY (project_id) REFERENCES core_project(id)
                )
            """)
            
            # 9. Audit Log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_auditlog (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    table_name TEXT,
                    record_id TEXT,
                    old_values TEXT,
                    new_values TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES core_employee(id)
                )
            """)
            
            # 10. System Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_systemsetting (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT,
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    data_type TEXT DEFAULT 'string' CHECK (data_type IN ('string', 'integer', 'float', 'boolean', 'json')),
                    is_public BOOLEAN DEFAULT 0
                )
            """)
            
            conn.commit()
            self.log("تم إنشاء هيكل قاعدة البيانات بنجاح")
            
        except Exception as e:
            self.log(f"خطأ في إنشاء هيكل قاعدة البيانات: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
            
    def create_indexes(self):
        """إنشاء الفهارس المحسنة"""
        self.log("إنشاء الفهارس المحسنة...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            indexes = [
                # Employee indexes
                "CREATE INDEX IF NOT EXISTS idx_employees_active ON core_employee(is_active, emp_status)",
                "CREATE INDEX IF NOT EXISTS idx_employees_department ON core_employee(department_id)",
                "CREATE INDEX IF NOT EXISTS idx_employees_hire_date ON core_employee(hire_date)",
                "CREATE INDEX IF NOT EXISTS idx_employees_email ON core_employee(email)",
                "CREATE INDEX IF NOT EXISTS idx_employees_emp_code ON core_employee(emp_code)",
                
                # Product indexes
                "CREATE INDEX IF NOT EXISTS idx_products_category ON core_product(category_id, is_active)",
                "CREATE INDEX IF NOT EXISTS idx_products_sku ON core_product(sku)",
                "CREATE INDEX IF NOT EXISTS idx_products_name ON core_product(name)",
                
                # Task indexes
                "CREATE INDEX IF NOT EXISTS idx_tasks_status_assigned ON core_task(status, assigned_to_id)",
                "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON core_task(due_date)",
                "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON core_task(priority)",
                "CREATE INDEX IF NOT EXISTS idx_tasks_project ON core_task(project_id)",
                
                # Project indexes
                "CREATE INDEX IF NOT EXISTS idx_projects_status ON core_project(status)",
                "CREATE INDEX IF NOT EXISTS idx_projects_manager ON core_project(manager_id)",
                "CREATE INDEX IF NOT EXISTS idx_projects_dates ON core_project(start_date, end_date)",
                
                # Meeting indexes
                "CREATE INDEX IF NOT EXISTS idx_meetings_datetime ON core_meeting(start_datetime)",
                "CREATE INDEX IF NOT EXISTS idx_meetings_organizer ON core_meeting(organizer_id)",
                "CREATE INDEX IF NOT EXISTS idx_meetings_status ON core_meeting(status)",
                
                # Audit indexes
                "CREATE INDEX IF NOT EXISTS idx_audit_user_action ON core_auditlog(user_id, action)",
                "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON core_auditlog(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_audit_table_record ON core_auditlog(table_name, record_id)",
                
                # System settings indexes
                "CREATE INDEX IF NOT EXISTS idx_settings_key ON core_systemsetting(key)",
                "CREATE INDEX IF NOT EXISTS idx_settings_category ON core_systemsetting(category)",
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
                
            conn.commit()
            self.log(f"تم إنشاء {len(indexes)} فهرس بنجاح")
            
        except Exception as e:
            self.log(f"خطأ في إنشاء الفهارس: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
            
    def insert_sample_data(self):
        """إدراج بيانات تجريبية"""
        self.log("إدراج بيانات تجريبية...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert sample departments
            departments = [
                (str(uuid.uuid4()), 'تقنية المعلومات', 'Information Technology', 'IT', 'قسم تقنية المعلومات والبرمجة'),
                (str(uuid.uuid4()), 'الموارد البشرية', 'Human Resources', 'HR', 'قسم إدارة الموارد البشرية'),
                (str(uuid.uuid4()), 'المالية والمحاسبة', 'Finance & Accounting', 'FIN', 'قسم الشؤون المالية والمحاسبة'),
                (str(uuid.uuid4()), 'المبيعات والتسويق', 'Sales & Marketing', 'SAL', 'قسم المبيعات والتسويق'),
                (str(uuid.uuid4()), 'العمليات والإنتاج', 'Operations & Production', 'OPS', 'قسم العمليات والإنتاج'),
            ]
            
            for dept in departments:
                cursor.execute("""
                    INSERT OR REPLACE INTO core_department 
                    (id, name, name_en, code, description)
                    VALUES (?, ?, ?, ?, ?)
                """, dept)
                
            self.log(f"تم إدراج {len(departments)} قسم")
            
            # Insert sample job positions
            job_positions = [
                (str(uuid.uuid4()), 'مطور برمجيات', 'Software Developer', departments[0][0], 'تطوير وبرمجة التطبيقات'),
                (str(uuid.uuid4()), 'محلل أنظمة', 'Systems Analyst', departments[0][0], 'تحليل وتصميم الأنظمة'),
                (str(uuid.uuid4()), 'أخصائي موارد بشرية', 'HR Specialist', departments[1][0], 'إدارة شؤون الموظفين'),
                (str(uuid.uuid4()), 'محاسب', 'Accountant', departments[2][0], 'المحاسبة والشؤون المالية'),
                (str(uuid.uuid4()), 'مندوب مبيعات', 'Sales Representative', departments[3][0], 'المبيعات وخدمة العملاء'),
            ]
            
            for job in job_positions:
                cursor.execute("""
                    INSERT OR REPLACE INTO core_jobposition 
                    (id, title, title_en, department_id, description)
                    VALUES (?, ?, ?, ?, ?)
                """, job)
                
            self.log(f"تم إدراج {len(job_positions)} منصب وظيفي")
            
            # Insert sample employees
            employees = [
                (str(uuid.uuid4()), 'EMP001', 'أحمد', 'محمد', 'Ahmed', 'Mohammed', 'ahmed.mohammed@eldawliya.com', '0501234567', departments[0][0], job_positions[0][0]),
                (str(uuid.uuid4()), 'EMP002', 'فاطمة', 'علي', 'Fatima', 'Ali', 'fatima.ali@eldawliya.com', '0501234568', departments[1][0], job_positions[2][0]),
                (str(uuid.uuid4()), 'EMP003', 'محمد', 'أحمد', 'Mohammed', 'Ahmed', 'mohammed.ahmed@eldawliya.com', '0501234569', departments[2][0], job_positions[3][0]),
                (str(uuid.uuid4()), 'EMP004', 'نورا', 'سالم', 'Nora', 'Salem', 'nora.salem@eldawliya.com', '0501234570', departments[3][0], job_positions[4][0]),
                (str(uuid.uuid4()), 'EMP005', 'خالد', 'عبدالله', 'Khalid', 'Abdullah', 'khalid.abdullah@eldawliya.com', '0501234571', departments[0][0], job_positions[1][0]),
            ]
            
            for emp in employees:
                cursor.execute("""
                    INSERT OR REPLACE INTO core_employee 
                    (id, emp_code, first_name, last_name, first_name_en, last_name_en, 
                     email, mobile, department_id, job_position_id, hire_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now', '-1 year'))
                """, emp)
                
            self.log(f"تم إدراج {len(employees)} موظف")
            
            # Insert sample system settings
            settings = [
                (str(uuid.uuid4()), 'company_name', 'شركة الدولية للأنظمة', 'اسم الشركة', 'company', 'string'),
                (str(uuid.uuid4()), 'company_name_en', 'ElDawliya Systems Company', 'اسم الشركة بالإنجليزية', 'company', 'string'),
                (str(uuid.uuid4()), 'default_currency', 'SAR', 'العملة الافتراضية', 'finance', 'string'),
                (str(uuid.uuid4()), 'working_hours_per_day', '8', 'ساعات العمل اليومية', 'hr', 'integer'),
                (str(uuid.uuid4()), 'working_days_per_week', '5', 'أيام العمل الأسبوعية', 'hr', 'integer'),
            ]
            
            for setting in settings:
                cursor.execute("""
                    INSERT OR REPLACE INTO core_systemsetting 
                    (id, key, value, description, category, data_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, setting)
                
            self.log(f"تم إدراج {len(settings)} إعداد نظام")
            
            conn.commit()
            self.log("تم إدراج جميع البيانات التجريبية بنجاح")
            
        except Exception as e:
            self.log(f"خطأ في إدراج البيانات التجريبية: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
            
    def validate_migration(self):
        """التحقق من صحة الهجرة"""
        self.log("التحقق من صحة الهجرة...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        validation_results = {}
        
        try:
            # Check tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE 'core_%'
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            expected_tables = [
                'core_department', 'core_jobposition', 'core_employee',
                'core_productcategory', 'core_product', 'core_project',
                'core_task', 'core_meeting', 'core_auditlog', 'core_systemsetting'
            ]
            
            missing_tables = [t for t in expected_tables if t not in tables]
            validation_results['tables'] = {
                'expected': len(expected_tables),
                'found': len(tables),
                'missing': missing_tables
            }
            
            if missing_tables:
                self.log(f"جداول مفقودة: {missing_tables}")
            else:
                self.log("✓ جميع الجداول المطلوبة موجودة")
                
            # Check data integrity
            for table in ['core_department', 'core_employee', 'core_systemsetting']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                validation_results[f'{table}_count'] = count
                self.log(f"✓ {table}: {count} سجل")
                
            # Check indexes
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%'
            """)
            
            indexes = [row[0] for row in cursor.fetchall()]
            validation_results['indexes_count'] = len(indexes)
            self.log(f"✓ تم إنشاء {len(indexes)} فهرس")
            
            # Overall validation
            is_valid = (
                len(missing_tables) == 0 and
                validation_results.get('core_department_count', 0) > 0 and
                validation_results.get('core_employee_count', 0) > 0
            )
            
            validation_results['is_valid'] = is_valid
            
            if is_valid:
                self.log("✅ التحقق من الهجرة مكتمل بنجاح")
            else:
                self.log("❌ فشل في التحقق من الهجرة")
                
            return validation_results
            
        except Exception as e:
            self.log(f"خطأ في التحقق من الهجرة: {e}")
            return {'is_valid': False, 'error': str(e)}
        finally:
            conn.close()
            
    def generate_migration_report(self, validation_results):
        """إنشاء تقرير الهجرة"""
        self.log("إنشاء تقرير الهجرة...")
        
        report_path = project_root / 'logs' / 'final_migration_report.txt'
        report_path.parent.mkdir(exist_ok=True)
        
        report_lines = [
            "=" * 60,
            "تقرير الهجرة الشاملة النهائية - نظام الدولية",
            "=" * 60,
            "",
            f"تاريخ التنفيذ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"مسار قاعدة البيانات: {self.db_path}",
            f"مسار النسخة الاحتياطية: {self.backup_path}",
            "",
            "نتائج التحقق:",
        ]
        
        if validation_results.get('tables'):
            tables_info = validation_results['tables']
            report_lines.extend([
                f"الجداول المتوقعة: {tables_info['expected']}",
                f"الجداول الموجودة: {tables_info['found']}",
                f"الجداول المفقودة: {len(tables_info['missing'])}",
            ])
            
            if tables_info['missing']:
                report_lines.append(f"قائمة الجداول المفقودة: {', '.join(tables_info['missing'])}")
                
        report_lines.extend([
            "",
            "إحصائيات البيانات:",
            f"الأقسام: {validation_results.get('core_department_count', 0)}",
            f"الموظفون: {validation_results.get('core_employee_count', 0)}",
            f"إعدادات النظام: {validation_results.get('core_systemsetting_count', 0)}",
            f"الفهارس: {validation_results.get('indexes_count', 0)}",
            "",
            "حالة الهجرة:",
        ])
        
        if validation_results.get('is_valid'):
            report_lines.append("✅ الهجرة مكتملة بنجاح")
        else:
            report_lines.append("❌ الهجرة فشلت أو غير مكتملة")
            if 'error' in validation_results:
                report_lines.append(f"الخطأ: {validation_results['error']}")
                
        report_lines.extend([
            "",
            "سجل العمليات:",
            ""
        ])
        
        report_lines.extend(self.migration_log)
        
        report_lines.extend([
            "",
            "=" * 60
        ])
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
            
        self.log(f"تم حفظ التقرير في: {report_path}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("ملخص الهجرة:")
        print("=" * 60)
        for line in report_lines[4:20]:  # Print key summary lines
            print(line)
        print("=" * 60)
        
    def run_final_migration(self):
        """تشغيل الهجرة النهائية الشاملة"""
        self.log("بدء الهجرة النهائية الشاملة لنظام الدولية")
        self.log("=" * 50)
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Create database structure
            self.create_database_structure()
            
            # Step 3: Create indexes
            self.create_indexes()
            
            # Step 4: Insert sample data
            self.insert_sample_data()
            
            # Step 5: Validate migration
            validation_results = self.validate_migration()
            
            # Step 6: Generate report
            self.generate_migration_report(validation_results)
            
            self.log("=" * 50)
            
            if validation_results.get('is_valid'):
                self.log("🎉 تمت الهجرة النهائية بنجاح!")
                self.log("يمكنك الآن استخدام النظام الجديد")
                return True
            else:
                self.log("⚠️ الهجرة مكتملة مع تحذيرات - راجع التقرير")
                return False
                
        except Exception as e:
            self.log(f"❌ خطأ في الهجرة النهائية: {e}")
            self.log("يمكنك استعادة النسخة الاحتياطية إذا لزم الأمر")
            return False


def main():
    """الدالة الرئيسية"""
    migration = FinalMigrationScript()
    success = migration.run_final_migration()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()