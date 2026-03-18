from django.urls import path
from .views import InboxView, ChatView, SendMessageView, StartChatView

app_name = "chat"

urlpatterns = [
    path("inbox/", InboxView.as_view(), name="inbox"),
    path("chat/<int:pk>/", ChatView.as_view(), name="chat"),
    path("send/<int:pk>/", SendMessageView.as_view(), name="send"),
    path("start/<str:username>/", StartChatView.as_view(), name="start"),
]