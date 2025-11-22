from django.contrib import admin
from .models import Question, QuestionCategory


@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'category', 'difficulty', 'position_type', 'is_active', 'created_at']
    list_filter = ['difficulty', 'position_type', 'category', 'is_active']
    search_fields = ['text']
    readonly_fields = ['created_at', 'updated_at']
