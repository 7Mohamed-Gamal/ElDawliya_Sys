"""
تطبيق إعداد قاعدة البيانات النهائي.
"""

import os
import re
import pyodbc
from wsgiref.simple_server import make_server

# HTML template for database setup page
HTML = """<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إعداد قاعدة البيانات - نظام الدولية</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; direction: rtl; }
        .container { max-width: 800px; margin: 0 auto; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); padding: 20px; }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; font-size: 16px; }
        input[type="checkbox"] { margin-left: 10px; }
        .error { background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px; margin-bottom: 20px; border: 1px solid #f5c6cb; }
        .success { background-color: #d4edda; color: #155724; padding: 10px; border-radius: 4px; margin-bottom: 20px; border: 1px solid #c3e6cb; }
        .btn-group { display: flex; justify-content: space-between; margin-top: 30px; }
        button { padding: 12px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button[name="test"] { background-color: #6c757d; color: white; }
        button[type="submit"]:not([name="test"]) { background-color: #4e73df; color: white; }
        button:hover { opacity: 0.9; }
        .help-text { font-size: 14px; color: #6c757d; margin-top: 5px; }
        .header { text-align: center; margin-bottom: 20px; }
        .logo { font-size: 24px; font-weight: bold; color: #4e73df; margin-bottom: 10px; }
        .alert { background-color: #e7f3fe; border-right: 5px solid #2196F3; padding: 15px; margin-bottom: 20px; }
        .alert h4 { margin-top: 0; color: #0c5460; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">نظام الشركة الدولية</div>
        </div>
        <h1>إعداد قاعدة البيانات</h1>
        
        {error}
        {success}
        
        <div class="alert">
            <h4><i style="margin-left: 10px;">ℹ️</i>معلومات</h4>
            <p>يجب إعداد الاتصال بقاعدة بيانات SQL Server لاستخدام النظام. يمكنك استخدام قاعدة بيانات موجودة أو إنشاء قاعدة بيانات جديدة.</p>
            <ul>
                <li>تأكد من تثبيت SQL Server وتشغيله على الخادم</li>
                <li>تأكد من تمكين بروتوكول TCP/IP في إعدادات SQL Server</li>
                <li>تأكد من فتح المنفذ المناسب (عادة 1433) في جدار الحماية</li>
            </ul>
        </div>
        
        <form method="post" action="/">
            <div class="form-group">
                <label for="host">اسم الخادم (Server Name):</label>
                <input type="text" id="host" name="host" value="{host}" placeholder="مثال: SERVERNAME\\SQLEXPRESS أو localhost" required>
                <div class="help-text">أدخل اسم خادم SQL Server أو عنوان IP الخاص به</div>
            </div>
            
            <div class="form-group">
                <label for="database">اسم قاعدة البيانات:</label>
                <input type="text" id="database" name="database" value="{database}" required>
                <div class="help-text">أدخل اسم قاعدة البيانات التي تريد استخدامها</div>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" id="use_windows_auth" name="use_windows_auth" {windows_auth} onclick="toggleAuthFields()"> 
                    استخدام مصادقة Windows
                </label>
                <div class="help-text">حدد هذا الخيار إذا كنت تريد استخدام مصادقة Windows بدلاً من مصادقة SQL Server</div>
            </div>
            
            <div id="sql_auth" style="{sql_auth_style}">
                <div class="form-group">
                    <label for="username">اسم المستخدم:</label>
                    <input type="text" id="username" name="username" value="{username}">
                </div>
                
                <div class="form-group">
                    <label for="password">كلمة المرور:</label>
                    <input type="password" id="password" name="password" value="{password}">
                </div>
            </div>
            
            <div class="form-group">
                <label for="port">المنفذ (Port):</label>
                <input type="text" id="port" name="port" value="{port}">
                <div class="help-text">المنفذ الافتراضي لـ SQL Server هو 1433</div>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" id="create_db" name="create_db"> 
                    إنشاء قاعدة البيانات إذا لم تكن موجودة
                </label>
                <div class="help-text">حدد هذا الخيار للسماح بإنشاء قاعدة البيانات تلقائيًا إذا لم تكن موجودة</div>
            </div>
            
            <div class="btn-group">
                <button type="submit" name="test" value="1">اختبار الاتصال</button>
                <button type="submit">حفظ الإعدادات</button>
            </div>
        </form>
    </div>
    
    <script>
        function toggleAuthFields() {
            var useWindowsAuth = document.getElementById('use_windows_auth');
            var sqlAuthFields = document.getElementById('sql_auth');
            
            if (useWindowsAuth.checked) {
                sqlAuthFields.style.display = 'none';
            } else {
                sqlAuthFields.style.display = 'block';
            }
        }
        
        // Call the function on page load to ensure correct initial state
        document.addEventListener('DOMContentLoaded', function() {
            toggleAuthFields();
        });
    </script>
</body>
</html>"""

# HTML template for success page
SUCCESS_HTML = """<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5;url=/" />
    <title>تم حفظ الإعدادات بنجاح</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; direction: rtl; text-align: center; }
        .container { max-width: 600px; margin: 100px auto; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); padding: 30px; }
        h1 { color: #155724; }
        .success-icon { font-size: 60px; color: #28a745; margin-bottom: 20px; }
        .message { margin: 20px 0; font-size: 18px; }
        .redirect-message { color: #6c757d; margin-top: 30px; }
        .btn { display: inline-block; padding: 10px 20px; background-color: #4e73df; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✓</div>
        <h1>تم حفظ إعدادات قاعدة البيانات بنجاح!</h1>
        <div class="message">
            تم تحديث إعدادات الاتصال بقاعدة البيانات بنجاح. يمكنك الآن استخدام النظام.
        </div>
        <a href="/" class="btn">الانتقال إلى الصفحة الرئيسية</a>
        <div class="redirect-message">
            سيتم توجيهك تلقائيًا إلى الصفحة الرئيسية خلال 5 ثوانٍ...
        </div>
    </div>
</body>
</html>"""

def parse_form_data(environ):
    """Parse form data from POST request."""
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    
    request_body = environ['wsgi.input'].read(request_body_size)
    form_data = {}
    
    if request_body:
        form_str = request_body.decode('utf-8')
        pairs = form_str.split('&')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                form_data[key] = value.replace('+', ' ')
    
    return form_data

def application(environ, start_response):
    """WSGI application for database setup."""
    # Default values
    values = {
        'host': 'localhost',
        'database': 'ElDawliya_Sys',
        'username': 'sa',
        'password': '',
        'port': '1433',
        'windows_auth': '',
        'sql_auth_style': 'display: block;',
        'error': '',
        'success': ''
    }
    
    # Handle POST request
    if environ['REQUEST_METHOD'] == 'POST':
        form_data = parse_form_data(environ)
        
        # Update values from form
        if 'host' in form_data:
            values['host'] = form_data['host']
        if 'database' in form_data:
            values['database'] = form_data['database']
        if 'username' in form_data:
            values['username'] = form_data['username']
        if 'password' in form_data:
            values['password'] = form_data['password']
        if 'port' in form_data:
            values['port'] = form_data['port']
        if 'use_windows_auth' in form_data:
            values['windows_auth'] = 'checked'
            values['sql_auth_style'] = 'display: none;'
        
        # Test connection
        try:
            # Try different ODBC drivers
            drivers = [
                'ODBC Driver 17 for SQL Server',
                'ODBC Driver 13 for SQL Server',
                'SQL Server Native Client 11.0',
                'SQL Server',
            ]
            
            conn = None
            driver_used = None
            last_error = None
            
            for driver in drivers:
                try:
                    if values['windows_auth']:
                        conn_str = f'DRIVER={{{driver}}};SERVER={values["host"]};Trusted_Connection=yes;'
                    else:
                        conn_str = f'DRIVER={{{driver}}};SERVER={values["host"]};UID={values["username"]};PWD={values["password"]}'
                    
                    conn = pyodbc.connect(conn_str, timeout=5)
                    driver_used = driver
                    break
                except pyodbc.Error as e:
                    last_error = str(e)
                    continue
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if conn is None:
                error_message = "فشل الاتصال بالخادم. يرجى التحقق من صحة إعدادات الاتصال."
                
                # تقديم رسائل خطأ أكثر تفصيلاً بناءً على نوع الخطأ
                if last_error:
                    if "08001" in last_error:
                        error_message += "<br>لا يمكن الوصول إلى الخادم. تأكد من أن اسم الخادم صحيح وأن SQL Server قيد التشغيل."
                    elif "28000" in last_error or "Login failed" in last_error:
                        if values['windows_auth']:
                            error_message += "<br>فشلت مصادقة Windows. جرب استخدام مصادقة SQL Server بدلاً من ذلك."
                        else:
                            error_message += "<br>فشل تسجيل الدخول. تأكد من صحة اسم المستخدم وكلمة المرور."
                    elif "IM002" in last_error:
                        error_message += "<br>لم يتم العثور على برنامج تشغيل ODBC لـ SQL Server. يرجى تثبيت برامج تشغيل SQL Server ODBC."
                    
                    error_message += f"<br><small>تفاصيل الخطأ: {last_error}</small>"
                
                values['error'] = f'<div class="error">{error_message}</div>'
            else:
                # Connection successful
                cursor = conn.cursor()
                
                # Check if database exists
                cursor.execute("""
                    SELECT name FROM sys.databases 
                    WHERE name = ?
                """, values['database'])
                
                db_exists = cursor.fetchone() is not None
                
                if not db_exists and 'create_db' in form_data:
                    # Create database
                    try:
                        cursor.execute(f"CREATE DATABASE [{values['database']}]")
                        conn.commit()
                        values['success'] = f'<div class="success">تم إنشاء قاعدة البيانات {values["database"]} بنجاح.</div>'
                        db_exists = True
                    except Exception as e:
                        values['error'] = f'<div class="error">فشل إنشاء قاعدة البيانات: {str(e)}</div>'
                elif not db_exists:
                    values['error'] = f'<div class="error">قاعدة البيانات {values["database"]} غير موجودة. يرجى تحديد خيار "إنشاء قاعدة البيانات" أدناه.</div>'
                
                # If just testing, show success message
                if 'test' in form_data:
                    if not values['error']:
                        values['success'] = '<div class="success">تم الاتصال بالخادم بنجاح!</div>'
                # Otherwise, update settings.py
                elif db_exists and not values['error']:
                    try:
                        # Find settings.py file
                        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ElDawliya_sys/settings.py')
                        with open(settings_path, 'r', encoding='utf-8') as f:
                            settings_content = f.read()
                        
                        # Prepare database config
                        if values['windows_auth']:
                            db_config = f"""'default': {{
        'ENGINE': 'mssql',
        'NAME': '{values["database"]}',
        'HOST': '{values["host"]}',
        'PORT': '{values["port"]}',
        'OPTIONS': {{
            'driver': '{driver_used}',
            'Trusted_Connection': 'yes',
        }},
    }}"""
                        else:
                            db_config = f"""'default': {{
        'ENGINE': 'mssql',
        'NAME': '{values["database"]}',
        'HOST': '{values["host"]}',
        'PORT': '{values["port"]}',
        'USER': '{values["username"]}',
        'PASSWORD': '{values["password"]}',
        'OPTIONS': {{
            'driver': '{driver_used}',
            'Trusted_Connection': 'no',
        }},
    }}"""
                        
                        # Update settings
                        if "'default':" in settings_content:
                            settings_content = re.sub(
                                r"'default': \{[^\}]*\},",
                                f"{db_config},",
                                settings_content
                            )
                        else:
                            settings_content = re.sub(
                                r"DATABASES = \{",
                                f"DATABASES = {{\n    {db_config},",
                                settings_content
                            )
                        
                        # Write back to file
                        with open(settings_path, 'w', encoding='utf-8') as f:
                            f.write(settings_content)
                        
                        # Return success page
                        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
                        return [SUCCESS_HTML.encode('utf-8')]
                    except Exception as e:
                        values['error'] = f'<div class="error">فشل تحديث ملف الإعدادات: {str(e)}</div>'
                
                conn.close()
                
        except Exception as e:
            values['error'] = f'<div class="error">حدث خطأ: {str(e)}</div>'
    
    # Render HTML
    html = HTML.format(**values)
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return [html.encode('utf-8')]

if __name__ == '__main__':
    print("Starting database setup server on http://localhost:8000")
    httpd = make_server('', 8000, application)
    httpd.serve_forever()
