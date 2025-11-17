"""
Offer URLs
"""
from django.urls import path
from products.offer_views import (
    create_offer, get_offers, accept_offer, reject_offer, counter_offer
)

urlpatterns = [
    path('', get_offers, name='get_offers'),
    path('create/', create_offer, name='create_offer'),
    path('<str:offer_id>/accept/', accept_offer, name='accept_offer'),
    path('<str:offer_id>/reject/', reject_offer, name='reject_offer'),
    path('<str:offer_id>/counter/', counter_offer, name='counter_offer'),
]

