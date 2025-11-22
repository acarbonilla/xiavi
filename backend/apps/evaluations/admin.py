from django.contrib import admin
from .models import Evaluation, QuestionEvaluation


class QuestionEvaluationInline(admin.TabularInline):
    model = QuestionEvaluation
    extra = 0


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['interview', 'overall_score', 'communication_score', 'content_score', 'created_at']
    search_fields = ['interview__applicant__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [QuestionEvaluationInline]


@admin.register(QuestionEvaluation)
class QuestionEvaluationAdmin(admin.ModelAdmin):
    list_display = ['video_response', 'score', 'created_at']
    search_fields = ['feedback']
    readonly_fields = ['created_at']
