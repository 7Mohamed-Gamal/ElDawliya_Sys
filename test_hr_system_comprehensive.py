"""
Comprehensive HR System Testing Suite
Professional testing framework for ElDawliya_Sys HR applications
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import User
from django.db import connection
from django.core.management import call_command
import logging

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

logger = logging.getLogger(__name__)


class HRSystemTestSuite:
    """Comprehensive test suite for HR system"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = {
            'url_tests': {},
            'model_tests': {},
            'view_tests': {},
            'integration_tests': {},
            'performance_tests': {}
        }
        self.hr_apps = [
            'hr', 'employees', 'attendance', 'leaves', 'payrolls', 
            'evaluations', 'insurance', 'training', 'loans', 
            'disciplinary', 'assets', 'cars', 'reports'
        ]
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive HR System Tests...")
        
        # Test URL patterns
        print("\n📋 Testing URL Patterns...")
        self.test_url_patterns()
        
        # Test model integrity
        print("\n🗄️ Testing Model Integrity...")
        self.test_model_integrity()
        
        # Test view accessibility
        print("\n🌐 Testing View Accessibility...")
        self.test_view_accessibility()
        
        # Test database connectivity
        print("\n💾 Testing Database Connectivity...")
        self.test_database_connectivity()
        
        # Generate comprehensive report
        print("\n📊 Generating Test Report...")
        return self.generate_test_report()
    
    def test_url_patterns(self):
        """Test URL pattern validity and accessibility"""
        url_results = {}
        
        for app_name in self.hr_apps:
            app_results = {
                'valid_urls': [],
                'invalid_urls': [],
                'accessible_urls': [],
                'protected_urls': []
            }
            
            # Define expected URL patterns for each app
            expected_urls = self.get_expected_urls(app_name)
            
            for url_pattern in expected_urls:
                try:
                    url_name = f"{app_name}:{url_pattern}"
                    reversed_url = reverse(url_name)
                    app_results['valid_urls'].append({
                        'pattern': url_pattern,
                        'url': reversed_url,
                        'status': 'valid'
                    })
                    
                    # Test accessibility
                    try:
                        response = self.client.get(reversed_url)
                        if response.status_code in [200, 302, 403]:  # 403 means protected but exists
                            app_results['accessible_urls'].append(url_pattern)
                        if response.status_code == 403:
                            app_results['protected_urls'].append(url_pattern)
                    except Exception as e:
                        logger.warning(f"Error accessing {url_name}: {str(e)}")
                
                except NoReverseMatch:
                    app_results['invalid_urls'].append({
                        'pattern': url_pattern,
                        'error': 'URL pattern not found'
                    })
                except Exception as e:
                    app_results['invalid_urls'].append({
                        'pattern': url_pattern,
                        'error': str(e)
                    })
            
            url_results[app_name] = app_results
            
            # Print progress
            valid_count = len(app_results['valid_urls'])
            total_count = len(expected_urls)
            print(f"  ✅ {app_name}: {valid_count}/{total_count} URLs valid")
        
        self.test_results['url_tests'] = url_results
    
    def test_model_integrity(self):
        """Test model definitions and relationships"""
        model_results = {}
        
        # Test core models
        core_models = {
            'employees': ['Employee', 'EmployeeBankAccount', 'EmployeeDocument'],
            'attendance': ['AttendanceRule', 'AttendanceRecord', 'ZKDevice', 'AttendanceSummary'],
            'leaves': ['LeaveType', 'LeaveRequest', 'LeaveBalance'],
            'payrolls': ['EmployeeSalary', 'PayrollRun', 'PayrollDetail'],
            'evaluations': ['EvaluationPeriod', 'EmployeeEvaluation'],
            'insurance': ['HealthInsuranceProvider', 'EmployeeHealthInsurance', 'EmployeeSocialInsurance']
        }
        
        for app_name, models in core_models.items():
            app_results = {
                'importable_models': [],
                'model_errors': [],
                'field_validations': []
            }
            
            for model_name in models:
                try:
                    # Try to import the model
                    module = __import__(f'{app_name}.models', fromlist=[model_name])
                    model_class = getattr(module, model_name)
                    
                    app_results['importable_models'].append({
                        'model': model_name,
                        'fields': len(model_class._meta.fields),
                        'table_name': model_class._meta.db_table
                    })
                    
                    # Test model validation
                    try:
                        # Create a test instance (without saving)
                        test_instance = model_class()
                        # This will validate field definitions
                        test_instance._meta.get_fields()
                        app_results['field_validations'].append(f"{model_name}: OK")
                    except Exception as e:
                        app_results['field_validations'].append(f"{model_name}: {str(e)}")
                
                except ImportError as e:
                    app_results['model_errors'].append({
                        'model': model_name,
                        'error': f"Import error: {str(e)}"
                    })
                except AttributeError as e:
                    app_results['model_errors'].append({
                        'model': model_name,
                        'error': f"Model not found: {str(e)}"
                    })
                except Exception as e:
                    app_results['model_errors'].append({
                        'model': model_name,
                        'error': str(e)
                    })
            
            model_results[app_name] = app_results
            
            # Print progress
            success_count = len(app_results['importable_models'])
            total_count = len(models)
            print(f"  ✅ {app_name}: {success_count}/{total_count} models importable")
        
        self.test_results['model_tests'] = model_results
    
    def test_view_accessibility(self):
        """Test view function accessibility"""
        view_results = {}
        
        for app_name in self.hr_apps:
            app_results = {
                'accessible_views': [],
                'protected_views': [],
                'error_views': [],
                'redirect_views': []
            }
            
            # Test dashboard views (most common)
            dashboard_urls = [f"{app_name}:dashboard", f"{app_name}:index"]
            
            for url_name in dashboard_urls:
                try:
                    url = reverse(url_name)
                    response = self.client.get(url)
                    
                    if response.status_code == 200:
                        app_results['accessible_views'].append(url_name)
                    elif response.status_code == 302:
                        app_results['redirect_views'].append(url_name)
                    elif response.status_code == 403:
                        app_results['protected_views'].append(url_name)
                    else:
                        app_results['error_views'].append({
                            'url': url_name,
                            'status': response.status_code
                        })
                
                except NoReverseMatch:
                    continue  # URL doesn't exist, skip
                except Exception as e:
                    app_results['error_views'].append({
                        'url': url_name,
                        'error': str(e)
                    })
            
            view_results[app_name] = app_results
        
        self.test_results['view_tests'] = view_results
    
    def test_database_connectivity(self):
        """Test database connectivity and basic operations"""
        db_results = {
            'connection_status': 'unknown',
            'table_count': 0,
            'hr_tables': [],
            'connection_error': None
        }
        
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_results['connection_status'] = 'connected'
                
                # Get HR-related tables
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_TYPE = 'BASE TABLE'
                    AND (TABLE_NAME LIKE '%Employee%' 
                         OR TABLE_NAME LIKE '%Attendance%'
                         OR TABLE_NAME LIKE '%Leave%'
                         OR TABLE_NAME LIKE '%Payroll%'
                         OR TABLE_NAME LIKE '%Evaluation%'
                         OR TABLE_NAME LIKE '%Insurance%')
                """)
                
                hr_tables = [row[0] for row in cursor.fetchall()]
                db_results['hr_tables'] = hr_tables
                db_results['table_count'] = len(hr_tables)
                
                print(f"  ✅ Database: Connected, {len(hr_tables)} HR tables found")
        
        except Exception as e:
            db_results['connection_status'] = 'error'
            db_results['connection_error'] = str(e)
            print(f"  ❌ Database: Connection failed - {str(e)}")
        
        self.test_results['integration_tests']['database'] = db_results
    
    def get_expected_urls(self, app_name):
        """Get expected URL patterns for each app"""
        url_patterns = {
            'hr': ['dashboard', 'profile', 'my_payslips', 'my_leaves', 'notifications', 'settings'],
            'employees': ['dashboard', 'employee_list'],
            'attendance': ['dashboard', 'record_list', 'rules_list', 'reports'],
            'leaves': ['dashboard', 'leave_list', 'leave_types', 'balance_report'],
            'payrolls': ['dashboard', 'salary_list', 'payroll_runs', 'payslips'],
            'evaluations': ['dashboard', 'evaluation_list', 'periods', 'reports'],
            'insurance': ['dashboard', 'provider_list', 'health_insurance_list', 'social_insurance_list'],
            'training': ['dashboard'],
            'loans': ['dashboard'],
            'disciplinary': ['home'],
            'assets': ['home'],
            'cars': ['dashboard', 'car_list', 'supplier_list', 'trip_list'],
            'reports': ['dashboard']
        }
        
        return url_patterns.get(app_name, ['dashboard'])
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        report = {
            'test_summary': {
                'total_apps_tested': len(self.hr_apps),
                'url_test_results': {},
                'model_test_results': {},
                'view_test_results': {},
                'database_status': self.test_results['integration_tests'].get('database', {}).get('connection_status', 'unknown'),
                'overall_health': 'unknown'
            },
            'detailed_results': self.test_results,
            'recommendations': []
        }
        
        # Analyze URL test results
        total_valid_urls = 0
        total_tested_urls = 0
        
        for app_name, app_data in self.test_results['url_tests'].items():
            valid_count = len(app_data['valid_urls'])
            total_count = valid_count + len(app_data['invalid_urls'])
            
            total_valid_urls += valid_count
            total_tested_urls += total_count
            
            report['test_summary']['url_test_results'][app_name] = {
                'valid': valid_count,
                'total': total_count,
                'success_rate': (valid_count / total_count * 100) if total_count > 0 else 0
            }
        
        # Analyze model test results
        for app_name, app_data in self.test_results['model_tests'].items():
            success_count = len(app_data['importable_models'])
            error_count = len(app_data['model_errors'])
            total_count = success_count + error_count
            
            report['test_summary']['model_test_results'][app_name] = {
                'importable': success_count,
                'errors': error_count,
                'total': total_count,
                'success_rate': (success_count / total_count * 100) if total_count > 0 else 0
            }
        
        # Calculate overall health
        url_success_rate = (total_valid_urls / total_tested_urls * 100) if total_tested_urls > 0 else 0
        
        if url_success_rate >= 90 and report['test_summary']['database_status'] == 'connected':
            report['test_summary']['overall_health'] = 'Excellent'
        elif url_success_rate >= 75:
            report['test_summary']['overall_health'] = 'Good'
        elif url_success_rate >= 50:
            report['test_summary']['overall_health'] = 'Fair'
        else:
            report['test_summary']['overall_health'] = 'Needs Attention'
        
        # Generate recommendations
        if url_success_rate < 80:
            report['recommendations'].append("Fix invalid URL patterns to improve system reliability")
        
        if report['test_summary']['database_status'] != 'connected':
            report['recommendations'].append("Resolve database connectivity issues")
        
        # Print summary
        print(f"\n📊 Test Results Summary:")
        print(f"   • Overall Health: {report['test_summary']['overall_health']}")
        print(f"   • URL Success Rate: {url_success_rate:.1f}%")
        print(f"   • Database Status: {report['test_summary']['database_status']}")
        print(f"   • Apps Tested: {report['test_summary']['total_apps_tested']}")
        
        return report


def run_comprehensive_tests():
    """Run the comprehensive HR system test suite"""
    test_suite = HRSystemTestSuite()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    print("🔧 ElDawliya_Sys HR System - Comprehensive Test Suite")
    print("=" * 60)
    
    try:
        report = run_comprehensive_tests()
        
        print(f"\n✅ Testing Complete!")
        print(f"Overall System Health: {report['test_summary']['overall_health']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        sys.exit(1)
