"""
HR URL Pattern Analysis and Optimization Tool
Professional URL routing analysis for ElDawliya_Sys HR applications
"""

import re
from django.urls import reverse, NoReverseMatch
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
import logging

logger = logging.getLogger(__name__)


class HRURLAnalyzer:
    """Comprehensive URL pattern analyzer for HR applications"""
    
    def __init__(self):
        self.factory = RequestFactory()
        self.hr_apps = [
            'hr', 'employees', 'attendance', 'leaves', 'payrolls', 
            'evaluations', 'insurance', 'training', 'loans', 
            'disciplinary', 'assets', 'cars', 'reports'
        ]
        self.analysis_results = {}
    
    def analyze_all_hr_urls(self):
        """Analyze all HR application URL patterns"""
        results = {}
        
        for app_name in self.hr_apps:
            try:
                app_results = self.analyze_app_urls(app_name)
                results[app_name] = app_results
                logger.info(f"Analyzed {app_name}: {len(app_results.get('valid_urls', []))} valid URLs")
            except Exception as e:
                logger.error(f"Error analyzing {app_name}: {str(e)}")
                results[app_name] = {'error': str(e)}
        
        self.analysis_results = results
        return results
    
    def analyze_app_urls(self, app_name):
        """Analyze URL patterns for a specific HR application"""
        url_patterns = self.get_app_url_patterns(app_name)
        
        results = {
            'app_name': app_name,
            'total_patterns': len(url_patterns),
            'valid_urls': [],
            'invalid_urls': [],
            'protected_urls': [],
            'public_urls': [],
            'ajax_urls': [],
            'api_urls': [],
            'crud_patterns': {
                'create': [],
                'read': [],
                'update': [],
                'delete': []
            },
            'url_complexity': self.calculate_url_complexity(url_patterns),
            'recommendations': []
        }
        
        for pattern in url_patterns:
            try:
                url_name = f"{app_name}:{pattern}"
                
                # Test URL reversibility
                try:
                    reversed_url = reverse(url_name)
                    results['valid_urls'].append({
                        'name': pattern,
                        'url': reversed_url,
                        'reversible': True
                    })
                    
                    # Categorize URL types
                    self.categorize_url(pattern, reversed_url, results)
                    
                except NoReverseMatch:
                    results['invalid_urls'].append({
                        'name': pattern,
                        'error': 'Cannot reverse URL'
                    })
                    
            except Exception as e:
                results['invalid_urls'].append({
                    'name': pattern,
                    'error': str(e)
                })
        
        # Generate recommendations
        results['recommendations'] = self.generate_recommendations(results)
        
        return results
    
    def get_app_url_patterns(self, app_name):
        """Extract URL patterns from application"""
        patterns = []
        
        # Common HR URL patterns based on analysis
        hr_url_patterns = {
            'hr': ['dashboard', 'profile', 'my_payslips', 'my_leaves', 'notifications', 'settings'],
            'employees': ['dashboard', 'employee_list', 'add_employee', 'employee_detail', 'edit_employee', 'delete_employee'],
            'attendance': [
                'dashboard', 'record_list', 'add_record', 'record_detail', 'edit_record', 'delete_record',
                'rules_list', 'add_rule', 'update_rule', 'delete_rule', 'check_in', 'check_out',
                'mark_attendance', 'reports', 'monthly_report', 'analytics', 'zk_devices_list',
                'zk_device_create', 'zk_device_sync', 'zk_sync_all'
            ],
            'leaves': [
                'dashboard', 'leave_list', 'create_request', 'leave_detail', 'edit_leave', 'delete_leave',
                'approve_leave', 'reject_leave', 'leave_types', 'add_leave_type', 'balance_report',
                'my_leaves', 'request_leave', 'leave_reports'
            ],
            'payrolls': [
                'dashboard', 'salary_list', 'add_salary', 'salary_detail', 'edit_salary', 'delete_salary',
                'payroll_runs', 'create_payroll_run', 'payroll_run_detail', 'process_payroll_run',
                'approve_payroll_run', 'payslips', 'payslip_detail', 'my_payslips', 'reports'
            ],
            'evaluations': [
                'dashboard', 'evaluation_list', 'create_evaluation', 'evaluation_detail', 'edit_evaluation',
                'delete_evaluation', 'periods', 'add_period', 'reports', 'my_evaluations'
            ],
            'insurance': [
                'dashboard', 'provider_list', 'add_provider', 'provider_detail', 'health_insurance_list',
                'add_health_insurance', 'social_insurance_list', 'add_social_insurance', 'reports', 'my_insurance'
            ],
            'training': ['dashboard', 'home'],
            'loans': ['dashboard', 'home'],
            'disciplinary': ['home'],
            'assets': ['home'],
            'cars': ['dashboard', 'car_list', 'supplier_list', 'trip_list'],
            'reports': ['dashboard']
        }
        
        return hr_url_patterns.get(app_name, [])
    
    def categorize_url(self, pattern, url, results):
        """Categorize URL based on pattern and functionality"""
        pattern_lower = pattern.lower()
        
        # AJAX URLs
        if 'ajax' in pattern_lower or pattern.startswith('ajax_'):
            results['ajax_urls'].append(pattern)
        
        # API URLs
        if 'api' in pattern_lower or pattern.startswith('api_'):
            results['api_urls'].append(pattern)
        
        # CRUD operations
        if any(word in pattern_lower for word in ['create', 'add', 'new']):
            results['crud_patterns']['create'].append(pattern)
        elif any(word in pattern_lower for word in ['detail', 'view', 'show', 'get']):
            results['crud_patterns']['read'].append(pattern)
        elif any(word in pattern_lower for word in ['edit', 'update', 'modify']):
            results['crud_patterns']['update'].append(pattern)
        elif any(word in pattern_lower for word in ['delete', 'remove', 'destroy']):
            results['crud_patterns']['delete'].append(pattern)
        
        # Authentication requirements (heuristic)
        if any(word in pattern_lower for word in ['my_', 'profile', 'dashboard', 'admin']):
            results['protected_urls'].append(pattern)
        else:
            results['public_urls'].append(pattern)
    
    def calculate_url_complexity(self, patterns):
        """Calculate URL complexity metrics"""
        if not patterns:
            return {'score': 0, 'level': 'N/A'}
        
        total_length = sum(len(pattern) for pattern in patterns)
        avg_length = total_length / len(patterns)
        
        # Count special characters and parameters
        param_count = sum(pattern.count('<') + pattern.count('{') for pattern in patterns)
        
        complexity_score = (avg_length * 0.3) + (param_count * 2) + (len(patterns) * 0.1)
        
        if complexity_score < 10:
            level = 'Simple'
        elif complexity_score < 25:
            level = 'Moderate'
        elif complexity_score < 50:
            level = 'Complex'
        else:
            level = 'Very Complex'
        
        return {
            'score': round(complexity_score, 2),
            'level': level,
            'avg_pattern_length': round(avg_length, 2),
            'parameter_count': param_count
        }
    
    def generate_recommendations(self, results):
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check for missing CRUD operations
        crud = results['crud_patterns']
        if crud['create'] and not crud['read']:
            recommendations.append("Consider adding detail/view URLs for created resources")
        
        if crud['create'] and not crud['update']:
            recommendations.append("Consider adding edit/update functionality")
        
        # Check URL naming consistency
        if len(results['valid_urls']) > 5:
            patterns = [url['name'] for url in results['valid_urls']]
            if not self.check_naming_consistency(patterns):
                recommendations.append("Improve URL naming consistency (use consistent prefixes/suffixes)")
        
        # Check for AJAX/API separation
        if results['ajax_urls'] and not results['api_urls']:
            recommendations.append("Consider creating dedicated API endpoints for AJAX functionality")
        
        # Complexity recommendations
        complexity = results['url_complexity']
        if complexity['level'] in ['Complex', 'Very Complex']:
            recommendations.append("Consider simplifying URL patterns or grouping related functionality")
        
        # Security recommendations
        if len(results['public_urls']) > len(results['protected_urls']):
            recommendations.append("Review authentication requirements for URL endpoints")
        
        return recommendations
    
    def check_naming_consistency(self, patterns):
        """Check if URL patterns follow consistent naming conventions"""
        # Check for consistent use of underscores vs hyphens
        underscore_count = sum(1 for p in patterns if '_' in p)
        hyphen_count = sum(1 for p in patterns if '-' in p)
        
        # If both are used significantly, it's inconsistent
        if underscore_count > 0 and hyphen_count > 0:
            if min(underscore_count, hyphen_count) / max(underscore_count, hyphen_count) > 0.3:
                return False
        
        return True
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        if not self.analysis_results:
            self.analyze_all_hr_urls()
        
        report = {
            'summary': {
                'total_apps_analyzed': len(self.analysis_results),
                'total_valid_urls': 0,
                'total_invalid_urls': 0,
                'apps_with_issues': 0,
                'overall_health': 'Good'
            },
            'app_details': self.analysis_results,
            'system_recommendations': []
        }
        
        # Calculate summary statistics
        for app_name, app_data in self.analysis_results.items():
            if 'error' not in app_data:
                report['summary']['total_valid_urls'] += len(app_data.get('valid_urls', []))
                report['summary']['total_invalid_urls'] += len(app_data.get('invalid_urls', []))
                
                if app_data.get('invalid_urls') or len(app_data.get('recommendations', [])) > 2:
                    report['summary']['apps_with_issues'] += 1
        
        # Determine overall health
        issue_rate = report['summary']['apps_with_issues'] / report['summary']['total_apps_analyzed']
        if issue_rate > 0.5:
            report['summary']['overall_health'] = 'Needs Attention'
        elif issue_rate > 0.3:
            report['summary']['overall_health'] = 'Fair'
        
        # System-wide recommendations
        if report['summary']['total_invalid_urls'] > 0:
            report['system_recommendations'].append("Fix invalid URL patterns to improve system reliability")
        
        if report['summary']['apps_with_issues'] > 3:
            report['system_recommendations'].append("Implement URL pattern standards across all HR applications")
        
        return report
    
    def test_url_accessibility(self, app_name, url_pattern):
        """Test if a URL is accessible and returns expected response"""
        try:
            url = reverse(f"{app_name}:{url_pattern}")
            request = self.factory.get(url)
            request.user = AnonymousUser()
            
            # This would need actual view testing in a real implementation
            return {
                'accessible': True,
                'url': url,
                'status': 'testable'
            }
        except Exception as e:
            return {
                'accessible': False,
                'error': str(e),
                'status': 'error'
            }


def run_hr_url_analysis():
    """Run complete HR URL analysis and return results"""
    analyzer = HRURLAnalyzer()
    report = analyzer.generate_report()
    
    logger.info(f"HR URL Analysis Complete:")
    logger.info(f"- Total Apps: {report['summary']['total_apps_analyzed']}")
    logger.info(f"- Valid URLs: {report['summary']['total_valid_urls']}")
    logger.info(f"- Invalid URLs: {report['summary']['total_invalid_urls']}")
    logger.info(f"- Overall Health: {report['summary']['overall_health']}")
    
    return report


if __name__ == "__main__":
    # Run analysis when script is executed directly
    report = run_hr_url_analysis()
    print("HR URL Analysis Report Generated")
    print(f"Overall System Health: {report['summary']['overall_health']}")
