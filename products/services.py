"""
Product services
"""
from datetime import datetime, timedelta
from products.models import Product, SavedProduct, Offer, Order, ShippingInfo
from authentication.models import User
import random
import string


class ProductService:
    """Product service"""
    
    @staticmethod
    def create_product(seller_id, data):
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
            gender=data.get('Gender', ''),
            size=data.get('Size', ''),
            condition=data.get('Condition', 'good'),
            sku=data.get('SKU/ID (Optional)', ''),
            tags=data.get('Tags/Keywords', []),
            images=data.get('Images', []),
            shipping_cost=float(data.get('Shipping Cost', 0.0)),
            processing_time_days=int(data.get('Processing Time (days)', 7))
        )
        
        # Set affiliate code only if provided and not empty
        affiliate_code = data.get('Affiliate Code (Optional)', '').strip() if data.get('Affiliate Code (Optional)') else ''
        if affiliate_code:
            product.affiliate_code = affiliate_code
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
        if user_id:
            from bson import ObjectId
            try:
                user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
                query = Product.objects(
                    Q(status='active') & (Q(approved=True) | (Q(seller_id=user_obj_id) & Q(approved=False)))
                )
            except:
                query = Product.objects(status='active', approved=True)
        else:
            query = Product.objects(status='active', approved=True)
        
        if filters:
            if filters.get('category'):
                query = query.filter(category=filters['category'])
            if filters.get('subcategory'):
                query = query.filter(subcategory=filters['subcategory'])
            if filters.get('brand'):
                query = query.filter(brand=filters['brand'])
            if filters.get('minPrice'):
                query = query.filter(price__gte=float(filters['minPrice']))
            if filters.get('maxPrice'):
                query = query.filter(price__lte=float(filters['maxPrice']))
            if filters.get('size'):
                query = query.filter(size=filters['size'])
            if filters.get('condition'):
                query = query.filter(condition=filters['condition'])
            if filters.get('search'):
                query = query.filter(title__icontains=filters['search'])
        
        # Sorting
        sort_by = filters.get('sortBy', 'newest')
        if sort_by == 'price':
            query = query.order_by('price')
        elif sort_by == 'newest':
            query = query.order_by('-created_at')
        else:
            query = query.order_by('-created_at')
        
        total = query.count()
        skip = (page - 1) * limit
        products = query.skip(skip).limit(limit)
        
        return products, total
    
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
        if user_id:
            try:
                # Convert user_id to ObjectId if it's a string
                if isinstance(user_id, str):
                    user_obj_id = ObjectId(user_id)
                else:
                    user_obj_id = user_id
                
                saved = SavedProduct.objects(user_id=user_obj_id, product_id=product_obj_id).first()
                is_saved = saved is not None
            except:
                # If user_id conversion fails, just skip saved check
                pass
        
        return product, is_saved, is_liked
    
    @staticmethod
    def update_product(product_id, seller_id, data):
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
        if 'Gender' in data:
            product.gender = data['Gender']
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
            product.images = data['Images']
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
        product = Product.objects(id=product_id, seller_id=seller_id).first()
        if not product:
            raise ValueError("Product not found")
        
        product.status = 'removed'
        product.save()
        
        return product
    
    @staticmethod
    def get_seller_products(seller_id, status=None, page=1, limit=20):
        """Get products by seller"""
        query = Product.objects(seller_id=seller_id)
        
        if status:
            query = query.filter(status=status)
        
        total = query.count()
        skip = (page - 1) * limit
        products = query.skip(skip).limit(limit)
        
        return products, total
    
    @staticmethod
    def save_product(user_id, product_id):
        """Save product to wishlist"""
        saved = SavedProduct.objects(user_id=user_id, product_id=product_id).first()
        if saved:
            return False, saved
        
        saved = SavedProduct(user_id=user_id, product_id=product_id)
        saved.save()
        return True, saved
    
    @staticmethod
    def unsave_product(user_id, product_id):
        """Remove product from wishlist"""
        saved = SavedProduct.objects(user_id=user_id, product_id=product_id).first()
        if saved:
            saved.delete()
            return True
        return False
    
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
    def create_offer(buyer_id, product_id, offer_amount):
        """Create an offer"""
        product = Product.objects(id=product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        if offer_amount > product.price:
            raise ValueError("Offer amount cannot be greater than product price")
        
        buyer = User.objects(id=buyer_id).first()
        seller = User.objects(id=product.seller_id.id).first()
        
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
        
        if 'offerId' in data and data['offerId']:
            # Order from offer
            offer = Offer.objects(id=data['offerId']).first()
            if not offer or offer.status != 'accepted':
                raise ValueError("Invalid offer")
            
            product = Product.objects(id=offer.product_id.id).first()
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
                shipping_cost=offer.shipping_cost,
                total_price=offer.offer_amount + offer.shipping_cost
            )
        else:
            # Order from cart (simplified - single product for now)
            product_id = data['cartItems'][0] if data.get('cartItems') else None
            if not product_id:
                raise ValueError("No items in cart")
            
            product = Product.objects(id=product_id).first()
            if not product:
                raise ValueError("Product not found")
            
            seller = User.objects(id=product.seller_id.id).first()
            order = Order(
                order_number=order_number,
                buyer_id=buyer_id,
                buyer_name=buyer.full_name,
                seller_id=product.seller_id.id,
                seller_name=seller.full_name,
                product_id=product_id,
                product_title=product.title,
                price=product.price,
                shipping_cost=product.shipping_cost,
                total_price=product.price + product.shipping_cost
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
        
        return order
    
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
    def update_order_status(order_id, seller_id, status, tracking_number=None):
        """Update order status (for shipping)"""
        order = Order.objects(id=order_id, seller_id=seller_id).first()
        if not order:
            raise ValueError("Order not found")
        
        order.status = status
        if tracking_number:
            order.tracking_number = tracking_number
        order.updated_at = datetime.utcnow()
        order.save()
        
        return order

