"""
Chat views
"""
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from chat.services import ChatService
from authentication.models import User

logger = logging.getLogger(__name__)


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
    """Upload file for chat - uses VPS storage if enabled, otherwise local storage"""
    try:
        if 'file' not in request.FILES:
            return Response({'success': False, 'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        import os
        import uuid
        from django.conf import settings
        
        # Generate unique filename to avoid conflicts
        file_extension = os.path.splitext(file.name)[1] if '.' in file.name else ''
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Read file content as bytes
        file_content = b''
        for chunk in file.chunks():
            file_content += chunk
        
        # Try to upload to VPS if configured, otherwise use local storage
        vps_enabled = getattr(settings, 'VPS_ENABLED', False)
        file_url = None
        storage_type = 'local'
        
        if vps_enabled:
            # Upload to VPS
            try:
                from storage.vps_helper import upload_file_to_vps
                success, result = upload_file_to_vps(
                    file_content,
                    'uploads/chat',
                    unique_filename
                )
                
                if success:
                    file_url = result
                    storage_type = 'vps'
                    logger.info(f"Chat file successfully uploaded to VPS: {file_url}")
                else:
                    # VPS upload failed, fallback to local storage
                    logger.warning(f"VPS upload failed for chat file: {result}. Falling back to local storage.")
                    vps_enabled = False  # Force local storage fallback
            except Exception as e:
                logger.error(f"Error uploading chat file to VPS: {str(e)}. Falling back to local storage.")
                vps_enabled = False  # Force local storage fallback
        
        # Fallback to local storage if VPS is disabled or upload failed
        if not vps_enabled or not file_url:
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'chat')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, 'wb+') as destination:
                destination.write(file_content)
            
            file_url = f"{settings.MEDIA_URL}chat/{unique_filename}"
            storage_type = 'local'
            logger.info(f"Chat file saved to local storage: {file_url}")
        
        return Response({
            'success': True,
            'fileUrl': file_url,
            'storageType': storage_type
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error uploading chat file: {str(e)}", exc_info=True)
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

