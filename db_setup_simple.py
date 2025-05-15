"""
تطبيق بسيط لإعداد قاعدة البيانات.
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
    <title>إعداد قاعدة البيانات</title>
</head>
<body>
    <div>
        <h1>إعداد قاعدة البيانات - نظام الدولية</h1>
        
        {error}
        {success}
        
        <div>
            <h3>معلومات</h3>
            <p>يجب إعداد الاتصال بقاعدة بيانات SQL Server لاستخدام النظام.</p>
            <ul>
                <li>تأكد من تثبيت SQL Server وتشغيله</li>
                <li>تأكد من صحة اسم الخادم</li>
            </ul>
        </div>
        
        <form method="post" action="/">
            <div>
                <label for="host">اسم الخادم:</label>
                <input type="text" id="host" name="host" value="{host}" placeholder="مثال: SERVERNAME\\SQLEXPRESS أو localhost" required>
            </div>
            <br>
            <div>
                <label for="database">اسم قاعدة البيانات:</label>
                <input type="text" id="database" name="database" value="{database}" required>
            </div>
            <br>
            <div>
                <label>
                    <input type="checkbox" id="use_windows_auth" name="use_windows_auth" {windows_auth} onclick="toggleAuthFields()"> 
                    استخدام مصادقة Windows
                </label>
            </div>
            <br>
            <div id="sql_auth" style="{sql_auth_style}">
                <div>
                    <label for="username">اسم المستخدم:</label>
                    <input type="text" id="username" name="username" value="{username}">
                </div>
                <br>
                <div>
                    <label for="password">كلمة المرور:</label>
                    <input type="password" id="password" name="password" value="{password}">
                </div>
                <br>
            </div>
            
            <div>
                <label for="port">المنفذ:</label>
                <input type="text" id="port" name="port" value="{port}">
            </div>
            <br>
            <div>
                <label>
                    <input type="checkbox" id="create_db" name="create_db"> 
                    إنشاء قاعدة البيانات إذا لم تكن موجودة
                </label>
            </div>
            <br>
            <div>
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
</head>
<body>
    <div>
        <h1>تم حفظ إعدادات قاعدة البيانات بنجاح!</h1>
        <p>تم تحديث إعدادات الاتصال بقاعدة البيانات بنجاح. يمكنك الآن استخدام النظام.</p>
        <a href="/">الانتقال إلى الصفحة الرئيسية</a>
        <p>سيتم توجيهك تلقائيًا إلى الصفحة الرئيسية خلال 5 ثوانٍ...</p>
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
                values['error'] = f'<p style="color: red;">{error_message}</p>'
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
                        values['success'] = f'<p style="color: green;">تم إنشاء قاعدة البيانات {values["database"]} بنجاح.</p>'
                        db_exists = True
                    except Exception as e:
                        values['error'] = f'<p style="color: red;">فشل إنشاء قاعدة البيانات: {str(e)}</p>'
                elif not db_exists:
                    values['error'] = f'<p style="color: red;">قاعدة البيانات {values["database"]} غير موجودة. يرجى تحديد خيار "إنشاء قاعدة البيانات" أدناه.</p>'
                
                # If just testing, show success message
                if 'test' in form_data:
                    if not values['error']:
                        values['success'] = '<p style="color: green;">تم الاتصال بالخادم بنجاح!</p>'
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
                        values['error'] = f'<p style="color: red;">فشل تحديث ملف الإعدادات: {str(e)}</p>'
                
                conn.close()
                
        except Exception as e:
            values['error'] = f'<p style="color: red;">حدث خطأ: {str(e)}</p>'
    
    # Render HTML
    html = HTML.format(**values)
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return [html.encode('utf-8')]

if __name__ == '__main__':
    print("Starting database setup server on http://localhost:8000")
    httpd = make_server('', 8000, application)
    httpd.serve_forever()
