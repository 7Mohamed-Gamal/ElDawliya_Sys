"""
هذا الملف يحتوي على تعليمات إضافة تطبيق مهام الموظفين إلى مشروع ElDawliya_System
"""

# خطوات إضافة تطبيق مهام الموظفين إلى المشروع:

"""
1. إضافة التطبيق إلى INSTALLED_APPS في ملف settings.py:
   ```python
   INSTALLED_APPS = [
       ...
       'employee_tasks',  # تطبيق مهام الموظفين
   ]
   ```

2. إضافة مسارات التطبيق إلى ملف urls.py الرئيسي:
   ```python
   urlpatterns = [
       ...
       path('employee-tasks/', include('employee_tasks.urls')),  # مسارات تطبيق مهام الموظفين
   ]
   ```

3. تشغيل أمر makemigrations لإنشاء ملفات الترحيل:
   ```
   python manage.py makemigrations employee_tasks
   ```

4. تشغيل أمر migrate لتطبيق الترحيلات على قاعدة البيانات:
   ```
   python manage.py migrate employee_tasks
   ```

5. تشغيل أمر إنشاء قسم مهام الموظفين في القائمة الجانبية:
   ```
   python manage.py create_employee_tasks_department
   ```

6. إضافة قسم مهام الموظفين إلى ملف home_dashboard.html:
   - إضافة بطاقات مهام الموظفين
   - إضافة تعريف CSS لبطاقات مهام الموظفين
   - إضافة قسم مهام الموظفين إلى قائمة التعيينات في JavaScript
"""
