"""
User-specific product views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from products.services import ProductService, OfferService, OrderService, ReviewService
from products.models import Product, Order, Offer, Review, SavedProduct
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
                'currency': product.currency if hasattr(product, 'currency') and product.currency else 'SAR',
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
            
            order_data = {
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
                'paymentStatus': order.payment_status,  # 'pending', 'completed', 'failed'
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
                'trackingNumber': order.tracking_number or '',
                'reviewSubmitted': order.review_submitted if hasattr(order, 'review_submitted') else False
            }
            
            # Add seller payout information for sellers
            if user_type == 'seller':
                order_data['platformFee'] = order.dolabb_fee
                order_data['sellerPayout'] = order.seller_payout
                order_data['affiliateCode'] = order.affiliate_code or ''
                order_data['paymentId'] = order.payment_id or ''
                order_data['shipmentProof'] = order.shipment_proof if hasattr(order, 'shipment_proof') and order.shipment_proof else None
            
            orders_list.append(order_data)
        
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
def update_order_status(request, order_id):
    """
    Update order status (seller action)
    Allows seller to update order status to: 'packed', 'ready', 'shipped', 'delivered', 'cancelled'
    """
    try:
        from django.conf import settings
        import os
        import uuid
        from datetime import datetime
        
        seller_id = str(request.user.id)
        new_status = request.data.get('status', '').strip().lower()
        tracking_number = request.data.get('trackingNumber', '')
        shipment_proof_url = None
        
        # Validate status
        allowed_statuses = ['pending', 'packed', 'ready', 'shipped', 'delivered', 'cancelled']
        if not new_status or new_status not in allowed_statuses:
            return Response({
                'success': False,
                'error': f'Invalid status. Allowed values: {", ".join(allowed_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle shipment proof upload (file or URL) - required for 'delivered' status
        if new_status == 'delivered':
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
                        'error': 'Shipment proof is required for delivered status. Provide shipmentProof (file) or shipmentProofUrl.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'success': False,
                    'error': 'Shipment proof is required for delivered status. Provide shipmentProof (file) or shipmentProofUrl.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update order status
        order = OrderService.update_order_status(
            order_id, 
            seller_id, 
            new_status, 
            tracking_number=tracking_number if tracking_number else None,
            shipment_proof=shipment_proof_url
        )
        
        # Send notifications based on status
        try:
            from notifications.notification_helper import NotificationHelper
            if new_status == 'delivered':
                # Notify buyer - item delivered
                NotificationHelper.send_item_delivered(str(order.buyer_id.id))
                # Notify buyer - review your purchase
                NotificationHelper.send_review_your_purchase(str(order.buyer_id.id))
            elif new_status == 'shipped':
                # Notify buyer - seller shipped item
                NotificationHelper.send_seller_shipped_item(str(order.buyer_id.id))
            elif new_status == 'cancelled':
                # Notify buyer - order canceled
                NotificationHelper.send_order_canceled(str(order.buyer_id.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending status change notifications: {str(e)}")
        
        response_data = {
            'success': True,
            'order': {
                'id': str(order.id),
                'status': order.status,
                'trackingNumber': order.tracking_number if order.tracking_number else None
            },
            'message': f'Order status updated to {new_status}'
        }
        
        if shipment_proof_url:
            response_data['order']['shipmentProof'] = order.shipment_proof
            response_data['message'] = 'Order marked as delivered with shipment proof. Earnings are now available for payout.'
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def ship_order(request, order_id):
    """
    Ship order (seller action)
    Accepts tracking number and optional shipment proof.
    Shipment proof is required for earnings to be available for payout.
    """
    try:
        from django.conf import settings
        import os
        import uuid
        from datetime import datetime
        
        seller_id = str(request.user.id)
        tracking_number = request.data.get('trackingNumber', '')
        shipment_proof_url = None
        
        # Handle shipment proof upload (file or URL)
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
        
        # Update order status: 'delivered' if shipment proof provided, 'shipped' otherwise
        order_status = 'delivered' if shipment_proof_url else 'shipped'
        
        # Update order status with tracking number and shipment proof
        order = OrderService.update_order_status(
            order_id, 
            seller_id, 
            order_status, 
            tracking_number=tracking_number if tracking_number else None,
            shipment_proof=shipment_proof_url
        )
        
        # Send notifications
        try:
            from notifications.notification_helper import NotificationHelper
            if order_status == 'delivered':
                # Notify buyer - item delivered
                NotificationHelper.send_item_delivered(str(order.buyer_id.id))
                # Notify buyer - review your purchase
                NotificationHelper.send_review_your_purchase(str(order.buyer_id.id))
            else:
                # Notify buyer - seller shipped item
                NotificationHelper.send_seller_shipped_item(str(order.buyer_id.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending shipping notifications: {str(e)}")
        
        response_data = {
            'success': True,
            'payment': {
                'id': str(order.id),
                'status': order.status,
                'trackingNumber': order.tracking_number
            }
        }
        
        if shipment_proof_url:
            response_data['payment']['shipmentProof'] = order.shipment_proof
            response_data['message'] = 'Order marked as delivered with shipment proof. Earnings are now available for payout.'
        else:
            response_data['message'] = 'Order shipped. Upload shipment proof to mark as delivered and make earnings available for payout.'
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    """Create a review for a delivered order (buyer action)"""
    try:
        buyer_id = str(request.user.id)
        order_id = request.data.get('orderId')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        if not order_id:
            return Response({'success': False, 'error': 'Order ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not rating:
            return Response({'success': False, 'error': 'Rating is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return Response({'success': False, 'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        
        review = ReviewService.create_review(order_id, buyer_id, rating, comment)
        
        return Response({
            'success': True,
            'message': 'Review submitted successfully',
            'review': {
                'id': str(review.id),
                'orderId': str(review.order_id.id),
                'rating': review.rating,
                'comment': review.comment,
                'createdAt': review.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_product_reviews(request, product_id):
    """Get reviews for a product"""
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        
        reviews, total = ReviewService.get_reviews_for_product(product_id, page, limit)
        
        reviews_list = []
        for review in reviews:
            buyer = User.objects(id=review.buyer_id.id).first()
            reviews_list.append({
                'id': str(review.id),
                'buyer': {
                    'id': str(buyer.id) if buyer else '',
                    'username': buyer.username if buyer else '',
                    'profileImage': buyer.profile_image if buyer else ''
                },
                'rating': review.rating,
                'comment': review.comment,
                'createdAt': review.created_at.isoformat()
            })
        
        return Response({
            'success': True,
            'reviews': reviews_list,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_seller_rating(request, seller_id):
    """Get seller rating statistics (public endpoint)"""
    try:
        stats = ReviewService.get_seller_rating_stats(seller_id)
        
        return Response({
            'success': True,
            'rating': stats
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_seller_reviews(request, seller_id):
    """Get reviews/comments for a seller"""
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        
        reviews, total = ReviewService.get_reviews_for_seller(seller_id, page, limit)
        
        reviews_list = []
        for review in reviews:
            buyer = User.objects(id=review.buyer_id.id).first()
            product = Product.objects(id=review.product_id.id).first()
            
            reviews_list.append({
                'id': str(review.id),
                'orderId': str(review.order_id.id),
                'orderNumber': review.order_id.order_number if hasattr(review.order_id, 'order_number') else '',
                'buyer': {
                    'id': str(buyer.id) if buyer else '',
                    'username': buyer.username if buyer else '',
                    'fullName': buyer.full_name if buyer else '',
                    'profileImage': buyer.profile_image if buyer else ''
                },
                'product': {
                    'id': str(product.id) if product else '',
                    'title': review.product_title or (product.title if product else ''),
                    'image': product.images[0] if product and product.images else ''
                },
                'rating': review.rating,
                'comment': review.comment,
                'createdAt': review.created_at.isoformat()
            })
        
        return Response({
            'success': True,
            'reviews': reviews_list,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit if total > 0 else 0,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_products_by_seller(request, seller_id):
    """Get products by a specific seller ID (public endpoint)"""
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status')  # Optional status filter
        
        products, total = ProductService.get_seller_products(seller_id, status_filter, page, limit)
        
        # Get user_id for checking saved status (if authenticated)
        user_id = None
        if hasattr(request.user, 'id') and request.user.id:
            try:
                user_id = str(request.user.id)
            except:
                user_id = None
        
        products_list = []
        for product in products:
            # Check if product is saved by the current user (if authenticated)
            is_saved = False
            if user_id and user_id != 'None' and user_id.strip():
                try:
                    from bson import ObjectId
                    user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
                    saved = SavedProduct.objects(user_id=user_obj_id, product_id=product.id).first()
                    is_saved = saved is not None
                except:
                    is_saved = False
            
            # Get seller info
            seller = None
            seller_rating = 0
            total_sales = 0
            if product.seller_id:
                try:
                    seller = User.objects(id=product.seller_id.id).first()
                    if seller:
                        try:
                            rating_stats = ReviewService.get_seller_rating_stats(str(seller.id))
                            seller_rating = rating_stats.get('average_rating', 0)
                        except:
                            seller_rating = 0
                except:
                    seller = None
            
            products_list.append({
                'id': str(product.id),
                'title': product.title,
                'description': product.description or '',
                'price': product.price,
                'originalPrice': product.original_price or product.price,
                'currency': product.currency if hasattr(product, 'currency') and product.currency else 'SAR',
                'images': product.images or [],
                'category': product.category,
                'subcategory': product.subcategory or '',
                'brand': product.brand or '',
                'size': product.size or '',
                'color': product.color or '',
                'condition': product.condition,
                'status': product.status,
                'approved': product.approved,
                'quantity': product.quantity,
                'isSaved': is_saved,
                'seller': {
                    'id': str(seller.id) if seller else '',
                    'username': seller.username if seller else '',
                    'fullName': seller.full_name if seller else '',
                    'profileImage': seller.profile_image if seller else '',
                    'rating': seller_rating
                },
                'createdAt': product.created_at.isoformat() if product.created_at else None,
                'updatedAt': product.updated_at.isoformat() if product.updated_at else None
            })
        
        return Response({
            'success': True,
            'products': products_list,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit if total > 0 else 0,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_dispute(request):
    """Create a dispute/report about a seller (buyer action)"""
    try:
        from admin_dashboard.services import DisputeService
        
        buyer_id = str(request.user.id)
        order_id = request.data.get('orderId')
        dispute_type = request.data.get('disputeType')
        description = request.data.get('description', '')
        
        if not order_id:
            return Response({'success': False, 'error': 'Order ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not dispute_type:
            return Response({'success': False, 'error': 'Dispute type is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if dispute_type not in ['product_quality', 'delivery_issue', 'payment_dispute']:
            return Response({'success': False, 'error': 'Invalid dispute type'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not description:
            return Response({'success': False, 'error': 'Description is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        dispute = DisputeService.create_dispute(buyer_id, order_id, dispute_type, description)
        
        return Response({
            'success': True,
            'message': 'Dispute/report submitted successfully. Admin will review it.',
            'dispute': {
                'id': str(dispute.id),
                'caseNumber': dispute.case_number,
                'type': dispute.dispute_type,
                'status': dispute.status,
                'createdAt': dispute.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_disputes(request):
    """Get buyer's own disputes"""
    try:
        from admin_dashboard.services import DisputeService
        
        buyer_id = str(request.user.id)
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status')  # Optional: 'open', 'resolved', 'closed'
        
        disputes, total = DisputeService.get_buyer_disputes(buyer_id, page, limit, status_filter)
        
        return Response({
            'success': True,
            'disputes': disputes,
            'pagination': {
                'currentPage': page,
                'totalPages': (total + limit - 1) // limit,
                'totalItems': total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_dispute_details(request, dispute_id):
    """Get buyer's dispute details"""
    try:
        from admin_dashboard.services import DisputeService
        
        buyer_id = str(request.user.id)
        dispute_details = DisputeService.get_dispute_details(dispute_id, buyer_id, 'buyer')
        
        return Response({
            'success': True,
            'dispute': dispute_details
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_dispute_comment(request, dispute_id):
    """Add a comment to dispute (buyer action)"""
    try:
        from admin_dashboard.services import DisputeService
        from authentication.models import User
        
        buyer_id = str(request.user.id)
        message = request.data.get('message', '').strip()
        
        if not message:
            return Response({'success': False, 'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        buyer = User.objects(id=buyer_id).first()
        buyer_name = buyer.full_name or buyer.username if buyer else 'Buyer'
        
        comment = DisputeService.add_dispute_comment(
            dispute_id=dispute_id,
            message=message,
            sender_id=buyer_id,
            sender_type='buyer',
            sender_name=buyer_name
        )
        
        return Response({
            'success': True,
            'message': 'Comment added successfully',
            'comment': comment
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
