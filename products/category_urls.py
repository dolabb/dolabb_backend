"""
Category URLs for public category API endpoints
"""
from django.urls import path
from products.category_views import (
    get_all_categories,
    get_category_details,
    get_category_filters
)

urlpatterns = [
    path('', get_all_categories, name='get_all_categories'),
    path('<str:category_key>/', get_category_details, name='get_category_details'),
    path('<str:category_key>/filters/', get_category_filters, name='get_category_filters'),
]

