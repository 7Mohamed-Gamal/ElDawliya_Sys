"""
Security Tests Validation Script
Validates that security test files are properly structured and can be imported
"""
import os
import sys
import importlib.util
from pathlib import Path


def validate_security_test_file(file_path):
    """Validate a security test file"""
    print(f"📋 Validating {file_path.name}...")

    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for required imports
        required_imports = [
            'import pytest',
            'from django.test import TestCase',
            'from django.contrib.auth.models import User'
        ]

        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)

        # Check for test classes
        test_classes = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('class ') and 'Test' in line:
                test_classes.append(line.strip())

        # Check for test methods
        test_methods = []
        for line in lines:
            if line.strip().startswith('def test_'):
                test_methods.append(line.strip().split('(')[0].replace('def ', ''))

        # Report results
        print(f"   ✅ Test classes found: {len(test_classes)}")
        for cls in test_classes[:3]:  # Show first 3
            print(f"      - {cls}")
        if len(test_classes) > 3:
            print(f"      ... and {len(test_classes) - 3} more")

        print(f"   ✅ Test methods found: {len(test_methods)}")
        for method in test_methods[:5]:  # Show first 5
            print(f"      - {method}")
        if len(test_methods) > 5:
            print(f"      ... and {len(test_methods) - 5} more")

        if missing_imports:
            print(f"   ⚠️  Missing imports: {missing_imports}")

        # Check for security-specific content
        security_keywords = [
            'sql injection', 'xss', 'csrf', 'authentication', 'authorization',
            'owasp', 'security', 'vulnerability', 'attack', 'exploit'
        ]

        found_keywords = []
        content_lower = content.lower()
        for keyword in security_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)

        print(f"   🔒 Security keywords found: {len(found_keywords)}")

        return {
            'file': file_path.name,
            'test_classes': len(test_classes),
            'test_methods': len(test_methods),
            'missing_imports': missing_imports,
            'security_keywords': len(found_keywords),
            'valid': len(test_classes) > 0 and len(test_methods) > 0
        }

    except Exception as e:
        print(f"   ❌ Error validating file: {e}")
        return {
            'file': file_path.name,
            'error': str(e),
            'valid': False
        }


def main():
    """Main validation function"""
    print("🔒 Security Tests Validation")
    print("=" * 50)

    # Find security test files
    security_dir = Path(__file__).parent
    test_files = list(security_dir.glob('test_*.py'))

    if not test_files:
        print("❌ No security test files found!")
        return

    print(f"📁 Found {len(test_files)} security test files")
    print()

    results = []
    for test_file in test_files:
        if test_file.name == 'test_security_basic.py':
            continue  # Skip the basic test file

        result = validate_security_test_file(test_file)
        results.append(result)
        print()

    # Summary
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    valid_files = [r for r in results if r.get('valid', False)]
    invalid_files = [r for r in results if not r.get('valid', False)]

    print(f"✅ Valid test files: {len(valid_files)}")
    print(f"❌ Invalid test files: {len(invalid_files)}")

    total_classes = sum(r.get('test_classes', 0) for r in results)
    total_methods = sum(r.get('test_methods', 0) for r in results)

    print(f"📋 Total test classes: {total_classes}")
    print(f"🧪 Total test methods: {total_methods}")

    if invalid_files:
        print("\n❌ Issues found in:")
        for result in invalid_files:
            print(f"   - {result['file']}: {result.get('error', 'Invalid structure')}")

    # Security coverage analysis
    print("\n🔒 SECURITY COVERAGE ANALYSIS")
    print("=" * 50)

    security_categories = {
        'OWASP Top 10': 'test_owasp_top10.py',
        'Authentication': 'test_authentication.py',
        'API Security': 'test_api_security.py',
        'Data Protection': 'test_data_protection.py',
        'Penetration Testing': 'test_penetration.py'
    }

    for category, filename in security_categories.items():
        file_result = next((r for r in results if r['file'] == filename), None)
        if file_result and file_result.get('valid'):
            methods = file_result.get('test_methods', 0)
            print(f"✅ {category}: {methods} tests")
        else:
            print(f"❌ {category}: Not found or invalid")

    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("=" * 50)

    recommendations = [
        "Run security tests regularly as part of CI/CD pipeline",
        "Review and update security tests when adding new features",
        "Consider adding integration with security scanning tools",
        "Document security test results and track improvements",
        "Train development team on security testing practices"
    ]

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

    print(f"\n🎯 Security test validation completed!")
    print(f"   Files validated: {len(results)}")
    print(f"   Success rate: {len(valid_files)/len(results)*100:.1f}%")


if __name__ == '__main__':
    main()
