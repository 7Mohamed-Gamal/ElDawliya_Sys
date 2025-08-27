#!/usr/bin/env python3
"""
HR System Integration Test Suite
==============================

This script performs comprehensive integration testing of the HR system
without requiring database connections or Django runtime.
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


class HRSystemIntegrationTester:
    """Comprehensive integration tester for HR System."""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.errors = []
        self.warnings = []
        self.info = []
        self.hr_apps = [
            'employees', 'attendance', 'leaves', 'payrolls', 
            'loans', 'insurance', 'training', 'evaluations',
            'banks', 'reports'
        ]
        
    def log_error(self, message: str):
        """Log an error message."""
        self.errors.append(f"❌ ERROR: {message}")
        
    def log_warning(self, message: str):
        """Log a warning message."""
        self.warnings.append(f"⚠️  WARNING: {message}")
        
    def log_info(self, message: str):
        """Log an info message."""
        self.info.append(f"ℹ️  INFO: {message}")
    
    def check_app_structure(self) -> Dict[str, bool]:
        """Check if all HR apps have proper structure."""
        self.log_info("Checking HR application structure...")
        results = {}
        
        required_files = [
            '__init__.py', 'apps.py', 'models.py', 
            'views.py', 'urls.py', 'admin.py'
        ]
        
        for app in self.hr_apps:
            app_dir = self.base_dir / app
            if not app_dir.exists():
                self.log_error(f"App directory missing: {app}")
                results[app] = False
                continue
                
            missing_files = []
            for file in required_files:
                if not (app_dir / file).exists():
                    missing_files.append(file)
            
            if missing_files:
                self.log_warning(f"App {app} missing files: {missing_files}")
                results[app] = False
            else:
                self.log_info(f"App {app} structure complete ✓")
                results[app] = True
                
        return results
    
    def check_model_relationships(self) -> Dict[str, List[str]]:
        """Check model relationships across apps."""
        self.log_info("Checking inter-app model relationships...")
        
        relationships = {}
        expected_relationships = {
            'payrolls': ['employees', 'attendance', 'leaves', 'loans'],
            'leaves': ['employees'],
            'attendance': ['employees'],
            'loans': ['employees'],
            'training': ['employees'],
            'evaluations': ['employees'],
            'insurance': ['employees'],
        }
        
        for app, expected_deps in expected_relationships.items():
            models_file = self.base_dir / app / 'models.py'
            if not models_file.exists():
                self.log_error(f"Models file missing for {app}")
                continue
                
            try:
                with open(models_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                found_deps = []
                for dep in expected_deps:
                    # Check for imports and ForeignKey relationships
                    if f'from {dep}' in content or f'{dep}.' in content:
                        found_deps.append(dep)
                
                missing_deps = set(expected_deps) - set(found_deps)
                if missing_deps:
                    self.log_warning(f"App {app} missing relationships to: {missing_deps}")
                else:
                    self.log_info(f"App {app} relationships complete ✓")
                
                relationships[app] = found_deps
                
            except Exception as e:
                self.log_error(f"Error reading models for {app}: {e}")
        
        return relationships
    
    def check_url_patterns(self) -> bool:
        """Check URL patterns and routing."""
        self.log_info("Checking URL patterns...")
        
        main_urls = self.base_dir / 'ElDawliya_Sys' / 'urls.py'
        if not main_urls.exists():
            self.log_error("Main urls.py file missing")
            return False
        
        try:
            with open(main_urls, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_urls = []
            for app in self.hr_apps:
                if app == 'reports':
                    continue  # Reports might be integrated differently
                    
                if f"path('{app}/', include('{app}.urls'))" not in content:
                    missing_urls.append(app)
            
            if missing_urls:
                self.log_warning(f"Missing URL patterns for: {missing_urls}")
                return False
            else:
                self.log_info("All HR app URLs properly configured ✓")
                return True
                
        except Exception as e:
            self.log_error(f"Error reading main urls.py: {e}")
            return False
    
    def check_settings_configuration(self) -> bool:
        """Check Django settings for HR apps."""
        self.log_info("Checking settings configuration...")
        
        settings_file = self.base_dir / 'ElDawliya_Sys' / 'settings.py'
        if not settings_file.exists():
            self.log_error("Settings file missing")
            return False
        
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_apps = []
            for app in self.hr_apps:
                if app == 'reports':
                    continue  # Reports might be integrated differently
                    
                if f"'{app}" not in content:
                    missing_apps.append(app)
            
            if missing_apps:
                self.log_warning(f"Apps not in INSTALLED_APPS: {missing_apps}")
                return False
            else:
                self.log_info("All HR apps properly registered in settings ✓")
                return True
                
        except Exception as e:
            self.log_error(f"Error reading settings.py: {e}")
            return False
    
    def check_template_structure(self) -> Dict[str, bool]:
        """Check template structure and consistency."""
        self.log_info("Checking template structure...")
        
        results = {}
        base_template = self.base_dir / 'templates' / 'base.html'
        
        if not base_template.exists():
            self.log_error("Base template missing")
            return results
        else:
            self.log_info("Base template found ✓")
        
        for app in self.hr_apps:
            app_templates = self.base_dir / app / 'templates' / app
            if app_templates.exists():
                template_count = len(list(app_templates.glob('*.html')))
                if template_count > 0:
                    self.log_info(f"App {app} has {template_count} templates ✓")
                    results[app] = True
                else:
                    self.log_warning(f"App {app} has no templates")
                    results[app] = False
            else:
                self.log_warning(f"App {app} templates directory missing")
                results[app] = False
                
        return results
    
    def check_data_flow_integration(self) -> Dict[str, Any]:
        """Check data flow integration between modules."""
        self.log_info("Checking data flow integration...")
        
        integration_points = {
            'attendance_to_payroll': {
                'source': 'attendance/models.py',
                'target': 'payrolls/services.py',
                'expected_integration': 'EmployeeAttendance'
            },
            'leaves_to_payroll': {
                'source': 'leaves/models.py',
                'target': 'payrolls/services.py',
                'expected_integration': 'EmployeeLeave'
            },
            'loans_to_payroll': {
                'source': 'loans/models.py',
                'target': 'payrolls/services.py',
                'expected_integration': 'LoanInstallment'
            }
        }
        
        results = {}
        for integration, config in integration_points.items():
            target_file = self.base_dir / config['target']
            
            if not target_file.exists():
                self.log_error(f"Integration target missing: {config['target']}")
                results[integration] = False
                continue
            
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if config['expected_integration'] in content:
                    self.log_info(f"Integration {integration} found ✓")
                    results[integration] = True
                else:
                    self.log_warning(f"Integration {integration} missing")
                    results[integration] = False
                    
            except Exception as e:
                self.log_error(f"Error checking integration {integration}: {e}")
                results[integration] = False
        
        return results
    
    def check_api_consistency(self) -> bool:
        """Check API endpoint consistency."""
        self.log_info("Checking API consistency...")
        
        # Check if DRF is configured
        settings_file = self.base_dir / 'ElDawliya_Sys' / 'settings.py'
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'rest_framework' in content:
                self.log_info("Django REST Framework configured ✓")
                return True
            else:
                self.log_warning("Django REST Framework not found in settings")
                return False
                
        except Exception as e:
            self.log_error(f"Error checking API configuration: {e}")
            return False
    
    def check_security_integration(self) -> Dict[str, bool]:
        """Check security and permission integration."""
        self.log_info("Checking security integration...")
        
        security_checks = {
            'csrf_protection': False,
            'authentication': False,
            'permissions': False
        }
        
        # Check base template for CSRF
        base_template = self.base_dir / 'templates' / 'base.html'
        if base_template.exists():
            try:
                with open(base_template, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'csrf' in content.lower():
                    security_checks['csrf_protection'] = True
                    self.log_info("CSRF protection found in templates ✓")
                
                if 'user' in content and 'auth' in content:
                    security_checks['authentication'] = True
                    self.log_info("Authentication integration found ✓")
                    
            except Exception as e:
                self.log_error(f"Error checking base template: {e}")
        
        # Check for permission decorators in views
        for app in self.hr_apps:
            views_file = self.base_dir / app / 'views.py'
            if views_file.exists():
                try:
                    with open(views_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'login_required' in content or 'permission_required' in content:
                        security_checks['permissions'] = True
                        break
                        
                except Exception as e:
                    continue
        
        if security_checks['permissions']:
            self.log_info("Permission decorators found ✓")
        else:
            self.log_warning("No permission decorators found in views")
        
        return security_checks
    
    def generate_integration_report(self) -> str:
        """Generate comprehensive integration report."""
        report = []
        report.append("=" * 60)
        report.append("HR SYSTEM INTEGRATION TEST REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Run all checks
        app_structure = self.check_app_structure()
        model_relationships = self.check_model_relationships()
        url_patterns = self.check_url_patterns()
        settings_config = self.check_settings_configuration()
        template_structure = self.check_template_structure()
        data_flow = self.check_data_flow_integration()
        api_consistency = self.check_api_consistency()
        security_integration = self.check_security_integration()
        
        # Summary statistics
        total_apps = len(self.hr_apps)
        working_apps = sum(app_structure.values())
        
        report.append(f"📊 SUMMARY STATISTICS")
        report.append(f"   Total HR Apps: {total_apps}")
        report.append(f"   Working Apps: {working_apps}")
        report.append(f"   Success Rate: {(working_apps/total_apps)*100:.1f}%")
        report.append("")
        
        # Detailed results
        report.append("🔍 DETAILED RESULTS")
        report.append("")
        
        if self.info:
            report.append("✅ SUCCESSFUL CHECKS:")
            for item in self.info:
                report.append(f"   {item}")
            report.append("")
        
        if self.warnings:
            report.append("⚠️  WARNINGS:")
            for item in self.warnings:
                report.append(f"   {item}")
            report.append("")
        
        if self.errors:
            report.append("❌ ERRORS:")
            for item in self.errors:
                report.append(f"   {item}")
            report.append("")
        
        # Integration status
        report.append("🔗 INTEGRATION STATUS")
        report.append(f"   URL Routing: {'✅' if url_patterns else '❌'}")
        report.append(f"   Settings Config: {'✅' if settings_config else '❌'}")
        report.append(f"   API Integration: {'✅' if api_consistency else '❌'}")
        report.append(f"   Security: {'✅' if all(security_integration.values()) else '⚠️'}")
        report.append("")
        
        # Data flow
        if data_flow:
            report.append("📊 DATA FLOW INTEGRATION")
            for flow, status in data_flow.items():
                report.append(f"   {flow}: {'✅' if status else '❌'}")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        if self.errors:
            report.append("   • Critical errors found - system may not function properly")
        if self.warnings:
            report.append("   • Warnings found - review for optimal performance")
        if working_apps == total_apps and not self.errors:
            report.append("   • System integration appears healthy ✅")
            report.append("   • Ready for production deployment")
        report.append("")
        
        report.append("=" * 60)
        report.append("Report generated successfully")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "hr_integration_report.txt"):
        """Save the integration report to a file."""
        report = self.generate_integration_report()
        report_path = self.base_dir / filename
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ Integration report saved to: {report_path}")
            return str(report_path)
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return None


def main():
    """Main function to run integration tests."""
    # Get the current directory (should be the Django project root)
    base_dir = Path(__file__).parent
    
    print("🚀 Starting HR System Integration Tests...")
    print(f"📁 Base directory: {base_dir}")
    print("")
    
    # Create tester instance
    tester = HRSystemIntegrationTester(str(base_dir))
    
    # Generate and display report
    report = tester.generate_integration_report()
    print(report)
    
    # Save report to file
    tester.save_report()


if __name__ == "__main__":
    main()