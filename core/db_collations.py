"""
تسجيل مقارنات مخصصة للغة العربية في SQLite
(Register custom collations for Arabic language in SQLite)
"""
import re
import unicodedata
from django.db.backends.signals import connection_created

def normalize_arabic(text):
    """
    تطبيع النص العربي للمقارنة بدون حساسية للحالة أو التشكيل
    (Normalize Arabic text for case-insensitive and diacritics-insensitive comparison)
    """
    if not text:
        return ""
    
    # تحويل إلى حروف صغيرة (Convert to lowercase)
    text = text.lower()
    
    # إزالة التشكيل (Remove diacritics)
    text = ''.join([c for c in unicodedata.normalize('NFD', text) 
                   if not unicodedata.combining(c)])
    
    # توحيد أشكال الألف (Normalize alef forms)
    text = re.sub(r'[أإآا]', 'ا', text)
    
    # توحيد التاء المربوطة والهاء (Normalize taa marbouta and haa)
    text = text.replace('ة', 'ه')
    
    # توحيد الياء والألف المقصورة (Normalize yaa and alef maqsura)
    text = text.replace('ى', 'ي')
    
    return text

def arabic_ci_as_collation(str1, str2):
    """
    دالة مقارنة مخصصة للغة العربية بدون حساسية للحالة أو التشكيل
    (Custom collation function for Arabic language that is case-insensitive and diacritics-insensitive)
    """
    if str1 is None and str2 is None:
        return 0
    if str1 is None:
        return -1
    if str2 is None:
        return 1
        
    # تطبيع النصوص (Normalize texts)
    norm1 = normalize_arabic(str1)
    norm2 = normalize_arabic(str2)
    
    # المقارنة (Comparison)
    if norm1 < norm2:
        return -1
    elif norm1 > norm2:
        return 1
    else:
        return 0

def register_collations(sender, connection, **kwargs):
    """
    تسجيل المقارنات المخصصة عند إنشاء اتصال قاعدة البيانات
    (Register custom collations when a database connection is created)
    """
    if connection.vendor == 'sqlite':
        # تسجيل مقارنة Arabic_CI_AS (Register Arabic_CI_AS collation)
        connection.connection.create_collation('Arabic_CI_AS', arabic_ci_as_collation)
        
        # يمكن إضافة مقارنات أخرى هنا (Other collations can be added here)

# توصيل الإشارة (Connect the signal)
connection_created.connect(register_collations)