"""
URL configuration for dolabb_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/admin/', include('admin_dashboard.urls')),
    path('api/products/', include('products.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/offers/', include('products.offer_urls')),
    path('api/payment/', include('payments.urls')),
    path('api/user/', include('products.user_urls')),
    path('api/affiliate/', include('affiliates.urls')),
    path('api/notifications/', include('notifications.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

