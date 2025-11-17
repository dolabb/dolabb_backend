"""
Notification URLs
"""
from django.urls import path
from notifications import views

urlpatterns = [
    # User notifications
    path('', views.get_notifications, name='get_notifications'),
    path('<str:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('<str:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('bulk-delete/', views.bulk_delete_notifications, name='bulk_delete_notifications'),
    
    # Admin notifications
    path('admin/create/', views.create_notification, name='create_notification'),
    path('admin/<str:notification_id>/send/', views.send_notification, name='send_notification'),
    path('admin/list/', views.get_admin_notifications, name='get_admin_notifications'),
    path('admin/<str:notification_id>/update/', views.update_notification, name='update_notification'),
    path('admin/<str:notification_id>/delete/', views.delete_admin_notification, name='delete_admin_notification'),
]

