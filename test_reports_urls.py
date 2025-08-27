#!/usr/bin/env python3
"""
Quick URL Test Script for Reports Namespace
==========================================
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_Sys.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

def test_reports_urls():
    """Test reports URLs specifically."""
    
    test_urls = [
        'reports:dashboard',
        'reports:categories',  
        'reports:analytics',
        # Other HR URLs that were added
        'leaves:dashboard',
        'insurance:dashboard',
        'evaluations:dashboard',
        'training:dashboard',
        'loans:dashboard',
    ]
    
    print("Testing URL patterns:")
    print("=" * 50)
    
    for url_name in test_urls:
        try:
            url_path = reverse(url_name)
            print(f"✅ {url_name:<25} -> {url_path}")
        except NoReverseMatch as e:
            print(f"❌ {url_name:<25} -> ERROR: {e}")
        except Exception as e:
            print(f"⚠️  {url_name:<25} -> UNEXPECTED: {e}")
    
    print("=" * 50)

if __name__ == '__main__':
    test_reports_urls()