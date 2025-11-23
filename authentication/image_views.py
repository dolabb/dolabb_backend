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
        
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if image_file.size > max_size:
            return Response({
                'success': False,
                'error': 'File size too large. Maximum size is 5MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type by content type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return Response({
                'success': False,
                'error': f'Invalid file type. Allowed types: JPEG, JPG, PNG, GIF, WEBP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_extension = os.path.splitext(image_file.name.lower())[1]
        if file_extension not in allowed_extensions:
            return Response({
                'success': False,
                'error': f'Invalid file extension. Allowed extensions: {", ".join(allowed_extensions)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate that file is actually an image by reading magic bytes
        # Read first few bytes to check file signature
        image_file.seek(0)
        file_header = image_file.read(12)
        image_file.seek(0)  # Reset file pointer
        
        # Check magic bytes for common image formats
        is_valid_image = False
        if file_header.startswith(b'\xFF\xD8\xFF'):  # JPEG
            is_valid_image = True
        elif file_header.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
            is_valid_image = True
        elif file_header.startswith(b'GIF87a') or file_header.startswith(b'GIF89a'):  # GIF
            is_valid_image = True
        elif file_header.startswith(b'RIFF') and b'WEBP' in file_header:  # WEBP
            is_valid_image = True
        
        if not is_valid_image:
            return Response({
                'success': False,
                'error': 'File is not a valid image. Please upload a valid JPEG, PNG, GIF, or WEBP image.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate unique filename
        import uuid
        file_extension = os.path.splitext(image_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Read file content
        image_bytes = b''
        for chunk in image_file.chunks():
            image_bytes += chunk
        
        # Try to upload to VPS if configured, otherwise use local storage
        vps_enabled = getattr(settings, 'VPS_ENABLED', False)
        absolute_url = None
        
        if vps_enabled:
            # Upload to VPS
            from storage.vps_helper import upload_file_to_vps
            success, result = upload_file_to_vps(
                image_bytes,
                'uploads/profiles',
                unique_filename
            )
            
            if success:
                absolute_url = result
                file_path = f"VPS:uploads/profiles/{unique_filename}"  # For metadata
            else:
                # Fallback to local storage if VPS upload fails
                import logging
                logging.warning(f"VPS upload failed, using local storage: {result}")
                vps_enabled = False
        
        if not vps_enabled:
            # Local storage fallback
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'profiles')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save file
            with open(file_path, 'wb+') as destination:
                destination.write(image_bytes)
            
            # Verify file was saved successfully
            if not os.path.exists(file_path):
                return Response({
                    'success': False,
                    'error': 'Failed to save image file'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Generate absolute URL - ensure consistent format
            media_url = settings.MEDIA_URL.rstrip('/')
            if not media_url.startswith('/'):
                media_url = '/' + media_url
            file_url = f"{media_url}/uploads/profiles/{unique_filename}"
            # Build absolute URL using request's build_absolute_uri for consistency
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
    import logging
    try:
        # Normalize the file path to prevent directory traversal attacks
        file_path = os.path.normpath(file_path).lstrip('/\\')
        
        # Construct full file path
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        full_path = os.path.normpath(full_path)
        media_root = os.path.normpath(os.path.abspath(settings.MEDIA_ROOT))
        
        # Security check: ensure the file is within MEDIA_ROOT (prevent directory traversal)
        if not os.path.abspath(full_path).startswith(media_root):
            logging.warning(f"Security check failed: {full_path} not in {media_root}")
            raise Http404("File not found")
        
        # Check if file exists and is a file (not a directory)
        # First try exact path, then try case-insensitive lookup
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            # Try case-insensitive lookup for the filename
            directory = os.path.dirname(full_path)
            filename = os.path.basename(full_path)
            if os.path.exists(directory):
                # List files in directory and find case-insensitive match
                try:
                    files = os.listdir(directory)
                    for f in files:
                        if f.lower() == filename.lower():
                            full_path = os.path.join(directory, f)
                            break
                    else:
                        logging.warning(f"File not found: {full_path} (directory exists: {directory})")
                        raise Http404("File not found")
                except OSError as e:
                    logging.error(f"Error listing directory {directory}: {str(e)}")
                    raise Http404("File not found")
            else:
                logging.warning(f"Directory does not exist: {directory}")
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
        
    except (FileNotFoundError, OSError, ValueError) as e:
        logging.error(f"Error serving media file {file_path}: {str(e)}")
        raise Http404("File not found")

