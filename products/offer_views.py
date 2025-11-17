"""
Offer views
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from products.services import OfferService
from products.models import Offer, Product
from authentication.models import User


@api_view(['POST'])
def create_offer(request):
    """Create offer"""
    try:
        buyer_id = str(request.user.id)
        product_id = request.data.get('productId')
        offer_amount = float(request.data.get('offerAmount'))
        
        offer = OfferService.create_offer(buyer_id, product_id, offer_amount)
        
        return Response({
            'success': True,
            'offer': {
                'id': str(offer.id),
                'productId': str(offer.product_id.id),
                'buyerId': str(offer.buyer_id.id),
                'offerAmount': offer.offer_amount,
                'status': offer.status,
                'createdAt': offer.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_offers(request):
    """Get offers"""
    try:
        user_id = str(request.user.id)
        user_type = 'buyer'  # Default, can be determined from user role
        if hasattr(request.user, 'role') and request.user.role == 'seller':
            user_type = 'seller'
        
        offers = OfferService.get_offers(user_id, user_type)
        
        offers_list = []
        for offer in offers:
            product = Product.objects(id=offer.product_id.id).first()
            offers_list.append({
                'id': str(offer.id),
                'productId': str(offer.product_id.id),
                'productTitle': product.title if product else '',
                'buyerId': str(offer.buyer_id.id),
                'buyerName': offer.buyer_name,
                'sellerId': str(offer.seller_id.id),
                'sellerName': offer.seller_name,
                'offerAmount': offer.offer_amount,
                'originalPrice': offer.original_price,
                'shippingCost': offer.shipping_cost,
                'status': offer.status,
                'expirationDate': offer.expiration_date.isoformat() if offer.expiration_date else None,
                'counterOfferAmount': offer.counter_offer_amount,
                'createdAt': offer.created_at.isoformat()
            })
        
        return Response({
            'success': True,
            'offers': offers_list
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def accept_offer(request, offer_id):
    """Accept offer"""
    try:
        seller_id = str(request.user.id)
        offer = OfferService.accept_offer(offer_id, seller_id)
        
        return Response({
            'success': True,
            'offer': {
                'id': str(offer.id),
                'status': offer.status
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def reject_offer(request, offer_id):
    """Reject offer"""
    try:
        seller_id = str(request.user.id)
        offer = OfferService.reject_offer(offer_id, seller_id)
        
        return Response({
            'success': True,
            'offer': {
                'id': str(offer.id),
                'status': offer.status
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def counter_offer(request, offer_id):
    """Counter offer"""
    try:
        seller_id = str(request.user.id)
        counter_amount = float(request.data.get('counterAmount'))
        
        offer = OfferService.counter_offer(offer_id, seller_id, counter_amount)
        
        return Response({
            'success': True,
            'offer': {
                'id': str(offer.id),
                'status': offer.status,
                'counterOfferAmount': offer.counter_offer_amount
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

