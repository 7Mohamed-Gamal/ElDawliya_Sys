from django.conf import settings

class DatabaseRouter:
    """
    موجه قواعد البيانات للتبديل بين قاعدتي البيانات الافتراضية والاحتياطية.
    يستخدم الإعداد ACTIVE_DB لتحديد قاعدة البيانات النشطة.
    """
    
    def db_for_read(self, model, **hints):
        """
        توجيه عمليات القراءة إلى قاعدة البيانات النشطة.
        """
        return settings.ACTIVE_DB
    
    def db_for_write(self, model, **hints):
        """
        توجيه عمليات الكتابة إلى قاعدة البيانات النشطة.
        """
        return settings.ACTIVE_DB
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        السماح بالعلاقات بين الكائنات في نفس قاعدة البيانات.
        """
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        السماح بترحيل جميع التطبيقات إلى جميع قواعد البيانات.
        """
        return True