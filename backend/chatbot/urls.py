from django.urls import path
from .views import ChatInterfaceView

urlpatterns = [
    path('ask/', ChatInterfaceView.as_view(), name='chatbot-query'),
    # You would also add URLs for listing past sessions or clearing history here
]