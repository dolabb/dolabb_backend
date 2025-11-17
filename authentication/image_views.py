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
        
        return Response({
            'success': True,
            'message': 'Image uploaded successfully',
            'image_url': absolute_url,
            'filename': unique_filename
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to upload image: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

