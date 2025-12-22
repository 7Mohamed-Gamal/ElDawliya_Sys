from rest_framework import serializers
from django.contrib.auth import get_user_model

# Import models with error handling
try:
    from ..models import APIKey, GeminiConversation, GeminiMessage, APIUsageLog
except ImportError:
    # Create dummy classes if models don't exist
    class APIKey:
        pass
    class GeminiConversation:
        pass
    class GeminiMessage:
        pass
    class APIUsageLog:
        pass

# Dynamic imports for disabled models - only import when needed
TblProducts = TblCategories = TblSuppliers = None
Task = None
Meeting = None

def get_inventory_models():
    """Dynamically import apps.inventory models if available"""
    try:
        from apps.inventory.models import TblProducts, TblCategories, TblSuppliers
        return TblProducts, TblCategories, TblSuppliers
    except ImportError:
        return None, None, None

def get_task_model():
    """Dynamically import task model if available"""
    try:
        from apps.projects.tasks.models import Task
        return Task
    except ImportError:
        return None

def get_meeting_model():
    """Dynamically import meeting model if available"""
    try:
        from apps.projects.meetings.models import Meeting
        return Meeting
    except ImportError:
        return None

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        """Meta class"""
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API Key model"""
    user = UserSerializer(read_only=True)

    class Meta:
        """Meta class"""
        model = APIKey
        fields = ['id', 'user', 'name', 'key', 'is_active', 'created_at', 'last_used', 'expires_at']
        read_only_fields = ['id', 'key', 'created_at', 'last_used']


# Gemini AI Request/Response Serializers
class GeminiChatRequestSerializer(serializers.Serializer):
    """Serializer for Gemini chat requests"""
    message = serializers.CharField(max_length=10000, help_text="الرسالة المراد إرسالها لـ Gemini")
    conversation_id = serializers.UUIDField(required=False, help_text="معرف المحادثة (اختياري)")
    model = serializers.CharField(default='gemini-1.5-flash', help_text="نموذج Gemini المراد استخدامه")
    temperature = serializers.FloatField(default=0.7, min_value=0.0, max_value=2.0, help_text="درجة الإبداع")
    max_tokens = serializers.IntegerField(default=1000, min_value=1, max_value=8192, help_text="الحد الأقصى للرموز")


class GeminiChatResponseSerializer(serializers.Serializer):
    """Serializer for Gemini chat responses"""
    response = serializers.CharField(help_text="رد Gemini")
    conversation_id = serializers.UUIDField(help_text="معرف المحادثة")
    tokens_used = serializers.IntegerField(help_text="عدد الرموز المستخدمة")
    model = serializers.CharField(help_text="النموذج المستخدم")