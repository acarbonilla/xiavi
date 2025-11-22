from django.db import models


class VideoResponse(models.Model):
    """
    Video responses for interview questions.
    """
    STATUS_CHOICES = (
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    interview = models.ForeignKey('interviews.Interview', on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE)
    video_file = models.FileField(upload_to='responses/videos/')
    duration = models.IntegerField(default=0, help_text='Duration in seconds')
    file_size = models.BigIntegerField(default=0, help_text='File size in bytes')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_responses'
        verbose_name = 'Video Response'
        verbose_name_plural = 'Video Responses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Response: {self.interview} - {self.question.text[:30]}"


class Transcript(models.Model):
    """
    Transcripts generated from video responses.
    """
    video_response = models.OneToOneField(VideoResponse, on_delete=models.CASCADE, related_name='transcript')
    text = models.TextField()
    confidence = models.FloatField(default=0.0, help_text='Transcription confidence score')
    word_count = models.IntegerField(default=0)
    processing_time = models.FloatField(default=0.0, help_text='Processing time in seconds')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transcripts'
        verbose_name = 'Transcript'
        verbose_name_plural = 'Transcripts'
    
    def __str__(self):
        return f"Transcript: {self.video_response}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate word count
        if self.text:
            self.word_count = len(self.text.split())
        super().save(*args, **kwargs)
