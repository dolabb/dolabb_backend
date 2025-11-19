"""
Product URLs
"""
from django.urls import path
from products import views

urlpatterns = [
    path('', views.get_products, name='get_products'),
    path('featured/', views.get_featured_products, name='featured_products'),
    path('trending/', views.get_trending_products, name='trending_products'),
    path('create/', views.create_product, name='create_product'),
    path('seller/', views.get_seller_products, name='seller_products'),
    path('<str:product_id>/update/', views.update_product, name='update_product'),
    path('<str:product_id>/delete/', views.delete_product, name='delete_product'),
    path('<str:product_id>/save/', views.save_product, name='save_product'),
    path('<str:product_id>/unsave/', views.unsave_product, name='unsave_product'),
    path('<str:product_id>/', views.get_product_detail, name='product_detail'),
]

