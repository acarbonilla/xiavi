from django.db import models


class QuestionCategory(models.Model):
    """
    Categories for organizing questions (e.g., Technical, Behavioral, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'question_categories'
        verbose_name = 'Question Category'
        verbose_name_plural = 'Question Categories'
    
    def __str__(self):
        return self.name


class Question(models.Model):
    """
    Question bank for interviews.
    """
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    
    POSITION_TYPE_CHOICES = (
        ('software_engineer', 'Software Engineer'),
        ('data_scientist', 'Data Scientist'),
        ('product_manager', 'Product Manager'),
        ('designer', 'Designer'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('general', 'General'),
    )
    
    text = models.TextField(help_text='The question text')
    category = models.ForeignKey(QuestionCategory, on_delete=models.SET_NULL, null=True, related_name='questions')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    position_type = models.CharField(max_length=50, choices=POSITION_TYPE_CHOICES, default='general')
    time_limit = models.IntegerField(default=120, help_text='Time limit in seconds')
    audio_file = models.FileField(upload_to='question_audio/', blank=True, null=True, help_text='TTS generated audio')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='created_questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_position_type_display()} - {self.text[:50]}..."
