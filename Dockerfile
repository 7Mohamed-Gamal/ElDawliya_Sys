# استخدم صورة Python الرسمية
FROM python:3.11-slim

# تثبيت أدوات النظام المطلوبة لبناء NumPy وPyODBC
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# إعداد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملفات المشروع وملف المتطلبات
COPY . /app
COPY requirements.txt /app

# تثبيت مكتبات بايثون
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# فتح المنفذ 8000 لتشغيل Django
EXPOSE 8000

# أمر التشغيل الافتراضي
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
