"""
تطبيق WSGI بسيط لإعداد قاعدة البيانات.

يمكن تشغيل هذا التطبيق بشكل مستقل عن Django عندما تكون قاعدة البيانات غير متاحة.
"""

import os
import sys
import re
import traceback
import pyodbc
from urllib.parse import parse_qs

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
                
                <form method="post" action="/" id="dbForm">
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
                fetch('/', {
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

def application(environ, start_response):
    """
    WSGI application for database setup.
    """
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
    
    error_message = ""
    success_message = ""
    
    # Handle form submission
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            # Get form data
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
            form_data = parse_qs(post_data)
            
            # Extract form values
            host = form_data.get('host', [''])[0]
            database = form_data.get('database', [''])[0]
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]
            port = form_data.get('port', ['1433'])[0]
            use_windows_auth = 'use_windows_auth' in form_data
            create_db = 'create_db' in form_data
            test_only = 'test_only' in form_data
            
            # Update form values
            form_values = {
                'host': host,
                'database': database,
                'username': username,
                'password': password,
                'port': port,
                'windows_auth_checked': 'checked' if use_windows_auth else '',
                'sql_auth_style': 'display: none;' if use_windows_auth else 'display: block;'
            }
            
            # Test database connection
            try:
                # Try different ODBC drivers in order of preference
                drivers = [
                    'ODBC Driver 17 for SQL Server',
                    'ODBC Driver 13 for SQL Server',
                    'SQL Server Native Client 11.0',
                    'SQL Server',
                ]
                
                connection_error = None
                conn = None
                driver_used = None
                
                for driver in drivers:
                    try:
                        # Build connection string based on authentication type
                        if use_windows_auth:
                            conn_str = f'DRIVER={{{driver}}};SERVER={host};Trusted_Connection=yes;'
                        else:
                            conn_str = f'DRIVER={{{driver}}};SERVER={host};UID={username};PWD={password}'
                        
                        # Test connection with a short timeout
                        conn = pyodbc.connect(conn_str, timeout=5)
                        driver_used = driver
                        break
                    except pyodbc.Error as e:
                        connection_error = str(e)
                        continue
                
                if conn is None:
                    error_message = f"""
                    <div class="error-banner">
                        <h5><i class="fas fa-exclamation-triangle me-2"></i>فشل الاتصال بقاعدة البيانات</h5>
                        <p>تعذر الاتصال باستخدام أي برنامج تشغيل متاح.</p>
                        <p>آخر خطأ: {connection_error}</p>
                    </div>
                    """
                else:
                    # Connection successful, check database
                    cursor = conn.cursor()
                    
                    try:
                        # Get all databases (excluding system databases)
                        cursor.execute("""
                            SELECT name
                            FROM sys.databases
                            WHERE database_id > 4
                            AND state_desc = 'ONLINE'
                            ORDER BY name
                        """)
                        
                        databases = [row[0] for row in cursor.fetchall()]
                        db_exists = database in databases
                        
                        if not db_exists:
                            if create_db:
                                # Create database
                                try:
                                    cursor.execute(f"CREATE DATABASE [{database}]")
                                    conn.commit()
                                    success_message = f"""
                                    <div class="success-banner">
                                        <h5><i class="fas fa-check-circle me-2"></i>تم إنشاء قاعدة البيانات بنجاح</h5>
                                        <p>تم إنشاء قاعدة البيانات {database} بنجاح.</p>
                                    </div>
                                    """
                                    db_exists = True
                                except pyodbc.Error as e:
                                    error_message = f"""
                                    <div class="error-banner">
                                        <h5><i class="fas fa-exclamation-triangle me-2"></i>فشل إنشاء قاعدة البيانات</h5>
                                        <p>تعذر إنشاء قاعدة البيانات {database}.</p>
                                        <p>الخطأ: {str(e)}</p>
                                    </div>
                                    """
                            else:
                                error_message = f"""
                                <div class="error-banner">
                                    <h5><i class="fas fa-exclamation-triangle me-2"></i>قاعدة البيانات غير موجودة</h5>
                                    <p>قاعدة البيانات {database} غير موجودة.</p>
                                    <p>حدد خيار "إنشاء قاعدة البيانات إذا لم تكن موجودة" لإنشائها تلقائيًا.</p>
                                </div>
                                """
                        
                    except pyodbc.Error as e:
                        # If we can't query databases, try a simpler query
                        try:
                            cursor.execute("SELECT DB_NAME()")
                            current_db = cursor.fetchone()[0]
                        except Exception as e2:
                            error_message = f"""
                            <div class="error-banner">
                                <h5><i class="fas fa-exclamation-triangle me-2"></i>خطأ في الاستعلام عن قواعد البيانات</h5>
                                <p>تعذر الاستعلام عن قواعد البيانات المتاحة.</p>
                                <p>الخطأ: {str(e2)}</p>
                            </div>
                            """
                    
                    cursor.close()
                    conn.close()
                    
                    # If this is just a test, return success message
                    if test_only and not error_message:
                        success_message = f"""
                        <div class="success-banner">
                            <h5><i class="fas fa-check-circle me-2"></i>تم الاتصال بنجاح</h5>
                            <p>تم الاتصال بالخادم {host} بنجاح.</p>
                            <p>قاعدة البيانات {database} {'موجودة' if db_exists else 'غير موجودة'}.</p>
                        </div>
                        """
                    
                    # If not a test and no errors, update settings.py file
                    if not test_only and not error_message:
                        try:
                            # Find settings.py file
                            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ElDawliya_sys/settings.py')
                            with open(settings_path, 'r', encoding='utf-8') as f:
                                settings_content = f.read()
                            
                            # Prepare the database configuration
                            if use_windows_auth:
                                db_config = f"""'default': {{
        'ENGINE': 'mssql',
        'NAME': '{database}',
        'HOST': '{host}',
        'PORT': '{port}',
        'OPTIONS': {{
            'driver': '{driver_used}',
            'Trusted_Connection': 'yes',
        }},
    }}"""
                            else:
                                db_config = f"""'default': {{
        'ENGINE': 'mssql',
        'NAME': '{database}',
        'HOST': '{host}',
        'PORT': '{port}',
        'USER': '{username}',
        'PASSWORD': '{password}',
        'OPTIONS': {{
            'driver': '{driver_used}',
            'Trusted_Connection': 'no',
        }},
    }}"""
                            
                            # Update the default database configuration
                            if "'default':" in settings_content:
                                settings_content = re.sub(
                                    r"'default': \{[^\}]*\},",
                                    f"{db_config},",
                                    settings_content
                                )
                            else:
                                # If there's no default configuration, add it to DATABASES
                                settings_content = re.sub(
                                    r"DATABASES = \{",
                                    f"DATABASES = {{\n    {db_config},",
                                    settings_content
                                )
                            
                            # Write back to settings file
                            with open(settings_path, 'w', encoding='utf-8') as f:
                                f.write(settings_content)
                            
                            # Redirect to home page
                            start_response('302 Found', [('Location', '/')])
                            return [b'Redirecting...']
                            
                        except Exception as e:
                            error_message = f"""
                            <div class="error-banner">
                                <h5><i class="fas fa-exclamation-triangle me-2"></i>خطأ في تحديث ملف الإعدادات</h5>
                                <p>تعذر تحديث ملف الإعدادات.</p>
                                <p>الخطأ: {str(e)}</p>
                            </div>
                            """
            
            except pyodbc.Error as e:
                error_msg = str(e)
                
                # Provide more helpful error messages
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
    
    # Serve the database setup page
    html = DB_SETUP_HTML.format(
        error_message=error_message,
        success_message=success_message,
        **form_values
    )
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return [html.encode('utf-8')]

if __name__ == '__main__':
    # Run the application with a simple WSGI server
    from wsgiref.simple_server import make_server
    
    print("Starting database setup server on http://localhost:8000")
    httpd = make_server('', 8000, application)
    httpd.serve_forever()
