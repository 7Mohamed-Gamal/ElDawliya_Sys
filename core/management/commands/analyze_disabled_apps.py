"""
أداة تحليل التطبيقات المعلقة وإصلاحها
=====================================

هذه الأداة تقوم بتحليل جميع التطبيقات المعلقة في النظام وتحديد أسباب التعليق
وتوفير حلول للإصلاح.
"""

import os
import sys
import importlib
import traceback
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps
from django.core.management import call_command
from django.db import connection
from django.urls import reverse
from django.test import Client


@dataclass
class AppStatus:
    """حالة التطبيق"""
    name: str
    is_enabled: bool = False
    has_import_errors: bool = False
    has_model_conflicts: bool = False
    has_url_errors: bool = False
    missing_packages: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0
    status: str = 'disabled'
    errors: List[str] = field(default_factory=list)
    notes: str = ''


@dataclass
class FixReport:
    """تقرير الإصلاح"""
    app_name: str
    errors_found: List[str] = field(default_factory=list)
    fixes_applied: List[str] = field(default_factory=list)
    success: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ''


class DependencyAnalyzer:
    """محلل التبعيات للتطبيقات"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(settings.BASE_DIR)
        
    def analyze_app_dependencies(self, app_name: str) -> Dict[str, List[str]]:
        """تحليل تبعيات التطبيق"""
        dependencies = {
            'imports': [],
            'models': [],
            'urls': [],
            'packages': []
        }
        
        try:
            app_path = self.base_dir / app_name
            if not app_path.exists():
                return dependencies
                
            # تحليل ملفات Python في التطبيق
            for py_file in app_path.rglob('*.py'):
                if py_file.name == '__pycache__':
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # البحث عن imports
                    imports = self._extract_imports(content)
                    dependencies['imports'].extend(imports)
                    
                    # البحث عن نماذج Django
                    models = self._extract_models(content)
                    dependencies['models'].extend(models)
                    
                except Exception as e:
                    self.logger.warning(f"خطأ في قراءة الملف {py_file}: {e}")
                    
        except Exception as e:
            self.logger.error(f"خطأ في تحليل التبعيات للتطبيق {app_name}: {e}")
            
        return dependencies
    
    def _extract_imports(self, content: str) -> List[str]:
        """استخراج imports من محتوى الملف"""
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
                
        return imports
    
    def _extract_models(self, content: str) -> List[str]:
        """استخراج نماذج Django من محتوى الملف"""
        models = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'class ' in line and '(models.Model)' in line:
                model_name = line.split('class ')[1].split('(')[0].strip()
                models.append(model_name)
                
        return models
    
    def get_import_errors(self, app_name: str) -> List[str]:
        """الحصول على أخطاء الاستيراد للتطبيق"""
        errors = []
        
        try:
            # محاولة استيراد التطبيق
            importlib.import_module(app_name)
        except ImportError as e:
            errors.append(f"خطأ استيراد: {str(e)}")
        except Exception as e:
            errors.append(f"خطأ عام في الاستيراد: {str(e)}")
            
        return errors
    
    def check_model_conflicts(self, app_name: str) -> List[str]:
        """فحص تضارب النماذج"""
        conflicts = []
        
        try:
            # محاولة تحميل نماذج التطبيق
            app_config = apps.get_app_config(app_name)
            models = app_config.get_models()
            
            for model in models:
                # فحص تضارب أسماء الجداول
                table_name = model._meta.db_table
                for other_app in apps.get_app_configs():
                    if other_app.label != app_name:
                        for other_model in other_app.get_models():
                            if other_model._meta.db_table == table_name:
                                conflicts.append(
                                    f"تضارب في اسم الجدول {table_name} بين "
                                    f"{model.__name__} و {other_model.__name__}"
                                )
                                
        except Exception as e:
            conflicts.append(f"خطأ في فحص تضارب النماذج: {str(e)}")
            
        return conflicts
    
    def validate_urls(self, app_name: str) -> List[str]:
        """التحقق من صحة URLs التطبيق"""
        errors = []
        
        try:
            app_path = self.base_dir / app_name / 'urls.py'
            if app_path.exists():
                # محاولة استيراد urls التطبيق
                urls_module = importlib.import_module(f'{app_name}.urls')
                
                # فحص وجود urlpatterns
                if not hasattr(urls_module, 'urlpatterns'):
                    errors.append("لا يحتوي ملف urls.py على urlpatterns")
                    
        except ImportError as e:
            errors.append(f"خطأ في استيراد urls: {str(e)}")
        except Exception as e:
            errors.append(f"خطأ في التحقق من URLs: {str(e)}")
            
        return errors


class ErrorFixer:
    """مصلح الأخطاء للتطبيقات"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def fix_import_errors(self, app_name: str, errors: List[str]) -> bool:
        """إصلاح أخطاء الاستيراد"""
        try:
            for error in errors:
                if 'No module named' in error:
                    # استخراج اسم المكتبة المفقودة
                    module_name = error.split("'")[1] if "'" in error else None
                    if module_name:
                        self.logger.info(f"محاولة تثبيت المكتبة المفقودة: {module_name}")
                        # يمكن إضافة منطق تثبيت المكتبات هنا
                        
            return True
        except Exception as e:
            self.logger.error(f"خطأ في إصلاح أخطاء الاستيراد: {e}")
            return False
    
    def fix_model_conflicts(self, app_name: str, conflicts: List[str]) -> bool:
        """إصلاح تضارب النماذج"""
        try:
            # منطق إصلاح تضارب النماذج
            # يمكن تطوير هذا لاحقاً حسب نوع التضارب
            return True
        except Exception as e:
            self.logger.error(f"خطأ في إصلاح تضارب النماذج: {e}")
            return False
    
    def fix_url_errors(self, app_name: str, url_errors: List[str]) -> bool:
        """إصلاح أخطاء URLs"""
        try:
            # منطق إصلاح أخطاء URLs
            return True
        except Exception as e:
            self.logger.error(f"خطأ في إصلاح أخطاء URLs: {e}")
            return False
    
    def install_missing_packages(self, packages: List[str]) -> bool:
        """تثبيت المكتبات المفقودة"""
        try:
            import subprocess
            for package in packages:
                self.logger.info(f"تثبيت المكتبة: {package}")
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"فشل في تثبيت {package}: {result.stderr}")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"خطأ في تثبيت المكتبات: {e}")
            return False


class AppTester:
    """مختبر التطبيقات"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = Client()
        
    def test_app_loading(self, app_name: str) -> bool:
        """اختبار تحميل التطبيق"""
        try:
            app_config = apps.get_app_config(app_name)
            return True
        except Exception as e:
            self.logger.error(f"فشل في تحميل التطبيق {app_name}: {e}")
            return False
    
    def test_models(self, app_name: str) -> bool:
        """اختبار نماذج التطبيق"""
        try:
            app_config = apps.get_app_config(app_name)
            models = app_config.get_models()
            
            for model in models:
                # اختبار إنشاء استعلام بسيط
                model.objects.all().count()
                
            return True
        except Exception as e:
            self.logger.error(f"فشل في اختبار نماذج {app_name}: {e}")
            return False
    
    def test_urls(self, app_name: str) -> bool:
        """اختبار URLs التطبيق"""
        try:
            # محاولة الوصول إلى URLs التطبيق
            urls_module = importlib.import_module(f'{app_name}.urls')
            return hasattr(urls_module, 'urlpatterns')
        except Exception as e:
            self.logger.error(f"فشل في اختبار URLs لـ {app_name}: {e}")
            return False
    
    def test_admin_interface(self, app_name: str) -> bool:
        """اختبار واجهة الإدارة للتطبيق"""
        try:
            from django.contrib import admin
            app_config = apps.get_app_config(app_name)
            models = app_config.get_models()
            
            for model in models:
                if admin.site.is_registered(model):
                    # النموذج مسجل في الإدارة
                    pass
                    
            return True
        except Exception as e:
            self.logger.error(f"فشل في اختبار واجهة الإدارة لـ {app_name}: {e}")
            return False
    
    def run_migrations(self, app_name: str) -> bool:
        """تشغيل migrations للتطبيق"""
        try:
            call_command('migrate', app_name, verbosity=0)
            return True
        except Exception as e:
            self.logger.error(f"فشل في تشغيل migrations لـ {app_name}: {e}")
            return False


class DisabledAppsAnalyzer:
    """المحلل الرئيسي للتطبيقات المعلقة"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.dependency_analyzer = DependencyAnalyzer()
        self.error_fixer = ErrorFixer()
        self.app_tester = AppTester()
        self.disabled_apps = self._get_disabled_apps()
        
    def _setup_logging(self) -> logging.Logger:
        """إعداد نظام التسجيل"""
        logger = logging.getLogger('disabled_apps_analyzer')
        logger.setLevel(logging.INFO)
        
        # إنشاء معالج الملف
        log_file = Path(settings.BASE_DIR) / 'logs' / 'disabled_apps_analysis.log'
        log_file.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # إنشاء معالج وحدة التحكم
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # تنسيق الرسائل
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _get_disabled_apps(self) -> List[str]:
        """الحصول على قائمة التطبيقات المعلقة"""
        # قائمة التطبيقات المعلقة من ملف الإعدادات
        disabled_apps = [
            'hr',
            'core',
            'audit',
            'meetings',
            'tasks',
            'inventory',
            'Purchase_orders',
            'cars',
            'attendance',
            'org',
            'employees',
            'companies',
            'leaves',
            'evaluations',
            'payrolls',
            'banks',
            'insurance',
            'training',
            'loans',
            'disciplinary',
            'tickets',
            'workflow',
            'assets',
            'rbac',
            'reports',
            'syssettings',
        ]
        
        return disabled_apps
    
    def analyze_all_disabled_apps(self) -> Dict[str, AppStatus]:
        """تحليل جميع التطبيقات المعلقة"""
        self.logger.info("بدء تحليل التطبيقات المعلقة...")
        
        app_statuses = {}
        
        for app_name in self.disabled_apps:
            self.logger.info(f"تحليل التطبيق: {app_name}")
            status = self._analyze_single_app(app_name)
            app_statuses[app_name] = status
            
        self.logger.info("انتهاء تحليل التطبيقات المعلقة")
        return app_statuses
    
    def _analyze_single_app(self, app_name: str) -> AppStatus:
        """تحليل تطبيق واحد"""
        status = AppStatus(name=app_name)
        
        try:
            # فحص وجود مجلد التطبيق
            app_path = Path(settings.BASE_DIR) / app_name
            if not app_path.exists():
                status.errors.append(f"مجلد التطبيق غير موجود: {app_path}")
                return status
            
            # تحليل التبعيات
            dependencies = self.dependency_analyzer.analyze_app_dependencies(app_name)
            status.dependencies = dependencies.get('imports', [])
            
            # فحص أخطاء الاستيراد
            import_errors = self.dependency_analyzer.get_import_errors(app_name)
            if import_errors:
                status.has_import_errors = True
                status.errors.extend(import_errors)
            
            # فحص تضارب النماذج
            model_conflicts = self.dependency_analyzer.check_model_conflicts(app_name)
            if model_conflicts:
                status.has_model_conflicts = True
                status.errors.extend(model_conflicts)
            
            # فحص أخطاء URLs
            url_errors = self.dependency_analyzer.validate_urls(app_name)
            if url_errors:
                status.has_url_errors = True
                status.errors.extend(url_errors)
            
            # تحديد الأولوية
            status.priority = self._calculate_priority(app_name)
            
            # تحديد الحالة
            if not status.errors:
                status.status = 'ready_to_enable'
            elif status.has_import_errors:
                status.status = 'import_errors'
            elif status.has_model_conflicts:
                status.status = 'model_conflicts'
            else:
                status.status = 'other_errors'
                
        except Exception as e:
            status.errors.append(f"خطأ في التحليل: {str(e)}")
            status.status = 'analysis_error'
            
        return status
    
    def _calculate_priority(self, app_name: str) -> int:
        """حساب أولوية التطبيق"""
        # التطبيقات الأساسية لها أولوية عالية
        high_priority = ['core', 'audit', 'org', 'hr']
        medium_priority = ['employees', 'attendance', 'companies']
        
        if app_name in high_priority:
            return 1
        elif app_name in medium_priority:
            return 2
        else:
            return 3
    
    def generate_priority_report(self, app_statuses: Dict[str, AppStatus]) -> str:
        """إنشاء تقرير الأولوية"""
        report = []
        report.append("=" * 60)
        report.append("تقرير تحليل التطبيقات المعلقة")
        report.append("=" * 60)
        report.append("")
        
        # ترتيب التطبيقات حسب الأولوية
        sorted_apps = sorted(app_statuses.items(), 
                           key=lambda x: (x[1].priority, x[0]))
        
        for priority in [1, 2, 3]:
            priority_apps = [app for app in sorted_apps if app[1].priority == priority]
            if priority_apps:
                priority_name = {1: "عالية", 2: "متوسطة", 3: "منخفضة"}[priority]
                report.append(f"الأولوية {priority_name}:")
                report.append("-" * 20)
                
                for app_name, status in priority_apps:
                    report.append(f"  • {app_name}")
                    report.append(f"    الحالة: {status.status}")
                    if status.errors:
                        report.append(f"    الأخطاء: {len(status.errors)}")
                        for error in status.errors[:3]:  # أول 3 أخطاء فقط
                            report.append(f"      - {error}")
                        if len(status.errors) > 3:
                            report.append(f"      ... و {len(status.errors) - 3} أخطاء أخرى")
                    report.append("")
                
        return "\n".join(report)
    
    def save_analysis_report(self, app_statuses: Dict[str, AppStatus]) -> str:
        """حفظ تقرير التحليل"""
        report_content = self.generate_priority_report(app_statuses)
        
        # حفظ التقرير في ملف
        report_file = Path(settings.BASE_DIR) / 'logs' / 'disabled_apps_analysis_report.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        self.logger.info(f"تم حفظ تقرير التحليل في: {report_file}")
        return str(report_file)


class Command(BaseCommand):
    """أمر Django لتحليل التطبيقات المعلقة"""
    
    help = 'تحليل التطبيقات المعلقة وإنشاء تقرير شامل'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            help='تحليل تطبيق محدد فقط'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='محاولة إصلاح الأخطاء المكتشفة'
        )
        parser.add_argument(
            '--report-only',
            action='store_true',
            help='إنشاء التقرير فقط بدون تحليل مفصل'
        )
    
    def handle(self, *args, **options):
        analyzer = DisabledAppsAnalyzer()
        
        if options['app']:
            # تحليل تطبيق محدد
            app_name = options['app']
            self.stdout.write(f"تحليل التطبيق: {app_name}")
            status = analyzer._analyze_single_app(app_name)
            
            self.stdout.write(f"حالة التطبيق {app_name}:")
            self.stdout.write(f"  الحالة: {status.status}")
            self.stdout.write(f"  الأولوية: {status.priority}")
            if status.errors:
                self.stdout.write(f"  الأخطاء:")
                for error in status.errors:
                    self.stdout.write(f"    - {error}")
        else:
            # تحليل جميع التطبيقات
            self.stdout.write("بدء تحليل جميع التطبيقات المعلقة...")
            app_statuses = analyzer.analyze_all_disabled_apps()
            
            # إنشاء وحفظ التقرير
            report_file = analyzer.save_analysis_report(app_statuses)
            
            # عرض ملخص
            total_apps = len(app_statuses)
            ready_apps = len([s for s in app_statuses.values() if s.status == 'ready_to_enable'])
            error_apps = total_apps - ready_apps
            
            self.stdout.write(
                self.style.SUCCESS(f"تم تحليل {total_apps} تطبيق معلق")
            )
            self.stdout.write(f"  جاهز للتفعيل: {ready_apps}")
            self.stdout.write(f"  يحتاج إصلاح: {error_apps}")
            self.stdout.write(f"  تقرير مفصل: {report_file}")
            
            if options['fix']:
                self.stdout.write("بدء محاولة إصلاح الأخطاء...")
                # يمكن إضافة منطق الإصلاح هنا