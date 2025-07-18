قم بمراجعة وقراءة كل ملفات# Project Structure

## Root Directory Organization

### Core Django Files
- `manage.py`: Django management script
- `requirements.txt`: Python dependencies
- `.env` / `.env.example`: Environment configuration
- `README.md`: Project documentation (Arabic)

### Main Project Package
- `ElDawliya_sys/`: Main Django project configuration
  - `settings.py`: Core settings with multi-database support
  - `urls.py`: Root URL configuration
  - `wsgi.py` / `asgi.py`: WSGI/ASGI application
  - `db_router.py`: Custom database routing logic

## Application Structure

### Core Business Applications
- `Hr/`: Human Resources management
  - `models/`: Modular model organization
  - `views/`: View modules (employee, department, job, salary)
  - `forms/`: Form definitions
  - `templates/Hr/`: HR-specific templates
  - `static/Hr/`: HR-specific assets
  - `migrations/`: Database migrations
  - `utils/`: Utility functions

- `inventory/`: Inventory and stock management
  - `models.py`: Database models for products, invoices, suppliers
  - `views/`: Modular views organization
  - `templates/inventory/`: Inventory templates
  - `voucher_handlers.py`: Business logic for vouchers
  - `services.py`: Business services layer

- `api/`: REST API application
  - `views.py`: API endpoints
  - `serializers.py`: Data serialization
  - `authentication.py`: Custom authentication classes
  - `permissions.py`: API permissions
  - `services.py`: AI integration services

### Supporting Applications
- `accounts/`: User authentication and management
- `administrator/`: System administration and settings
- `meetings/`: Meeting management
- `tasks/`: Task management system
- `employee_tasks/`: Personal task management
- `Purchase_orders/`: Purchase order workflow
- `notifications/`: Notification system
- `audit/`: Audit trail and logging
- `attendance/`: Attendance tracking
- `cars/`: Vehicle management

### Shared Resources
- `core/`: Core utilities and shared functionality
- `templates/`: Global templates
  - `base.html`: Base template with RTL support
  - `components/`: Reusable template components
- `static/`: Global static files
  - `css/`: Stylesheets
  - `js/`: JavaScript files
- `media/`: User-uploaded files
- `staticfiles/`: Collected static files for production

## File Naming Conventions

### Python Files
- `models.py`: Database models
- `views.py`: View functions/classes
- `urls.py`: URL patterns
- `forms.py`: Form definitions
- `admin.py`: Django admin configuration
- `apps.py`: Application configuration
- `tests.py`: Test cases
- `signals.py`: Django signals
- `utils.py`: Utility functions
- `services.py`: Business logic services

### Template Organization
- `templates/app_name/`: App-specific templates
- `templates/components/`: Reusable components
- Base template naming: `base.html`, `base_updated.html`
- Feature templates: `feature_list.html`, `feature_detail.html`, `feature_form.html`

### Static Files
- `static/app_name/css/`: App-specific stylesheets
- `static/app_name/js/`: App-specific JavaScript
- `static/css/`: Global stylesheets
- `static/js/`: Global JavaScript

## Configuration Files

### Setup Scripts
- `setup_api.py`: API configuration setup
- `db_setup_*.py`: Database setup scripts
- `quick_start.py`: Quick start configuration
- `*.bat`: Windows batch scripts for common tasks

### Documentation
- `docs/`: Project documentation
- `*.md`: Markdown documentation files
- `README_*.md`: Specific setup guides

## Key Architectural Patterns

### Model Organization
- Use UUID primary keys for main entities
- Arabic field names with English alternatives
- Comprehensive meta classes with verbose names
- Foreign key relationships with proper related_names

### View Structure
- Modular view organization in subdirectories
- Separate views for different functionalities
- Class-based views for CRUD operations
- Function-based views for specific business logic

### URL Patterns
- Namespaced URLs per application
- RESTful URL structure where applicable
- Arabic-friendly URL patterns
- API versioning (`/api/v1/`)

### Template Hierarchy
- Base templates with RTL support
- Component-based template structure
- Consistent naming conventions
- Bootstrap 5 integration with Arabic fonts

### Database Design
- Multi-database support with routing
- Fallback mechanisms for database connectivity
- SQL Server optimized with proper collations
- Migration management with conflict resolution