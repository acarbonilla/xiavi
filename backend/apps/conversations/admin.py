from django.contrib import admin
from .models import Topic, ConversationSession, ConversationMessage, ConversationFeedback


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty', 'conversation_count', 'is_active', 'created_at']
    list_filter = ['difficulty', 'is_active']
    search_fields = ['name', 'description']


class ConversationMessageInline(admin.TabularInline):
    model = ConversationMessage
    extra = 0
    readonly_fields = ['role', 'text', 'duration', 'timestamp']


@admin.register(ConversationSession)
class ConversationSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'status', 'message_count', 'duration', 'started_at']
    list_filter = ['status', 'topic']
    search_fields = ['user__username']
    readonly_fields = ['started_at', 'ended_at', 'duration', 'message_count', 
                      'user_message_count', 'total_speaking_time']
    inlines = [ConversationMessageInline]


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'text', 'duration', 'timestamp']
    list_filter = ['role']
    search_fields = ['text']
    readonly_fields = ['timestamp']


@admin.register(ConversationFeedback)
class ConversationFeedbackAdmin(admin.ModelAdmin):
    list_display = ['session', 'overall_score', 'clarity_score', 'fluency_score', 'created_at']
    search_fields = ['feedback_text']
    readonly_fields = ['created_at']
