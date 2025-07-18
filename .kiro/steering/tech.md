# Technology Stack

## Framework & Core
- **Django 4.2.22**: Main web framework
- **Python 3.7+**: Programming language
- **Django REST Framework 3.15.2**: API development
- **SQL Server**: Primary database with MSSQL Django backend

## Database & ORM
- **mssql-django 1.4.1**: SQL Server adapter
- **pyodbc 4.0.39**: Database connectivity
- **Database Router**: Custom routing for multi-database setup
- **Fallback mechanism**: Automatic switching between database hosts

## Authentication & Security
- **JWT (Simple JWT 5.3.0)**: Token-based authentication
- **Custom API Key system**: API authentication
- **Django Allauth 0.54.0**: User authentication
- **CORS Headers 4.1.0**: Cross-origin resource sharing

## UI & Frontend
- **Bootstrap 5**: CSS framework
- **jQuery**: JavaScript library
- **FullCalendar.js**: Calendar components
- **Chart.js**: Data visualization
- **Crispy Forms**: Form rendering
- **Cairo Font**: Arabic typography

## AI & External Services
- **Google Generative AI 0.8.3**: Gemini AI integration
- **python-dotenv 1.0.1**: Environment variable management

## Documentation & API
- **drf-yasg 1.21.7**: Swagger/OpenAPI documentation
- **Swagger UI & ReDoc**: Interactive API documentation

## Development & Testing
- **pytest 7.3.1**: Testing framework
- **pytest-django 4.5.2**: Django testing integration
- **coverage 7.2.7**: Code coverage
- **black 24.3.0**: Code formatting
- **flake8 6.0.0**: Code linting

## Production & Deployment
- **gunicorn 23.0.0**: WSGI server
- **whitenoise 6.4.0**: Static file serving
- **sentry-sdk 2.8.0**: Error monitoring

## Common Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run with API server
python run_api_server.py
```

### API Management
```bash
# Create API key
python manage.py create_api_key username --name "Key Name" --expires-days 30

# Setup API groups
python manage.py setup_api_groups

# Test API functionality
python api_examples.py
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test api
python manage.py test Hr

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Database Management
```bash
# Check migrations
python check_migrations.py

# Database setup scripts
python db_setup_final.py
python simple_db_setup.py
```

### Quick Start Scripts
```bash
# Windows batch files
start_complete_system.bat
start_with_api.bat
test_system_functionality.py
```