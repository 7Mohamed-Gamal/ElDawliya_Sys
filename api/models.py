from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class APIKey(models.Model):
    """Model for API key management"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=100, help_text="اسم مفتاح API")
    key = models.CharField(max_length=64, unique=True, help_text="مفتاح API")
    is_active = models.BooleanField(default=True, help_text="هل المفتاح نشط؟")
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="تاريخ انتهاء الصلاحية")

    class Meta:
        verbose_name = "مفتاح API"
        verbose_name_plural = "مفاتيح API"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def is_expired(self):
        """Check if the API key is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class GeminiConversation(models.Model):
    """Model to store Gemini AI conversations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gemini_conversations')
    title = models.CharField(max_length=200, help_text="عنوان المحادثة")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "محادثة Gemini"
        verbose_name_plural = "محادثات Gemini"
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class GeminiMessage(models.Model):
    """Model to store individual messages in Gemini conversations"""
    ROLE_CHOICES = [
        ('user', 'المستخدم'),
        ('assistant', 'المساعد'),
        ('system', 'النظام'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(GeminiConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField(help_text="محتوى الرسالة")
    timestamp = models.DateTimeField(auto_now_add=True)
    tokens_used = models.IntegerField(default=0, help_text="عدد الرموز المستخدمة")

    class Meta:
        verbose_name = "رسالة Gemini"
        verbose_name_plural = "رسائل Gemini"
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class APIUsageLog(models.Model):
    """Model to log API usage for monitoring and analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=200, help_text="نقطة النهاية المستخدمة")
    method = models.CharField(max_length=10, help_text="طريقة HTTP")
    status_code = models.IntegerField(help_text="رمز الاستجابة")
    response_time = models.FloatField(help_text="وقت الاستجابة بالثواني")
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name = "سجل استخدام API"
        verbose_name_plural = "سجلات استخدام API"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.endpoint} - {self.status_code} - {self.timestamp}"


class AIProvider(models.Model):
    """نموذج لمقدمي خدمات الذكاء الاصطناعي"""
    PROVIDER_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI GPT'),
        ('claude', 'Anthropic Claude'),
        ('huggingface', 'Hugging Face'),
        ('ollama', 'Ollama (Local)'),
        ('custom', 'مخصص'),
    ]

    name = models.CharField(max_length=100, choices=PROVIDER_CHOICES, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    api_endpoint = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    requires_api_key = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مقدم خدمة الذكاء الاصطناعي"
        verbose_name_plural = "مقدمو خدمات الذكاء الاصطناعي"
        ordering = ['display_name']

    def __str__(self):
        return self.display_name


class AIConfiguration(models.Model):
    """إعدادات الذكاء الاصطناعي للمستخدمين"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_configurations')
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=500, help_text="مفتاح API")
    model_name = models.CharField(max_length=200, default='gemini-1.5-flash', help_text="اسم النموذج")
    is_default = models.BooleanField(default=False, help_text="الإعداد الافتراضي")
    is_active = models.BooleanField(default=True)
    max_tokens = models.IntegerField(default=1000, help_text="الحد الأقصى للرموز")
    temperature = models.FloatField(default=0.7, help_text="درجة الإبداع (0-1)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "إعداد الذكاء الاصطناعي"
        verbose_name_plural = "إعدادات الذكاء الاصطناعي"
        unique_together = ['user', 'provider']
        ordering = ['-is_default', 'provider__display_name']

    def __str__(self):
        return f"{self.user.username} - {self.provider.display_name}"

    def save(self, *args, **kwargs):
        # إذا كان هذا الإعداد افتراضي، قم بإلغاء الافتراضي من الآخرين
        if self.is_default:
            AIConfiguration.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
