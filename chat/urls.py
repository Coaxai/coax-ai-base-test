from django.urls import path
from .views import ChatAPIView, ChatHistoryAPIView

urlpatterns = [
    # path('', ChatAPIView.as_view(), name='chat'),  # POST /api/chat/
    path('send/', ChatAPIView.as_view(), name='chat-send'),
    path('history/',ChatHistoryAPIView.as_view(), name='chat-history' )
]
