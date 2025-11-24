#!/usr/bin/env python
"""
تحليل شامل لحالة النظام والتطبيقات المعلقة
==========================================

هذا السكريبت يقوم بتحليل شامل للنظام الحالي ويحدد:
- التطبيقات المعلقة وأسباب التعليق
- المشاكل في قاعدة البيانات
- الأخطاء في الاستيراد
- التبعيات المفقودة
- ترتيب الأولوية للإصلاح
"""

import os
import sys
import django
import importlib
import traceback
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# إعداد Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings.base')

try:
    django.setup()
except Exception as e:
    print(f"خطأ في إعداد Django: {e}")
    sys.exit(1)

from django.conf import settings
from django.apps import apps
from django.db import connection
from django.core.management import call_command


class SystemAnalyzer:
    """محلل النظام الشامل"""
    
    def __init__(self):
        self.base_dir = Path(settings.BASE_DIR)
        self.analysis_results = {}
        self.disabled_apps = self._get_disabled_apps()
        
    def _get_disabled_apps(self) -> List[str]:
        """الحصول على قائمة التطبيقات المعلقة من ملف الإعدادات"""
        # قراءة ملف الإعدادات للعثور على التطبيقات المعلقة
        settings_file = self.base_dir / 'ElDawliya_sys' / 'settings' / 'base.py'
        
        disabled_apps = []
        
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # البحث عن التطبيقات المعلقة (المعلقة بـ #)
            lines = content.split('\n')
            in_local_apps = False
            
            for line in lines:
                line = line.strip()
                
                if 'LOCAL_APPS = [' in line:
                    in_local_apps = True
                    continue
                elif in_local_apps and ']' in line and not line.startswith('#'):
                    break
                elif in_local_apps and line.startswith('#') and '.apps.' in line:
                    # استخراج اسم التطبيق من السطر المعلق
                    app_line = line.replace('#', '').strip().replace("'", "").replace('"', '').replace(',', '')
                    if '.apps.' in app_line:
                        app_name = app_line.split('.apps.')[0].strip()
                        disabled_apps.append(app_name)
                    elif line.endswith("',") or line.endswith('",'):
                        app_name = app_line
                        disabled_apps.append(app_name)
                        
        except Exception as e:
            print(f"خطأ في قراءة ملف الإعدادات: {e}")
            
        # إضافة التطبيقات المعروفة المعلقة
        known_disabled = [
            'hr', 'core', 'audit', 'meetings', 'tasks', 'inventory',
            'Purchase_orders', 'cars', 'attendance', 'org', 'employees',
            'companies', 'leaves', 'evaluations', 'payrolls', 'banks',
            'insurance', 'training', 'loans', 'disciplinary', 'tickets',
            'workflow', 'assets', 'rbac', 'reports', 'syssettings'
        ]
        
        for app in known_disabled:
            if app not in disabled_apps:
                disabled_apps.append(app)
                
        return disabled_apps
    
    def analyze_app_structure(self, app_name: str) -> Dict:
        """تحليل بنية التطبيق"""
        app_path = self.base_dir / app_name
        analysis = {
            'exists': app_path.exists(),
            'has_init': False,
            'has_apps': False,
            'has_models': False,
            'has_views': False,
            'has_urls': False,
            'has_admin': False,
            'has_migrations': False,
            'files': [],
            'errors': []
        }
        
        if not analysis['exists']:
            analysis['errors'].append(f"مجلد التطبيق غير موجود: {app_path}")
            return analysis
            
        try:
            # فحص الملفات الأساسية
            analysis['has_init'] = (app_path / '__init__.py').exists()
            analysis['has_apps'] = (app_path / 'apps.py').exists()
            analysis['has_models'] = (app_path / 'models.py').exists()
            analysis['has_views'] = (app_path / 'views.py').exists()
            analysis['has_urls'] = (app_path / 'urls.py').exists()
            analysis['has_admin'] = (app_path / 'admin.py').exists()
            analysis['has_migrations'] = (app_path / 'migrations').exists()
            
            # جمع قائمة الملفات
            for file_path in app_path.rglob('*.py'):
                if '__pycache__' not in str(file_path):
                    analysis['files'].append(str(file_path.relative_to(app_path)))
                    
        except Exception as e:
            analysis['errors'].append(f"خطأ في تحليل بنية التطبيق: {e}")
            
        return analysis
    
    def test_app_import(self, app_name: str) -> Dict:
        """اختبار استيراد التطبيق"""
        result = {
            'can_import': False,
            'import_errors': [],
            'missing_modules': []
        }
        
        try:
            # محاولة استيراد التطبيق
            module = importlib.import_module(app_name)
            result['can_import'] = True
            
            # محاولة استيراد apps.py إذا وجد
            try:
                apps_module = importlib.import_module(f'{app_name}.apps')
            except ImportError as e:
                result['import_errors'].append(f"خطأ في استيراد apps.py: {e}")
                
        except ImportError as e:
            result['import_errors'].append(str(e))
            
            # تحليل الخطأ لاستخراج المكتبات المفقودة
            error_str = str(e)
            if 'No module named' in error_str:
                module_name = error_str.split("'")[1] if "'" in error_str else None
                if module_name:
                    result['missing_modules'].append(module_name)
                    
        except Exception as e:
            result['import_errors'].append(f"خطأ عام في الاستيراد: {e}")
            
        return result
    
    def analyze_models(self, app_name: str) -> Dict:
        """تحليل نماذج التطبيق"""
        result = {
            'has_models_file': False,
            'models_count': 0,
            'models': [],
            'syntax_errors': [],
            'import_errors': []
        }
        
        models_file = self.base_dir / app_name / 'models.py'
        
        if not models_file.exists():
            return result
            
        result['has_models_file'] = True
        
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # البحث عن تعريفات النماذج
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('class ') and '(models.Model)' in line:
                    model_name = line.split('class ')[1].split('(')[0].strip()
                    result['models'].append(model_name)
                    
            result['models_count'] = len(result['models'])
            
            # محاولة تجميع الملف للتحقق من الأخطاء النحوية
            try:
                compile(content, str(models_file), 'exec')
            except SyntaxError as e:
                result['syntax_errors'].append(f"خطأ نحوي في السطر {e.lineno}: {e.msg}")
                
        except Exception as e:
            result['import_errors'].append(f"خطأ في قراءة ملف النماذج: {e}")
            
        return result
    
    def check_database_tables(self, app_name: str) -> Dict:
        """فحص جداول قاعدة البيانات للتطبيق"""
        result = {
            'tables_exist': False,
            'tables': [],
            'missing_tables': [],
            'db_errors': []
        }
        
        try:
            with connection.cursor() as cursor:
                # الحصول على قائمة الجداول
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                all_tables = [row[0] for row in cursor.fetchall()]
                
                # البحث عن جداول التطبيق
                app_tables = [table for table in all_tables if table.startswith(f'{app_name}_')]
                result['tables'] = app_tables
                result['tables_exist'] = len(app_tables) > 0
                
        except Exception as e:
            result['db_errors'].append(f"خطأ في فحص قاعدة البيانات: {e}")
            
        return result
    
    def analyze_dependencies(self, app_name: str) -> Dict:
        """تحليل تبعيات التطبيق"""
        result = {
            'internal_dependencies': [],
            'external_dependencies': [],
            'django_dependencies': [],
            'unknown_dependencies': []
        }
        
        app_path = self.base_dir / app_name
        if not app_path.exists():
            return result
            
        try:
            for py_file in app_path.rglob('*.py'):
                if '__pycache__' in str(py_file):
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # تحليل imports
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('import ') or line.startswith('from '):
                            self._categorize_import(line, result)
                            
                except Exception:
                    continue
                    
        except Exception as e:
            pass
            
        return result
    
    def _categorize_import(self, import_line: str, result: Dict):
        """تصنيف سطر الاستيراد"""
        if 'django' in import_line:
            if import_line not in result['django_dependencies']:
                result['django_dependencies'].append(import_line)
        elif any(app in import_line for app in self.disabled_apps):
            if import_line not in result['internal_dependencies']:
                result['internal_dependencies'].append(import_line)
        elif any(pkg in import_line for pkg in ['rest_framework', 'crispy_forms', 'corsheaders']):
            if import_line not in result['external_dependencies']:
                result['external_dependencies'].append(import_line)
        else:
            if import_line not in result['unknown_dependencies']:
                result['unknown_dependencies'].append(import_line)
    
    def calculate_priority(self, app_name: str, analysis: Dict) -> int:
        """حساب أولوية التطبيق للإصلاح"""
        priority = 3  # أولوية منخفضة افتراضياً
        
        # التطبيقات الأساسية
        if app_name in ['core', 'audit', 'org']:
            priority = 1
        elif app_name in ['hr', 'employees', 'attendance', 'companies']:
            priority = 2
            
        # تعديل الأولوية بناءً على التحليل
        if analysis['structure']['exists'] and analysis['import']['can_import']:
            priority = max(1, priority - 1)  # رفع الأولوية
            
        if analysis['import']['import_errors'] or analysis['models']['syntax_errors']:
            priority = min(3, priority + 1)  # خفض الأولوية
            
        return priority
    
    def run_full_analysis(self) -> Dict:
        """تشغيل التحليل الشامل"""
        print("بدء التحليل الشامل للنظام...")
        print(f"عدد التطبيقات المعلقة: {len(self.disabled_apps)}")
        print("-" * 50)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_disabled_apps': len(self.disabled_apps),
            'apps_analysis': {},
            'summary': {
                'ready_to_enable': [],
                'need_minor_fixes': [],
                'need_major_fixes': [],
                'missing_or_broken': []
            }
        }
        
        for i, app_name in enumerate(self.disabled_apps, 1):
            print(f"[{i}/{len(self.disabled_apps)}] تحليل التطبيق: {app_name}")
            
            app_analysis = {
                'structure': self.analyze_app_structure(app_name),
                'import': self.test_app_import(app_name),
                'models': self.analyze_models(app_name),
                'database': self.check_database_tables(app_name),
                'dependencies': self.analyze_dependencies(app_name),
                'priority': 0,
                'status': 'unknown'
            }
            
            # حساب الأولوية
            app_analysis['priority'] = self.calculate_priority(app_name, app_analysis)
            
            # تحديد الحالة
            if not app_analysis['structure']['exists']:
                app_analysis['status'] = 'missing'
                results['summary']['missing_or_broken'].append(app_name)
            elif app_analysis['import']['can_import'] and not app_analysis['models']['syntax_errors']:
                app_analysis['status'] = 'ready'
                results['summary']['ready_to_enable'].append(app_name)
            elif app_analysis['import']['import_errors'] or app_analysis['models']['syntax_errors']:
                if len(app_analysis['import']['import_errors']) <= 2:
                    app_analysis['status'] = 'minor_fixes'
                    results['summary']['need_minor_fixes'].append(app_name)
                else:
                    app_analysis['status'] = 'major_fixes'
                    results['summary']['need_major_fixes'].append(app_name)
            else:
                app_analysis['status'] = 'needs_investigation'
                results['summary']['need_major_fixes'].append(app_name)
            
            results['apps_analysis'][app_name] = app_analysis
            
        return results
    
    def generate_report(self, results: Dict) -> str:
        """إنشاء تقرير مفصل"""
        report = []
        report.append("=" * 80)
        report.append("تقرير التحليل الشامل للتطبيقات المعلقة")
        report.append("=" * 80)
        report.append(f"تاريخ التحليل: {results['timestamp']}")
        report.append(f"إجمالي التطبيقات المعلقة: {results['total_disabled_apps']}")
        report.append("")
        
        # ملخص الحالة
        report.append("ملخص الحالة:")
        report.append("-" * 20)
        report.append(f"جاهز للتفعيل: {len(results['summary']['ready_to_enable'])}")
        report.append(f"يحتاج إصلاحات بسيطة: {len(results['summary']['need_minor_fixes'])}")
        report.append(f"يحتاج إصلاحات كبيرة: {len(results['summary']['need_major_fixes'])}")
        report.append(f"مفقود أو معطل: {len(results['summary']['missing_or_broken'])}")
        report.append("")
        
        # ترتيب حسب الأولوية
        for priority in [1, 2, 3]:
            priority_apps = [
                (name, analysis) for name, analysis in results['apps_analysis'].items()
                if analysis['priority'] == priority
            ]
            
            if priority_apps:
                priority_name = {1: "عالية", 2: "متوسطة", 3: "منخفضة"}[priority]
                report.append(f"الأولوية {priority_name}:")
                report.append("-" * 30)
                
                for app_name, analysis in sorted(priority_apps):
                    report.append(f"  📱 {app_name}")
                    report.append(f"     الحالة: {analysis['status']}")
                    report.append(f"     موجود: {'✅' if analysis['structure']['exists'] else '❌'}")
                    report.append(f"     يمكن استيراده: {'✅' if analysis['import']['can_import'] else '❌'}")
                    report.append(f"     عدد النماذج: {analysis['models']['models_count']}")
                    
                    if analysis['import']['import_errors']:
                        report.append(f"     أخطاء الاستيراد:")
                        for error in analysis['import']['import_errors'][:2]:
                            report.append(f"       - {error}")
                        if len(analysis['import']['import_errors']) > 2:
                            report.append(f"       ... و {len(analysis['import']['import_errors']) - 2} أخطاء أخرى")
                    
                    if analysis['models']['syntax_errors']:
                        report.append(f"     أخطاء النماذج:")
                        for error in analysis['models']['syntax_errors'][:2]:
                            report.append(f"       - {error}")
                    
                    report.append("")
        
        # توصيات الإصلاح
        report.append("توصيات الإصلاح:")
        report.append("-" * 20)
        
        if results['summary']['ready_to_enable']:
            report.append("1. التطبيقات الجاهزة للتفعيل (يمكن تفعيلها مباشرة):")
            for app in results['summary']['ready_to_enable']:
                report.append(f"   - {app}")
            report.append("")
        
        if results['summary']['need_minor_fixes']:
            report.append("2. التطبيقات التي تحتاج إصلاحات بسيطة:")
            for app in results['summary']['need_minor_fixes']:
                report.append(f"   - {app}")
            report.append("")
        
        if results['summary']['need_major_fixes']:
            report.append("3. التطبيقات التي تحتاج إصلاحات كبيرة:")
            for app in results['summary']['need_major_fixes']:
                report.append(f"   - {app}")
            report.append("")
        
        if results['summary']['missing_or_broken']:
            report.append("4. التطبيقات المفقودة أو المعطلة:")
            for app in results['summary']['missing_or_broken']:
                report.append(f"   - {app}")
            report.append("")
        
        return "\n".join(report)
    
    def save_results(self, results: Dict, report: str):
        """حفظ نتائج التحليل"""
        # إنشاء مجلد التقارير
        reports_dir = self.base_dir / 'logs'
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # حفظ البيانات الخام
        json_file = reports_dir / f'system_analysis_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # حفظ التقرير النصي
        report_file = reports_dir / f'system_analysis_report_{timestamp}.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\nتم حفظ نتائج التحليل:")
        print(f"البيانات الخام: {json_file}")
        print(f"التقرير: {report_file}")
        
        return str(json_file), str(report_file)


def main():
    """الدالة الرئيسية"""
    try:
        analyzer = SystemAnalyzer()
        
        # تشغيل التحليل الشامل
        results = analyzer.run_full_analysis()
        
        # إنشاء التقرير
        report = analyzer.generate_report(results)
        
        # حفظ النتائج
        json_file, report_file = analyzer.save_results(results, report)
        
        # عرض التقرير
        print("\n" + "=" * 80)
        print(report)
        
        return True
        
    except Exception as e:
        print(f"خطأ في تشغيل التحليل: {e}")
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)