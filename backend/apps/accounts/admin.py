from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, LearnerProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'language_level', 'first_name', 'last_name', 'is_staff']
    list_filter = ['language_level', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Learning Info', {'fields': ('language_level', 'native_language', 'target_language', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Learning Info', {'fields': ('language_level', 'native_language', 'target_language', 'phone')}),
    )





@admin.register(LearnerProfile)
class LearnerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_conversations', 'total_speaking_time', 'current_streak', 'longest_streak']
    search_fields = ['user__username']
    readonly_fields = ['total_conversations', 'total_speaking_time', 'current_streak', 'longest_streak', 
                      'last_conversation_date']
