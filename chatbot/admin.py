from django.contrib import admin
from .models import ChatSession, ChatMessage, ApiKey


class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'organization', 'session_name', 'created_at')
    search_fields = ('session_name', 'organization__name')  # Searching by organization name
    list_filter = ('organization', 'created_at')  # Filters on the right sidebar
    ordering = ('-created_at',)  # Order by created date descending


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'is_bot', 'created_at', 'api_key', 'organization')
    search_fields = ('sender', 'organization__name', 'message')  # Searching by sender, organization name, or message content
    list_filter = ('is_bot', 'created_at', 'organization')  # Filters for bot messages and organization
    ordering = ('-created_at',)  # Order by created date descending


class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'organization', 'has_expired', 'created_at', 'domain')
    search_fields = ('key', 'organization__name')  # Searching by API key or organization name
    list_filter = ( 'has_expired', 'organization')  # Filters on the right sidebar
    ordering = ('-created_at',)  # Order by created date descending


# Register models and their respective admin classes
admin.site.register(ChatSession, ChatSessionAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(ApiKey, ApiKeyAdmin)