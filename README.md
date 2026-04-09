# نظام الدولية (ElDawliya System)

نظام إداري متكامل لإدارة الموارد البشرية، المخازن، المشتريات، والمشاريع للشركة الدولية.

## التقنيات المستخدمة (Technology Stack)

- **Backend:** Django 4.2+, Python 3.11
- **Database:** SQL Server (via mssql-django)
- **Task Queue:** Celery & Redis
- **Frontend:** Django Templates, Bootstrap 5, JavaScript
- **API:** Django Rest Framework
- **Deployment:** Docker, Gunicorn, WhiteNoise

## التعليمات البرمجية وإعداد النظام (Setup Instructions)

### المتطلبات الأساسية (Prerequisites)

- Python 3.11+
- SQL Server
- Redis Server
- ODBC Driver 17 for SQL Server

### خطوات التثبيت (Installation Steps)

1. **استنساخ المستودع (Clone the repo):**
   ```bash
   git clone https://github.com/7Mohamed-Gamal7/ElDawliya_Sys
   cd ElDawliya_Sys
   ```

2. **إنشاء بيئة افتراضية (Create virtual environment):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **تثبيت التبعيات (Install dependencies):**
   ```bash
   pip install -r requirements.txt
   ```

4. **إعداد ملف البيئة (Configure .env):**
   قم بنسخ ملف `.env.example` إلى `.env` وقم بتعديل القيم حسب بيئتك:
   ```bash
   cp .env.example .env
   ```

5. **تشغيل التهجيرات (Run migrations):**
   ```bash
   python manage.py migrate
   ```

6. **تشغيل خادم التطوير (Run server):**
   ```bash
   python manage.py runserver
   ```

## هيكل المشروع (Project Structure Overview)

- `accounts/`: إدارة المستخدمين والصلاحيات.
- `apps/hr/`: نظام الموارد البشرية وشؤون الموظفين.
- `apps/inventory/`: إدارة المخازن والمستودعات.
- `apps/procurement/`: إدارة المشتريات وطلبات الشراء.
- `apps/projects/`: إدارة المشاريع والمهام والاجتماعات.
- `apps/finance/`: الإدارة المالية والبنوك.
- `notifications/`: نظام التنبيهات والرسائل.
- `api/`: واجهات برمجة التطبيقات (REST API).

## أوامر الإدارة المتاحة (Management Commands)

- `python manage.py validate_config`: للتحقق من صحة إعدادات النظام.
- `python manage.py create_admin`: لإنشاء مستخدم مدير للنظام.

## توثيق واجهة البرمجة (API Documentation)

يمكن الوصول إلى توثيق Swagger و ReDoc عبر الروابط التالية عند تشغيل الخادم:
- Swagger: `/api/v1/swagger/`
- ReDoc: `/api/v1/redoc/`

## الترخيص (License)

هذا المشروع محمي بموجب حقوق الملكية للشركة الدولية.
