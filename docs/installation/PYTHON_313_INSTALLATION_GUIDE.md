# 🐍 دليل تثبيت الحزم على Python 3.13.5
## Python 3.13 Package Installation Guide

**التاريخ**: 2025-11-17  
**المشروع**: ElDawliya_Sys  
**Python Version**: 3.13.5  
**نظام التشغيل**: Windows

---

## 🔍 المشكلة

عند تثبيت الحزم باستخدام `pip install -r requirements.txt`، تفشل الحزم التالية:
- ❌ **pyodbc** 4.0.39 - لا يدعم Python 3.13
- ❌ **pandas** 2.0.3 - لا يدعم Python 3.13

**السبب**: Python 3.13.5 إصدار جديد جداً (صدر في أكتوبر 2024)، ومعظم الحزم لم تبني wheels له بعد.

---

## ✅ الحل الموصى به: تحديث الحزم

### الخطوة 1: تحديث requirements.txt ✅

تم تحديث الحزم التالية في `requirements.txt`:

```diff
# Database
- pyodbc==4.0.39
+ pyodbc>=5.0.0  # Updated for Python 3.13 support

# Data Science & Analytics
- pandas==2.0.3
- numpy>=1.21,<2.0
- matplotlib==3.8.2
+ pandas>=2.2.3  # Updated for Python 3.13 support (first version with 3.13 compatibility)
+ numpy>=1.26.0,<2.0  # Updated for Python 3.13 support
+ matplotlib>=3.9.0  # Updated for Python 3.13 support
```

### الخطوة 2: تثبيت الحزم

#### الطريقة الأولى: استخدام السكريبت الآلي (موصى بها) 🚀

```powershell
# تشغيل سكريبت التثبيت الآلي
.\install_packages.ps1
```

هذا السكريبت سيقوم بـ:
1. ✅ ترقية pip, setuptools, wheel
2. ✅ تثبيت pyodbc مع معالجة الأخطاء
3. ✅ تثبيت numpy أولاً (dependency لـ pandas)
4. ✅ تثبيت pandas
5. ✅ تثبيت باقي الحزم
6. ✅ التحقق من التثبيت

#### الطريقة الثانية: التثبيت اليدوي

```powershell
# 1. ترقية pip
python -m pip install --upgrade pip setuptools wheel

# 2. تثبيت الحزم الحرجة أولاً
python -m pip install "pyodbc>=5.0.0"
python -m pip install "numpy>=1.26.0,<2.0"
python -m pip install "pandas>=2.2.3"
python -m pip install "matplotlib>=3.9.0"

# 3. تثبيت باقي الحزم
python -m pip install -r requirements.txt
```

---

## 🔧 حل مشكلة pyodbc (إذا استمر الفشل)

### المشكلة: pyodbc يحتاج إلى Microsoft C++ Build Tools

إذا فشل تثبيت pyodbc مع رسالة:
```
error: Microsoft Visual C++ 14.0 or greater is required
```

### الحل 1: تثبيت Microsoft C++ Build Tools ⭐

```powershell
# باستخدام winget (Windows Package Manager)
winget install Microsoft.VisualStudio.2022.BuildTools

# أو التحميل اليدوي من:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**خطوات التثبيت**:
1. قم بتشغيل المثبت
2. اختر "Desktop development with C++"
3. تأكد من تحديد:
   - ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
   - ✅ Windows 10/11 SDK
4. انقر "Install"
5. أعد تشغيل PowerShell
6. حاول التثبيت مرة أخرى

### الحل 2: استخدام Pre-built Wheels

```powershell
# تثبيت من Christoph Gohlke's wheels (unofficial)
# قم بتحميل الملف المناسب من:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyodbc

# ثم ثبّت:
pip install pyodbc‑5.x.x‑cp313‑cp313‑win_amd64.whl
```

### الحل 3: استخدام بديل (مؤقت)

إذا كنت بحاجة لحل سريع، يمكنك استخدام `pypyodbc` (pure Python):

```powershell
pip install pypyodbc
```

**ملاحظة**: `pypyodbc` أبطأ من `pyodbc` لكنه لا يحتاج إلى compilation.

---

## 🔧 حل مشكلة pandas (إذا استمر الفشل)

### المشكلة: pandas 2.0.3 لا يدعم Python 3.13

**الحل**: تحديث إلى pandas 2.2.3 أو أحدث (تم بالفعل في requirements.txt)

```powershell
# تثبيت أحدث إصدار
python -m pip install --upgrade pandas

# أو تحديد الإصدار
python -m pip install "pandas>=2.2.3"
```

**ملاحظة**: pandas 2.2.3 هو أول إصدار يدعم Python 3.13 رسمياً (صدر في سبتمبر 2024).

---

## 🔄 الحل البديل: استخدام Python 3.12

إذا استمرت المشاكل، يمكنك استخدام Python 3.12 (أكثر استقراراً):

### الخطوة 1: تثبيت Python 3.12

```powershell
# باستخدام winget
winget install Python.Python.3.12

# أو التحميل من:
# https://www.python.org/downloads/release/python-3120/
```

### الخطوة 2: إنشاء بيئة افتراضية جديدة

```powershell
# حذف البيئة القديمة
Remove-Item -Recurse -Force venv

# إنشاء بيئة جديدة بـ Python 3.12
py -3.12 -m venv venv

# تفعيل البيئة
.\venv\Scripts\Activate.ps1

# تثبيت الحزم
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## ✅ التحقق من التثبيت

بعد التثبيت، تحقق من نجاح العملية:

```powershell
# 1. التحقق من Python
python --version
# يجب أن يظهر: Python 3.13.5

# 2. التحقق من الحزم الحرجة
python -c "import django; print('Django:', django.__version__)"
python -c "import pyodbc; print('pyodbc:', pyodbc.version)"
python -c "import pandas; print('pandas:', pandas.__version__)"
python -c "import numpy; print('numpy:', numpy.__version__)"

# 3. التحقق من Django
python manage.py check

# 4. عرض جميع الحزم المثبتة
pip list
```

---

## 📊 جدول توافق الحزم مع Python 3.13

| الحزمة | الإصدار القديم | الإصدار الجديد | دعم Python 3.13 | ملاحظات |
|--------|----------------|----------------|-----------------|----------|
| **pyodbc** | 4.0.39 | ≥5.0.0 | ✅ نعم | يحتاج C++ Build Tools |
| **pandas** | 2.0.3 | ≥2.2.3 | ✅ نعم | أول إصدار يدعم 3.13 |
| **numpy** | ≥1.21 | ≥1.26.0 | ✅ نعم | dependency لـ pandas |
| **matplotlib** | 3.8.2 | ≥3.9.0 | ✅ نعم | يحتاج numpy |
| **Django** | 4.2.26 | - | ✅ نعم | يعمل بدون مشاكل |

---

## 🚨 الأخطاء الشائعة وحلولها

### خطأ 1: "Microsoft Visual C++ 14.0 or greater is required"

**الحل**: تثبيت Microsoft C++ Build Tools (انظر أعلاه)

### خطأ 2: "No matching distribution found for pandas==2.0.3"

**الحل**: تحديث requirements.txt (تم بالفعل)

### خطأ 3: "Failed to build wheel for pyodbc"

**الحل**: 
1. تثبيت C++ Build Tools
2. أو استخدام pre-built wheel
3. أو استخدام pypyodbc

### خطأ 4: "ImportError: DLL load failed"

**الحل**: تثبيت Microsoft ODBC Driver for SQL Server

```powershell
# تحميل من:
# https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

# أو باستخدام winget:
winget install Microsoft.ODBCDriver.18
```

---

## 📝 الخطوات التالية

بعد التثبيت الناجح:

```powershell
# 1. التحقق من Django
python manage.py check

# 2. تطبيق الهجرات
python manage.py makemigrations
python manage.py migrate

# 3. تشغيل الاختبارات
python manage.py test

# 4. تشغيل السيرفر
python manage.py runserver
```

---

## 📚 مصادر إضافية

- [Python 3.13 Release Notes](https://docs.python.org/3.13/whatsnew/3.13.html)
- [pandas 2.2.3 Release Notes](https://pandas.pydata.org/pandas-docs/stable/whatsnew/v2.2.3.html)
- [pyodbc Documentation](https://github.com/mkleehammer/pyodbc/wiki)
- [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

---

**تم إنشاؤه بواسطة**: Augment Agent  
**التاريخ**: 2025-11-17  
**الحالة**: ✅ جاهز للاستخدام

