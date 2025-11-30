"""
URL configuration for dolabb_backend project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from authentication.image_views import serve_media_file

def api_root(request):
    """Root endpoint showing API information"""
    return JsonResponse({
        'message': 'Dolabb Backend API is running',
        'version': '1.0.0',
        'status': 'active',
        'base_url': 'https://dolabb-backend-2vsj.onrender.com',
        'endpoints': {
            'authentication': '/api/auth/',
            'admin_dashboard': '/api/admin/',
            'products': '/api/products/',
            'chat': '/api/chat/',
            'offers': '/api/offers/',
            'payment': '/api/payments/',
            'user': '/api/user/',
            'seller': '/api/seller/',
            'affiliate': '/api/affiliate/',
            'notifications': '/api/notifications/',
            'admin_panel': '/admin/',
            'websocket_chat': '/ws/chat/{conversation_id}/',
            'websocket_notifications': '/ws/notifications/{user_id}/',
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/admin/', include('admin_dashboard.urls')),
    path('api/products/', include('products.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/offers/', include('products.offer_urls')),
    path('api/payment/', include('payments.urls')),  # Keep for backward compatibility
    path('api/payments/', include('payments.urls')),  # Primary route (matches frontend)
    path('api/user/', include('products.user_urls')),
    path('api/seller/', include('products.seller_urls')),
    path('api/affiliate/', include('affiliates.urls')),
    path('api/notifications/', include('notifications.urls')),
]

# Serve media files - works in both development and production
if settings.DEBUG:
    # In development, use Django's static file serving
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, use custom view to serve media files
    urlpatterns += [
        re_path(r'^media/(?P<file_path>.*)$', serve_media_file, name='serve_media'),
    ]

