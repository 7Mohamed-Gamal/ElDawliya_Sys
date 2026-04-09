"""
Custom WSGI handler to catch database errors during application startup.

This module provides a wrapper around the Django WSGI application that catches
database connection errors during the application startup and shows a database
setup page directly, without requiring a working database connection.
"""

import os
import sys
import re
import traceback
import pyodbc
from urllib.parse import parse_qs, quote

# HTML template for database setup page
DB_SETUP_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إعداد قاعدة البيانات - نظام الدولية</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            direction: rtl;
            text-align: right;
            font-family: 'Cairo', sans-serif;
            background-color: #f8f9fa;
        }
        .container {
            max-width: 900px;
            margin: 50px auto;
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .card-header {
            background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);
            padding: 1.5rem;
            border-bottom: none;
            color: white;
        }
        .error-banner {
            background-color: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .success-banner {
            background-color: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .form-control {
            border-radius: 10px;
            padding: 0.75rem 1rem;
            border: 2px solid #e3e6f0;
        }
        .btn-primary {
            background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
        }
        .loader {
            display: inline-block;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h4 class="mb-0">
                    <i class="fas fa-database me-2"></i>
                    إعداد قاعدة بيانات النظام
                </h4>
            </div>
            <div class="card-body p-4">
                <div class="text-center mb-4">
                    <h2>نظام الشركة الدولية</h2>
                </div>

                {error_message}
                {success_message}

                <div class="alert alert-info mb-4">
                    <h5><i class="fas fa-info-circle me-2"></i>تعليمات</h5>
                    <p>يرجى إعداد الاتصال بقاعدة البيانات لمتابعة استخدام النظام.</p>
                    <ul>
                        <li>تأكد من تثبيت SQL Server وتشغيله</li>
                        <li>تأكد من صحة اسم الخادم (مثال: <code>DESKTOP-PC\\SQLEXPRESS</code> أو <code>localhost</code>)</li>
                        <li>يمكنك إنشاء قاعدة بيانات جديدة إذا لم تكن موجودة</li>
                    </ul>
                </div>

                <form method="post" action="/db-setup-handler" id="dbForm">
                    <div class="mb-3">
                        <label for="host" class="form-label">اسم الخادم (Server Name)</label>
                        <input type="text" class="form-control" id="host" name="host"
                               placeholder="مثال: SERVERNAME\\SQLEXPRESS أو localhost" value="{host}" required>
                        <div class="form-text">أدخل اسم الخادم أو عنوان IP الخاص بخادم SQL Server</div>
                    </div>

                    <div class="mb-3">
                        <label for="database" class="form-label">اسم قاعدة البيانات</label>
                        <input type="text" class="form-control" id="database" name="database"
                               placeholder="اسم قاعدة البيانات" value="{database}" required>
                    </div>

                    <div class="mb-3 form-check">
                        <input type="checkbox" class="form-check-input" id="use_windows_auth" name="use_windows_auth" value="1" {windows_auth_checked}>
                        <label class="form-check-label" for="use_windows_auth">استخدام مصادقة Windows</label>
                    </div>

                    <div id="sql_auth_fields" {sql_auth_style}>
                        <div class="mb-3">
                            <label for="username" class="form-label">اسم المستخدم</label>
                            <input type="text" class="form-control" id="username" name="username" placeholder="اسم المستخدم" value="{username}">
                        </div>

                        <div class="mb-3">
                            <label for="password" class="form-label">كلمة المرور</label>
                            <input type="password" class="form-control" id="password" name="password" placeholder="كلمة المرور" value="{password}">
                        </div>
                    </div>

                    <div class="mb-3">
                        <label for="port" class="form-label">المنفذ (Port)</label>
                        <input type="text" class="form-control" id="port" name="port" value="{port}">
                    </div>

                    <div class="mb-3 form-check">
                        <input type="checkbox" class="form-check-input" id="create_db" name="create_db" value="1">
                        <label class="form-check-label" for="create_db">إنشاء قاعدة البيانات إذا لم تكن موجودة</label>
                    </div>

                    <div class="row mt-4">
                        <div class="col-md-6 mb-3">
                            <button type="button" class="btn btn-secondary w-100" id="testBtn">
                                <i class="fas fa-plug me-2"></i>اختبار الاتصال
                            </button>
                        </div>
                        <div class="col-md-6 mb-3">
                            <button type="submit" class="btn btn-primary w-100" id="saveBtn">
                                <i class="fas fa-save me-2"></i>حفظ الإعدادات
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const useWindowsAuth = document.getElementById('use_windows_auth');
            const sqlAuthFields = document.getElementById('sql_auth_fields');
            const testBtn = document.getElementById('testBtn');
            const saveBtn = document.getElementById('saveBtn');
            const dbForm = document.getElementById('dbForm');

            // Toggle Windows authentication fields
            useWindowsAuth.addEventListener('change', function() {
                if (this.checked) {
                    sqlAuthFields.style.display = 'none';
                } else {
                    sqlAuthFields.style.display = 'block';
                }
            });

            // Test connection button
            testBtn.addEventListener('click', function() {
                // Show loading state
                testBtn.disabled = true;
                testBtn.innerHTML = '<span class="loader"></span> جاري الاختبار...';

                // Get form data
                const formData = new FormData(dbForm);
                formData.append('test_only', '1');

                // Send form data to the same URL with test_only parameter
                fetch('/db-setup-handler', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.text())
                .then(html => {
                    // Replace the entire page with the response
                    document.open();
                    document.write(html);
                    document.close();
                })
                .catch(error => {
                    // Reset button state
                    testBtn.disabled = false;
                    testBtn.innerHTML = '<i class="fas fa-plug me-2"></i>اختبار الاتصال';

                    // Show error message
                    alert('حدث خطأ أثناء اختبار الاتصال: ' + error.message);
                });
            });

            // Form submission
            dbForm.addEventListener('submit', function() {
                // Show loading state
                saveBtn.disabled = true;
                saveBtn.innerHTML = '<span class="loader"></span> جاري الحفظ...';
            });
        });
    </script>
</body>
</html>
"""

def db_setup_application(environ, start_response, error_message=None, success_message=None, form_data=None):
    """
    Simple WSGI application that serves the database setup page.
    """
    path = environ.get('PATH_INFO', '')

    # Default form values
    form_values = {
        'host': 'localhost',
        'database': 'ElDawliya_Sys',
        'username': 'sa',
        'password': '',
        'port': '1433',
        'windows_auth_checked': '',
        'sql_auth_style': 'display: block;'
    }

    # Update with form data if provided
    if form_data:
        form_values.update(form_data)
        if form_values.get('use_windows_auth'):
            form_values['windows_auth_checked'] = 'checked'
            form_values['sql_auth_style'] = 'display: none;'

    # Handle form submission
    if path == '/db-setup-handler' and environ['REQUEST_METHOD'] == 'POST':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
            post_data = parse_qs(request_body)

            host = post_data.get('host', [''])[0]
            database = post_data.get('database', [''])[0]
            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]
            port = post_data.get('port', ['1433'])[0]
            use_windows_auth = 'use_windows_auth' in post_data
            create_db = 'create_db' in post_data
            test_only = 'test_only' in post_data

            # Update form values for display
            form_values.update({
                'host': host,
                'database': database,
                'username': username,
                'password': password, # Keep password for re-display
                'port': port,
                'windows_auth_checked': 'checked' if use_windows_auth else '',
                'sql_auth_style': 'display: none;' if use_windows_auth else 'display: block;'
            })

            # Construct connection string
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};
                SERVER={host},{port};
                DATABASE={database};"
            )
            if use_windows_auth:
                conn_str += "Trusted_Connection=yes;"
            else:
                conn_str += f"UID={username};PWD={password};"

            # Attempt to connect
            conn = None
            try:
                conn = pyodbc.connect(conn_str, autocommit=True)
                cursor = conn.cursor()

                if create_db:
                    # Check if DB exists, if not, create it
                    cursor.execute(f"SELECT DB_ID('{database}')")
                    if cursor.fetchone()[0] is None:
                        cursor.execute(f"CREATE DATABASE {database}")
                        success_message = f"قاعدة البيانات '{database}' تم إنشاؤها بنجاح.<br>"

                if not test_only:
                    # Save settings to environment variables or a config file
                    # For simplicity, we'll just set them in the current process
                    os.environ['DB_HOST'] = host
                    os.environ['DB_PORT'] = port
                    os.environ['DB_NAME'] = database
                    if use_windows_auth:
                        os.environ['DB_TRUSTED_CONNECTION'] = 'yes'
                        os.environ.pop('DB_USER', None)
                        os.environ.pop('DB_PASSWORD', None)
                    else:
                        os.environ['DB_USER'] = username
                        os.environ['DB_PASSWORD'] = password
                        os.environ.pop('DB_TRUSTED_CONNECTION', None)

                    success_message = (success_message or "") + "تم حفظ إعدادات قاعدة البيانات بنجاح. يمكنك الآن إعادة تشغيل التطبيق."

                else:
                    success_message = "تم اختبار الاتصال بنجاح!"

            except pyodbc.Error as db_err:
                error_msg = str(db_err)
                if "IM002" in error_msg:
                    error_msg = "برنامج التشغيل غير موجود. يرجى تثبيت برامج تشغيل SQL Server ODBC."
                elif "28000" in error_msg and "Login failed" in error_msg:
                    if use_windows_auth:
                        error_msg = "فشلت مصادقة Windows. جرب مصادقة SQL Server بدلاً من ذلك."
                    else:
                        error_msg = "فشل تسجيل الدخول. يرجى التحقق من اسم المستخدم وكلمة المرور."
                elif "08001" in error_msg:
                    error_msg = "الخادم غير موجود أو تم رفض الاتصال. تحقق من اسم الخادم وإعدادات جدار الحماية."

                error_message = f"""
                <div class="error-banner">
                    <h5><i class="fas fa-exclamation-triangle me-2"></i>خطأ في الاتصال بقاعدة البيانات</h5>
                    <p>{error_msg}</p>
                </div>
                """

        except Exception as e:
            error_message = f"""
            <div class="error-banner">
                <h5><i class="fas fa-exclamation-triangle me-2"></i>حدث خطأ أثناء معالجة الطلب</h5>
                <p>{str(e)}</p>
                <pre>{traceback.format_exc()}</pre>
            </div>
            """

    # Prepare error message HTML if provided
    error_html = error_message or ""
    success_html = success_message or ""

    # Serve the database setup page
    html = DB_SETUP_HTML.format(
        error_message=error_html,
        success_message=success_html,
        **form_values
    )
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return [html.encode('utf-8')]

class DatabaseErrorMiddleware:
    """
    WSGI middleware that catches database connection errors during startup
    and shows the database setup page.
    """
    def __init__(self, application):
        """
        __init__ function
        """
        self.application = application

    def __call__(self, environ, start_response):
        """
        Call the application and catch any database errors.
        If a database error occurs, show the database setup page.
        """
        path = environ.get('PATH_INFO', '')

        # Always allow access to the database setup handler
        if path == '/db-setup-handler':
            return db_setup_application(environ, start_response)

        try:
            # Try to handle the request normally
            return self.application(environ, start_response)

        except Exception as e:
            # Check if it's a database error
            error_message = str(e).lower()

            # Check for common database connection failure messages
            connection_error = any(msg in error_message for msg in [
                'could not connect',
                'connection refused',
                'server is not found',
                'login failed',
                'unable to open database',
                'timeout expired',
                'network-related',
                'connection timed out',
                'no such table',
                'failed to connect'
            ])

            if not connection_error:
                # If not a connection error, re-raise
                raise

            # It's a database error, show the setup page
            return db_setup_application(environ, start_response, str(e))

def get_wsgi_application():
    """
    Return the Django WSGI application wrapped with the database error handler.
    """
    # Set the Django settings module if not already set
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings.development')

    try:
        # Try to import Django WSGI application
        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()

        # Wrap the application with our custom middleware
        return DatabaseErrorMiddleware(application)

    except Exception as e:
        # If Django can't be loaded due to database error, return the simple application
        error_message = str(e)
        def simple_app(environ, start_response):
            """
simple_app function
"""
            return db_setup_application(environ, start_response, error_message)

        return simple_app
