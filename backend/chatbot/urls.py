from django.urls import path
from .views import ChatHistoryView, ChatInterfaceStreamView, ChatInterfaceView

urlpatterns = [
    path('ask/', ChatInterfaceView.as_view(), name='chatbot-query'),
    path('ask/stream/', ChatInterfaceStreamView.as_view(), name='chatbot-query-stream'),
    path('history/', ChatHistoryView.as_view(), name='chatbot-history'),
]