"""
Product services
"""
from datetime import datetime, timedelta
from products.models import Product, SavedProduct, Offer, Order, ShippingInfo, Review
from authentication.models import User
import random
import string
from bson import ObjectId
import os
import base64
import uuid
from django.conf import settings


class ProductService:
    """Product service"""
    
    @staticmethod
    def process_base64_images(images, request=None):
        """Convert base64 images to URLs by saving them to server"""
        if not images:
            return []
        
        processed_images = []
        for image_data in images:
            # If already a URL, keep it as is
            if isinstance(image_data, str):
                if image_data.startswith('http://') or image_data.startswith('https://'):
                    processed_images.append(image_data)
                    continue
                
                # Check if it's base64
                if image_data.startswith('data:image'):
                    try:
                        # Extract base64 data
                        header, encoded = image_data.split(',', 1)
                        # Get file extension from header
                        if 'jpeg' in header or 'jpg' in header:
                            ext = '.jpg'
                        elif 'png' in header:
                            ext = '.png'
                        elif 'gif' in header:
                            ext = '.gif'
                        elif 'webp' in header:
                            ext = '.webp'
                        else:
                            ext = '.jpg'  # default
                        
                        # Decode base64
                        image_bytes = base64.b64decode(encoded)
                        
                        # Generate unique filename
                        unique_filename = f"{uuid.uuid4()}{ext}"
                        
                        # Try to upload to VPS if configured, otherwise use local storage
                        vps_enabled = getattr(settings, 'VPS_ENABLED', False)
                        absolute_url = None
                        
                        if vps_enabled:
                            # Upload to VPS
                            from storage.vps_helper import upload_file_to_vps
                            success, result = upload_file_to_vps(
                                image_bytes,
                                'uploads/products',
                                unique_filename
                            )
                            
                            if success:
                                absolute_url = result
                            else:
                                # Fallback to local storage if VPS upload fails
                                import logging
                                logging.warning(f"VPS upload failed for product image, using local storage: {result}")
                                vps_enabled = False
                        
                        if not vps_enabled:
                            # Local storage fallback
                            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'products')
                            os.makedirs(upload_dir, exist_ok=True)
                            
                            file_path = os.path.join(upload_dir, unique_filename)
                            
                            # Save file
                            with open(file_path, 'wb') as f:
                                f.write(image_bytes)
                            
                            # Generate URL
                            media_url = settings.MEDIA_URL.rstrip('/')
                            file_url = f"{media_url}/uploads/products/{unique_filename}"
                            
                            # Build absolute URL if request is available
                            if request:
                                absolute_url = f"{request.scheme}://{request.get_host()}{file_url}"
                            else:
                                # Fallback to default if no request
                                absolute_url = f"https://dolabb-backend-2vsj.onrender.com{file_url}"
                        
                        if absolute_url:
                            processed_images.append(absolute_url)
                    except Exception as e:
                        # If base64 processing fails, skip this image
                        import logging
                        logging.error(f"Failed to process base64 image: {str(e)}")
                        continue
                else:
                    # Not base64, not URL - might be a relative path, keep as is
                    processed_images.append(image_data)
            else:
                # Not a string, skip
                continue
        
        return processed_images
    
    @staticmethod
    def create_product(seller_id, data, request=None):
        """Create a new product"""
        seller = User.objects(id=seller_id).first()
        if not seller:
            raise ValueError("Seller not found")
        
        # Change user role from buyer to seller if they create a product
        role_changed = False
        if seller.role == 'buyer':
            seller.role = 'seller'
            seller.save()
            role_changed = True
        
        # Convert seller_id to ObjectId if it's a string
        from bson import ObjectId
        if isinstance(seller_id, str):
            seller_obj_id = ObjectId(seller_id)
        else:
            seller_obj_id = seller_id
        
        product = Product(
            title=data['itemtitle'],
            description=data.get('description', ''),
            seller_id=seller_obj_id,
            seller_name=seller.full_name,
            category=data['category'],
            subcategory=data.get('subcategory', ''),
            brand=data.get('brand', ''),
            price=float(data['price']),
            original_price=float(data.get('originalPrice', data['price'])),
            currency=data.get('currency', 'SAR'),
            quantity=int(data.get('Quantity', 1)),
            gender=data.get('Gender', data.get('gender', '')),
            size=data.get('Size', ''),
            color=data.get('Color', ''),
            condition=data.get('Condition', 'good'),
            sku=data.get('SKU/ID (Optional)', ''),
            tags=data.get('Tags/Keywords', []),
            images=ProductService.process_base64_images(data.get('Images', []), request),
            shipping_cost=float(data.get('Shipping Cost', 0.0)),
            processing_time_days=int(data.get('Processing Time (days)', 7))
        )
        
        # Set tax percentage if provided (optional field)
        tax_percentage = data.get('Tax Percentage', data.get('taxPercentage', None))
        if tax_percentage is not None:
            try:
                product.tax_percentage = float(tax_percentage)
            except (ValueError, TypeError):
                product.tax_percentage = None
        else:
            product.tax_percentage = None
        
        # Set affiliate code only if provided and not empty
        affiliate_code = data.get('Affiliate Code (Optional)', '').strip() if data.get('Affiliate Code (Optional)') else ''
        if affiliate_code:
            product.affiliate_code = affiliate_code
            
            # Update affiliate code usage count when product is created
            try:
                from authentication.models import Affiliate
                # Find affiliate by code (exact match, no status filter - count should update regardless of status)
                # Use __iexact for case-insensitive matching in MongoDB
                affiliate = Affiliate.objects(affiliate_code__iexact=affiliate_code.strip()).first()
                
                if affiliate:
                    # Reload affiliate to get latest data (important for concurrent updates)
                    affiliate.reload()
                    
                    # Get current count, handling None or empty string
                    try:
                        current_count = int(affiliate.code_usage_count) if affiliate.code_usage_count and str(affiliate.code_usage_count).strip() else 0
                    except (ValueError, TypeError):
                        current_count = 0
                    
                    # Increment count
                    new_count = current_count + 1
                    affiliate.code_usage_count = str(new_count)
                    affiliate.last_activity = datetime.utcnow()
                    affiliate.save()
                    
                    # Log for debugging
                    import logging
                    logging.info(f"Updated affiliate code usage count for {affiliate_code}: {current_count} -> {new_count} (Affiliate ID: {affiliate.id})")
                else:
                    import logging
                    logging.warning(f"Affiliate code not found: {affiliate_code}")
            except Exception as e:
                # Log error but don't fail product creation
                import logging
                logging.error(f"Failed to update affiliate code usage count for {affiliate_code}: {str(e)}", exc_info=True)
        else:
            product.affiliate_code = None
        
        # Create ShippingInfo embedded document instance
        shipping_info = ShippingInfo(
            cost=product.shipping_cost,
            estimated_days=product.processing_time_days,
            locations=data.get('Shipping Locations', [])
        )
        product.shipping_info = shipping_info
        
        # Auto-approve products when created
        product.approved = True
        product.save()
        
        # Send notifications
        try:
            from notifications.notification_helper import NotificationHelper
            
            # Send seller verification notification if role changed
            if role_changed:
                NotificationHelper.send_seller_verification_approved(str(seller.id))
            
            # Send listing published notification
            NotificationHelper.send_listing_published(str(seller.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending notifications: {str(e)}")
        
        return product
    
    @staticmethod
    def get_products(filters=None, page=1, limit=20, user_id=None):
        """Get products with filters and pagination"""
        # Show approved products, or unapproved products if user is the seller
        from mongoengine import Q
        if user_id and user_id != 'None' and user_id.strip():
            from bson import ObjectId
            try:
                user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
                query = Product.objects(
                    Q(status='active') & (Q(approved=True) | (Q(seller_id=user_obj_id) & Q(approved=False)))
                )
            except (Exception, ValueError):
                query = Product.objects(status='active', approved=True)
        else:
            query = Product.objects(status='active', approved=True)
        
        if filters:
            if filters.get('category'):
                query = query.filter(category=filters['category'])
            if filters.get('subcategory'):
                # Handle subcategory filtering - support exact match and case-insensitive
                subcategory = filters['subcategory'].strip() if isinstance(filters['subcategory'], str) else str(filters.get('subcategory', ''))
                if subcategory:
                    # Use case-insensitive matching for subcategory
                    query = query.filter(Q(subcategory__iexact=subcategory) | Q(subcategory=subcategory))
            if filters.get('brand'):
                brand = filters['brand'].strip() if isinstance(filters['brand'], str) else str(filters.get('brand', ''))
                if brand:
                    # Use case-insensitive matching for brand
                    query = query.filter(Q(brand__iexact=brand) | Q(brand=brand))
            if filters.get('minPrice'):
                min_price = filters['minPrice'].strip() if isinstance(filters['minPrice'], str) else str(filters['minPrice'])
                if min_price:
                    try:
                        query = query.filter(price__gte=float(min_price))
                    except (ValueError, TypeError):
                        pass
            if filters.get('maxPrice'):
                max_price = filters['maxPrice'].strip() if isinstance(filters['maxPrice'], str) else str(filters['maxPrice'])
                if max_price:
                    try:
                        query = query.filter(price__lte=float(max_price))
                    except (ValueError, TypeError):
                        pass
            if filters.get('size'):
                size = filters['size'].strip() if isinstance(filters['size'], str) else str(filters.get('size', ''))
                if size:
                    # Support sizes from 2XS to One Size (case-insensitive)
                    query = query.filter(Q(size__iexact=size) | Q(size=size))
            if filters.get('color'):
                color = filters['color'].strip() if isinstance(filters['color'], str) else str(filters.get('color', ''))
                if color:
                    # Use case-insensitive matching for color
                    query = query.filter(Q(color__iexact=color) | Q(color=color))
            if filters.get('condition'):
                # Map user-friendly condition names to database values
                condition_str = filters['condition'].strip() if isinstance(filters['condition'], str) else str(filters.get('condition', ''))
                condition = condition_str.lower() if condition_str else ''
                condition_mapping = {
                    'brand new': 'new',
                    'like new': 'like-new',
                    'used - excellent': 'good',  # Map to 'good' as it's closest
                    'used - good': 'good',
                    'used - fair': 'fair',
                    'new': 'new',
                    'like-new': 'like-new',
                    'good': 'good',
                    'fair': 'fair'
                }
                db_condition = condition_mapping.get(condition, condition)
                if db_condition in ['new', 'like-new', 'good', 'fair']:
                    query = query.filter(condition=db_condition)
            if filters.get('search'):
                search_term = filters['search'].strip() if isinstance(filters['search'], str) else str(filters.get('search', ''))
                if search_term:
                    query = query.filter(title__icontains=search_term)
            if filters.get('onSale'):
                # Filter for products that have original_price > price (on sale)
                # Products are on sale if original_price exists and is greater than current price
                # We need to filter in Python since MongoDB doesn't support field-to-field comparison easily
                # This will be handled by filtering the results after query
                pass  # Will filter in Python after fetching
        
        # Sorting - handle different sortBy options
        sort_by = filters.get('sortBy', 'newly listed') if filters else 'newly listed'
        if sort_by:
            sort_by_lower = sort_by.lower().strip()
            
            # Low to High / Price: Low to High
            if sort_by_lower in ['low to high', 'price: low to high', 'price-low-to-high', 'price_asc', 'price_ascending', 'price low to high']:
                query = query.order_by('price')
            # High to Low / Price: High to Low
            elif sort_by_lower in ['high to low', 'price: high to low', 'price-high-to-low', 'price_desc', 'price_descending', 'price high to low']:
                query = query.order_by('-price')
            # Newly Listed
            elif sort_by_lower in ['newly listed', 'newest', 'new', 'newly-listed']:
                query = query.order_by('-created_at')
            # Relevance
            elif sort_by_lower in ['relevance', 'relevant']:
                # Relevance: sort by likes_count first, then by created_at
                query = query.order_by('-likes_count', '-created_at')
            else:
                # Default: newly listed first
                query = query.order_by('-created_at')
        else:
            # Default: newly listed first
            query = query.order_by('-created_at')
        
        # Handle onSale filter - filter products where original_price > price
        if filters and filters.get('onSale'):
            # We need to filter in memory since MongoDB doesn't support field-to-field comparison easily
            # First get all matching products, then filter
            all_products = list(query)
            filtered_products = [
                p for p in all_products 
                if p.original_price and p.original_price > 0 and p.price and p.original_price > p.price
            ]
            total = len(filtered_products)
            skip = (page - 1) * limit
            products = filtered_products[skip:skip + limit]
            return products, total
        
        total = query.count()
        skip = (page - 1) * limit
        products = query.skip(skip).limit(limit)
        
        return products, total
    
    @staticmethod
    def get_available_filters_for_products(filters=None):
        """Get available filter options based on current filters"""
        from collections import defaultdict
        
        # Build base query
        query = Product.objects(status='active', approved=True)
        
        # Apply same filters as get_products to get relevant filter options
        if filters:
            from mongoengine import Q
            if filters.get('category'):
                query = query.filter(category=filters['category'])
            if filters.get('subcategory'):
                subcategory = filters['subcategory'].strip() if isinstance(filters['subcategory'], str) else str(filters.get('subcategory', ''))
                if subcategory:
                    query = query.filter(Q(subcategory__iexact=subcategory) | Q(subcategory=subcategory))
        
        # Get distinct brands
        brands_pipeline = [
            {'$match': {'status': 'active', 'approved': True, 'brand': {'$exists': True, '$ne': None, '$ne': ''}}},
            {'$group': {'_id': '$brand'}},
            {'$project': {'brand': '$_id', '_id': 0}}
        ]
        
        # Apply category filter if present
        if filters and filters.get('category'):
            brands_pipeline[0]['$match']['category'] = filters['category']
        if filters and filters.get('subcategory'):
            subcategory = filters['subcategory'].strip() if isinstance(filters['subcategory'], str) else str(filters.get('subcategory', ''))
            if subcategory:
                brands_pipeline[0]['$match']['subcategory'] = subcategory
        
        # Get distinct sizes
        sizes_pipeline = [
            {'$match': {'status': 'active', 'approved': True, 'size': {'$exists': True, '$ne': None, '$ne': ''}}},
            {'$group': {'_id': '$size'}},
            {'$project': {'size': '$_id', '_id': 0}}
        ]
        
        if filters and filters.get('category'):
            sizes_pipeline[0]['$match']['category'] = filters['category']
        if filters and filters.get('subcategory'):
            subcategory = filters['subcategory'].strip() if isinstance(filters['subcategory'], str) else str(filters.get('subcategory', ''))
            if subcategory:
                sizes_pipeline[0]['$match']['subcategory'] = subcategory
        
        # Get distinct colors
        colors_pipeline = [
            {'$match': {'status': 'active', 'approved': True, 'color': {'$exists': True, '$ne': None, '$ne': ''}}},
            {'$group': {'_id': '$color'}},
            {'$project': {'color': '$_id', '_id': 0}}
        ]
        
        if filters and filters.get('category'):
            colors_pipeline[0]['$match']['category'] = filters['category']
        if filters and filters.get('subcategory'):
            subcategory = filters['subcategory'].strip() if isinstance(filters['subcategory'], str) else str(filters.get('subcategory', ''))
            if subcategory:
                colors_pipeline[0]['$match']['subcategory'] = subcategory
        
        # Get price range
        price_pipeline = [
            {'$match': {'status': 'active', 'approved': True}},
            {'$group': {
                '_id': None,
                'min': {'$min': '$price'},
                'max': {'$max': '$price'}
            }}
        ]
        
        if filters and filters.get('category'):
            price_pipeline[0]['$match']['category'] = filters['category']
        if filters and filters.get('subcategory'):
            subcategory = filters['subcategory'].strip() if isinstance(filters['subcategory'], str) else str(filters.get('subcategory', ''))
            if subcategory:
                price_pipeline[0]['$match']['subcategory'] = subcategory
        
        # Execute aggregations
        brands_data = list(Product.objects.aggregate(*brands_pipeline))
        sizes_data = list(Product.objects.aggregate(*sizes_pipeline))
        colors_data = list(Product.objects.aggregate(*colors_pipeline))
        price_data = list(Product.objects.aggregate(*price_pipeline))
        
        # Format results
        brands_list = sorted([item['brand'].strip() for item in brands_data if item.get('brand') and item['brand'].strip()])
        sizes_list = sorted([item['size'].strip() for item in sizes_data if item.get('size') and item['size'].strip()])
        colors_list = sorted([item['color'].strip() for item in colors_data if item.get('color') and item['color'].strip()])
        
        price_range = {'min': 0.0, 'max': 0.0}
        if price_data and price_data[0].get('min') is not None:
            price_range = {
                'min': float(price_data[0]['min']),
                'max': float(price_data[0]['max'])
            }
        
        return {
            'availableBrands': brands_list,
            'availableSizes': sizes_list,
            'availableColors': colors_list,
            'priceRange': price_range
        }
    
    @staticmethod
    def get_categories_with_subcategories():
        """Get all categories with their subcategories, brands, and colors using MongoDB aggregation"""
        from collections import defaultdict
        
        # Use MongoDB aggregation to get distinct values efficiently
        # This avoids loading all products into memory
        
        # Get distinct categories with their subcategories using aggregation
        pipeline = [
            {'$match': {'status': 'active', 'approved': True}},
            {'$group': {
                '_id': {
                    'category': '$category',
                    'subcategory': '$subcategory'
                }
            }},
            {'$project': {
                'category': '$_id.category',
                'subcategory': '$_id.subcategory',
                '_id': 0
            }}
        ]
        
        # Get distinct brands using aggregation
        brands_pipeline = [
            {'$match': {'status': 'active', 'approved': True, 'brand': {'$exists': True, '$ne': None, '$ne': ''}}},
            {'$group': {'_id': '$brand'}},
            {'$project': {'brand': '$_id', '_id': 0}}
        ]
        
        # Get distinct colors using aggregation
        colors_pipeline = [
            {'$match': {'status': 'active', 'approved': True, 'color': {'$exists': True, '$ne': None, '$ne': ''}}},
            {'$group': {'_id': '$color'}},
            {'$project': {'color': '$_id', '_id': 0}}
        ]
        
        # Get distinct sizes using aggregation
        sizes_pipeline = [
            {'$match': {'status': 'active', 'approved': True, 'size': {'$exists': True, '$ne': None, '$ne': ''}}},
            {'$group': {'_id': '$size'}},
            {'$project': {'size': '$_id', '_id': 0}}
        ]
        
        # Execute aggregations
        category_subcategory_pairs = list(Product.objects.aggregate(*pipeline))
        brands_data = list(Product.objects.aggregate(*brands_pipeline))
        colors_data = list(Product.objects.aggregate(*colors_pipeline))
        sizes_data = list(Product.objects.aggregate(*sizes_pipeline))
        
        # Process categories and subcategories
        categories_dict = defaultdict(set)
        for item in category_subcategory_pairs:
            category = item.get('category')
            subcategory = item.get('subcategory', '').strip()
            if category and subcategory:
                categories_dict[category].add(subcategory)
        
        # Convert to the desired format
        categories_list = []
        category_order = ['women', 'men', 'watches', 'jewelry', 'accessories']
        
        for category in category_order:
            subcategories = sorted(list(categories_dict[category])) if category in categories_dict else []
            categories_list.append({
                'category': category,
                'subcategories': subcategories
            })
        
        # Also include any categories that might exist in products but not in the predefined list
        for category in categories_dict:
            if category not in category_order:
                subcategories = sorted(list(categories_dict[category]))
                categories_list.append({
                    'category': category,
                    'subcategories': subcategories
                })
        
        # Extract and sort brands
        brands_list = sorted([item['brand'].strip() for item in brands_data if item.get('brand') and item['brand'].strip()])
        
        # Extract and sort colors
        colors_list = sorted([item['color'].strip() for item in colors_data if item.get('color') and item['color'].strip()])
        
        # Extract and sort sizes - maintain order: 2XS, XS, S, M, L, XL, 2XL, 3XL, One Size, etc.
        size_order = ['2XS', 'XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL', 'One Size']
        sizes_raw = [item['size'].strip() for item in sizes_data if item.get('size') and item['size'].strip()]
        
        # Sort sizes: first by predefined order, then alphabetically for others
        sizes_list = []
        for size in size_order:
            for s in sizes_raw:
                if s.upper() == size.upper():
                    sizes_list.append(s)
                    break
        
        # Add remaining sizes alphabetically
        remaining_sizes = sorted([s for s in sizes_raw if s not in sizes_list], key=str.lower)
        sizes_list.extend(remaining_sizes)
        
        return {
            'categories': categories_list,
            'brands': brands_list,
            'colors': colors_list,
            'sizes': sizes_list
        }
    
    @staticmethod
    def get_product_by_id(product_id, user_id=None):
        """Get product by ID"""
        from bson import ObjectId
        
        # Convert product_id to ObjectId if it's a string
        try:
            if isinstance(product_id, str):
                product_obj_id = ObjectId(product_id)
            else:
                product_obj_id = product_id
        except:
            raise ValueError("Invalid product ID format")
        
        product = Product.objects(id=product_obj_id).first()
        if not product:
            raise ValueError("Product not found")
        
        is_saved = False
        is_liked = False
        if user_id and user_id != 'None' and user_id.strip():
            try:
                # Convert user_id to ObjectId if it's a string
                if isinstance(user_id, str):
                    user_obj_id = ObjectId(user_id)
                else:
                    user_obj_id = user_id
                
                saved = SavedProduct.objects(user_id=user_obj_id, product_id=product_obj_id).first()
                is_saved = saved is not None
            except (Exception, ValueError):
                # If user_id conversion fails, just skip saved check
                is_saved = False
        
        return product, is_saved, is_liked
    
    @staticmethod
    def update_product(product_id, seller_id, data, request=None):
        """Update product"""
        from bson import ObjectId
        
        # Convert product_id and seller_id to ObjectId if needed
        try:
            if isinstance(product_id, str):
                product_obj_id = ObjectId(product_id)
            else:
                product_obj_id = product_id
            
            if isinstance(seller_id, str):
                seller_obj_id = ObjectId(seller_id)
            else:
                seller_obj_id = seller_id
        except:
            raise ValueError("Invalid ID format")
        
        product = Product.objects(id=product_obj_id, seller_id=seller_obj_id).first()
        if not product:
            raise ValueError("Product not found")
        
        # Update all fields that are provided
        if 'itemtitle' in data:
            product.title = data['itemtitle']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = float(data['price'])
        if 'originalPrice' in data:
            product.original_price = float(data['originalPrice'])
        if 'category' in data:
            product.category = data['category']
        if 'subcategory' in data:
            product.subcategory = data['subcategory']
        if 'brand' in data:
            product.brand = data['brand']
        if 'currency' in data:
            product.currency = data['currency']
        if 'Quantity' in data:
            product.quantity = int(data['Quantity'])
        elif 'quantity' in data:
            product.quantity = int(data['quantity'])
        if 'Gender' in data:
            product.gender = data['Gender']
        elif 'gender' in data:
            product.gender = data['gender']
        if 'Size' in data:
            product.size = data['Size']
        if 'Color' in data:
            product.color = data['Color']
        if 'Condition' in data:
            product.condition = data['Condition']
        if 'SKU/ID (Optional)' in data:
            product.sku = data['SKU/ID (Optional)']
        if 'Tags/Keywords' in data:
            product.tags = data['Tags/Keywords']
        if 'Images' in data:
            product.images = ProductService.process_base64_images(data['Images'], request)
        if 'Shipping Cost' in data:
            product.shipping_cost = float(data['Shipping Cost'])
        if 'Processing Time (days)' in data:
            product.processing_time_days = int(data['Processing Time (days)'])
        if 'Affiliate Code (Optional)' in data:
            new_affiliate_code = data['Affiliate Code (Optional)']
            new_affiliate_code = new_affiliate_code.strip() if new_affiliate_code and new_affiliate_code.strip() else None
            
            # Get old affiliate code before updating
            old_affiliate_code = product.affiliate_code
            
            # Only set if provided and not empty
            product.affiliate_code = new_affiliate_code
            
            # Update affiliate code usage count if code is being added or changed
            # Only increment if:
            # 1. New code is different from old code (or old code was None)
            # 2. New code is not empty
            if new_affiliate_code and new_affiliate_code != old_affiliate_code:
                try:
                    from authentication.models import Affiliate
                    # Find affiliate by code (case-insensitive)
                    affiliate = Affiliate.objects(affiliate_code__iexact=new_affiliate_code.strip()).first()
                    
                    if affiliate:
                        # Reload affiliate to get latest data (important for concurrent updates)
                        affiliate.reload()
                        
                        # Get current count, handling None or empty string
                        try:
                            current_count = int(affiliate.code_usage_count) if affiliate.code_usage_count and str(affiliate.code_usage_count).strip() else 0
                        except (ValueError, TypeError):
                            current_count = 0
                        
                        # Increment count
                        new_count = current_count + 1
                        affiliate.code_usage_count = str(new_count)
                        affiliate.last_activity = datetime.utcnow()
                        affiliate.save()
                        
                        # Log for debugging
                        import logging
                        logging.info(f"Updated affiliate code usage count for {new_affiliate_code}: {current_count} -> {new_count} (Affiliate ID: {affiliate.id}) - Product Update")
                except Exception as e:
                    # Log error but don't fail product update
                    import logging
                    logging.error(f"Failed to update affiliate code usage count for {new_affiliate_code}: {str(e)}", exc_info=True)
        if 'Tax Percentage' in data or 'taxPercentage' in data:
            tax_percentage = data.get('Tax Percentage', data.get('taxPercentage', None))
            if tax_percentage is not None:
                try:
                    product.tax_percentage = float(tax_percentage)
                except (ValueError, TypeError):
                    product.tax_percentage = None
            else:
                product.tax_percentage = None
        
        # Update shipping_info if shipping fields are provided
        if 'Shipping Cost' in data or 'Processing Time (days)' in data or 'Shipping Locations' in data:
            if not product.shipping_info:
                product.shipping_info = ShippingInfo()
            
            if 'Shipping Cost' in data:
                product.shipping_info.cost = float(data['Shipping Cost'])
            if 'Processing Time (days)' in data:
                product.shipping_info.estimated_days = int(data['Processing Time (days)'])
            if 'Shipping Locations' in data:
                product.shipping_info.locations = data['Shipping Locations']
        
        product.updated_at = datetime.utcnow()
        product.save()
        
        return product
    
    @staticmethod
    def delete_product(product_id, seller_id):
        """Delete product"""
        from bson import ObjectId
        
        # Convert product_id and seller_id to ObjectId if needed
        try:
            if isinstance(product_id, str):
                product_obj_id = ObjectId(product_id)
            else:
                product_obj_id = product_id
            
            if isinstance(seller_id, str):
                seller_obj_id = ObjectId(seller_id)
            else:
                seller_obj_id = seller_id
        except:
            raise ValueError("Invalid ID format")
        
        product = Product.objects(id=product_obj_id, seller_id=seller_obj_id).first()
        if not product:
            raise ValueError("Product not found")
        
        # Delete related SavedProduct entries (wishlist items)
        SavedProduct.objects(product_id=product_obj_id).delete()
        
        # Actually delete the product from database
        product.delete()
        
        return product
    
    @staticmethod
    def get_seller_products(seller_id, status=None, page=1, limit=20):
        """Get products by seller"""
        from bson import ObjectId
        
        # Convert seller_id to ObjectId if needed
        try:
            if isinstance(seller_id, str):
                seller_obj_id = ObjectId(seller_id)
            else:
                seller_obj_id = seller_id
        except (Exception, ValueError):
            raise ValueError("Invalid seller ID format")
        
        query = Product.objects(seller_id=seller_obj_id)
        
        if status:
            query = query.filter(status=status)
        
        # Order by newest first
        query = query.order_by('-created_at')
        
        total = query.count()
        skip = (page - 1) * limit
        products = query.skip(skip).limit(limit)
        
        return products, total
    
    @staticmethod
    def save_product(user_id, product_id):
        """Save product to wishlist"""
        from bson import ObjectId
        
        # Convert user_id and product_id to ObjectId if needed
        try:
            if isinstance(user_id, str):
                user_obj_id = ObjectId(user_id)
            else:
                user_obj_id = user_id
            
            if isinstance(product_id, str):
                product_obj_id = ObjectId(product_id)
            else:
                product_obj_id = product_id
        except (Exception, ValueError):
            raise ValueError("Invalid ID format")
        
        # Check if already saved
        saved = SavedProduct.objects(user_id=user_obj_id, product_id=product_obj_id).first()
        if saved:
            return False, saved
        
        # Create new saved product entry
        saved = SavedProduct(user_id=user_obj_id, product_id=product_obj_id)
        saved.save()
        return True, saved
    
    @staticmethod
    def unsave_product(user_id, product_id):
        """Remove product from wishlist"""
        from bson import ObjectId
        
        # Convert user_id and product_id to ObjectId if needed
        try:
            if isinstance(user_id, str):
                user_obj_id = ObjectId(user_id)
            else:
                user_obj_id = user_id
            
            if isinstance(product_id, str):
                product_obj_id = ObjectId(product_id)
            else:
                product_obj_id = product_id
        except (Exception, ValueError):
            raise ValueError("Invalid ID format")
        
        # Find and delete saved product
        saved = SavedProduct.objects(user_id=user_obj_id, product_id=product_obj_id).first()
        if saved:
            saved.delete()
            return True
        return False
    
    @staticmethod
    def get_saved_products(user_id):
        """Get saved products for a user (for login response)"""
        try:
            # Convert user_id to ObjectId if needed
            if isinstance(user_id, str):
                user_obj_id = ObjectId(user_id)
            else:
                user_obj_id = user_id
        except (Exception, ValueError):
            return []
        
        # Get all saved products for this user
        saved_products = SavedProduct.objects(user_id=user_obj_id)
        
        saved_products_list = []
        for saved in saved_products:
            try:
                # Handle ReferenceField - product_id might be an ObjectId or a Product object
                product_obj_id = None
                if hasattr(saved.product_id, 'id'):
                    product_obj_id = saved.product_id.id
                elif isinstance(saved.product_id, ObjectId):
                    product_obj_id = saved.product_id
                elif isinstance(saved.product_id, str):
                    product_obj_id = ObjectId(saved.product_id)
                else:
                    product_obj_id = saved.product_id
                
                # Get the product
                product = Product.objects(id=product_obj_id).first()
                if product:
                    # Get first image or empty string
                    image = product.images[0] if product.images and len(product.images) > 0 else ''
                    
                    saved_products_list.append({
                        'id': str(product.id),
                        'name': product.title,
                        'price': product.price,
                        'image': image
                    })
            except:
                # Skip if product not found or error
                continue
        
        return saved_products_list
    
    @staticmethod
    def get_cart(user_id):
        """Get cart items for a user with total amount"""
        from bson import ObjectId
        
        try:
            # Convert user_id to ObjectId if needed
            if isinstance(user_id, str):
                user_obj_id = ObjectId(user_id)
            else:
                user_obj_id = user_id
        except (Exception, ValueError):
            return [], 0.0
        
        # Get all saved products for this user (cart items)
        saved_products = SavedProduct.objects(user_id=user_obj_id).order_by('-created_at')
        
        cart_items = []
        total_amount = 0.0
        
        for saved in saved_products:
            try:
                # Handle ReferenceField - product_id might be an ObjectId or a Product object
                # This is the same way it's handled in save_product and other methods
                product_obj_id = None
                
                # Try to get product_id from ReferenceField
                if hasattr(saved.product_id, 'id'):
                    # ReferenceField is dereferenced, get the id
                    product_obj_id = saved.product_id.id
                elif isinstance(saved.product_id, ObjectId):
                    # Already an ObjectId
                    product_obj_id = saved.product_id
                elif isinstance(saved.product_id, str):
                    # String, convert to ObjectId
                    try:
                        product_obj_id = ObjectId(saved.product_id)
                    except (Exception, ValueError):
                        # Invalid ObjectId format, skip this item
                        continue
                else:
                    # Try to use as is
                    product_obj_id = saved.product_id
                
                # Validate product_obj_id before querying
                if not product_obj_id:
                    continue
                
                # Get the product - same way as in create_offer
                product = Product.objects(id=product_obj_id).first()
                if product and product.status == 'active':  # Only include active products
                    # Get first image or empty string
                    image = product.images[0] if product.images and len(product.images) > 0 else ''
                    
                    cart_item = {
                        'id': str(product.id),
                        'title': product.title,
                        'price': product.price,
                        'image': image
                    }
                    
                    cart_items.append(cart_item)
                    total_amount += product.price
            except Exception as e:
                # Skip if product not found or error - log for debugging
                import logging
                logging.error(f"Error processing cart item: {str(e)}")
                continue
        
        return cart_items, total_amount
    
    @staticmethod
    def get_featured_products(user_id=None):
        """Get featured products - shows 4 most recent products"""
        from mongoengine import Q
        if user_id:
            from bson import ObjectId
            try:
                user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
                query = Product.objects(
                    Q(status='active') & (Q(approved=True) | (Q(seller_id=user_obj_id) & Q(approved=False)))
                ).order_by('-created_at')
            except:
                query = Product.objects(status='active', approved=True).order_by('-created_at')
        else:
            query = Product.objects(status='active', approved=True).order_by('-created_at')
        # Always return first 4 products (no pagination)
        products = query.limit(4)
        return products
    
    @staticmethod
    def get_trending_products(user_id=None):
        """Get trending products - shows 4 best-selling products (most orders)"""
        from mongoengine import Q
        from products.models import Order
        
        # Get base query for active products
        if user_id:
            from bson import ObjectId
            try:
                user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
                base_query = Product.objects(
                    Q(status='active') & (Q(approved=True) | (Q(seller_id=user_obj_id) & Q(approved=False)))
                )
            except:
                base_query = Product.objects(status='active', approved=True)
        else:
            base_query = Product.objects(status='active', approved=True)
        
        # Get all active products and calculate sales count for each
        all_products = base_query.all()
        
        # Calculate sales count (completed orders) for each product
        products_with_sales = []
        for product in all_products:
            sales_count = Order.objects(
                product_id=product.id,
                payment_status='completed'
            ).count()
            products_with_sales.append({
                'product': product,
                'sales_count': sales_count
            })
        
        # Sort by sales count (descending), then by created_at (newest first) for tie-breaking
        products_with_sales.sort(key=lambda x: (x['sales_count'], x['product'].created_at), reverse=True)
        
        # Return first 4 products
        trending_products = [item['product'] for item in products_with_sales[:4]]
        return trending_products
    
    @staticmethod
    def get_all_categories_formatted():
        """Get all categories with subcategories and featured collections in the format specified by documentation"""
        from collections import defaultdict
        
        # Category definitions from documentation
        category_definitions = {
            'women': {
                'name': 'Women',
                'subcategories': ['tops', 'shoes', 'jeans', 'bags-purses', 'sweaters', 'sunglasses', 
                                 'skirts', 'hats', 'dresses', 'coats-jackets', 'plus-size'],
                'featured': ['wardrobe-essentials', 'denim-everything', 'lifestyle-sneakers', 
                           'office-wear', 'gym-gear']
            },
            'men': {
                'name': 'Men',
                'subcategories': ['tshirts', 'shoes', 'shirts', 'bags', 'hoodies', 'hats', 'jeans', 
                                 'sweaters', 'sunglasses', 'coats-jackets', 'big-tall'],
                'featured': ['wardrobe-essentials', 'denim-everything', 'lifestyle-sneakers', 
                           'office-wear', 'gym-gear']
            },
            'watches': {
                'name': 'Watches',
                'subcategories': ['mens-watches', 'womens-watches', 'smart-watches', 'luxury-watches', 
                                 'sports-watches', 'vintage-watches', 'dress-watches', 'casual-watches'],
                'featured': ['best-sellers', 'new-arrivals', 'on-sale']
            },
            'jewellery': {
                'name': 'Jewellery',
                'subcategories': ['rings', 'necklaces', 'earrings', 'bracelets', 'pendants', 'chains', 
                                 'anklets', 'brooches', 'cufflinks'],
                'featured': ['gold-collection', 'silver-collection', 'diamond-collection', 'vintage-jewellery']
            },
            'accessories': {
                'name': 'Accessories',
                'subcategories': ['bags', 'belts', 'hats-caps', 'sunglasses', 'scarves', 'wallets', 
                                 'phone-cases', 'keychains', 'hair-accessories', 'ties-bow-ties'],
                'featured': ['designer-bags', 'luxury-accessories', 'trending-now']
            }
        }
        
        # Subcategory name mappings
        subcategory_names = {
            'tops': 'Tops', 'shoes': 'Shoes', 'jeans': 'Jeans', 'bags-purses': 'Bags & Purses',
            'sweaters': 'Sweaters', 'sunglasses': 'Sunglasses', 'skirts': 'Skirts', 'hats': 'Hats',
            'dresses': 'Dresses', 'coats-jackets': 'Coats & Jackets', 'plus-size': 'Plus Size',
            'tshirts': 'T-shirts', 'shirts': 'Shirts', 'bags': 'Bags', 'hoodies': 'Hoodies',
            'big-tall': 'Big & Tall', 'mens-watches': "Men's Watches", 'womens-watches': "Women's Watches",
            'smart-watches': 'Smart Watches', 'luxury-watches': 'Luxury Watches', 
            'sports-watches': 'Sports Watches', 'vintage-watches': 'Vintage Watches',
            'dress-watches': 'Dress Watches', 'casual-watches': 'Casual Watches',
            'rings': 'Rings', 'necklaces': 'Necklaces', 'earrings': 'Earrings', 'bracelets': 'Bracelets',
            'pendants': 'Pendants', 'chains': 'Chains', 'anklets': 'Anklets', 'brooches': 'Brooches',
            'cufflinks': 'Cufflinks', 'belts': 'Belts', 'hats-caps': 'Hats & Caps', 'scarves': 'Scarves',
            'wallets': 'Wallets', 'phone-cases': 'Phone Cases', 'keychains': 'Keychains',
            'hair-accessories': 'Hair Accessories', 'ties-bow-ties': 'Ties & Bow Ties'
        }
        
        # Featured collection name mappings
        featured_names = {
            'wardrobe-essentials': 'Wardrobe essentials',
            'denim-everything': 'Denim everything',
            'lifestyle-sneakers': 'Lifestyle sneakers',
            'office-wear': 'Office wear',
            'gym-gear': 'Gym gear',
            'best-sellers': 'Best Sellers',
            'new-arrivals': 'New Arrivals',
            'on-sale': 'On Sale',
            'gold-collection': 'Gold Collection',
            'silver-collection': 'Silver Collection',
            'diamond-collection': 'Diamond Collection',
            'vintage-jewellery': 'Vintage Jewellery',
            'designer-bags': 'Designer Bags',
            'luxury-accessories': 'Luxury Accessories',
            'trending-now': 'Trending Now'
        }
        
        # Get product counts for each category/subcategory
        categories_list = []
        
        for category_key, category_info in category_definitions.items():
            # Map 'jewellery' (API) to 'jewelry' (database) for querying
            db_category_key = 'jewelry' if category_key == 'jewellery' else category_key
            
            # Count total products in category
            total_products = Product.objects(
                category=db_category_key,
                status='active',
                approved=True
            ).count()
            
            # Build subcategories with counts
            subcategories_list = []
            for subcat_key in category_info['subcategories']:
                count = Product.objects(
                    category=db_category_key,
                    subcategory=subcat_key,
                    status='active',
                    approved=True
                ).count()
                
                subcategories_list.append({
                    'id': subcat_key,
                    'name': subcategory_names.get(subcat_key, subcat_key.replace('-', ' ').title()),
                    'key': subcat_key,
                    'href': f'/{category_key}/{subcat_key}',
                    'productCount': count
                })
            
            # Build featured collections with counts
            featured_list = []
            for feat_key in category_info['featured']:
                # For featured collections, we'll count products that match the collection criteria
                # This is a simplified version - you may want to add a 'featured_collection' field to products
                count = Product.objects(
                    category=db_category_key,
                    status='active',
                    approved=True
                ).count()  # Simplified - you can enhance this based on your business logic
                
                featured_list.append({
                    'id': feat_key,
                    'name': featured_names.get(feat_key, feat_key.replace('-', ' ').title()),
                    'key': feat_key,
                    'href': f'/{category_key}/{feat_key}',
                    'productCount': count
                })
            
            # Use 'jewellery' in API response even though model uses 'jewelry'
            display_key = 'jewellery' if category_key == 'jewelry' else category_key
            
            categories_list.append({
                'id': display_key,
                'name': category_info['name'],
                'key': display_key,
                'href': f'/{display_key}',
                'subCategories': subcategories_list,
                'featured': featured_list,
                'totalProducts': total_products
            })
        
        return categories_list
    
    @staticmethod
    def get_category_details(category_key):
        """Get detailed information about a specific category"""
        category_definitions = {
            'women': {
                'name': 'Women',
                'subcategories': ['tops', 'shoes', 'jeans', 'bags-purses', 'sweaters', 'sunglasses', 
                                 'skirts', 'hats', 'dresses', 'coats-jackets', 'plus-size'],
                'featured': ['wardrobe-essentials', 'denim-everything', 'lifestyle-sneakers', 
                           'office-wear', 'gym-gear']
            },
            'men': {
                'name': 'Men',
                'subcategories': ['tshirts', 'shoes', 'shirts', 'bags', 'hoodies', 'hats', 'jeans', 
                                 'sweaters', 'sunglasses', 'coats-jackets', 'big-tall'],
                'featured': ['wardrobe-essentials', 'denim-everything', 'lifestyle-sneakers', 
                           'office-wear', 'gym-gear']
            },
            'watches': {
                'name': 'Watches',
                'subcategories': ['mens-watches', 'womens-watches', 'smart-watches', 'luxury-watches', 
                                 'sports-watches', 'vintage-watches', 'dress-watches', 'casual-watches'],
                'featured': ['best-sellers', 'new-arrivals', 'on-sale']
            },
            'jewellery': {
                'name': 'Jewellery',
                'subcategories': ['rings', 'necklaces', 'earrings', 'bracelets', 'pendants', 'chains', 
                                 'anklets', 'brooches', 'cufflinks'],
                'featured': ['gold-collection', 'silver-collection', 'diamond-collection', 'vintage-jewellery']
            },
            'accessories': {
                'name': 'Accessories',
                'subcategories': ['bags', 'belts', 'hats-caps', 'sunglasses', 'scarves', 'wallets', 
                                 'phone-cases', 'keychains', 'hair-accessories', 'ties-bow-ties'],
                'featured': ['designer-bags', 'luxury-accessories', 'trending-now']
            }
        }
        
        # Handle both 'jewelry' (model) and 'jewellery' (documentation) for compatibility
        normalized_key = category_key
        if category_key == 'jewelry':
            normalized_key = 'jewellery'
        elif category_key == 'jewellery':
            normalized_key = 'jewellery'
        
        if normalized_key not in category_definitions:
            raise ValueError(f"Invalid category: {category_key}")
        
        category_info = category_definitions[normalized_key]
        
        # Subcategory name mappings
        subcategory_names = {
            'tops': 'Tops', 'shoes': 'Shoes', 'jeans': 'Jeans', 'bags-purses': 'Bags & Purses',
            'sweaters': 'Sweaters', 'sunglasses': 'Sunglasses', 'skirts': 'Skirts', 'hats': 'Hats',
            'dresses': 'Dresses', 'coats-jackets': 'Coats & Jackets', 'plus-size': 'Plus Size',
            'tshirts': 'T-shirts', 'shirts': 'Shirts', 'bags': 'Bags', 'hoodies': 'Hoodies',
            'big-tall': 'Big & Tall', 'mens-watches': "Men's Watches", 'womens-watches': "Women's Watches",
            'smart-watches': 'Smart Watches', 'luxury-watches': 'Luxury Watches', 
            'sports-watches': 'Sports Watches', 'vintage-watches': 'Vintage Watches',
            'dress-watches': 'Dress Watches', 'casual-watches': 'Casual Watches',
            'rings': 'Rings', 'necklaces': 'Necklaces', 'earrings': 'Earrings', 'bracelets': 'Bracelets',
            'pendants': 'Pendants', 'chains': 'Chains', 'anklets': 'Anklets', 'brooches': 'Brooches',
            'cufflinks': 'Cufflinks', 'belts': 'Belts', 'hats-caps': 'Hats & Caps', 'scarves': 'Scarves',
            'wallets': 'Wallets', 'phone-cases': 'Phone Cases', 'keychains': 'Keychains',
            'hair-accessories': 'Hair Accessories', 'ties-bow-ties': 'Ties & Bow Ties'
        }
        
        # Featured collection name mappings
        featured_names = {
            'wardrobe-essentials': 'Wardrobe essentials',
            'denim-everything': 'Denim everything',
            'lifestyle-sneakers': 'Lifestyle sneakers',
            'office-wear': 'Office wear',
            'gym-gear': 'Gym gear',
            'best-sellers': 'Best Sellers',
            'new-arrivals': 'New Arrivals',
            'on-sale': 'On Sale',
            'gold-collection': 'Gold Collection',
            'silver-collection': 'Silver Collection',
            'diamond-collection': 'Diamond Collection',
            'vintage-jewellery': 'Vintage Jewellery',
            'designer-bags': 'Designer Bags',
            'luxury-accessories': 'Luxury Accessories',
            'trending-now': 'Trending Now'
        }
        
        # Handle both 'jewelry' (model) and 'jewellery' (documentation) for compatibility
        normalized_key = category_key
        if category_key == 'jewelry':
            normalized_key = 'jewelry'  # Use model key for query
        elif category_key == 'jewellery':
            normalized_key = 'jewelry'  # Use model key for query
        
        # Count total products
        total_products = Product.objects(
            category=normalized_key,
            status='active',
            approved=True
        ).count()
        
        # Build subcategories with counts
        subcategories_list = []
        for subcat_key in category_info['subcategories']:
            count = Product.objects(
                category=normalized_key,
                subcategory=subcat_key,
                status='active',
                approved=True
            ).count()
            
            subcategories_list.append({
                'id': subcat_key,
                'name': subcategory_names.get(subcat_key, subcat_key.replace('-', ' ').title()),
                'key': subcat_key,
                'href': f'/{category_key}/{subcat_key}',
                'productCount': count
            })
        
        # Build featured collections with counts
        featured_list = []
        for feat_key in category_info['featured']:
            count = Product.objects(
                category=normalized_key,
                status='active',
                approved=True
            ).count()  # Simplified - enhance based on business logic
            
            featured_list.append({
                'id': feat_key,
                'name': featured_names.get(feat_key, feat_key.replace('-', ' ').title()),
                'key': feat_key,
                'href': f'/{category_key}/{feat_key}',
                'productCount': count
            })
        
        # Return with original category_key (jewellery) even if we queried with jewelry
        return {
            'id': category_key if category_key == 'jewellery' else normalized_key,
            'name': category_info['name'],
            'key': category_key if category_key == 'jewellery' else normalized_key,
            'href': f'/{category_key if category_key == "jewellery" else normalized_key}',
            'subCategories': subcategories_list,
            'featured': featured_list,
            'totalProducts': total_products
        }
    
    @staticmethod
    def get_category_filters(category_key, subcategory_key=None):
        """Get available filter options for a category/subcategory"""
        from collections import defaultdict
        
        # Handle both 'jewelry' (model) and 'jewellery' (documentation) for compatibility
        normalized_key = category_key
        if category_key == 'jewelry':
            normalized_key = 'jewelry'  # Use model key for query
        elif category_key == 'jewellery':
            normalized_key = 'jewelry'  # Use model key for query
        
        # Build query
        query = {
            'category': normalized_key,
            'status': 'active',
            'approved': True
        }
        
        if subcategory_key:
            query['subcategory'] = subcategory_key
        
        # Get distinct brands with counts
        brands_pipeline = [
            {'$match': {**query, 'brand': {'$exists': True, '$ne': None, '$ne': ''}}},
            {'$group': {'_id': '$brand', 'count': {'$sum': 1}}},
            {'$project': {'name': '$_id', 'count': 1, '_id': 0}},
            {'$sort': {'name': 1}}
        ]
        
        # Get distinct sizes with counts
        sizes_pipeline = [
            {'$match': {**query, 'size': {'$exists': True, '$ne': None, '$ne': ''}}},
            {'$group': {'_id': '$size', 'count': {'$sum': 1}}},
            {'$project': {'name': '$_id', 'count': 1, '_id': 0}},
            {'$sort': {'name': 1}}
        ]
        
        # Get distinct colors with counts
        colors_pipeline = [
            {'$match': {**query, 'color': {'$exists': True, '$ne': None, '$ne': ''}}},
            {'$group': {'_id': '$color', 'count': {'$sum': 1}}},
            {'$project': {'name': '$_id', 'count': 1, '_id': 0}},
            {'$sort': {'name': 1}}
        ]
        
        # Get distinct conditions with counts
        conditions_pipeline = [
            {'$match': {**query, 'condition': {'$exists': True, '$ne': None, '$ne': ''}}},
            {'$group': {'_id': '$condition', 'count': {'$sum': 1}}},
            {'$project': {'name': '$_id', 'count': 1, '_id': 0}},
            {'$sort': {'name': 1}}
        ]
        
        # Get price range
        price_pipeline = [
            {'$match': query},
            {'$group': {
                '_id': None,
                'min': {'$min': '$price'},
                'max': {'$max': '$price'}
            }}
        ]
        
        # Execute aggregations
        brands_data = list(Product.objects.aggregate(*brands_pipeline))
        sizes_data = list(Product.objects.aggregate(*sizes_pipeline))
        colors_data = list(Product.objects.aggregate(*colors_pipeline))
        conditions_data = list(Product.objects.aggregate(*conditions_pipeline))
        price_data = list(Product.objects.aggregate(*price_pipeline))
        
        # Format results
        brands = [{'name': item['name'], 'count': item['count']} for item in brands_data]
        sizes = [{'name': item['name'], 'count': item['count']} for item in sizes_data]
        colors = [{'name': item['name'], 'count': item['count']} for item in colors_data]
        conditions = [{'name': item['name'], 'count': item['count']} for item in conditions_data]
        
        price_range = {'min': 0.0, 'max': 0.0}
        if price_data and price_data[0].get('min') is not None:
            price_range = {
                'min': float(price_data[0]['min']),
                'max': float(price_data[0]['max'])
            }
        
        return {
            'brands': brands,
            'sizes': sizes,
            'colors': colors,
            'conditions': conditions,
            'priceRange': price_range
        }


class OfferService:
    """Offer service"""
    
    @staticmethod
    def create_offer(buyer_id, product_id, offer_amount, shipping_address=None, zip_code=None, house_number=None):
        """Create an offer with optional shipping details"""
        product = Product.objects(id=product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        if offer_amount > product.price:
            raise ValueError("Offer amount cannot be greater than product price")
        
        buyer = User.objects(id=buyer_id).first()
        seller = User.objects(id=product.seller_id.id).first()
        
        # Prevent sellers from buying their own products
        if str(buyer_id) == str(product.seller_id.id):
            raise ValueError("You cannot make an offer on your own product")
        
        offer = Offer(
            product_id=product_id,
            buyer_id=buyer_id,
            buyer_name=buyer.full_name,
            seller_id=product.seller_id.id,
            seller_name=seller.full_name,
            offer_amount=float(offer_amount),
            original_price=product.price,
            currency=product.currency or 'SAR',  # Store currency from product at time of offer
            shipping_cost=product.shipping_cost,
            expiration_date=datetime.utcnow() + timedelta(days=7)
        )
        
        # Add shipping details if provided
        if shipping_address:
            offer.shipping_address = shipping_address
        if zip_code:
            offer.zip_code = zip_code
        if house_number:
            offer.house_number = house_number
        
        offer.save()
        
        # Send notification to seller - new offer received
        try:
            from notifications.notification_helper import NotificationHelper
            NotificationHelper.send_new_offer_received(str(offer.seller_id.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending new offer notification: {str(e)}")
        
        return offer
    
    @staticmethod
    def get_offers(user_id, user_type='buyer'):
        """Get offers for user"""
        # Exclude new optional fields to avoid validation errors on old documents
        # Only load fields that exist in all documents
        fields_to_load = [
            'id', 'product_id', 'buyer_id', 'buyer_name', 'seller_id', 'seller_name',
            'offer_amount', 'original_price', 'shipping_cost', 'shipping_address',
            'zip_code', 'house_number', 'status', 'expiration_date', 'counter_offer_amount',
            'created_at', 'updated_at'
        ]
        
        if user_type == 'buyer':
            offers = Offer.objects(buyer_id=user_id).only(*fields_to_load).order_by('-created_at')
        else:
            offers = Offer.objects(seller_id=user_id).only(*fields_to_load).order_by('-created_at')
        
        return offers
    
    @staticmethod
    def accept_offer(offer_id, seller_id):
        """Accept offer"""
        offer = Offer.objects(id=offer_id, seller_id=seller_id).first()
        if not offer:
            raise ValueError("Offer not found")
        
        offer.status = 'accepted'
        offer.updated_at = datetime.utcnow()
        offer.save()
        
        # Update product quantity - deduct 1 when offer is accepted
        if offer.product_id:
            product = Product.objects(id=offer.product_id.id).first()
            if product:
                # Deduct 1 from quantity
                if product.quantity is None or product.quantity <= 0:
                    product.quantity = 0
                else:
                    product.quantity -= 1
                
                # Mark as sold if quantity reaches 0
                if product.quantity <= 0:
                    product.status = 'sold'
                
                product.updated_at = datetime.utcnow()
                product.save()
        
        # Send notification to buyer - offer accepted
        try:
            from notifications.notification_helper import NotificationHelper
            NotificationHelper.send_offer_accepted(
                str(offer.buyer_id.id),
                offer_id=str(offer.id),
                product_id=str(offer.product_id.id)
            )
        except Exception as e:
            import logging
            logging.error(f"Error sending offer accepted notification: {str(e)}")
        
        return offer
    
    @staticmethod
    def reject_offer(offer_id, seller_id):
        """Reject offer"""
        offer = Offer.objects(id=offer_id, seller_id=seller_id).first()
        if not offer:
            raise ValueError("Offer not found")
        
        offer.status = 'rejected'
        offer.updated_at = datetime.utcnow()
        offer.save()
        
        # Send notification to buyer - offer declined
        try:
            from notifications.notification_helper import NotificationHelper
            NotificationHelper.send_offer_declined(str(offer.buyer_id.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending offer declined notification: {str(e)}")
        
        return offer
    
    @staticmethod
    def counter_offer(offer_id, user_id, counter_amount):
        """Counter offer - allows both buyer and seller to counter (max 4 times each)"""
        offer = Offer.objects(id=offer_id).first()
        if not offer:
            raise ValueError("Offer not found. It may have been deleted or already processed.")
        
        # Determine if user is buyer or seller
        is_buyer = str(offer.buyer_id.id) == str(user_id)
        is_seller = str(offer.seller_id.id) == str(user_id)
        
        if not is_buyer and not is_seller:
            raise ValueError("You are not authorized to counter this offer")
        
        # Determine who is countering
        counterer_type = 'buyer' if is_buyer else 'seller'
        
        # Check if same person is trying to counter twice in a row
        # Handle case where last_countered_by might not exist in old documents
        if hasattr(offer, 'last_countered_by') and offer.last_countered_by == counterer_type:
            raise ValueError("You cannot counter your own last counter. Wait for the other party to respond.")
        
        # Check counter limits (max 4 counters per person)
        # Handle case where counter counts might not exist in old documents
        buyer_count = getattr(offer, 'buyer_counter_count', 0) or 0
        seller_count = getattr(offer, 'seller_counter_count', 0) or 0
        
        if is_buyer and buyer_count >= 4:
            raise ValueError("You have reached the maximum number of counter offers (4). Please accept or reject the current offer.")
        
        if is_seller and seller_count >= 4:
            raise ValueError("You have reached the maximum number of counter offers (4). Please accept or reject the current offer.")
        
        # Update counter offer
        offer.counter_offer_amount = float(counter_amount)
        offer.status = 'countered'
        offer.last_countered_by = counterer_type
        
        # Increment counter count
        # Handle case where counter counts might not exist in old documents
        if is_buyer:
            offer.buyer_counter_count = (getattr(offer, 'buyer_counter_count', 0) or 0) + 1
        else:
            offer.seller_counter_count = (getattr(offer, 'seller_counter_count', 0) or 0) + 1
        
        offer.updated_at = datetime.utcnow()
        offer.save()
        
        # Send notification to the other party
        try:
            from notifications.notification_helper import NotificationHelper
            if is_buyer:
                # Buyer countered - notify seller
                NotificationHelper.send_counter_offer_received(str(offer.seller_id.id), 'seller')
            else:
                # Seller countered - notify buyer
                NotificationHelper.send_counter_offer_received(str(offer.buyer_id.id), 'buyer')
        except Exception as e:
            import logging
            logging.error(f"Error sending counter offer notification: {str(e)}")
        
        return offer
    
    @staticmethod
    def get_order_summary(offer_id, user_id):
        """
        Get order summary for an accepted offer
        Returns product details, prices, shipping, VAT (15%), and final total
        """
        from products.services import OrderService
        
        # Get the offer
        offer = Offer.objects(id=offer_id).first()
        if not offer:
            raise ValueError("Offer not found")
        
        # Check if offer is accepted
        if offer.status != 'accepted':
            raise ValueError("Offer must be accepted to view order summary")
        
        # Verify user has access (either buyer or seller)
        if str(offer.buyer_id.id) != str(user_id) and str(offer.seller_id.id) != str(user_id):
            raise ValueError("You don't have permission to view this order summary")
        
        # Get product details
        product = Product.objects(id=offer.product_id.id).first()
        if not product:
            raise ValueError("Product not found")
        
        # Get product image (first image from images array)
        product_image = product.images[0] if product.images and len(product.images) > 0 else ''
        
        # Get prices
        original_price = float(offer.original_price)
        # Determine the accepted offer price:
        # - If counter_offer_amount exists, it means seller made a counter offer (or multiple counter offers)
        #   and buyer accepted the latest counter offer. Use the counter_offer_amount (latest counter).
        # - If no counter_offer_amount, it means seller accepted buyer's original offer. Use offer_amount.
        # Note: If seller sends multiple counter offers, each one overwrites counter_offer_amount,
        # so the latest counter offer amount is always stored in counter_offer_amount.
        if offer.counter_offer_amount is not None:
            offer_price = float(offer.counter_offer_amount)
        else:
            offer_price = float(offer.offer_amount)
        shipping_price = float(offer.shipping_cost)
        
        # Calculate platform fee (based on offer price)
        platform_fee = OrderService.calculate_platform_fee(offer_price)
        
        # Calculate subtotal (offer price + shipping + platform fee)
        subtotal = offer_price + shipping_price + platform_fee
        
        # Calculate VAT/Tax if product has tax_percentage set
        vat_percentage = None
        vat_amount = 0.0
        if product.tax_percentage is not None and product.tax_percentage > 0:
            vat_percentage = float(product.tax_percentage)
            vat_amount = round(subtotal * (vat_percentage / 100.0), 2)
        
        # Calculate final total (subtotal + VAT if tax exists)
        final_total = round(subtotal + vat_amount, 2)
        
        # Get currency from offer (stored when offer was created) or product as fallback
        currency = offer.currency if hasattr(offer, 'currency') and offer.currency else (product.currency if product and hasattr(product, 'currency') and product.currency else 'SAR')
        
        result = {
            'product': {
                'id': str(product.id),
                'title': product.title,
                'image': product_image
            },
            'currency': currency,  # Include currency in order summary
            'originalPrice': original_price,
            'offerPrice': offer_price,
            'shippingPrice': shipping_price,
            'platformFee': platform_fee,
            'subtotal': round(subtotal, 2),
            'finalTotal': final_total
        }
        
        # Only include VAT in response if tax is applied
        if vat_percentage is not None and vat_percentage > 0:
            result['vat'] = {
                'percentage': vat_percentage,
                'amount': vat_amount
            }
        
        return result


class OrderService:
    """Order service"""
    
    @staticmethod
    def calculate_platform_fee(order_amount):
        """
        Calculate platform fee based on order amount using configurable settings
        Rules:
        - Minimum fee (for amounts <= threshold_amount_1)
        - Fee percentage (for amounts > threshold_amount_1 and <= threshold_amount_2)
        - Maximum fee (for amounts > threshold_amount_2)
        """
        from admin_dashboard.models import FeeSettings
        
        # Get fee settings from database
        settings = FeeSettings.objects().first()
        if not settings:
            # Use defaults if settings don't exist
            minimum_fee = 5.0
            fee_percentage = 5.0
            threshold_1 = 100.0
            threshold_2 = 2000.0
            maximum_fee = 100.0
        else:
            minimum_fee = settings.minimum_fee
            fee_percentage = settings.fee_percentage
            threshold_1 = settings.threshold_amount_1
            threshold_2 = settings.threshold_amount_2
            maximum_fee = settings.maximum_fee
        
        if order_amount <= threshold_1:
            return round(minimum_fee, 2)
        elif order_amount <= threshold_2:
            return round(order_amount * (fee_percentage / 100.0), 2)
        else:
            return round(maximum_fee, 2)
    
    @staticmethod
    def calculate_affiliate_commission(platform_fee, affiliate=None):
        """
        Calculate affiliate commission based on affiliate's commission rate or default
        If affiliate has individual commission rate (and it's not '0'), use it; otherwise use default from settings
        """
        from admin_dashboard.models import FeeSettings
        
        # Get default commission percentage from settings
        settings = FeeSettings.objects().first()
        if settings:
            default_commission_percentage = settings.default_affiliate_commission_percentage
        else:
            default_commission_percentage = 25.0  # Default 25%
        
        # Use affiliate's individual commission rate if available and valid, otherwise use default
        commission_percentage = default_commission_percentage
        if affiliate and affiliate.commission_rate:
            try:
                affiliate_rate = float(affiliate.commission_rate)
                # Only use affiliate's rate if it's greater than 0 (0 means use default)
                if affiliate_rate > 0:
                    commission_percentage = affiliate_rate
            except (ValueError, TypeError):
                pass  # Use default if conversion fails
        
        return round(platform_fee * (commission_percentage / 100.0), 2)
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number"""
        return f"ORD-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"
    
    @staticmethod
    def create_order(buyer_id, data):
        """
        Create order from checkout.
        Returns a single Order instance.
        """
        buyer = User.objects(id=buyer_id).first()
        if not buyer:
            raise ValueError("Buyer not found")
        
        order_number = OrderService.generate_order_number()
        while Order.objects(order_number=order_number).first():
            order_number = OrderService.generate_order_number()
        
        # Get affiliate code if provided in checkout, otherwise will use product's affiliate_code (from listing)
        affiliate_code = data.get('affiliateCode', '').strip() if data.get('affiliateCode') else None
        
        affiliate = None
        if affiliate_code:
            from authentication.models import Affiliate
            affiliate = Affiliate.objects(affiliate_code=affiliate_code, status='active').first()
            if not affiliate:
                affiliate_code = None  # Invalid affiliate code, ignore it
        
        if 'offerId' in data and data['offerId']:
            # Order from offer
            offer = Offer.objects(id=data['offerId']).first()
            if not offer or offer.status != 'accepted':
                raise ValueError("Invalid offer")
            
            product = Product.objects(id=offer.product_id.id).first()
            
            # Prevent sellers from buying their own products
            if str(buyer_id) == str(offer.seller_id.id):
                raise ValueError("You cannot purchase your own product")
            
            # If no affiliate code in checkout, use product's affiliate_code (from listing)
            if not affiliate_code and product and product.affiliate_code:
                affiliate_code = product.affiliate_code.strip()
                if affiliate_code:
                    from authentication.models import Affiliate
                    affiliate = Affiliate.objects(affiliate_code=affiliate_code, status='active').first()
                    if not affiliate:
                        affiliate_code = None  # Invalid affiliate code, ignore it
            
            base_amount = offer.offer_amount
            shipping = offer.shipping_cost
            subtotal = base_amount + shipping
        else:
            # Order from cart
            cart_items = data.get('cartItems') or []
            if not cart_items:
                raise ValueError("No items in cart")

            # Load all products from cart
            products_in_cart = []
            for pid in cart_items:
                product = Product.objects(id=pid).first()
                if not product:
                    raise ValueError("One of the products in cart was not found")
                products_in_cart.append(product)

            # Validate products and prevent self-purchase
            for p in products_in_cart:
                if p.status != 'active':
                    raise ValueError("One of the products in cart is not available")
                if str(buyer_id) == str(p.seller_id.id):
                    raise ValueError("You cannot purchase your own product")

            # Check that all products are from the same seller
            seller_ids = {str(p.seller_id.id) for p in products_in_cart}
            if len(seller_ids) > 1:
                raise ValueError("All items in cart must be from the same seller")

            # Calculate totals
            base_amount = 0.0
            shipping = 0.0
            for p in products_in_cart:
                base_amount += p.price
                shipping += p.shipping_cost

            subtotal = base_amount + shipping
            # Use first product as the primary product
            product = products_in_cart[0]
            product_id = str(product.id)
            seller = User.objects(id=str(product.seller_id.id)).first()
        
        # Create order
        if 'offerId' in data and data['offerId'] or (product is not None and seller is not None):
            # Calculate platform fee (based on base amount, not including shipping)
            platform_fee = OrderService.calculate_platform_fee(base_amount)
            
            # Calculate affiliate commission (using affiliate's individual rate or default)
            # IMPORTANT: Affiliate commission is calculated from platform fee, NOT from order fee
            # The commission comes from the platform's revenue, not from the seller's payout
            affiliate_commission = 0.0
            if affiliate and affiliate_code:
                affiliate_commission = OrderService.calculate_affiliate_commission(platform_fee, affiliate)
            
            # Calculate seller payout (subtotal - platform fee)
            # NOTE: Affiliate commission is NOT deducted from seller payout
            # Seller pays only the platform fee, and affiliate commission comes from platform fee
            seller_payout = subtotal - platform_fee
            
            # Total price includes everything (buyer pays: base + shipping + platform fee)
            total_price = base_amount + shipping + platform_fee
            
            # Create order
            if 'offerId' in data and data['offerId']:
                # Get currency from offer (stored when offer was created)
                order_currency = offer.currency if hasattr(offer, 'currency') and offer.currency else (product.currency if product else 'SAR')
                order = Order(
                    order_number=order_number,
                    buyer_id=buyer_id,
                    buyer_name=buyer.full_name,
                    seller_id=offer.seller_id.id,
                    seller_name=offer.seller_name,
                    product_id=offer.product_id.id,
                    product_title=product.title,
                    offer_id=offer.id,
                    price=offer.original_price,
                    offer_price=offer.offer_amount,
                    currency=order_currency,  # Store currency from offer
                    shipping_cost=shipping,
                    total_price=total_price,
                    dolabb_fee=platform_fee,
                    affiliate_code=affiliate_code,
                    affiliate_commission=affiliate_commission,
                    seller_payout=seller_payout
                )
            else:
                # Get currency from product
                order_currency = product.currency if product and hasattr(product, 'currency') and product.currency else 'SAR'
                order = Order(
                    order_number=order_number,
                    buyer_id=buyer_id,
                    buyer_name=buyer.full_name,
                    seller_id=product.seller_id.id,
                    seller_name=seller.full_name,
                    product_id=product_id,
                    product_title=product.title,
                    price=base_amount,
                    currency=order_currency,  # Store currency from product
                    shipping_cost=shipping,
                    total_price=total_price,
                    dolabb_fee=platform_fee,
                    affiliate_code=affiliate_code,
                    affiliate_commission=affiliate_commission,
                    seller_payout=seller_payout
                )
            
            # Add delivery address
            address = data.get('deliveryAddress', {})
            order.delivery_address = address.get('address', '')
            order.full_name = address.get('fullName', '')
            order.phone = address.get('phone', '')
            order.city = address.get('city', '')
            order.postal_code = address.get('postalCode', '')
            order.country = address.get('country', '')
            order.additional_info = address.get('additionalInfo', '')
            
            order.save()
            
            # DO NOT send notifications here - emails will be sent only when payment is confirmed as 'paid'
            # This prevents sending "order created" and "item sold" emails for failed payments
            # Notifications will be sent in verify_payment or payment_webhook when payment status is 'paid'
            
            # Create affiliate transaction record (but don't update earnings yet - only when payment is completed)
            if affiliate and affiliate_code and affiliate_commission > 0:
                try:
                    from affiliates.models import AffiliateTransaction
                    from admin_dashboard.models import FeeSettings
                    
                    # Get the commission rate that was used
                    settings = FeeSettings.objects().first()
                    if affiliate and affiliate.commission_rate:
                        try:
                            used_commission_rate = float(affiliate.commission_rate)
                        except (ValueError, TypeError):
                            used_commission_rate = settings.default_affiliate_commission_percentage if settings else 25.0
                    else:
                        used_commission_rate = settings.default_affiliate_commission_percentage if settings else 25.0
                    
                    # Get currency from order
                    order_currency = order.currency if hasattr(order, 'currency') and order.currency else 'SAR'
                    
                    transaction = AffiliateTransaction(
                        affiliate_id=affiliate.id,
                        affiliate_name=affiliate.full_name,
                        referred_user_id=buyer_id,
                        referred_user_name=buyer.full_name,
                        transaction_id=order.id,
                        commission_rate=used_commission_rate,  # Store the actual rate used
                        commission_amount=affiliate_commission,
                        currency=order_currency,  # Store currency from order
                        status='pending'  # Will be updated to 'paid' when payment is completed
                    )
                    transaction.save()
                except Exception as e:
                    # Log error but don't fail the order creation
                    import logging
                    logging.error(f"Failed to create affiliate transaction: {str(e)}")
            
            return order
    
    @staticmethod
    def update_affiliate_earnings_on_payment_completion(order):
        """
        Update affiliate earnings when payment is completed.
        This reflects earnings immediately on payment success, but keeps transaction status as 'pending'
        until buyer submits review AND seller uploads shipment_proof.
        """
        # Only process if payment is completed
        if order.payment_status != 'completed':
            return
        
        if not order.affiliate_code or order.affiliate_commission <= 0:
            return
        
        try:
            from authentication.models import Affiliate
            from affiliates.models import AffiliateTransaction
            
            affiliate = Affiliate.objects(affiliate_code=order.affiliate_code, status='active').first()
            if not affiliate:
                return
            
            # Check if earnings were already updated for this order
            existing_transaction = AffiliateTransaction.objects(
                transaction_id=order.id,
                affiliate_id=affiliate.id
            ).first()
            
            if existing_transaction and existing_transaction.status == 'paid':
                # Already fully processed, skip to avoid double-counting
                return
            
            # Get currency from order
            order_currency = order.currency if hasattr(order, 'currency') and order.currency else 'SAR'
            
            # Get current earnings (legacy fields - kept for backward compatibility)
            current_earnings = float(affiliate.total_earnings) if affiliate.total_earnings else 0.0
            current_pending = float(affiliate.pending_earnings) if affiliate.pending_earnings else 0.0
            
            # Update legacy fields (for backward compatibility)
            affiliate.total_earnings = str(round(current_earnings + order.affiliate_commission, 2))
            affiliate.pending_earnings = str(round(current_pending + order.affiliate_commission, 2))
            
            # Update currency-separated earnings
            if not affiliate.earnings_by_currency:
                affiliate.earnings_by_currency = {}
            
            currency_earnings = affiliate.earnings_by_currency.get(order_currency, {
                'total': 0.0,
                'pending': 0.0,
                'paid': 0.0
            })
            
            # Add commission to currency-specific earnings
            currency_earnings['total'] = round(currency_earnings.get('total', 0.0) + order.affiliate_commission, 2)
            currency_earnings['pending'] = round(currency_earnings.get('pending', 0.0) + order.affiliate_commission, 2)
            affiliate.earnings_by_currency[order_currency] = currency_earnings
            
            affiliate.last_activity = datetime.utcnow()
            affiliate.save()
            
            # Ensure transaction exists and is marked as 'pending' (will be updated to 'paid' when review + shipment proof are provided)
            if not existing_transaction:
                # Create transaction if it doesn't exist (shouldn't happen normally, but handle edge cases)
                transaction = AffiliateTransaction(
                    affiliate_id=affiliate.id,
                    affiliate_name=affiliate.full_name,
                    referred_user_id=order.buyer_id.id,
                    referred_user_name=order.buyer_name,
                    transaction_id=order.id,
                    commission_rate=float(affiliate.commission_rate) if affiliate.commission_rate else 0.0,
                    commission_amount=order.affiliate_commission,
                    currency=order_currency,  # Store currency
                    status='pending'  # Will be updated to 'paid' when review + shipment proof are provided
                )
                transaction.save()
            elif existing_transaction.status != 'paid':
                # Keep status as 'pending' (will be updated to 'paid' later)
                existing_transaction.status = 'pending'
                existing_transaction.save()
            
        except Exception as e:
            # Log error but don't fail the process
            import logging
            logging.error(f"Failed to update affiliate earnings on payment completion: {str(e)}")
    
    @staticmethod
    def update_affiliate_earnings_on_review_and_shipment(order):
        """
        Update affiliate transaction status to 'paid' when buyer submits review AND seller has uploaded shipment_proof.
        Earnings are already added on payment completion, so this method only updates the transaction status.
        This ensures earnings are marked as 'paid' (available for payout) only when the transaction is fully completed:
        - Payment is completed (earnings already added)
        - Buyer has reviewed
        - Seller has uploaded shipment proof (can request payout)
        """
        # Only process if payment is completed
        if order.payment_status != 'completed':
            return
        
        # Only process if shipment proof is uploaded (seller can request payout)
        if not order.shipment_proof or not order.shipment_proof.strip():
            return
        
        # Only process if buyer has submitted review
        if not order.review_submitted:
            return
            
        if not order.affiliate_code or order.affiliate_commission <= 0:
            return
        
        try:
            from authentication.models import Affiliate
            from affiliates.models import AffiliateTransaction
            
            affiliate = Affiliate.objects(affiliate_code=order.affiliate_code, status='active').first()
            if not affiliate:
                return
            
            # Find the transaction for this order
            existing_transaction = AffiliateTransaction.objects(
                transaction_id=order.id,
                affiliate_id=affiliate.id
            ).first()
            
            if not existing_transaction:
                # Transaction should exist (created on order creation), but if not, create it
                # This handles edge cases where payment was completed but transaction wasn't created
                transaction = AffiliateTransaction(
                    affiliate_id=affiliate.id,
                    affiliate_name=affiliate.full_name,
                    referred_user_id=order.buyer_id.id,
                    referred_user_name=order.buyer_name,
                    transaction_id=order.id,
                    commission_rate=float(affiliate.commission_rate) if affiliate.commission_rate else 0.0,
                    commission_amount=order.affiliate_commission,
                    status='paid'
                )
                transaction.save()
                
                # Add earnings if they weren't added on payment completion (edge case)
                current_earnings = float(affiliate.total_earnings) if affiliate.total_earnings else 0.0
                current_pending = float(affiliate.pending_earnings) if affiliate.pending_earnings else 0.0
                
                # Check if earnings need to be added (rough check - if total_earnings is 0 or very low)
                # This is a fallback for edge cases
                if current_earnings < order.affiliate_commission:
                    affiliate.total_earnings = str(round(current_earnings + order.affiliate_commission, 2))
                    affiliate.pending_earnings = str(round(current_pending + order.affiliate_commission, 2))
                    affiliate.last_activity = datetime.utcnow()
                    affiliate.save()
            elif existing_transaction.status != 'paid':
                # Update transaction status to 'paid' (earnings were already added on payment completion)
                existing_transaction.status = 'paid'
                existing_transaction.save()
                
                # Send commission approved notification
                try:
                    from notifications.notification_helper import NotificationHelper
                    NotificationHelper.send_commission_approved(str(affiliate.id))
                except Exception as e:
                    import logging
                    logging.error(f"Error sending commission approved notification: {str(e)}")
            
        except Exception as e:
            # Log error but don't fail the process
            import logging
            logging.error(f"Failed to update affiliate earnings: {str(e)}")
    
    @staticmethod
    def get_user_orders(user_id, user_type='buyer', status=None, payment_status=None, page=1, limit=20):
        """Get orders for user with optional status and payment_status filters"""
        if user_type == 'buyer':
            query = Order.objects(buyer_id=user_id)
        else:
            query = Order.objects(seller_id=user_id)
        
        if status:
            query = query.filter(status=status)
        
        # Allow filtering by payment status (e.g., completed, pending)
        if payment_status:
            query = query.filter(payment_status=payment_status)
        
        total = query.count()
        skip = (page - 1) * limit
        orders = query.skip(skip).limit(limit).order_by('-created_at')
        
        return orders, total
    
    @staticmethod
    def update_order_status(order_id, seller_id, status, tracking_number=None, shipment_proof=None):
        """
        Update order status (for shipping)
        If shipment_proof is provided, it will be saved to the order.
        This is required for earnings to be available for payout.
        """
        order = Order.objects(id=order_id, seller_id=seller_id).first()
        if not order:
            raise ValueError("Order not found")
        
        old_status = order.status
        order.status = status
        if tracking_number:
            order.tracking_number = tracking_number
        if shipment_proof:
            order.shipment_proof = shipment_proof
        order.updated_at = datetime.utcnow()
        order.save()
        
        # Send notifications based on status change
        try:
            from notifications.notification_helper import NotificationHelper
            if status == 'cancelled' and old_status != 'cancelled':
                # Notify buyer - order canceled
                NotificationHelper.send_order_canceled(str(order.buyer_id.id))
                # Notify seller - buyer rejected order
                NotificationHelper.send_buyer_rejected_order(str(order.seller_id.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending order cancellation notifications: {str(e)}")
        
        # Reload order to get latest state
        order.reload()
        
        # Update affiliate earnings if shipment_proof is uploaded AND review already exists
        # This handles the case where seller uploads shipment_proof after buyer has reviewed
        if shipment_proof and shipment_proof.strip() and order.review_submitted:
            OrderService.update_affiliate_earnings_on_review_and_shipment(order)
        
        return order


class ReviewService:
    """Review service"""
    
    @staticmethod
    def create_review(order_id, buyer_id, rating, comment):
        """
        Create a review for an order
        
        Security checks to prevent spam and fake reviews:
        1. Order must exist and belong to the buyer (prevents unauthorized reviews)
        2. Order must have payment_status='completed' (only paid orders can be reviewed)
        3. Order must be delivered (only delivered orders can be reviewed)
        4. Order must not already be marked as reviewed (prevents duplicate submissions)
        5. Review must not already exist in database (database-level duplicate prevention)
        
        This ensures each buyer can only submit ONE review per purchase (order),
        preventing spam and ensuring review authenticity.
        """
        from products.models import Review, Order, Product, User
        
        # Verify order exists and belongs to buyer
        order = Order.objects(id=order_id, buyer_id=buyer_id).first()
        if not order:
            raise ValueError("Order not found or does not belong to buyer")
        
        # Security: Only allow reviews for completed payments
        if order.payment_status != 'completed':
            raise ValueError("Can only review orders with completed payment")
        
        # Check if order is delivered
        if order.status != 'delivered':
            raise ValueError("Can only review delivered orders")
        
        # Security check 1: Check if order is already marked as reviewed (first check)
        if hasattr(order, 'review_submitted') and order.review_submitted:
            raise ValueError("Review already submitted for this order. You can only submit one review per purchase.")
        
        # Security check 2: Check if review already exists for this order (database-level check)
        # This prevents duplicate reviews and ensures one review per order per buyer
        existing_review = Review.objects(order_id=order_id, buyer_id=buyer_id).first()
        if existing_review:
            raise ValueError("Review already submitted for this order. Each buyer can only submit one review per purchase to prevent spam and ensure review authenticity.")
        
        # Get product and seller info
        product = Product.objects(id=order.product_id.id).first()
        seller = User.objects(id=order.seller_id.id).first()
        buyer = User.objects(id=buyer_id).first()
        
        # Create review
        review = Review(
            order_id=order,
            buyer_id=buyer,
            buyer_name=buyer.full_name or buyer.username if buyer else '',
            seller_id=seller,
            seller_name=order.seller_name or (seller.username if seller else ''),
            product_id=product,
            product_title=order.product_title or (product.title if product else ''),
            rating=rating,
            comment=comment
        )
        review.save()
        
        # Mark order as reviewed
        order.review_submitted = True
        order.save()
        
        # Send notification to seller - buyer confirmed delivery
        try:
            from notifications.notification_helper import NotificationHelper
            NotificationHelper.send_buyer_confirmed_delivery(str(order.seller_id.id))
        except Exception as e:
            import logging
            logging.error(f"Error sending review notification: {str(e)}")
        
        # Update affiliate earnings if review is submitted AND shipment_proof is uploaded
        # This ensures earnings are only credited when transaction is fully completed
        if order.shipment_proof and order.shipment_proof.strip():
            OrderService.update_affiliate_earnings_on_review_and_shipment(order)
        
        return review
    
    @staticmethod
    def get_reviews_for_product(product_id, page=1, limit=20):
        """Get reviews for a product"""
        from products.models import Review
        
        query = Review.objects(product_id=product_id)
        total = query.count()
        skip = (page - 1) * limit
        reviews = query.skip(skip).limit(limit).order_by('-created_at')
        
        return reviews, total
    
    @staticmethod
    def get_reviews_for_seller(seller_id, page=1, limit=20):
        """Get reviews for a seller"""
        from products.models import Review
        
        query = Review.objects(seller_id=seller_id)
        total = query.count()
        skip = (page - 1) * limit
        reviews = query.skip(skip).limit(limit).order_by('-created_at')
        
        return reviews, total
    
    @staticmethod
    def get_buyer_reviews(buyer_id, page=1, limit=20):
        """Get reviews submitted by a buyer"""
        from products.models import Review
        
        query = Review.objects(buyer_id=buyer_id)
        total = query.count()
        skip = (page - 1) * limit
        reviews = query.skip(skip).limit(limit).order_by('-created_at')
        
        return reviews, total
    
    @staticmethod
    def get_seller_rating_stats(seller_id):
        """Get rating statistics for a seller"""
        from products.models import Review
        
        reviews = Review.objects(seller_id=seller_id)
        total_reviews = reviews.count()
        
        if total_reviews == 0:
            return {
                'average_rating': 0,
                'total_reviews': 0,
                'rating_distribution': {
                    '5': 0,
                    '4': 0,
                    '3': 0,
                    '2': 0,
                    '1': 0
                }
            }
        
        total_rating = sum(review.rating for review in reviews)
        average_rating = round(total_rating / total_reviews, 2)
        
        rating_distribution = {
            '5': reviews.filter(rating=5).count(),
            '4': reviews.filter(rating=4).count(),
            '3': reviews.filter(rating=3).count(),
            '2': reviews.filter(rating=2).count(),
            '1': reviews.filter(rating=1).count()
        }
        
        return {
            'average_rating': average_rating,
            'total_reviews': total_reviews,
            'rating_distribution': rating_distribution
        }

