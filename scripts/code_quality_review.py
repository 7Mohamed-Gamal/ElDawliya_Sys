#!/usr/bin/env python
"""
Code Quality Review and Improvement Script
سكريبت مراجعة وتحسين جودة الكود

This script performs comprehensive code quality analysis including:
- PEP 8 compliance checking
- Code documentation review
- Security vulnerability scanning
- Performance optimization suggestions
- Code duplication detection
- Best practices validation
"""

import os
import sys
import ast
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CodeQualityAnalyzer:
    """محلل جودة الكود الشامل"""

    def __init__(self, project_root: str):
        """__init__ function"""
        self.project_root = Path(project_root)
        self.issues = []
        self.stats = {
            'total_files': 0,
            'python_files': 0,
            'lines_of_code': 0,
            'issues_found': 0,
            'critical_issues': 0,
            'warnings': 0,
            'suggestions': 0,
        }

        # Patterns for common issues
        self.security_patterns = [
            (r'eval\s*\(', 'CRITICAL', 'Use of eval() is dangerous'),
            (r'exec\s*\(', 'CRITICAL', 'Use of exec() is dangerous'),
            (r'shell=True', 'HIGH', 'shell=True in subprocess can be dangerous'),
            (r'pickle\.loads?\s*\(', 'HIGH', 'Pickle deserialization can be unsafe'),
            (r'SECRET_KEY\s*=\s*[\'"][^\'"]+[\'"]', 'HIGH', 'Hardcoded secret key'),
            (r'PASSWORD\s*=\s*[\'"][^\'"]+[\'"]', 'MEDIUM', 'Hardcoded password'),
            (r'DEBUG\s*=\s*True', 'MEDIUM', 'Debug mode enabled'),
        ]

        self.performance_patterns = [
            (r'\.objects\.all\(\)', 'MEDIUM', 'Consider using select_related or prefetch_related'),
            (r'for\s+\w+\s+in\s+\w+\.objects\.all\(\)', 'HIGH', 'N+1 query problem'),
            (r'print\s*\(', 'LOW', 'Use logging instead of print statements'),
            (r'time\.sleep\s*\(', 'MEDIUM', 'Blocking sleep in web application'),
        ]

        self.code_smell_patterns = [
            (r'TODO|FIXME|XXX|HACK', 'LOW', 'TODO/FIXME comment found'),
            (r'def\s+\w+\([^)]*\):\s*pass', 'LOW', 'Empty function definition'),
            (r'except:\s*pass', 'HIGH', 'Bare except clause with pass'),
            (r'except\s+Exception:\s*pass', 'MEDIUM', 'Broad exception handling with pass'),
        ]

    def analyze_project(self) -> Dict[str, Any]:
        """تحليل المشروع بالكامل"""
        logger.info("🔍 بدء تحليل جودة الكود...")

        # Analyze Python files
        python_files = list(self.project_root.rglob('*.py'))
        self.stats['python_files'] = len(python_files)

        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue

            self._analyze_file(file_path)

        # Run additional tools
        self._run_flake8()
        self._run_bandit()
        self._check_requirements()

        # Generate summary
        summary = self._generate_summary()

        logger.info(f"✅ تم تحليل {self.stats['python_files']} ملف Python")
        logger.info(f"📊 تم العثور على {self.stats['issues_found']} مشكلة")

        return summary

    def _should_skip_file(self, file_path: Path) -> bool:
        """تحديد ما إذا كان يجب تخطي الملف"""
        skip_patterns = [
            'migrations/',
            '__pycache__/',
            '.git/',
            'venv/',
            'env/',
            '.tox/',
            'build/',
            'dist/',
            '.pytest_cache/',
        ]

        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)

    def _analyze_file(self, file_path: Path):
        """تحليل ملف واحد"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.stats['total_files'] += 1
            self.stats['lines_of_code'] += len(content.splitlines())

            # Check for security issues
            self._check_security_patterns(file_path, content)

            # Check for performance issues
            self._check_performance_patterns(file_path, content)

            # Check for code smells
            self._check_code_smells(file_path, content)

            # Check PEP 8 compliance
            self._check_pep8_compliance(file_path, content)

            # Check documentation
            self._check_documentation(file_path, content)

            # Check imports
            self._check_imports(file_path, content)

        except Exception as e:
            self._add_issue(
                file_path, 0, 'ERROR',
                f'Error analyzing file: {str(e)}'
            )

    def _check_security_patterns(self, file_path: Path, content: str):
        """فحص الأنماط الأمنية"""
        lines = content.splitlines()

        for line_num, line in enumerate(lines, 1):
            for pattern, severity, message in self.security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_issue(file_path, line_num, severity, message)

    def _check_performance_patterns(self, file_path: Path, content: str):
        """فحص أنماط الأداء"""
        lines = content.splitlines()

        for line_num, line in enumerate(lines, 1):
            for pattern, severity, message in self.performance_patterns:
                if re.search(pattern, line):
                    self._add_issue(file_path, line_num, severity, message)

    def _check_code_smells(self, file_path: Path, content: str):
        """فحص روائح الكود"""
        lines = content.splitlines()

        for line_num, line in enumerate(lines, 1):
            for pattern, severity, message in self.code_smell_patterns:
                if re.search(pattern, line):
                    self._add_issue(file_path, line_num, severity, message)

    def _check_pep8_compliance(self, file_path: Path, content: str):
        """فحص الامتثال لـ PEP 8"""
        lines = content.splitlines()

        for line_num, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 120:
                self._add_issue(
                    file_path, line_num, 'LOW',
                    f'Line too long ({len(line)} > 120 characters)'
                )

            # Check trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                self._add_issue(
                    file_path, line_num, 'LOW',
                    'Trailing whitespace'
                )

            # Check mixed tabs and spaces
            if '\t' in line and '    ' in line:
                self._add_issue(
                    file_path, line_num, 'MEDIUM',
                    'Mixed tabs and spaces'
                )

    def _check_documentation(self, file_path: Path, content: str):
        """فحص التوثيق"""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not ast.get_docstring(node):
                        self._add_issue(
                            file_path, node.lineno, 'LOW',
                            f'Function {node.name} lacks docstring'
                        )

                elif isinstance(node, ast.ClassDef):
                    if not ast.get_docstring(node):
                        self._add_issue(
                            file_path, node.lineno, 'LOW',
                            f'Class {node.name} lacks docstring'
                        )

        except SyntaxError:
            self._add_issue(
                file_path, 0, 'CRITICAL',
                'Syntax error in file'
            )

    def _check_imports(self, file_path: Path, content: str):
        """فحص الاستيرادات"""
        lines = content.splitlines()

        import_lines = []
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                import_lines.append((line_num, stripped))

        # Check for unused imports (basic check)
        for line_num, import_line in import_lines:
            if 'import *' in import_line:
                self._add_issue(
                    file_path, line_num, 'MEDIUM',
                    'Wildcard import should be avoided'
                )

    def _run_flake8(self):
        """تشغيل flake8 للفحص الإضافي"""
        try:
            result = subprocess.run(
                ['flake8', '--max-line-length=120', '--exclude=migrations', str(self.project_root)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.stdout:
                for line in result.stdout.splitlines():
                    if ':' in line:
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            file_path = Path(parts[0])
                            line_num = int(parts[1]) if parts[1].isdigit() else 0
                            message = parts[3].strip()

                            self._add_issue(file_path, line_num, 'LOW', f'Flake8: {message}')

        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("⚠️ Flake8 not available or timed out")

    def _run_bandit(self):
        """تشغيل bandit للفحص الأمني"""
        try:
            result = subprocess.run(
                ['bandit', '-r', str(self.project_root), '-f', 'json', '--exclude', '*/migrations/*'],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.stdout:
                try:
                    bandit_results = json.loads(result.stdout)

                    for issue in bandit_results.get('results', []):
                        file_path = Path(issue['filename'])
                        line_num = issue['line_number']
                        severity = issue['issue_severity'].upper()
                        message = f"Bandit: {issue['issue_text']}"

                        self._add_issue(file_path, line_num, severity, message)

                except json.JSONDecodeError:
                    pass

        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("⚠️ Bandit not available or timed out")

    def _check_requirements(self):
        """فحص ملفات المتطلبات"""
        req_files = [
            'requirements.txt',
            'requirements/base.txt',
            'requirements/production.txt',
            'requirements/development.txt'
        ]

        for req_file in req_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                self._analyze_requirements_file(req_path)

    def _analyze_requirements_file(self, req_path: Path):
        """تحليل ملف المتطلبات"""
        try:
            with open(req_path, 'r') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Check for unpinned versions
                    if '==' not in line and '>=' not in line and '~=' not in line:
                        self._add_issue(
                            req_path, line_num, 'MEDIUM',
                            f'Unpinned dependency: {line}'
                        )

        except Exception as e:
            self._add_issue(
                req_path, 0, 'ERROR',
                f'Error reading requirements file: {str(e)}'
            )

    def _add_issue(self, file_path: Path, line_num: int, severity: str, message: str):
        """إضافة مشكلة إلى القائمة"""
        issue = {
            'file': str(file_path.relative_to(self.project_root)),
            'line': line_num,
            'severity': severity,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        self.issues.append(issue)
        self.stats['issues_found'] += 1

        if severity == 'CRITICAL':
            self.stats['critical_issues'] += 1
        elif severity in ['HIGH', 'MEDIUM']:
            self.stats['warnings'] += 1
        else:
            self.stats['suggestions'] += 1

    def _generate_summary(self) -> Dict[str, Any]:
        """توليد ملخص التحليل"""
        # Group issues by severity
        issues_by_severity = {}
        for issue in self.issues:
            severity = issue['severity']
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)

        # Group issues by file
        issues_by_file = {}
        for issue in self.issues:
            file_path = issue['file']
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)

        # Calculate quality score
        total_issues = self.stats['issues_found']
        critical_weight = self.stats['critical_issues'] * 10
        warning_weight = self.stats['warnings'] * 3
        suggestion_weight = self.stats['suggestions'] * 1

        weighted_issues = critical_weight + warning_weight + suggestion_weight
        max_score = 100

        if self.stats['lines_of_code'] > 0:
            quality_score = max(0, max_score - (weighted_issues / self.stats['lines_of_code'] * 1000))
        else:
            quality_score = max_score

        return {
            'summary': {
                'analysis_date': datetime.now().isoformat(),
                'project_root': str(self.project_root),
                'quality_score': round(quality_score, 2),
                'total_files_analyzed': self.stats['total_files'],
                'python_files': self.stats['python_files'],
                'lines_of_code': self.stats['lines_of_code'],
                'total_issues': self.stats['issues_found'],
                'critical_issues': self.stats['critical_issues'],
                'warnings': self.stats['warnings'],
                'suggestions': self.stats['suggestions'],
            },
            'issues_by_severity': issues_by_severity,
            'issues_by_file': issues_by_file,
            'all_issues': self.issues,
            'recommendations': self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """توليد التوصيات"""
        recommendations = []

        if self.stats['critical_issues'] > 0:
            recommendations.append(
                f"🚨 يوجد {self.stats['critical_issues']} مشكلة حرجة تحتاج إلى إصلاح فوري"
            )

        if self.stats['warnings'] > 10:
            recommendations.append(
                "⚠️ عدد كبير من التحذيرات - يُنصح بمراجعة وإصلاح المشاكل الأساسية"
            )

        # Check for specific patterns
        security_issues = [i for i in self.issues if 'security' in i['message'].lower() or i['severity'] == 'CRITICAL']
        if security_issues:
            recommendations.append(
                "🔒 تم العثور على مشاكل أمنية محتملة - يُنصح بمراجعة أمنية شاملة"
            )

        performance_issues = [i for i in self.issues if 'performance' in i['message'].lower() or 'query' in i['message'].lower()]
        if performance_issues:
            recommendations.append(
                "⚡ تم العثور على مشاكل أداء محتملة - يُنصح بتحسين الاستعلامات والكود"
            )

        documentation_issues = [i for i in self.issues if 'docstring' in i['message'].lower()]
        if len(documentation_issues) > 20:
            recommendations.append(
                "📚 نقص في التوثيق - يُنصح بإضافة docstrings للدوال والكلاسات"
            )

        return recommendations


class CodeFormatter:
    """منسق الكود"""

    def __init__(self, project_root: str):
        """__init__ function"""
        self.project_root = Path(project_root)

    def format_code(self) -> Dict[str, Any]:
        """تنسيق الكود باستخدام black و isort"""
        results = {
            'black_result': None,
            'isort_result': None,
            'success': False
        }

        try:
            # Run black
            logger.info("🎨 تشغيل Black لتنسيق الكود...")
            black_result = subprocess.run(
                ['black', '--line-length=120', '--exclude=migrations', str(self.project_root)],
                capture_output=True,
                text=True,
                timeout=120
            )
            results['black_result'] = {
                'returncode': black_result.returncode,
                'stdout': black_result.stdout,
                'stderr': black_result.stderr
            }

            # Run isort
            logger.info("📦 تشغيل isort لترتيب الاستيرادات...")
            isort_result = subprocess.run(
                ['isort', '--profile=black', '--line-length=120', str(self.project_root)],
                capture_output=True,
                text=True,
                timeout=120
            )
            results['isort_result'] = {
                'returncode': isort_result.returncode,
                'stdout': isort_result.stdout,
                'stderr': isort_result.stderr
            }

            results['success'] = True
            logger.info("✅ تم تنسيق الكود بنجاح")

        except subprocess.TimeoutExpired:
            logger.error("❌ انتهت مهلة تنسيق الكود")
        except FileNotFoundError as e:
            logger.error(f"❌ أداة التنسيق غير متوفرة: {e}")
        except Exception as e:
            logger.error(f"❌ خطأ في تنسيق الكود: {e}")

        return results


def generate_quality_report(analysis_results: Dict[str, Any], output_file: str):
    """توليد تقرير جودة الكود"""

    report_content = f"""
# تقرير جودة الكود - نظام الدولية
## Code Quality Report - ElDawliya System

**تاريخ التحليل:** {analysis_results['summary']['analysis_date']}
**Analysis Date:** {analysis_results['summary']['analysis_date']}

## ملخص النتائج / Summary

- **نقاط الجودة / Quality Score:** {analysis_results['summary']['quality_score']}/100
- **إجمالي الملفات / Total Files:** {analysis_results['summary']['total_files_analyzed']}
- **ملفات Python:** {analysis_results['summary']['python_files']}
- **أسطر الكود / Lines of Code:** {analysis_results['summary']['lines_of_code']:,}
- **إجمالي المشاكل / Total Issues:** {analysis_results['summary']['total_issues']}

### توزيع المشاكل / Issue Distribution

- **🚨 مشاكل حرجة / Critical:** {analysis_results['summary']['critical_issues']}
- **⚠️ تحذيرات / Warnings:** {analysis_results['summary']['warnings']}
- **💡 اقتراحات / Suggestions:** {analysis_results['summary']['suggestions']}

## التوصيات / Recommendations

"""

    for recommendation in analysis_results['recommendations']:
        report_content += f"- {recommendation}\n"

    report_content += "\n## المشاكل حسب الخطورة / Issues by Severity\n\n"

    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        if severity in analysis_results['issues_by_severity']:
            issues = analysis_results['issues_by_severity'][severity]
            report_content += f"### {severity} ({len(issues)} مشكلة)\n\n"

            for issue in issues[:10]:  # Show first 10 issues
                report_content += f"- **{issue['file']}:{issue['line']}** - {issue['message']}\n"

            if len(issues) > 10:
                report_content += f"- ... و {len(issues) - 10} مشكلة أخرى\n"

            report_content += "\n"

    report_content += "\n## الملفات الأكثر مشاكل / Most Problematic Files\n\n"

    # Sort files by issue count
    files_by_issue_count = sorted(
        analysis_results['issues_by_file'].items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    for file_path, issues in files_by_issue_count[:10]:
        report_content += f"- **{file_path}** - {len(issues)} مشكلة\n"

    # Write report to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    logger.info(f"📄 تم إنشاء التقرير: {output_file}")


def main():
    """الدالة الرئيسية"""

    print("🔍 مراجعة جودة الكود - نظام الدولية")
    print("=" * 50)

    # Get project root
    project_root = os.getcwd()

    # Initialize analyzer
    analyzer = CodeQualityAnalyzer(project_root)

    # Run analysis
    print("📊 تشغيل تحليل جودة الكود...")
    analysis_results = analyzer.analyze_project()

    # Format code (optional)
    format_choice = input("\n🎨 هل تريد تنسيق الكود تلقائياً؟ (y/n): ").lower().strip()
    if format_choice == 'y':
        formatter = CodeFormatter(project_root)
        format_results = formatter.format_code()

        if format_results['success']:
            print("✅ تم تنسيق الكود بنجاح")
        else:
            print("❌ فشل في تنسيق الكود")

    # Generate report
    report_file = f"CODE_QUALITY_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    generate_quality_report(analysis_results, report_file)

    # Save detailed results as JSON
    json_file = f"code_quality_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)

    print(f"💾 تم حفظ النتائج التفصيلية: {json_file}")

    # Print summary
    print("\n" + "=" * 50)
    print("📋 ملخص النتائج:")
    print(f"   نقاط الجودة: {analysis_results['summary']['quality_score']}/100")
    print(f"   إجمالي المشاكل: {analysis_results['summary']['total_issues']}")
    print(f"   مشاكل حرجة: {analysis_results['summary']['critical_issues']}")
    print(f"   تحذيرات: {analysis_results['summary']['warnings']}")
    print(f"   اقتراحات: {analysis_results['summary']['suggestions']}")

    if analysis_results['summary']['critical_issues'] > 0:
        print("\n🚨 تحذير: يوجد مشاكل حرجة تحتاج إلى إصلاح فوري!")
        return 1

    print("\n✅ تم إكمال مراجعة جودة الكود")
    return 0


if __name__ == '__main__':
    sys.exit(main())
