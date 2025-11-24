"""
Security Test Runner
Comprehensive security test execution and reporting
"""
import os
import sys
import django
import pytest
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()


class SecurityTestRunner:
    """
    Security test runner with comprehensive reporting
    """
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.report_path = project_root / 'tests' / 'security' / 'reports'
        self.report_path.mkdir(exist_ok=True)
    
    def run_all_security_tests(self):
        """Run all security tests and generate report"""
        print("🔒 Starting Comprehensive Security Testing...")
        print("=" * 60)
        
        self.start_time = datetime.now()
        
        # Test categories
        test_categories = [
            {
                'name': 'OWASP Top 10',
                'file': 'test_owasp_top10.py',
                'description': 'Tests for OWASP Top 10 vulnerabilities'
            },
            {
                'name': 'Authentication & Authorization',
                'file': 'test_authentication.py',
                'description': 'Authentication and authorization security tests'
            },
            {
                'name': 'API Security',
                'file': 'test_api_security.py',
                'description': 'REST API security tests'
            },
            {
                'name': 'Data Protection',
                'file': 'test_data_protection.py',
                'description': 'Data encryption and privacy tests'
            },
            {
                'name': 'Penetration Testing',
                'file': 'test_penetration.py',
                'description': 'Advanced penetration testing scenarios'
            }
        ]
        
        for category in test_categories:
            print(f"\n📋 Running {category['name']} Tests...")
            print(f"   {category['description']}")
            print("-" * 40)
            
            result = self._run_test_category(category)
            self.test_results[category['name']] = result
            
            # Print summary
            if result['success']:
                print(f"✅ {category['name']}: {result['passed']}/{result['total']} tests passed")
            else:
                print(f"❌ {category['name']}: {result['passed']}/{result['total']} tests passed")
                if result['failures']:
                    print(f"   Failures: {len(result['failures'])}")
                if result['errors']:
                    print(f"   Errors: {len(result['errors'])}")
        
        self.end_time = datetime.now()
        
        # Generate comprehensive report
        self._generate_security_report()
        
        # Print final summary
        self._print_final_summary()
    
    def _run_test_category(self, category):
        """Run a specific test category"""
        test_file = project_root / 'tests' / 'security' / category['file']
        
        if not test_file.exists():
            return {
                'success': False,
                'total': 0,
                'passed': 0,
                'failures': [],
                'errors': [f"Test file {category['file']} not found"],
                'duration': 0
            }
        
        # Run pytest with JSON report
        start_time = time.time()
        
        try:
            # Run pytest and capture results
            result = pytest.main([
                str(test_file),
                '--tb=short',
                '--quiet',
                '--disable-warnings'
            ])
            
            duration = time.time() - start_time
            
            # For now, return basic result structure
            # In a real implementation, you would parse pytest output
            return {
                'success': result == 0,
                'total': 1,  # Placeholder
                'passed': 1 if result == 0 else 0,
                'failures': [] if result == 0 else ['Some tests failed'],
                'errors': [],
                'duration': duration
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                'success': False,
                'total': 0,
                'passed': 0,
                'failures': [],
                'errors': [str(e)],
                'duration': duration
            }
    
    def _generate_security_report(self):
        """Generate comprehensive security report"""
        report_data = {
            'test_run': {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'duration': (self.end_time - self.start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            },
            'summary': self._calculate_summary(),
            'categories': self.test_results,
            'recommendations': self._generate_recommendations(),
            'security_checklist': self._generate_security_checklist()
        }
        
        # Save JSON report
        json_report_path = self.report_path / f'security_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Generate HTML report
        html_report_path = self.report_path / f'security_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        self._generate_html_report(report_data, html_report_path)
        
        print(f"\n📊 Security reports generated:")
        print(f"   JSON: {json_report_path}")
        print(f"   HTML: {html_report_path}")
    
    def _calculate_summary(self):
        """Calculate overall test summary"""
        total_tests = sum(result['total'] for result in self.test_results.values())
        total_passed = sum(result['passed'] for result in self.test_results.values())
        total_failures = sum(len(result['failures']) for result in self.test_results.values())
        total_errors = sum(len(result['errors']) for result in self.test_results.values())
        
        return {
            'total_tests': total_tests,
            'passed': total_passed,
            'failures': total_failures,
            'errors': total_errors,
            'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0,
            'categories_tested': len(self.test_results)
        }
    
    def _generate_recommendations(self):
        """Generate security recommendations based on test results"""
        recommendations = []
        
        # Analyze test results and generate recommendations
        for category, result in self.test_results.items():
            if not result['success']:
                if category == 'OWASP Top 10':
                    recommendations.extend([
                        "Review and implement OWASP Top 10 security controls",
                        "Conduct regular security code reviews",
                        "Implement input validation and output encoding",
                        "Use parameterized queries to prevent SQL injection"
                    ])
                elif category == 'Authentication & Authorization':
                    recommendations.extend([
                        "Implement strong password policies",
                        "Add multi-factor authentication (MFA)",
                        "Review and strengthen session management",
                        "Implement proper access controls and role-based permissions"
                    ])
                elif category == 'API Security':
                    recommendations.extend([
                        "Implement API rate limiting and throttling",
                        "Add comprehensive API input validation",
                        "Use proper API authentication mechanisms (JWT, OAuth)",
                        "Implement API versioning and deprecation policies"
                    ])
                elif category == 'Data Protection':
                    recommendations.extend([
                        "Encrypt sensitive data at rest and in transit",
                        "Implement data anonymization for logs and exports",
                        "Review and strengthen backup security",
                        "Implement data retention and deletion policies"
                    ])
                elif category == 'Penetration Testing':
                    recommendations.extend([
                        "Conduct regular penetration testing",
                        "Implement Web Application Firewall (WAF)",
                        "Review and harden server configurations",
                        "Implement intrusion detection and monitoring"
                    ])
        
        # Remove duplicates and add general recommendations
        recommendations = list(set(recommendations))
        recommendations.extend([
            "Keep all dependencies and frameworks up to date",
            "Implement comprehensive logging and monitoring",
            "Conduct regular security training for development team",
            "Establish incident response procedures"
        ])
        
        return recommendations
    
    def _generate_security_checklist(self):
        """Generate security implementation checklist"""
        return {
            'authentication': [
                "Strong password policy implemented",
                "Multi-factor authentication available",
                "Session management secure",
                "Account lockout protection",
                "Password reset security"
            ],
            'authorization': [
                "Role-based access control implemented",
                "Principle of least privilege applied",
                "Object-level permissions enforced",
                "API authorization properly implemented"
            ],
            'input_validation': [
                "All user inputs validated",
                "SQL injection protection implemented",
                "XSS protection in place",
                "File upload security implemented",
                "CSRF protection enabled"
            ],
            'data_protection': [
                "Sensitive data encrypted",
                "Secure communication (HTTPS)",
                "Database security implemented",
                "Backup security ensured",
                "Data retention policies defined"
            ],
            'infrastructure': [
                "Security headers implemented",
                "Error handling secure",
                "Logging and monitoring in place",
                "Regular security updates applied",
                "Security configuration reviewed"
            ]
        }
    
    def _generate_html_report(self, report_data, output_path):
        """Generate HTML security report"""
        html_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير الأمان الشامل - نظام الدولية</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            direction: rtl;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .summary {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #495057;
        }
        .summary-card .number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .danger { color: #dc3545; }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #495057;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .test-category {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        .test-category-header {
            background: #e9ecef;
            padding: 15px 20px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .test-category-content {
            padding: 20px;
        }
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .status-success {
            background: #d4edda;
            color: #155724;
        }
        .status-danger {
            background: #f8d7da;
            color: #721c24;
        }
        .recommendations {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
        }
        .recommendations h3 {
            color: #856404;
            margin-top: 0;
        }
        .recommendations ul {
            margin: 0;
            padding-right: 20px;
        }
        .recommendations li {
            margin-bottom: 8px;
        }
        .checklist {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .checklist-category {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
        }
        .checklist-category h4 {
            margin-top: 0;
            color: #495057;
        }
        .checklist-item {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .checklist-item input {
            margin-left: 10px;
        }
        .footer {
            background: #495057;
            color: white;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 تقرير الأمان الشامل</h1>
            <p>نظام الدولية - اختبارات الأمان والثغرات</p>
            <p>تاريخ التقرير: {timestamp}</p>
        </div>
        
        <div class="summary">
            <h2>ملخص النتائج</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>إجمالي الاختبارات</h3>
                    <div class="number">{total_tests}</div>
                </div>
                <div class="summary-card">
                    <h3>الاختبارات الناجحة</h3>
                    <div class="number success">{passed_tests}</div>
                </div>
                <div class="summary-card">
                    <h3>الاختبارات الفاشلة</h3>
                    <div class="number danger">{failed_tests}</div>
                </div>
                <div class="summary-card">
                    <h3>معدل النجاح</h3>
                    <div class="number">{success_rate:.1f}%</div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>نتائج الاختبارات حسب الفئة</h2>
                {test_categories_html}
            </div>
            
            <div class="section">
                <h2>التوصيات الأمنية</h2>
                <div class="recommendations">
                    <h3>🔧 التوصيات المقترحة</h3>
                    <ul>
                        {recommendations_html}
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2>قائمة التحقق الأمنية</h2>
                <div class="checklist">
                    {checklist_html}
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>تم إنشاء هذا التقرير بواسطة نظام اختبار الأمان الآلي</p>
            <p>مدة الاختبار: {duration:.2f} ثانية</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Generate HTML content
        summary = report_data['summary']
        
        # Test categories HTML
        test_categories_html = ""
        for category, result in report_data['categories'].items():
            status_class = "status-success" if result['success'] else "status-danger"
            status_text = "نجح" if result['success'] else "فشل"
            
            test_categories_html += f"""
            <div class="test-category">
                <div class="test-category-header">
                    <span>{category}</span>
                    <span class="status-badge {status_class}">{status_text}</span>
                </div>
                <div class="test-category-content">
                    <p>الاختبارات الناجحة: {result['passed']}/{result['total']}</p>
                    <p>مدة التنفيذ: {result['duration']:.2f} ثانية</p>
                </div>
            </div>
            """
        
        # Recommendations HTML
        recommendations_html = ""
        for rec in report_data['recommendations']:
            recommendations_html += f"<li>{rec}</li>"
        
        # Checklist HTML
        checklist_html = ""
        for category, items in report_data['security_checklist'].items():
            checklist_html += f"""
            <div class="checklist-category">
                <h4>{category}</h4>
                {' '.join([f'<div class="checklist-item"><input type="checkbox"> <span>{item}</span></div>' for item in items])}
            </div>
            """
        
        # Fill template
        html_content = html_template.format(
            timestamp=report_data['test_run']['timestamp'],
            total_tests=summary['total_tests'],
            passed_tests=summary['passed'],
            failed_tests=summary['failures'] + summary['errors'],
            success_rate=summary['success_rate'],
            duration=report_data['test_run']['duration'],
            test_categories_html=test_categories_html,
            recommendations_html=recommendations_html,
            checklist_html=checklist_html
        )
        
        # Save HTML report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _print_final_summary(self):
        """Print final test summary"""
        summary = self._calculate_summary()
        
        print("\n" + "=" * 60)
        print("🔒 SECURITY TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failures']} ❌")
        print(f"Errors: {summary['errors']} ⚠️")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Duration: {(self.end_time - self.start_time).total_seconds():.2f} seconds")
        print("=" * 60)
        
        if summary['success_rate'] >= 90:
            print("🎉 Excellent! Your application has strong security measures.")
        elif summary['success_rate'] >= 70:
            print("👍 Good security posture, but there's room for improvement.")
        elif summary['success_rate'] >= 50:
            print("⚠️  Moderate security level. Please address the identified issues.")
        else:
            print("🚨 Critical security issues detected. Immediate action required!")


def main():
    """Main function to run security tests"""
    runner = SecurityTestRunner()
    runner.run_all_security_tests()


if __name__ == '__main__':
    main()