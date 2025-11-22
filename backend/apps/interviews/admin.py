from django.contrib import admin
from .models import Interview, InterviewQuestion


class InterviewQuestionInline(admin.TabularInline):
    model = InterviewQuestion
    extra = 1


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'position_title', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'position_type']
    search_fields = ['applicant__username', 'position_title']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']
    inlines = [InterviewQuestionInline]
