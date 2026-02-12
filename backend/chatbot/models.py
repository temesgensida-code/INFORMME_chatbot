from django.conf import settings
from django.db import models

class Document(models.Model):
    SOURCE_TYPES = (
        ('pdf', 'PDF File'),
        ('url', 'Website Link'),
    )
    title = models.CharField(max_length=255)
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPES)
    file = models.FileField(upload_to='knowledge_base/', null=True, blank=True)
    url = models.URLField(max_length=500, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat with {self.user.email} - {self.id}"

class Message(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('ai', 'AI'),
    )
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']