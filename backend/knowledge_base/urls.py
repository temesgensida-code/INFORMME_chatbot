from django.urls import path
from .views import (
    DocumentUploadView,
    ChatView,
    WebsiteLinkView,
    AdminDocumentListView,
    AdminDocumentDeleteView,
    AdminContextRefreshView,
)

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('website-link/', WebsiteLinkView.as_view(), name='website-link-upload'),
    path('chat/', ChatView.as_view(), name='chat-query'),
    path('admin/documents/', AdminDocumentListView.as_view(), name='admin-document-list'),
    path('admin/documents/<int:document_id>/', AdminDocumentDeleteView.as_view(), name='admin-document-delete'),
    path('admin/refresh-context/', AdminContextRefreshView.as_view(), name='admin-refresh-context'),
    # Add paths for chat history and document listing...
]