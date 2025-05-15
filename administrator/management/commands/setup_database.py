import os
import re
import sys
import pyodbc
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = 'إعداد اتصال قاعدة البيانات بدون الحاجة إلى قاعدة بيانات موجودة'

    def add_arguments(self, parser):
        parser.add_argument('--host', type=str, help='خادم قاعدة البيانات')
        parser.add_argument('--name', type=str, help='اسم قاعدة البيانات')
        parser.add_argument('--user', type=str, help='اسم المستخدم')
        parser.add_argument('--password', type=str, help='كلمة المرور')
        parser.add_argument('--port', type=str, default='1433', help='منفذ قاعدة البيانات')
        parser.add_argument('--windows-auth', action='store_true', help='استخدام مصادقة Windows')
        parser.add_argument('--create-db', action='store_true', help='إنشاء قاعدة البيانات إذا لم تكن موجودة')
        parser.add_argument('--test', action='store_true', help='اختبار الاتصال فقط بدون حفظ الإعدادات')

    def handle(self, *args, **options):
        # التحقق من وجود الخيارات المطلوبة
        if not options['host']:
            self.stdout.write(self.style.ERROR('يجب تحديد خادم قاعدة البيانات (--host)'))
            return
        
        if not options['name']:
            self.stdout.write(self.style.ERROR('يجب تحديد اسم قاعدة البيانات (--name)'))
            return
        
        if not options['windows_auth'] and (not options['user'] or not options['password']):
            self.stdout.write(self.style.ERROR('يجب تحديد اسم المستخدم وكلمة المرور عند عدم استخدام مصادقة Windows'))
            return
        
        # اختبار الاتصال بقاعدة البيانات
        try:
            self.stdout.write(self.style.WARNING(f'محاولة الاتصال بالخادم: {options["host"]}...'))
            
            # تجربة مختلف برامج تشغيل ODBC بترتيب الأفضلية
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
                    # بناء سلسلة الاتصال بناءً على نوع المصادقة
                    if options['windows_auth']:
                        conn_str = f'DRIVER={{{driver}}};SERVER={options["host"]};Trusted_Connection=yes;'
                    else:
                        conn_str = f'DRIVER={{{driver}}};SERVER={options["host"]};UID={options["user"]};PWD={options["password"]}'
                    
                    self.stdout.write(f'محاولة الاتصال باستخدام برنامج التشغيل: {driver}')
                    # اختبار الاتصال مع مهلة قصيرة
                    conn = pyodbc.connect(conn_str, timeout=5)
                    self.stdout.write(self.style.SUCCESS(f'تم الاتصال بنجاح باستخدام برنامج التشغيل: {driver}'))
                    driver_used = driver
                    break
                except pyodbc.Error as e:
                    connection_error = str(e)
                    self.stdout.write(self.style.WARNING(f'فشل الاتصال باستخدام برنامج التشغيل {driver}: {connection_error}'))
                    continue
            
            if conn is None:
                self.stdout.write(self.style.ERROR(f'تعذر الاتصال باستخدام أي برنامج تشغيل متاح. آخر خطأ: {connection_error}'))
                return
            
            # الاتصال ناجح، الحصول على قواعد البيانات
            cursor = conn.cursor()
            
            try:
                # الحصول على جميع قواعد البيانات (باستثناء قواعد البيانات النظام)
                cursor.execute("""
                    SELECT name
                    FROM sys.databases
                    WHERE database_id > 4
                    AND state_desc = 'ONLINE'
                    ORDER BY name
                """)
                
                databases = [row[0] for row in cursor.fetchall()]
                self.stdout.write(f'تم العثور على {len(databases)} قاعدة بيانات: {", ".join(databases)}')
                
                # التحقق مما إذا كانت قاعدة البيانات المحددة موجودة
                db_exists = options['name'] in databases
                
                if not db_exists:
                    if options['create_db']:
                        self.stdout.write(self.style.WARNING(f'قاعدة البيانات {options["name"]} غير موجودة. جاري إنشاؤها...'))
                        try:
                            # إنشاء قاعدة البيانات
                            cursor.execute(f"CREATE DATABASE [{options['name']}]")
                            conn.commit()
                            self.stdout.write(self.style.SUCCESS(f'تم إنشاء قاعدة البيانات {options["name"]} بنجاح'))
                            db_exists = True
                        except pyodbc.Error as e:
                            self.stdout.write(self.style.ERROR(f'فشل إنشاء قاعدة البيانات: {str(e)}'))
                            return
                    else:
                        self.stdout.write(self.style.ERROR(f'قاعدة البيانات {options["name"]} غير موجودة. استخدم --create-db لإنشائها'))
                        return
                
            except pyodbc.Error as e:
                self.stdout.write(self.style.ERROR(f'خطأ في الاستعلام عن قواعد البيانات: {str(e)}'))
                # إذا لم نتمكن من الاستعلام عن قواعد البيانات، نجرب استعلامًا أبسط
                try:
                    cursor.execute("SELECT DB_NAME()")
                    current_db = cursor.fetchone()[0]
                    self.stdout.write(f'استخدام قاعدة البيانات الحالية: {current_db}')
                except Exception as e2:
                    self.stdout.write(self.style.ERROR(f'خطأ في الاستعلام البديل: {str(e2)}'))
                    return
            
            cursor.close()
            conn.close()
            
            # إذا كان هذا مجرد اختبار، نتوقف هنا
            if options['test']:
                self.stdout.write(self.style.SUCCESS('تم اختبار الاتصال بنجاح'))
                return
            
            # تحديث ملف settings.py
            try:
                settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'ElDawliya_sys/settings.py')
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings_content = f.read()
                
                # إعداد تكوين قاعدة البيانات
                if options['windows_auth']:
                    db_config = f"""'default': {{
        'ENGINE': 'mssql',
        'NAME': '{options['name']}',
        'HOST': '{options['host']}',
        'PORT': '{options['port']}',
        'OPTIONS': {{
            'driver': '{driver_used}',
            'Trusted_Connection': 'yes',
        }},
    }}"""
                else:
                    db_config = f"""'default': {{
        'ENGINE': 'mssql',
        'NAME': '{options['name']}',
        'HOST': '{options['host']}',
        'PORT': '{options['port']}',
        'USER': '{options['user']}',
        'PASSWORD': '{options['password']}',
        'OPTIONS': {{
            'driver': '{driver_used}',
            'Trusted_Connection': 'no',
        }},
    }}"""
                
                # تحديث تكوين قاعدة البيانات الافتراضية
                if "'default':" in settings_content:
                    settings_content = re.sub(
                        r"'default': \{[^\}]*\},",
                        f"{db_config},",
                        settings_content
                    )
                else:
                    # إذا لم يكن هناك تكوين افتراضي، نضيفه إلى DATABASES
                    settings_content = re.sub(
                        r"DATABASES = \{",
                        f"DATABASES = {{\n    {db_config},",
                        settings_content
                    )
                
                # كتابة التغييرات إلى ملف الإعدادات
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(settings_content)
                
                self.stdout.write(self.style.SUCCESS('تم تحديث إعدادات قاعدة البيانات بنجاح'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'خطأ في تحديث إعدادات قاعدة البيانات: {str(e)}'))
                return
            
        except pyodbc.Error as e:
            error_msg = str(e)
            self.stdout.write(self.style.ERROR(f'خطأ ODBC: {error_msg}'))
            
            # تقديم رسائل خطأ أكثر فائدة
            if "IM002" in error_msg:
                self.stdout.write(self.style.ERROR("برنامج التشغيل غير موجود. يرجى تثبيت برامج تشغيل SQL Server ODBC."))
            elif "28000" in error_msg and "Login failed" in error_msg:
                if options['windows_auth']:
                    self.stdout.write(self.style.ERROR("فشلت مصادقة Windows. جرب مصادقة SQL Server بدلاً من ذلك."))
                else:
                    self.stdout.write(self.style.ERROR("فشل تسجيل الدخول. يرجى التحقق من اسم المستخدم وكلمة المرور."))
            elif "08001" in error_msg:
                self.stdout.write(self.style.ERROR("الخادم غير موجود أو تم رفض الاتصال. تحقق من اسم الخادم وإعدادات جدار الحماية."))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطأ عام: {str(e)}'))
