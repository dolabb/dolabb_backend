"""
Image optimization utilities for faster uploads
"""
import io
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def optimize_image(image_bytes, max_width=1920, max_height=1920, quality=85, format='JPEG'):
    """
    Optimize image by resizing and compressing
    
    Args:
        image_bytes: Original image bytes
        max_width: Maximum width (default 1920px)
        max_height: Maximum height (default 1920px)
        quality: JPEG quality 1-100 (default 85)
        format: Output format ('JPEG', 'PNG', 'WEBP')
    
    Returns:
        tuple: (optimized_bytes, original_size, optimized_size, format_used)
    """
    try:
        original_size = len(image_bytes)
        
        # Open image
        image = Image.open(io.BytesIO(image_bytes))
        original_format = image.format
        
        # Convert RGBA to RGB for JPEG
        if format == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image
        elif image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        # Resize if needed (maintain aspect ratio)
        width, height = image.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"Image resized from {width}x{height} to {new_size[0]}x{new_size[1]}")
        
        # Optimize and save
        output = io.BytesIO()
        
        # Use WebP for better compression if supported
        if format == 'WEBP' or (format == 'JPEG' and original_format == 'WEBP'):
            image.save(output, format='WEBP', quality=quality, method=6)
            format_used = 'WEBP'
        elif format == 'PNG' or original_format == 'PNG':
            # PNG optimization
            image.save(output, format='PNG', optimize=True)
            format_used = 'PNG'
        else:
            # JPEG optimization
            image.save(output, format='JPEG', quality=quality, optimize=True, progressive=True)
            format_used = 'JPEG'
        
        optimized_bytes = output.getvalue()
        optimized_size = len(optimized_bytes)
        
        compression_ratio = (1 - optimized_size / original_size) * 100 if original_size > 0 else 0
        
        logger.info(f"Image optimized: {original_size} bytes -> {optimized_size} bytes ({compression_ratio:.1f}% reduction)")
        
        return optimized_bytes, original_size, optimized_size, format_used
        
    except Exception as e:
        logger.error(f"Error optimizing image: {str(e)}", exc_info=True)
        # Return original if optimization fails
        return image_bytes, len(image_bytes), len(image_bytes), None


def should_optimize_image(file_size, content_type):
    """
    Determine if image should be optimized
    
    Args:
        file_size: File size in bytes
        content_type: MIME type
    
    Returns:
        bool: True if should optimize
    """
    # Only optimize images larger than 500KB
    if file_size < 500 * 1024:
        return False
    
    # Only optimize image types
    image_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    return content_type in image_types

