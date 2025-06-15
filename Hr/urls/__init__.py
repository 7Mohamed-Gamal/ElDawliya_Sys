# =============================================================================
# ElDawliya HR Management System - DISABLED URLs Configuration
# =============================================================================
# This file has been disabled to prevent namespace conflicts
# The main URL configuration is in Hr/urls.py
# =============================================================================

# DISABLED: This file was causing namespace conflicts with the main Hr/urls.py
# The main project uses Hr/urls.py, not this file.
# This directory structure was creating duplicate namespaces.

# If you need to use this modular URL structure in the future:
# 1. Rename this directory to something like 'urls_modular'
# 2. Update the main project to use this structure instead of Hr/urls.py
# 3. Ensure no duplicate namespace names

# For now, this file is disabled to fix the namespace conflicts.

"""
DISABLED URL CONFIGURATION

This file was causing Django URL namespace conflicts because:
1. The main project includes 'Hr.urls' which points to Hr/urls.py
2. This __init__.py file was also being loaded, creating duplicate namespaces
3. Multiple URL files in this directory had conflicting namespace names

To re-enable this modular structure:
1. Move or rename the main Hr/urls.py file
2. Update ElDawliya_sys/urls.py to point to this directory
3. Resolve any remaining namespace conflicts
"""

# Disabled to prevent conflicts
# app_name = 'hr'

# DISABLED: URL patterns commented out to prevent namespace conflicts
# urlpatterns = [
#     # All URL patterns have been disabled to prevent conflicts
#     # The main URL configuration is in Hr/urls.py
# ]

# Empty URL patterns to prevent import errors
urlpatterns = []

# =============================================================================
# DISABLED SECTIONS
# =============================================================================

# All sections below have been disabled to prevent namespace conflicts

# DISABLED: Development settings
# DISABLED: Error handlers

# This file has been completely disabled to resolve URL namespace conflicts
# Use Hr/urls.py for the main URL configuration
