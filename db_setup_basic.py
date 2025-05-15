"""
تطبيق بسيط جدًا لإعداد قاعدة البيانات.
"""

import os
import sys
import re
import pyodbc
from wsgiref.simple_server import make_server

# HTML template for database setup page
HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Database Setup</title>
</head>
<body>
    <div>
        <h1>Database Setup</h1>
        
        {error}
        {success}
        
        <form method="post" action="/">
            <div>
                <label for="host">Server Name:</label>
                <input type="text" id="host" name="host" value="{host}" placeholder="Example: SERVERNAME\\SQLEXPRESS or localhost" required>
            </div>
            <br>
            <div>
                <label for="database">Database Name:</label>
                <input type="text" id="database" name="database" value="{database}" required>
            </div>
            <br>
            <div>
                <label>
                    <input type="checkbox" id="use_windows_auth" name="use_windows_auth" {windows_auth}> 
                    Use Windows Authentication
                </label>
            </div>
            <br>
            <div id="sql_auth" style="{sql_auth_style}">
                <div>
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" value="{username}">
                </div>
                <br>
                <div>
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" value="{password}">
                </div>
                <br>
            </div>
            
            <div>
                <label for="port">Port:</label>
                <input type="text" id="port" name="port" value="{port}">
            </div>
            <br>
            <div>
                <label>
                    <input type="checkbox" id="create_db" name="create_db"> 
                    Create database if it doesn't exist
                </label>
            </div>
            <br>
            <div>
                <button type="submit" name="test" value="1">Test Connection</button>
                <button type="submit">Save Settings</button>
            </div>
        </form>
        
        <script>
            document.getElementById('use_windows_auth').addEventListener('change', function() {
                document.getElementById('sql_auth').style.display = this.checked ? 'none' : 'block';
            });
        </script>
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
            
            for driver in drivers:
                try:
                    if values['windows_auth']:
                        conn_str = f'DRIVER={{{driver}}};SERVER={values["host"]};Trusted_Connection=yes;'
                    else:
                        conn_str = f'DRIVER={{{driver}}};SERVER={values["host"]};UID={values["username"]};PWD={values["password"]}'
                    
                    conn = pyodbc.connect(conn_str, timeout=5)
                    driver_used = driver
                    break
                except Exception:
                    continue
            
            if conn is None:
                values['error'] = '<p style="color: red;">Connection failed. Check your settings.</p>'
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
                        values['success'] = f'<p style="color: green;">Database {values["database"]} created successfully.</p>'
                        db_exists = True
                    except Exception as e:
                        values['error'] = f'<p style="color: red;">Failed to create database: {str(e)}</p>'
                elif not db_exists:
                    values['error'] = f'<p style="color: red;">Database {values["database"]} does not exist. Check the option to create it.</p>'
                
                # If just testing, show success message
                if 'test' in form_data:
                    if not values['error']:
                        values['success'] = '<p style="color: green;">Connection successful!</p>'
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
                        
                        # Redirect to home page
                        start_response('302 Found', [('Location', '/')])
                        return [b'Redirecting...']
                    except Exception as e:
                        values['error'] = f'<p style="color: red;">Failed to update settings: {str(e)}</p>'
                
                conn.close()
                
        except Exception as e:
            values['error'] = f'<p style="color: red;">Error: {str(e)}</p>'
    
    # Render HTML
    html = HTML.format(**values)
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return [html.encode('utf-8')]

if __name__ == '__main__':
    print("Starting database setup server on http://localhost:8000")
    httpd = make_server('', 8000, application)
    httpd.serve_forever()
