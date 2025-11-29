"""
Chat views
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from chat.services import ChatService
from authentication.models import User


@api_view(['GET'])
def get_conversations(request):
    """Get all conversations"""
    try:
        user_id = str(request.user.id)
        conversations = ChatService.get_conversations(user_id)
        
        return Response({
            'success': True,
            'conversations': conversations
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_messages(request, conversation_id):
    """Get messages for a conversation with pagination
    
    Messages are ordered by createdAt in descending order (newest first).
    Page 1 contains the most recent messages.
    """
    try:
        user_id = str(request.user.id)
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 50))
        
        # Ensure page is at least 1
        if page < 1:
            page = 1
        
        messages, total = ChatService.get_messages(conversation_id, user_id, page, limit)
        
        # Calculate total pages (handle empty conversations)
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        
        # If page exceeds total pages, return empty array but with correct pagination metadata
        if page > total_pages and total_pages > 0:
            messages = []
        
        return Response({
            'success': True,
            'messages': messages,
            'pagination': {
                'currentPage': page,
                'totalPages': total_pages,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def send_message(request):
    """Send a message"""
    try:
        sender_id = str(request.user.id)
        receiver_id = request.data.get('receiverId') or request.data.get('userId')
        text = request.data.get('text', '')
        product_id = request.data.get('productId')
        attachments = request.data.get('attachments', [])
        offer_id = request.data.get('offerId')
        
        if not receiver_id:
            return Response({'success': False, 'error': 'Receiver ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        message = ChatService.send_message(sender_id, receiver_id, text, product_id, attachments, offer_id)
        
        return Response({
            'success': True,
            'message': {
                'id': str(message.id),
                'text': message.text,
                'timestamp': message.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def upload_file(request):
    """Upload file for chat"""
    try:
        if 'file' not in request.FILES:
            return Response({'success': False, 'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        # Save file (simplified - should use proper file storage)
        import os
        from django.conf import settings
        
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'chat')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        file_url = f"{settings.MEDIA_URL}chat/{file.name}"
        
        return Response({
            'success': True,
            'fileUrl': file_url
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

