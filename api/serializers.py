from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import APIKey, GeminiConversation, GeminiMessage, APIUsageLog

# Import models from other apps
from Hr.models.employee_model import Employee
from Hr.models.department_models import Department
from inventory.models import TblProducts, TblCategories, TblSuppliers
from tasks.models import Task
from meetings.models import Meeting

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API Key model"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = APIKey
        fields = ['id', 'user', 'name', 'key', 'is_active', 'created_at', 'last_used', 'expires_at']
        read_only_fields = ['id', 'key', 'created_at', 'last_used']


class GeminiMessageSerializer(serializers.ModelSerializer):
    """Serializer for Gemini Message model"""
    class Meta:
        model = GeminiMessage
        fields = ['id', 'role', 'content', 'timestamp', 'tokens_used']
        read_only_fields = ['id', 'timestamp', 'tokens_used']


class GeminiConversationSerializer(serializers.ModelSerializer):
    """Serializer for Gemini Conversation model"""
    messages = GeminiMessageSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = GeminiConversation
        fields = ['id', 'user', 'title', 'created_at', 'updated_at', 'is_active', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']


class APIUsageLogSerializer(serializers.ModelSerializer):
    """Serializer for API Usage Log model"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = APIUsageLog
        fields = ['id', 'user', 'endpoint', 'method', 'status_code', 'response_time', 'timestamp', 'ip_address']
        read_only_fields = ['id', 'timestamp']


# HR Serializers
class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    class Meta:
        model = Department
        fields = ['id', 'dept_name', 'dept_description', 'dept_manager', 'created_at']


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model"""
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'emp_name', 'emp_email', 'emp_phone', 'emp_position',
            'department', 'emp_hire_date', 'emp_salary', 'emp_status'
        ]


# Inventory Serializers
class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    class Meta:
        model = TblCategories
        fields = ['cat_id', 'cat_name']


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model"""
    class Meta:
        model = TblSuppliers
        fields = ['supplier_id', 'supplier_name']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    category = CategorySerializer(source='cat', read_only=True)

    class Meta:
        model = TblProducts
        fields = [
            'product_id', 'product_name', 'initial_balance', 'elwarad',
            'elmonsarf', 'qte_in_stock', 'category', 'unit_price',
            'minimum_threshold', 'maximum_threshold', 'location'
        ]


# Task Serializers
class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'created_by',
            'priority', 'status', 'due_date', 'created_at', 'updated_at'
        ]


# Meeting Serializers
class MeetingSerializer(serializers.ModelSerializer):
    """Serializer for Meeting model"""
    organizer = UserSerializer(read_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'description', 'organizer', 'date_time',
            'duration', 'location', 'status', 'created_at'
        ]


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


class GeminiAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for Gemini data analysis requests"""
    data_type = serializers.ChoiceField(
        choices=[
            ('employees', 'الموظفين'),
            ('inventory', 'المخزون'),
            ('tasks', 'المهام'),
            ('meetings', 'الاجتماعات'),
        ],
        help_text="نوع البيانات المراد تحليلها"
    )
    analysis_type = serializers.ChoiceField(
        choices=[
            ('summary', 'ملخص'),
            ('trends', 'الاتجاهات'),
            ('insights', 'الرؤى'),
            ('recommendations', 'التوصيات'),
        ],
        help_text="نوع التحليل المطلوب"
    )
    filters = serializers.JSONField(required=False, help_text="مرشحات إضافية")


class GeminiAnalysisResponseSerializer(serializers.Serializer):
    """Serializer for Gemini data analysis responses"""
    analysis = serializers.CharField(help_text="نتيجة التحليل")
    data_summary = serializers.JSONField(help_text="ملخص البيانات")
    insights = serializers.ListField(child=serializers.CharField(), help_text="الرؤى المستخرجة")
    recommendations = serializers.ListField(child=serializers.CharField(), help_text="التوصيات")
