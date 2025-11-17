"""
Notification views
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from notifications.services import NotificationService
from admin_dashboard.views import check_admin


@api_view(['GET'])
def get_notifications(request):
    """Get user notifications"""
    try:
        user_id = str(request.user.id)
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        is_read = request.GET.get('isRead')
        is_read_bool = None if is_read is None else is_read.lower() == 'true'
        
        notifications, total = NotificationService.get_notifications(user_id, page, limit, is_read_bool)
        
        return Response({
            'success': True,
            'notifications': notifications,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        user_id = str(request.user.id)
        notification = NotificationService.mark_as_read(notification_id, user_id)
        
        return Response({
            'success': True,
            'message': 'Notification marked as read'
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def mark_all_read(request):
    """Mark all notifications as read"""
    try:
        user_id = str(request.user.id)
        NotificationService.mark_all_as_read(user_id)
        
        return Response({
            'success': True,
            'message': 'All notifications marked as read'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_notification(request, notification_id):
    """Delete notification"""
    try:
        user_id = str(request.user.id)
        NotificationService.delete_notification(notification_id, user_id)
        
        return Response({
            'success': True,
            'message': 'Notification deleted'
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def bulk_delete_notifications(request):
    """Bulk delete notifications"""
    try:
        user_id = str(request.user.id)
        notification_ids = request.data.get('notificationIds', [])
        
        NotificationService.bulk_delete_notifications(user_id, notification_ids)
        
        return Response({
            'success': True,
            'message': 'Notifications deleted'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Admin notification management
@api_view(['POST'])
def create_notification(request):
    """Create notification (admin)"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        title = request.data.get('title')
        message = request.data.get('message')
        notification_type = request.data.get('type')
        target_audience = request.data.get('targetAudience')
        admin_id = str(request.user.id)
        scheduled_for = request.data.get('scheduledFor')
        variables = request.data.get('variables', {})
        
        notification = NotificationService.create_notification(
            title, message, notification_type, target_audience, admin_id, scheduled_for, variables
        )
        
        return Response({
            'success': True,
            'notification': {
                'id': str(notification.id),
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'targetAudience': notification.target_audience
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def send_notification(request, notification_id):
    """Send notification (admin)"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        count = NotificationService.send_notification(notification_id)
        
        return Response({
            'success': True,
            'message': f'Notification sent to {count} users'
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_admin_notifications(request):
    """Get admin notifications"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        search = request.GET.get('search')
        notification_type = request.GET.get('type')
        date_from = request.GET.get('dateFrom')
        date_to = request.GET.get('dateTo')
        
        notifications, total = NotificationService.get_admin_notifications(
            page, limit, search, notification_type, date_from, date_to
        )
        
        return Response({
            'success': True,
            'notifications': notifications,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_notification(request, notification_id):
    """Update notification (admin)"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        title = request.data.get('title')
        message = request.data.get('message')
        active = request.data.get('active')
        
        notification = NotificationService.update_notification(notification_id, title, message, active)
        
        return Response({
            'success': True,
            'notification': {
                'id': str(notification.id),
                'title': notification.title,
                'message': notification.message,
                'active': notification.active
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_admin_notification(request, notification_id):
    """Delete admin notification"""
    if not check_admin(request):
        return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        NotificationService.delete_admin_notification(notification_id)
        
        return Response({
            'success': True,
            'message': 'Notification deleted'
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

