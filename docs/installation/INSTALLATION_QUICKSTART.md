# 🚀 دليل التثبيت السريع
## Quick Installation Guide - ElDawliya System

---

## ⚡ التثبيت السريع (3 خطوات)

### الخطوة 1: تفعيل البيئة الافتراضية

```powershell
# إنشاء البيئة (إذا لم تكن موجودة)
python -m venv venv

# تفعيل البيئة
.\venv\Scripts\Activate.ps1
```

### الخطوة 2: تثبيت الحزم

#### ✅ إذا كنت تستخدم Python 3.13:

```powershell
# استخدم السكريبت الآلي (موصى به)
.\install_packages.ps1

# أو التثبيت اليدوي
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

#### ✅ إذا كنت تستخدم Python 3.12:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-python312.txt
```

### الخطوة 3: إعداد المشروع

```powershell
# نسخ ملف البيئة
Copy-Item .env.example .env

# تعديل .env بمعلومات قاعدة البيانات الخاصة بك
notepad .env

# تطبيق الهجرات
python manage.py migrate

# إنشاء مستخدم admin
python manage.py createsuperuser

# تشغيل السيرفر
python manage.py runserver
```

---

## 🔧 حل المشاكل الشائعة

### ❌ مشكلة: فشل تثبيت pyodbc

**الحل**:
```powershell
# تثبيت Microsoft C++ Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools

# ثم أعد التثبيت
python -m pip install pyodbc
```

### ❌ مشكلة: فشل تثبيت pandas

**الحل**:
```powershell
# تأكد من تثبيت numpy أولاً
python -m pip install "numpy>=1.26.0"

# ثم ثبت pandas
python -m pip install "pandas>=2.2.3"
```

### ❌ مشكلة: Python 3.13 غير متوافق

**الحل**: استخدم Python 3.12 بدلاً من ذلك
```powershell
# تثبيت Python 3.12
winget install Python.Python.3.12

# إنشاء بيئة جديدة
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1

# تثبيت الحزم
python -m pip install -r requirements-python312.txt
```

---

## 📚 للمزيد من التفاصيل

- **دليل Python 3.13**: راجع `PYTHON_313_INSTALLATION_GUIDE.md`
- **دليل النشر الكامل**: راجع `DEPLOYMENT_GUIDE.md`
- **التقرير النهائي**: راجع `FINAL_AUDIT_REPORT.md`

---

## ✅ التحقق من التثبيت

```powershell
# التحقق من Django
python manage.py check

# التحقق من الحزم
python -c "import django, pyodbc, pandas; print('✓ All packages OK')"
```

---

**الحالة**: ✅ جاهز للاستخدام  
**التاريخ**: 2025-11-17

