"""
WebSocket routing for chat
"""
from django.urls import re_path
from chat import consumers

websocket_urlpatterns = [
    # Match any alphanumeric conversation ID (MongoDB ObjectIds are 24 hex chars, but keep flexible)
    re_path(r'ws/chat/(?P<conversation_id>[\w-]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/notifications/(?P<user_id>[\w-]+)/$', consumers.NotificationConsumer.as_asgi()),
]

