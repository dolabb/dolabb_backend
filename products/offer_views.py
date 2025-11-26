"""
Offer views
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from products.services import OfferService, OrderService
from products.models import Offer, Product, Order
from authentication.models import User
from payments.models import Payment
import os
from django.conf import settings
from datetime import datetime


@api_view(['POST'])
def create_offer(request):
    """Create offer with optional shipping details"""
    try:
        buyer_id = str(request.user.id)
        product_id = request.data.get('productId')
        offer_amount = float(request.data.get('offerAmount'))
        shipping_address = request.data.get('shippingAddress', '').strip()
        zip_code = request.data.get('zipCode', '').strip()
        house_number = request.data.get('houseNumber', '').strip()
        
        offer = OfferService.create_offer(
            buyer_id, 
            product_id, 
            offer_amount,
            shipping_address=shipping_address if shipping_address else None,
            zip_code=zip_code if zip_code else None,
            house_number=house_number if house_number else None
        )
        
        return Response({
            'success': True,
            'offer': {
                'id': str(offer.id),
                'productId': str(offer.product_id.id),
                'buyerId': str(offer.buyer_id.id),
                'offerAmount': offer.offer_amount,
                'shippingAddress': offer.shipping_address or '',
                'zipCode': offer.zip_code or '',
                'houseNumber': offer.house_number or '',
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
                'shippingAddress': offer.shipping_address or '',
                'zipCode': offer.zip_code or '',
                'houseNumber': offer.house_number or '',
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


@api_view(['GET'])
def get_accepted_offers(request):
    """Get all accepted offers with payment status and order details"""
    try:
        seller_id = str(request.user.id)
        
        # Get all accepted and paid offers for this seller
        offers = Offer.objects(seller_id=seller_id, status__in=['accepted', 'paid']).order_by('-created_at')
        
        offers_list = []
        for offer in offers:
            # Get product details
            product = Product.objects(id=offer.product_id.id).first()
            
            # Get associated order if exists
            order = Order.objects(offer_id=offer.id).first()
            
            # Get payment details if order exists
            payment_status = 'not_paid'
            payment_id = None
            moyasar_payment_id = None
            order_status = None
            order_id = None
            shipment_proof = None
            
            if order:
                order_id = str(order.id)
                order_status = order.status
                payment_status = order.payment_status
                payment_id = order.payment_id
                shipment_proof = order.shipment_proof
                
                # Get Moyasar payment ID from Payment model
                if payment_id:
                    payment = Payment.objects(moyasar_payment_id=payment_id).first()
                    if payment:
                        moyasar_payment_id = payment.moyasar_payment_id
            
            # Get buyer details
            buyer = User.objects(id=offer.buyer_id.id).first()
            
            offer_data = {
                'id': str(offer.id),
                'product': {
                    'id': str(product.id) if product else '',
                    'title': product.title if product else '',
                    'images': product.images if product else [],
                    'price': float(product.price) if product and product.price else 0.0,
                    'originalPrice': float(product.original_price) if product and product.original_price else 0.0,
                    'currency': product.currency if product else 'SAR'
                },
                'buyer': {
                    'id': str(buyer.id) if buyer else '',
                    'name': offer.buyer_name or (buyer.full_name if buyer else ''),
                    'email': buyer.email if buyer else '',
                    'phone': buyer.phone if buyer else ''
                },
                'offerAmount': float(offer.offer_amount),
                'originalPrice': float(offer.original_price),
                'shippingCost': float(offer.shipping_cost),
                'shippingAddress': offer.shipping_address or '',
                'zipCode': offer.zip_code or '',
                'houseNumber': offer.house_number or '',
                'paymentStatus': payment_status,  # 'pending', 'completed', 'failed', 'not_paid'
                'isPaidOnMoyasar': payment_status == 'completed',
                'moyasarPaymentId': moyasar_payment_id,
                'orderId': order_id,
                'orderStatus': order_status,  # 'pending', 'packed', 'ready', 'shipped', 'delivered', 'cancelled'
                'shipmentProof': shipment_proof,
                'createdAt': offer.created_at.isoformat(),
                'updatedAt': offer.updated_at.isoformat()
            }
            
            offers_list.append(offer_data)
        
        return Response({
            'success': True,
            'offers': offers_list,
            'total': len(offers_list)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_accepted_offer_detail(request, offer_id):
    """Get detailed information about a specific accepted offer"""
    try:
        seller_id = str(request.user.id)
        
        # Get the offer
        offer = Offer.objects(id=offer_id, seller_id=seller_id, status='accepted').first()
        if not offer:
            return Response({
                'success': False,
                'error': 'Offer not found or not accepted'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get product details
        product = Product.objects(id=offer.product_id.id).first()
        
        # Get associated order if exists
        order = Order.objects(offer_id=offer.id).first()
        
        # Get payment details if order exists
        payment_status = 'not_paid'
        payment_id = None
        moyasar_payment_id = None
        order_status = None
        order_id = None
        shipment_proof = None
        tracking_number = None
        order_number = None
        
        if order:
            order_id = str(order.id)
            order_number = order.order_number
            order_status = order.status
            payment_status = order.payment_status
            payment_id = order.payment_id
            shipment_proof = order.shipment_proof
            tracking_number = order.tracking_number
            
            # Get Moyasar payment ID from Payment model
            if payment_id:
                payment = Payment.objects(moyasar_payment_id=payment_id).first()
                if payment:
                    moyasar_payment_id = payment.moyasar_payment_id
        
        # Get buyer details
        buyer = User.objects(id=offer.buyer_id.id).first()
        
        offer_data = {
            'id': str(offer.id),
            'product': {
                'id': str(product.id) if product else '',
                'title': product.title if product else '',
                'description': product.description if product else '',
                'images': product.images if product else [],
                'price': float(product.price) if product and product.price else 0.0,
                'originalPrice': float(product.original_price) if product and product.original_price else 0.0,
                'currency': product.currency if product else 'SAR',
                'category': product.category if product else '',
                'condition': product.condition if product else ''
            },
            'buyer': {
                'id': str(buyer.id) if buyer else '',
                'name': offer.buyer_name or (buyer.full_name if buyer else ''),
                'email': buyer.email if buyer else '',
                'phone': buyer.phone if buyer else '',
                'profileImage': buyer.profile_image if buyer else ''
            },
            'offerAmount': float(offer.offer_amount),
            'originalPrice': float(offer.original_price),
            'shippingCost': float(offer.shipping_cost),
            'shippingAddress': offer.shipping_address or '',
            'zipCode': offer.zip_code or '',
            'houseNumber': offer.house_number or '',
            'paymentStatus': payment_status,  # 'pending', 'completed', 'failed', 'not_paid'
            'isPaidOnMoyasar': payment_status == 'completed',
            'moyasarPaymentId': moyasar_payment_id,
            'order': {
                'id': order_id,
                'orderNumber': order_number,
                'status': order_status,  # 'pending', 'packed', 'ready', 'shipped', 'delivered', 'cancelled'
                'trackingNumber': tracking_number,
                'shipmentProof': shipment_proof
            },
            'createdAt': offer.created_at.isoformat(),
            'updatedAt': offer.updated_at.isoformat()
        }
        
        return Response({
            'success': True,
            'offer': offer_data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def upload_shipment_proof(request, offer_id):
    """Upload shipment proof and update order status to Delivered"""
    try:
        seller_id = str(request.user.id)
        
        # Get the offer (accepted or paid)
        offer = Offer.objects(id=offer_id, seller_id=seller_id, status__in=['accepted', 'paid']).first()
        if not offer:
            return Response({
                'success': False,
                'error': 'Offer not found or not accepted'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get associated order
        order = Order.objects(offer_id=offer.id).first()
        if not order:
            return Response({
                'success': False,
                'error': 'Order not found for this offer'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if payment is completed (offer status should be 'paid' or payment_status should be 'completed')
        if offer.status != 'paid' and order.payment_status != 'completed':
            return Response({
                'success': False,
                'error': 'Payment must be completed before uploading shipment proof'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if shipment proof is provided
        if 'shipmentProof' not in request.FILES and 'shipmentProofUrl' not in request.data:
            return Response({
                'success': False,
                'error': 'Shipment proof image is required. Use "shipmentProof" field for file upload or "shipmentProofUrl" for URL.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        shipment_proof_url = None
        
        # Handle file upload
        if 'shipmentProof' in request.FILES:
            image_file = request.FILES['shipmentProof']
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if image_file.content_type not in allowed_types:
                return Response({
                    'success': False,
                    'error': 'Invalid file type. Only images (JPEG, PNG, GIF, WebP) are allowed.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate unique filename
            import uuid
            file_extension = os.path.splitext(image_file.name)[1]
            unique_filename = f"shipment_{uuid.uuid4().hex[:12]}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{file_extension}"
            
            # Try VPS upload first if enabled
            vps_enabled = getattr(settings, 'VPS_ENABLED', False)
            absolute_url = None
            
            if vps_enabled:
                try:
                    from storage.vps_helper import upload_file_to_vps
                    image_bytes = image_file.read()
                    success, result = upload_file_to_vps(
                        image_bytes,
                        'uploads/shipments',
                        unique_filename
                    )
                    if success:
                        absolute_url = result
                except Exception as e:
                    import logging
                    logging.warning(f"VPS upload failed: {str(e)}")
            
            # Fallback to local storage
            if not absolute_url:
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'shipments')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, unique_filename)
                
                # Save file
                with open(file_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
                
                # Generate URL
                media_url = settings.MEDIA_URL.rstrip('/')
                if not media_url.startswith('/'):
                    media_url = '/' + media_url
                file_url = f"{media_url}/uploads/shipments/{unique_filename}"
                absolute_url = request.build_absolute_uri(file_url)
            
            shipment_proof_url = absolute_url
        
        # Handle URL (if provided directly)
        elif 'shipmentProofUrl' in request.data:
            shipment_proof_url = request.data.get('shipmentProofUrl', '').strip()
            if not shipment_proof_url:
                return Response({
                    'success': False,
                    'error': 'Shipment proof URL cannot be empty'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update order with shipment proof and status
        order.shipment_proof = shipment_proof_url
        order.status = 'delivered'
        order.updated_at = datetime.utcnow()
        order.save()
        
        return Response({
            'success': True,
            'message': 'Shipment proof uploaded and order status updated to Delivered',
            'order': {
                'id': str(order.id),
                'orderNumber': order.order_number,
                'status': order.status,
                'shipmentProof': order.shipment_proof
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

