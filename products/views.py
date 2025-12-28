"""
Product views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from products.services import ProductService, OfferService, OrderService, ReviewService
from products.models import Product, SavedProduct, Order
from authentication.models import User


@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):
    """Get products with filters"""
    # Get sortBy and normalize it
    sort_by = request.GET.get('sortBy', 'newly listed')
    # Normalize common variations
    if sort_by:
        sort_by_lower = sort_by.lower().strip()
        if sort_by_lower in ['relevance', 'relevant']:
            sort_by = 'relevance'
        elif sort_by_lower in ['low to high', 'price: low to high', 'price-low-to-high', 'price_asc', 'price_ascending', 'price low to high']:
            sort_by = 'low to high'
        elif sort_by_lower in ['high to low', 'price: high to low', 'price-high-to-low', 'price_desc', 'price_descending', 'price high to low']:
            sort_by = 'high to low'
        elif sort_by_lower in ['newly listed', 'newest', 'new', 'newly-listed']:
            sort_by = 'newly listed'
    
    # Build filters dictionary, removing empty strings
    filters = {}
    if request.GET.get('category'):
        filters['category'] = request.GET.get('category').strip()
    if request.GET.get('subcategory'):
        filters['subcategory'] = request.GET.get('subcategory').strip()
    if request.GET.get('brand'):
        filters['brand'] = request.GET.get('brand').strip()
    if request.GET.get('minPrice'):
        min_price = request.GET.get('minPrice').strip()
        if min_price:
            filters['minPrice'] = min_price
    if request.GET.get('maxPrice'):
        max_price = request.GET.get('maxPrice').strip()
        if max_price:
            filters['maxPrice'] = max_price
    if request.GET.get('size'):
        filters['size'] = request.GET.get('size').strip()
    if request.GET.get('color'):
        filters['color'] = request.GET.get('color').strip()
    if request.GET.get('condition'):
        filters['condition'] = request.GET.get('condition').strip()
    if request.GET.get('search'):
        filters['search'] = request.GET.get('search').strip()
    if request.GET.get('onSale'):
        on_sale = request.GET.get('onSale', '').strip().lower()
        if on_sale in ['true', '1', 'yes']:
            filters['onSale'] = True
    filters['sortBy'] = sort_by
    
    # Check if client wants new format (default to new format for documentation compliance)
    use_new_format = request.GET.get('format', 'new').lower() != 'legacy'
    
    try:
        page = int(request.GET.get('page', 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    
    try:
        limit = int(request.GET.get('limit', 20))
        if limit < 1:
            limit = 20
        if limit > 100:  # Cap at 100 to prevent performance issues
            limit = 100
    except (ValueError, TypeError):
        limit = 20
    
    try:
        user_id = None
        if hasattr(request.user, 'id') and request.user.id:
            try:
                user_id = str(request.user.id)
            except:
                user_id = None
        
        products, total = ProductService.get_products(filters, page, limit, user_id)
        
        products_list = []
        for product in products:
            try:
                is_saved = False
                is_liked = False
                if user_id and user_id != 'None' and user_id.strip():
                    try:
                        from bson import ObjectId
                        user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
                        saved = SavedProduct.objects(user_id=user_obj_id, product_id=product.id).first()
                        is_saved = saved is not None
                    except:
                        is_saved = False
                
                # Handle seller_id safely
                seller = None
                seller_rating = 0
                total_sales = 0
                if product.seller_id:
                    try:
                        # Handle ReferenceField - seller_id might be an ObjectId or a User object
                        from bson import ObjectId
                        seller_obj_id = None
                        if hasattr(product.seller_id, 'id'):
                            seller_obj_id = product.seller_id.id
                        elif isinstance(product.seller_id, ObjectId):
                            seller_obj_id = product.seller_id
                        elif isinstance(product.seller_id, str):
                            seller_obj_id = ObjectId(product.seller_id)
                        else:
                            seller_obj_id = product.seller_id
                        
                        if seller_obj_id:
                            seller = User.objects(id=seller_obj_id).first()
                            if seller:
                                # Get seller rating and total sales
                                try:
                                    from products.services import ReviewService
                                    rating_stats = ReviewService.get_seller_rating_stats(str(seller.id))
                                    seller_rating = rating_stats.get('average_rating', 0)
                                    total_sales = Order.objects(
                                        seller_id=seller.id,
                                        payment_status='completed'
                                    ).count()
                                except:
                                    pass
                    except:
                        seller = None
                
                # Build product object matching documentation format
                product_obj = {
                    'id': str(product.id) if product.id else '',
                    'title': product.title if product.title else '',
                    'description': product.description or '',
                    'price': float(product.price) if product.price else 0.0,
                    'originalPrice': float(product.original_price) if product.original_price else float(product.price) if product.price else 0.0,
                    'currency': product.currency if hasattr(product, 'currency') and product.currency else 'SAR',
                    'images': product.images or [],
                    'category': product.category if product.category else '',
                    'subcategory': product.subcategory or '',
                    'brand': product.brand or '',
                    'size': product.size or '',
                    'color': product.color or '',
                    'condition': product.condition if product.condition else '',
                    'tags': product.tags or [],
                    'seller': {
                        'id': str(seller.id) if seller and hasattr(seller, 'id') and seller.id else '',
                        'username': seller.username if seller and hasattr(seller, 'username') else '',
                        'profileImage': seller.profile_image if seller and hasattr(seller, 'profile_image') else '',
                        'rating': seller_rating,
                        'totalSales': total_sales
                    },
                    'isSaved': is_saved,
                    'isLiked': is_liked,
                    'likes': product.likes_count if hasattr(product, 'likes_count') else 0,
                    'status': product.status if product.status else 'active',
                    'quantity': product.quantity if hasattr(product, 'quantity') else 1,
                    'createdAt': product.created_at.isoformat() if product.created_at else None,
                    'updatedAt': product.updated_at.isoformat() if product.updated_at else None
                }
                
                # Add shipping info if available
                if hasattr(product, 'shipping_info') and product.shipping_info:
                    product_obj['shippingInfo'] = {
                        'cost': product.shipping_cost if hasattr(product, 'shipping_cost') else 0.0,
                        'estimatedDays': product.shipping_info.estimated_days if hasattr(product.shipping_info, 'estimated_days') else product.processing_time_days if hasattr(product, 'processing_time_days') else 7,
                        'locations': product.shipping_info.locations if hasattr(product.shipping_info, 'locations') else []
                    }
                elif hasattr(product, 'shipping_cost') or hasattr(product, 'processing_time_days'):
                    product_obj['shippingInfo'] = {
                        'cost': product.shipping_cost if hasattr(product, 'shipping_cost') else 0.0,
                        'estimatedDays': product.processing_time_days if hasattr(product, 'processing_time_days') else 7,
                        'locations': []
                    }
                
                products_list.append(product_obj)
            except Exception as e:
                # Skip products that cause errors and continue
                import logging
                logging.error(f"Error processing product: {str(e)}")
                continue
        
        # Get available filters for response
        available_filters = ProductService.get_available_filters_for_products(filters)
        
        # Calculate pagination
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        
        # Return in new format (documentation compliant) or legacy format
        if use_new_format:
            return Response({
                'success': True,
                'products': products_list,
                'pagination': {
                    'currentPage': page,
                    'totalPages': total_pages,
                    'totalItems': total,
                    'itemsPerPage': limit,
                    'hasNextPage': page < total_pages,
                    'hasPreviousPage': page > 1
                },
                'filters': available_filters
            }, status=status.HTTP_200_OK)
        else:
            # Legacy format - return array directly for backward compatibility
            return Response(products_list, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        import logging
        logging.error(f"Error in get_products: {str(e)}")
        return Response({'success': False, 'error': 'Internal server error. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    """Get all categories with their subcategories, brands, colors, and sizes"""
    try:
        data = ProductService.get_categories_with_subcategories()
        return Response({
            'success': True,
            'categories': data['categories'],
            'brands': data['brands'],
            'colors': data['colors'],
            'sizes': data['sizes']
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_detail(request, product_id):
    """Get product details"""
    try:
        user_id = None
        if hasattr(request.user, 'id'):
            user_id = str(request.user.id)
        
        product, is_saved, is_liked = ProductService.get_product_by_id(product_id, user_id)
        
        # Get seller - handle ReferenceField properly
        seller = None
        if product.seller_id:
            try:
                # Try to get seller_id as ObjectId
                from bson import ObjectId
                seller_obj_id = None
                
                # If seller_id is a ReferenceField that's been dereferenced
                if hasattr(product.seller_id, 'id'):
                    seller_obj_id = product.seller_id.id
                # If seller_id is already an ObjectId
                elif isinstance(product.seller_id, ObjectId):
                    seller_obj_id = product.seller_id
                # If seller_id is a string
                elif isinstance(product.seller_id, str):
                    seller_obj_id = ObjectId(product.seller_id)
                else:
                    seller_obj_id = product.seller_id
                
                if seller_obj_id:
                    seller = User.objects(id=seller_obj_id).first()
            except Exception as e:
                # If anything fails, seller will remain None
                seller = None
        
        # Get shipping info
        shipping_info = None
        if product.shipping_info:
            shipping_info = {
                'cost': product.shipping_info.cost,
                'estimated_days': product.shipping_info.estimated_days,
                'locations': product.shipping_info.locations
            }
        
        # Calculate seller rating and total sales
        seller_rating = 0
        total_sales = 0
        
        if seller:
            try:
                # Get seller rating statistics
                rating_stats = ReviewService.get_seller_rating_stats(str(seller.id))
                seller_rating = rating_stats.get('average_rating', 0)
                
                # Count total completed sales for the seller
                # Use seller.id directly - MongoEngine handles ObjectId conversion
                total_sales = Order.objects(
                    seller_id=seller.id,
                    payment_status='completed'
                ).count()
            except Exception as e:
                # If calculation fails, keep defaults (0)
                seller_rating = 0
                total_sales = 0
        
        # Build product data - matching create/update response structure
        product_data = {
            'id': str(product.id),
            'itemtitle': product.title,
            'description': product.description or '',
            'price': product.price,
            'originalPrice': product.original_price or product.price,
            'category': product.category,
            'subcategory': product.subcategory or '',
            'brand': product.brand or '',
            'currency': product.currency,
            'Quantity': product.quantity,
            'Gender': product.gender or '',
            'Size': product.size or '',
            'Color': product.color or '',
            'Condition': product.condition,
            'SKU/ID (Optional)': product.sku or '',
            'Tags/Keywords': product.tags or [],
            'Images': product.images or [],
            'Shipping Cost': product.shipping_cost,
            'Processing Time (days)': product.processing_time_days,
            'Shipping Locations': shipping_info['locations'] if shipping_info else [],
            'status': product.status,
            'reviewed': product.reviewed,
            'approved': product.approved,
            'seller_id': str(product.seller_id.id) if hasattr(product.seller_id, 'id') else str(product.seller_id),
            'seller_name': product.seller_name,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None,
            # Additional fields for frontend compatibility
            'seller': {
                'id': str(seller.id) if seller else '',
                'username': seller.username if seller else '',
                'profileImage': seller.profile_image if seller else '',
                'rating': seller_rating,
                'totalSales': total_sales
            },
            'likes': product.likes_count,
            'isLiked': is_liked,
            'isSaved': is_saved,
            'shippingInfo': {
                'cost': product.shipping_cost,
                'estimatedDays': product.shipping_info.estimated_days if product.shipping_info else product.processing_time_days,
                'locations': product.shipping_info.locations if product.shipping_info else []
            }
        }
        
        # Add affiliate code only if it exists
        if product.affiliate_code:
            product_data['Affiliate Code (Optional)'] = product.affiliate_code
        
        # Add tax percentage only if it exists
        if product.tax_percentage is not None:
            product_data['Tax Percentage'] = product.tax_percentage
        
        return Response(product_data, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_product(request):
    """Create product"""
    try:
        seller_id = str(request.user.id)
        
        # Handle both single product and array of products
        data = request.data
        is_array = isinstance(data, list)
        
        if not is_array:
            data = [data]
        
        products = []
        for product_data in data:
            product = ProductService.create_product(seller_id, product_data, request)
            
            # Get shipping info
            shipping_info = None
            if product.shipping_info:
                shipping_info = {
                    'cost': product.shipping_info.cost,
                    'estimated_days': product.shipping_info.estimated_days,
                    'locations': product.shipping_info.locations
                }
            
            product_dict = {
                'id': str(product.id),
                'itemtitle': product.title,
                'description': product.description or '',
                'price': product.price,
                'originalPrice': product.original_price or product.price,
                'category': product.category,
                'subcategory': product.subcategory or '',
                'brand': product.brand or '',
                'currency': product.currency,
                'Quantity': product.quantity,
                'Gender': product.gender or '',
                'Size': product.size or '',
                'Condition': product.condition,
                'SKU/ID (Optional)': product.sku or '',
                'Tags/Keywords': product.tags or [],
                'Images': product.images or [],
                'Shipping Cost': product.shipping_cost,
                'Processing Time (days)': product.processing_time_days,
                'Shipping Locations': shipping_info['locations'] if shipping_info else [],
                'status': product.status,
                'seller_id': str(product.seller_id.id),
                'seller_name': product.seller_name,
                'created_at': product.created_at.isoformat() if product.created_at else None,
                'updated_at': product.updated_at.isoformat() if product.updated_at else None
            }
            
            # Add affiliate code only if it exists
            if product.affiliate_code:
                product_dict['Affiliate Code (Optional)'] = product.affiliate_code
            
            # Add tax percentage only if it exists
            if product.tax_percentage is not None:
                product_dict['Tax Percentage'] = product.tax_percentage
            
            products.append(product_dict)
        
        # Return array if multiple products, single object if one product
        if len(products) == 1 and not isinstance(request.data, list):
            return Response({
                'success': True,
                'product': products[0]
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': True,
                'products': products,
                'count': len(products)
            }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_product(request, product_id):
    """Update product"""
    try:
        seller_id = str(request.user.id)
        product = ProductService.update_product(product_id, seller_id, request.data, request)
        
        # Get shipping info
        shipping_info = None
        if product.shipping_info:
            shipping_info = {
                'cost': product.shipping_info.cost,
                'estimated_days': product.shipping_info.estimated_days,
                'locations': product.shipping_info.locations
            }
        
        # Build product data
        product_data = {
            'id': str(product.id),
            'itemtitle': product.title,
            'description': product.description or '',
            'price': product.price,
            'originalPrice': product.original_price or product.price,
            'category': product.category,
            'subcategory': product.subcategory or '',
            'brand': product.brand or '',
            'currency': product.currency,
            'Quantity': product.quantity,
            'Gender': product.gender or '',
            'Size': product.size or '',
            'Color': product.color or '',
            'Condition': product.condition,
            'SKU/ID (Optional)': product.sku or '',
            'Tags/Keywords': product.tags or [],
            'Images': product.images or [],
            'Shipping Cost': product.shipping_cost,
            'Processing Time (days)': product.processing_time_days,
            'Shipping Locations': shipping_info['locations'] if shipping_info else [],
            'status': product.status,
            'seller_id': str(product.seller_id.id) if hasattr(product.seller_id, 'id') else str(product.seller_id),
            'seller_name': product.seller_name,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None
        }
        
        # Add affiliate code only if it exists
        if product.affiliate_code:
            product_data['Affiliate Code (Optional)'] = product.affiliate_code
        
        # Add tax percentage only if it exists
        if product.tax_percentage is not None:
            product_data['Tax Percentage'] = product.tax_percentage
        
        return Response({
            'success': True,
            'product': product_data
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_product(request, product_id):
    """Delete product"""
    try:
        seller_id = str(request.user.id)
        product = ProductService.delete_product(product_id, seller_id)
        
        return Response({
            'success': True,
            'message': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_seller_products(request):
    """Get products by authenticated seller"""
    try:
        # Get seller_id from authenticated user token
        seller_id = str(request.user.id)
        
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
            # Check if product is saved by the current user
            is_saved = False
            if user_id and user_id != 'None' and user_id.strip():
                try:
                    from bson import ObjectId
                    user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
                    saved = SavedProduct.objects(user_id=user_obj_id, product_id=product.id).first()
                    is_saved = saved is not None
                except:
                    is_saved = False
            
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
                'createdAt': product.created_at.isoformat() if product.created_at else None,
                'updatedAt': product.updated_at.isoformat() if product.updated_at else None
            })
        
        # Return products array directly
        return Response(products_list, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def save_product(request, product_id):
    """Save product to wishlist"""
    try:
        user_id = str(request.user.id)
        was_newly_saved, saved = ProductService.save_product(user_id, product_id)
        
        # Return True if product is saved (whether it was just saved or already saved)
        return Response({
            'success': True,
            'isSaved': True  # Product is now saved (or was already saved)
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_cart(request):
    """Get cart items with total amount"""
    try:
        user_id = str(request.user.id)
        cart_items, total_amount = ProductService.get_cart(user_id)
        
        return Response({
            'success': True,
            'cart': cart_items,
            'totalAmount': round(total_amount, 2),
            'itemCount': len(cart_items)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def unsave_product(request, product_id):
    """Remove product from wishlist"""
    try:
        user_id = str(request.user.id)
        ProductService.unsave_product(user_id, product_id)
        
        return Response({
            'success': True,
            'isSaved': False
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_featured_products(request):
    """Get featured products - returns most recent products (default: 5, can be customized via ?limit=5)"""
    try:
        user_id = None
        if hasattr(request.user, 'id'):
            user_id = str(request.user.id)
        
        # Get limit from query parameter, default to 5
        try:
            limit = int(request.query_params.get('limit', 5))
            # Ensure limit is positive and reasonable (max 50)
            limit = max(1, min(limit, 50))
        except (ValueError, TypeError):
            limit = 5
        
        products = ProductService.get_featured_products(user_id=user_id, limit=limit)
        
        products_list = []
        for product in products:
            seller = User.objects(id=product.seller_id.id).first()
            
            products_list.append({
                'id': str(product.id),
                'title': product.title,
                'description': product.description,
                'price': product.price,
                'currency': product.currency if hasattr(product, 'currency') and product.currency else 'SAR',
                'images': product.images,
                'seller': {
                    'id': str(seller.id) if seller else '',
                    'username': seller.username if seller else '',
                    'profileImage': seller.profile_image if seller else ''
                }
            })
        
        return Response({
            'products': products_list
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_trending_products(request):
    """Get trending products - returns best-selling products (default: 5, can be customized via ?limit=5)"""
    try:
        user_id = None
        if hasattr(request.user, 'id'):
            user_id = str(request.user.id)
        
        # Get limit from query parameter, default to 5
        try:
            limit = int(request.query_params.get('limit', 5))
            # Ensure limit is positive and reasonable (max 50)
            limit = max(1, min(limit, 50))
        except (ValueError, TypeError):
            limit = 5
        
        products_with_counts = ProductService.get_trending_products(user_id=user_id, limit=limit)
        
        products_list = []
        for item in products_with_counts:
            try:
                product = item['product']
                purchase_count = item['purchase_count']
                
                seller = None
                if product.seller_id:
                    seller = User.objects(id=product.seller_id.id).first()
                
                products_list.append({
                    'id': str(product.id),
                    'title': product.title,
                    'description': product.description,
                    'price': product.price,
                    'currency': product.currency if hasattr(product, 'currency') and product.currency else 'SAR',
                    'images': product.images if hasattr(product, 'images') and product.images else [],
                    'purchaseCount': purchase_count,
                    'seller': {
                        'id': str(seller.id) if seller else '',
                        'username': seller.username if seller else '',
                        'profileImage': seller.profile_image if seller else ''
                    }
                })
            except Exception as e:
                # Skip products that cause errors, but log them
                import logging
                logging.warning(f"Error processing product {getattr(item.get('product', {}), 'id', 'unknown')} in trending products: {str(e)}")
                continue
        
        return Response({
            'products': products_list
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import logging
        logging.error(f"Error in get_trending_products endpoint: {str(e)}")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_hero_section_public(request):
    """Get hero section (public endpoint)"""
    try:
        from admin_dashboard.services import HeroSectionService
        hero_data = HeroSectionService.get_hero_section(active_only=True)
        return Response({
            'success': True,
            'heroSection': hero_data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
