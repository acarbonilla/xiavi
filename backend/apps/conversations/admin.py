from django.contrib import admin
from .models import Topic, ConversationSession, ConversationMessage, ConversationFeedback, DocumentUpload, DocumentChunk


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'conversation_count', 'is_active', 'created_at')
    list_filter = ('difficulty', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('difficulty', 'name')


@admin.register(ConversationSession)
class ConversationSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'topic', 'status', 'started_at', 'duration', 'message_count')
    list_filter = ('status', 'started_at', 'topic')
    search_fields = ('user__username', 'user__email', 'topic__name')
    readonly_fields = ('started_at', 'ended_at', 'duration', 'message_count', 'user_message_count', 'total_speaking_time')
    ordering = ('-started_at',)


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'text_preview', 'duration', 'timestamp')
    list_filter = ('role', 'timestamp')
    search_fields = ('text', 'session__user__username')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'


@admin.register(ConversationFeedback)
class ConversationFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'overall_score', 'clarity_score', 'fluency_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('session__user__username', 'feedback_text')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(DocumentUpload)
class DocumentUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'filename', 'file_type', 'session', 'file_size_kb', 'processed', 'chunk_count', 'uploaded_at')
    list_filter = ('file_type', 'processed', 'uploaded_at')
    search_fields = ('filename', 'session__user__username')
    readonly_fields = ('uploaded_at', 'chunk_count')
    ordering = ('-uploaded_at',)
    
    def file_size_kb(self, obj):
        return f"{obj.file_size / 1024:.1f} KB"
    file_size_kb.short_description = 'File Size'


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'chunk_index', 'token_count', 'text_preview')
    list_filter = ('document__file_type',)
    search_fields = ('text', 'document__filename')
    readonly_fields = ('embedding',)
    ordering = ('document', 'chunk_index')
    
    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Text Preview'
