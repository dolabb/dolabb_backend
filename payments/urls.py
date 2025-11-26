"""
Payment URLs
"""
from django.urls import path
from payments import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('process/', views.process_payment, name='process_payment'),
    path('webhook/', views.payment_webhook, name='payment_webhook'),
    path('verify/', views.verify_payment, name='verify_payment'),
]

