from django.urls import path
from .api_views import (
    InboxAPIView,
    ConversationMessagesAPIView,
    StartChatAPIView,
    DeleteMessageAPIView,
)

urlpatterns = [
    path("inbox/", InboxAPIView.as_view(), name="api-chat-inbox"),
    path("<int:pk>/messages/", ConversationMessagesAPIView.as_view(), name="api-chat-messages"),
    path("start/<str:username>/", StartChatAPIView.as_view(), name="api-chat-start"),
    path("message/<int:pk>/", DeleteMessageAPIView.as_view(), name="api-chat-delete-message"),
]