"""
Chat URLs
"""
from django.urls import path
from chat import views

urlpatterns = [
    path('conversations/', views.get_conversations, name='get_conversations'),
    path('conversations/<str:conversation_id>/messages/', views.get_messages, name='get_messages'),
    path('unread-status/', views.get_unread_status, name='get_unread_status'),
    path('send/', views.send_message, name='send_message'),
    path('upload/', views.upload_file, name='upload_file'),
]

