"""
User-specific product views
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from products.services import ProductService, OfferService, OrderService
from products.models import Product, Order, Offer
from authentication.models import User


@api_view(['GET'])
def get_user_products(request):
    """Get user's own products (for seller)"""
    try:
        seller_id = str(request.user.id)
        status_filter = request.GET.get('status')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        
        products, total = ProductService.get_seller_products(seller_id, status_filter, page, limit)
        
        products_list = []
        for product in products:
            products_list.append({
                'id': str(product.id),
                'title': product.title,
                'description': product.description,
                'price': product.price,
                'images': product.images,
                'status': product.status,
                'createdAt': product.created_at.isoformat()
            })
        
        return Response({
            'products': products_list,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_user_orders(request):
    """Get user orders (buyer or seller)"""
    try:
        user_id = str(request.user.id)
        user_type = 'buyer'
        if hasattr(request.user, 'role') and request.user.role == 'seller':
            user_type = 'seller'
        
        status_filter = request.GET.get('status')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        
        orders, total = OrderService.get_user_orders(user_id, user_type, status_filter, page, limit)
        
        orders_list = []
        for order in orders:
            product = Product.objects(id=order.product_id.id).first()
            if user_type == 'buyer':
                seller = User.objects(id=order.seller_id.id).first()
                other_user = {
                    'id': str(seller.id) if seller else '',
                    'username': seller.username if seller else '',
                    'profileImage': seller.profile_image if seller else ''
                }
            else:
                buyer = User.objects(id=order.buyer_id.id).first()
                other_user = {
                    'id': str(buyer.id) if buyer else '',
                    'username': buyer.username if buyer else '',
                    'profileImage': buyer.profile_image if buyer else ''
                }
            
            orders_list.append({
                'id': str(order.id),
                'orderNumber': order.order_number,
                'product': {
                    'id': str(product.id) if product else '',
                    'title': product.title if product else order.product_title,
                    'images': product.images if product else []
                },
                'buyer' if user_type == 'seller' else 'seller': other_user,
                'orderDate': order.created_at.isoformat(),
                'status': order.status,
                'totalPrice': order.total_price,
                'shippingAddress': {
                    'fullName': order.full_name,
                    'phone': order.phone,
                    'address': order.delivery_address,
                    'city': order.city,
                    'postalCode': order.postal_code,
                    'country': order.country,
                    'additionalInfo': order.additional_info
                },
                'trackingNumber': order.tracking_number or ''
            })
        
        return Response({
            'payments' if user_type == 'seller' else 'orders': orders_list,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_user_offers(request):
    """Get user offers"""
    try:
        user_id = str(request.user.id)
        user_type = 'buyer'
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
                'offerAmount': offer.offer_amount,
                'originalPrice': offer.original_price,
                'status': offer.status,
                'createdAt': offer.created_at.isoformat()
            })
        
        return Response({
            'success': True,
            'offers': offers_list
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def ship_order(request, order_id):
    """Ship order (seller action)"""
    try:
        seller_id = str(request.user.id)
        tracking_number = request.data.get('trackingNumber', '')
        
        order = OrderService.update_order_status(order_id, seller_id, 'shipped', tracking_number)
        
        return Response({
            'success': True,
            'payment': {
                'id': str(order.id),
                'status': order.status,
                'trackingNumber': order.tracking_number
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

