from django.urls import path
from .views import DocumentUploadView, ChatView

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('chat/', ChatView.as_view(), name='chat-query'),
    # Add paths for chat history and document listing...
]