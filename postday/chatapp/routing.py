from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Bu yo'l chat.html dagi WebSocket manzili bilan bir xil bo'lishi shart
    # 'conversation_id' qismi URL dan ID ni ajratib olib Consumer ga uzatadi
    re_path(r'ws/chat/(?P<conversation_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]