"""
Offer URLs
"""
from django.urls import path
from products.offer_views import (
    create_offer, get_offers, accept_offer, reject_offer, counter_offer,
    get_accepted_offers, get_accepted_offer_detail, upload_shipment_proof
)

urlpatterns = [
    path('', get_offers, name='get_offers'),
    path('create/', create_offer, name='create_offer'),
    path('<str:offer_id>/accept/', accept_offer, name='accept_offer'),
    path('<str:offer_id>/reject/', reject_offer, name='reject_offer'),
    path('<str:offer_id>/counter/', counter_offer, name='counter_offer'),
    path('accepted/', get_accepted_offers, name='get_accepted_offers'),
    path('accepted/<str:offer_id>/', get_accepted_offer_detail, name='get_accepted_offer_detail'),
    path('accepted/<str:offer_id>/upload-shipment-proof/', upload_shipment_proof, name='upload_shipment_proof'),
]

