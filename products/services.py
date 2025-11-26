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
        if seller.role == 'buyer':
            seller.role = 'seller'
            seller.save()
        
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
        
        # Set affiliate code only if provided and not empty
        affiliate_code = data.get('Affiliate Code (Optional)', '').strip() if data.get('Affiliate Code (Optional)') else ''
        if affiliate_code:
            product.affiliate_code = affiliate_code
            
            # Update affiliate code usage count when product is created
            try:
                from authentication.models import Affiliate
                affiliate = Affiliate.objects(affiliate_code=affiliate_code, status='active').first()
                if affiliate:
                    current_count = int(affiliate.code_usage_count) if affiliate.code_usage_count else 0
                    affiliate.code_usage_count = str(current_count + 1)
                    affiliate.last_activity = datetime.utcnow()
                    affiliate.save()
            except Exception as e:
                # Log error but don't fail product creation
                import logging
                logging.error(f"Failed to update affiliate code usage count: {str(e)}")
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
        
        total = query.count()
        skip = (page - 1) * limit
        products = query.skip(skip).limit(limit)
        
        return products, total
    
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
            affiliate_code = data['Affiliate Code (Optional)']
            # Only set if provided and not empty
            product.affiliate_code = affiliate_code if affiliate_code and affiliate_code.strip() else None
        
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
    def get_featured_products(limit=10, page=1, user_id=None):
        """Get featured products"""
        from mongoengine import Q
        if user_id:
            from bson import ObjectId
            try:
                user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
                query = Product.objects(
                    Q(status='active') & (Q(approved=True) | (Q(seller_id=user_obj_id) & Q(approved=False)))
                ).order_by('-likes_count', '-created_at')
            except:
                query = Product.objects(status='active', approved=True).order_by('-likes_count', '-created_at')
        else:
            query = Product.objects(status='active', approved=True).order_by('-likes_count', '-created_at')
        total = query.count()
        skip = (page - 1) * limit
        products = query.skip(skip).limit(limit)
        return products, total
    
    @staticmethod
    def get_trending_products(limit=10, page=1, user_id=None):
        """Get trending products"""
        # Trending based on recent activity (simplified)
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
        total = query.count()
        skip = (page - 1) * limit
        products = query.skip(skip).limit(limit)
        return products, total


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
        
        return offer
    
    @staticmethod
    def get_offers(user_id, user_type='buyer'):
        """Get offers for user"""
        if user_type == 'buyer':
            offers = Offer.objects(buyer_id=user_id).order_by('-created_at')
        else:
            offers = Offer.objects(seller_id=user_id).order_by('-created_at')
        
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
        
        return offer
    
    @staticmethod
    def counter_offer(offer_id, seller_id, counter_amount):
        """Counter offer"""
        offer = Offer.objects(id=offer_id, seller_id=seller_id).first()
        if not offer:
            raise ValueError("Offer not found")
        
        offer.counter_offer_amount = float(counter_amount)
        offer.status = 'countered'
        offer.updated_at = datetime.utcnow()
        offer.save()
        
        return offer


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
        """Create order from checkout"""
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
            # Order from cart (simplified - single product for now)
            product_id = data['cartItems'][0] if data.get('cartItems') else None
            if not product_id:
                raise ValueError("No items in cart")
            
            product = Product.objects(id=product_id).first()
            if not product:
                raise ValueError("Product not found")
            
            # Prevent sellers from buying their own products
            if str(buyer_id) == str(product.seller_id.id):
                raise ValueError("You cannot purchase your own product")
            
            # If no affiliate code in checkout, use product's affiliate_code (from listing)
            if not affiliate_code and product.affiliate_code:
                affiliate_code = product.affiliate_code.strip()
                if affiliate_code:
                    from authentication.models import Affiliate
                    affiliate = Affiliate.objects(affiliate_code=affiliate_code, status='active').first()
                    if not affiliate:
                        affiliate_code = None  # Invalid affiliate code, ignore it
            
            seller = User.objects(id=product.seller_id.id).first()
            base_amount = product.price
            shipping = product.shipping_cost
            subtotal = base_amount + shipping
        
        # Calculate platform fee (based on base amount, not including shipping)
        platform_fee = OrderService.calculate_platform_fee(base_amount)
        
        # Calculate affiliate commission (using affiliate's individual rate or default)
        affiliate_commission = 0.0
        if affiliate and affiliate_code:
            affiliate_commission = OrderService.calculate_affiliate_commission(platform_fee, affiliate)
        
        # Calculate seller payout (subtotal - platform fee)
        seller_payout = subtotal - platform_fee
        
        # Total price includes everything (buyer pays: base + shipping + platform fee)
        total_price = base_amount + shipping + platform_fee
        
        # Create order
        if 'offerId' in data and data['offerId']:
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
                shipping_cost=shipping,
                total_price=total_price,
                dolabb_fee=platform_fee,
                affiliate_code=affiliate_code,
                affiliate_commission=affiliate_commission,
                seller_payout=seller_payout
            )
        else:
            order = Order(
                order_number=order_number,
                buyer_id=buyer_id,
                buyer_name=buyer.full_name,
                seller_id=product.seller_id.id,
                seller_name=seller.full_name,
                product_id=product_id,
                product_title=product.title,
                price=base_amount,
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
                
                transaction = AffiliateTransaction(
                    affiliate_id=affiliate.id,
                    affiliate_name=affiliate.full_name,
                    referred_user_id=buyer_id,
                    referred_user_name=buyer.full_name,
                    transaction_id=order.id,
                    commission_rate=used_commission_rate,  # Store the actual rate used
                    commission_amount=affiliate_commission,
                    status='pending'  # Will be updated to 'paid' when payment is completed
                )
                transaction.save()
            except Exception as e:
                # Log error but don't fail the order creation
                import logging
                logging.error(f"Failed to create affiliate transaction: {str(e)}")
        
        return order
    
    @staticmethod
    def update_affiliate_earnings_on_review_and_shipment(order):
        """
        Update affiliate earnings when buyer submits review AND seller has uploaded shipment_proof
        This ensures earnings are only credited when the transaction is fully completed:
        - Payment is completed
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
            
            # Check if earnings were already updated for this order
            existing_transaction = AffiliateTransaction.objects(
                transaction_id=order.id,
                affiliate_id=affiliate.id
            ).first()
            
            if existing_transaction and existing_transaction.status == 'paid':
                # Already processed, skip to avoid double-counting
                return
            
            # Update total earnings (only when review is submitted and shipment proof is uploaded)
            current_earnings = float(affiliate.total_earnings) if affiliate.total_earnings else 0.0
            affiliate.total_earnings = str(round(current_earnings + order.affiliate_commission, 2))
            
            # Update pending earnings (only when review is submitted and shipment proof is uploaded)
            current_pending = float(affiliate.pending_earnings) if affiliate.pending_earnings else 0.0
            affiliate.pending_earnings = str(round(current_pending + order.affiliate_commission, 2))
            
            affiliate.last_activity = datetime.utcnow()
            affiliate.save()
            
            # Update transaction status to 'paid'
            if existing_transaction:
                existing_transaction.status = 'paid'
                existing_transaction.save()
            
        except Exception as e:
            # Log error but don't fail the process
            import logging
            logging.error(f"Failed to update affiliate earnings: {str(e)}")
    
    @staticmethod
    def get_user_orders(user_id, user_type='buyer', status=None, page=1, limit=20):
        """Get orders for user"""
        if user_type == 'buyer':
            query = Order.objects(buyer_id=user_id)
        else:
            query = Order.objects(seller_id=user_id)
        
        if status:
            query = query.filter(status=status)
        
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
        
        order.status = status
        if tracking_number:
            order.tracking_number = tracking_number
        if shipment_proof:
            order.shipment_proof = shipment_proof
        order.updated_at = datetime.utcnow()
        order.save()
        
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
        """Create a review for an order"""
        from products.models import Review, Order, Product, User
        
        # Verify order exists and belongs to buyer
        order = Order.objects(id=order_id, buyer_id=buyer_id).first()
        if not order:
            raise ValueError("Order not found or does not belong to buyer")
        
        # Check if order is delivered
        if order.status != 'delivered':
            raise ValueError("Can only review delivered orders")
        
        # Check if review already exists
        existing_review = Review.objects(order_id=order_id, buyer_id=buyer_id).first()
        if existing_review:
            raise ValueError("Review already submitted for this order")
        
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
