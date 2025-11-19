"""
Image upload views
"""
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from authentication.models import UploadedFile


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_image(request):
    """Upload image - Combined endpoint for all user types"""
    if 'image' not in request.FILES:
        return Response({
            'success': False,
            'error': 'No image file provided. Please use "image" as the field name.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        image_file = request.FILES['image']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return Response({
                'success': False,
                'error': f'Invalid file type. Allowed types: {", ".join(allowed_types)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if image_file.size > max_size:
            return Response({
                'success': False,
                'error': 'File size too large. Maximum size is 10MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'profiles')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        import uuid
        file_extension = os.path.splitext(image_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # Generate absolute URL
        file_url = f"{settings.MEDIA_URL}uploads/profiles/{unique_filename}"
        absolute_url = request.build_absolute_uri(file_url)
        
        # Get user ID if authenticated
        uploaded_by = None
        if hasattr(request, 'user') and request.user and hasattr(request.user, 'id'):
            uploaded_by = str(request.user.id)
        
        # Save file metadata to database
        uploaded_file = UploadedFile(
            filename=unique_filename,
            original_filename=image_file.name,
            file_path=file_path,
            file_url=absolute_url,
            file_size=str(image_file.size),
            content_type=image_file.content_type,
            upload_type='profile',
            uploaded_by=uploaded_by
        )
        uploaded_file.save()
        
        return Response({
            'success': True,
            'message': 'Image uploaded successfully',
            'image_url': absolute_url,
            'filename': unique_filename,
            'file_id': str(uploaded_file.id)
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to upload image: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def serve_media_file(request, file_path):
    """Serve media files in production"""
    try:
        # Normalize the file path to prevent directory traversal attacks
        file_path = os.path.normpath(file_path).lstrip('/\\')
        
        # Construct full file path
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        full_path = os.path.normpath(full_path)
        media_root = os.path.normpath(os.path.abspath(settings.MEDIA_ROOT))
        
        # Security check: ensure the file is within MEDIA_ROOT (prevent directory traversal)
        if not os.path.abspath(full_path).startswith(media_root):
            raise Http404("File not found")
        
        # Check if file exists and is a file (not a directory)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise Http404("File not found")
        
        # Determine content type
        import mimetypes
        content_type, _ = mimetypes.guess_type(full_path)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Return file response (FileResponse handles file closing automatically)
        file_handle = open(full_path, 'rb')
        response = FileResponse(file_handle, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(full_path)}"'
        return response
        
    except (FileNotFoundError, OSError, ValueError):
        raise Http404("File not found")

