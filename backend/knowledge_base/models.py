from django.db import models
from django.conf import settings

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='knowledge_base/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    source_type = models.CharField(max_length=10, default='pdf')
    url = models.URLField(max_length=500, null=True, blank=True)

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('ai', 'AI')])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)