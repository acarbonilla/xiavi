from django.contrib import admin
from .models import VideoResponse, Transcript


class TranscriptInline(admin.StackedInline):
    model = Transcript
    extra = 0


@admin.register(VideoResponse)
class VideoResponseAdmin(admin.ModelAdmin):
    list_display = ['interview', 'question', 'status', 'duration', 'created_at']
    list_filter = ['status']
    search_fields = ['interview__applicant__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TranscriptInline]


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ['video_response', 'word_count', 'confidence', 'created_at']
    search_fields = ['text']
    readonly_fields = ['word_count', 'created_at']
