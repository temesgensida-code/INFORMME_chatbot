from django.urls import path
from .views import DocumentUploadView, ChatView, WebsiteLinkView

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('website-link/', WebsiteLinkView.as_view(), name='website-link-upload'),
    path('chat/', ChatView.as_view(), name='chat-query'),
    # Add paths for chat history and document listing...
]