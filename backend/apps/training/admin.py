from django.contrib import admin
from .models import TrainingSession, TrainingFeedback


class TrainingFeedbackInline(admin.TabularInline):
    model = TrainingFeedback
    extra = 0


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'question', 'status', 'created_at', 'completed_at']
    list_filter = ['status']
    search_fields = ['applicant__username']
    readonly_fields = ['created_at', 'completed_at']
    inlines = [TrainingFeedbackInline]


@admin.register(TrainingFeedback)
class TrainingFeedbackAdmin(admin.ModelAdmin):
    list_display = ['session', 'score', 'created_at']
    search_fields = ['feedback']
    readonly_fields = ['created_at']
