from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import APIKey, GeminiConversation, GeminiMessage, APIUsageLog, AIProvider, AIConfiguration


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin interface for API Keys"""
    list_display = ['name', 'user', 'is_active', 'created_at', 'last_used', 'expires_at', 'key_preview']
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['key', 'created_at', 'last_used']
    date_hierarchy = 'created_at'

    def key_preview(self, obj):
        """Show a preview of the API key"""
        if obj.key:
            return f"{obj.key[:8]}...{obj.key[-8:]}"
        return "-"
    key_preview.short_description = "مفتاح API (معاينة)"

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user')


class GeminiMessageInline(admin.TabularInline):
    """Inline admin for Gemini messages"""
    model = GeminiMessage
    extra = 0
    readonly_fields = ['timestamp', 'tokens_used']
    fields = ['role', 'content', 'timestamp', 'tokens_used']

    def get_queryset(self, request):
        """Limit messages shown in inline"""
        return super().get_queryset(request).order_by('-timestamp')[:10]


@admin.register(GeminiConversation)
class GeminiConversationAdmin(admin.ModelAdmin):
    """Admin interface for Gemini Conversations"""
    list_display = ['title', 'user', 'is_active', 'created_at', 'updated_at', 'message_count']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'message_count']
    date_hierarchy = 'created_at'
    inlines = [GeminiMessageInline]

    def message_count(self, obj):
        """Count messages in conversation"""
        return obj.messages.count()
    message_count.short_description = "عدد الرسائل"

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user').prefetch_related('messages')


@admin.register(GeminiMessage)
class GeminiMessageAdmin(admin.ModelAdmin):
    """Admin interface for Gemini Messages"""
    list_display = ['conversation_link', 'role', 'content_preview', 'timestamp', 'tokens_used']
    list_filter = ['role', 'timestamp']
    search_fields = ['content', 'conversation__title']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

    def conversation_link(self, obj):
        """Link to conversation"""
        url = reverse('admin:api_geminiconversation_change', args=[obj.conversation.id])
        return format_html('<a href="{}">{}</a>', url, obj.conversation.title)
    conversation_link.short_description = "المحادثة"

    def content_preview(self, obj):
        """Show content preview"""
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = "محتوى الرسالة"

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('conversation', 'conversation__user')


@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    """Admin interface for API Usage Logs"""
    list_display = ['endpoint', 'method', 'user', 'status_code', 'response_time', 'timestamp', 'ip_address']
    list_filter = ['method', 'status_code', 'timestamp']
    search_fields = ['endpoint', 'user__username', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user', 'api_key')

    def has_add_permission(self, request):
        """Disable adding logs manually"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing logs"""
        return False


@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    """Admin interface for AI Providers"""
    list_display = ['display_name', 'name', 'is_active', 'requires_api_key', 'created_at']
    list_filter = ['is_active', 'requires_api_key', 'name']
    search_fields = ['display_name', 'name', 'description']
    readonly_fields = ['created_at']

    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('إعدادات تقنية', {
            'fields': ('api_endpoint', 'requires_api_key', 'is_active')
        }),
        ('معلومات النظام', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(AIConfiguration)
class AIConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for AI Configurations"""
    list_display = ['user', 'provider', 'model_name', 'is_default', 'is_active', 'created_at']
    list_filter = ['provider', 'is_default', 'is_active', 'created_at']
    search_fields = ['user__username', 'provider__display_name', 'model_name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('user', 'provider')
        }),
        ('إعدادات النموذج', {
            'fields': ('model_name', 'api_key', 'max_tokens', 'temperature')
        }),
        ('حالة الإعداد', {
            'fields': ('is_default', 'is_active')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user', 'provider')

    def save_model(self, request, obj, form, change):
        """Handle default configuration logic"""
        # إذا كان هذا الإعداد افتراضي، قم بإلغاء الافتراضي من الآخرين
        if obj.is_default:
            AIConfiguration.objects.filter(
                user=obj.user,
                is_default=True
            ).exclude(id=obj.id).update(is_default=False)
        super().save_model(request, obj, form, change)
