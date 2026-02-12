from rest_framework import serializers
from .models import Document, ChatSession, Message

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'source_type', 'file', 'url', 'uploaded_at', 'is_processed']
        read_only_fields = ['source_type', 'url', 'uploaded_at', 'is_processed']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['sender', 'content', 'timestamp']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = ChatSession
        fields = ['id', 'user', 'created_at', 'messages']