"""
Chat services
"""
from datetime import datetime
from chat.models import Conversation, Message
from authentication.models import User
from products.models import Product, Offer
import uuid


class ChatService:
    """Chat service"""
    
    @staticmethod
    def get_or_create_conversation(user1_id, user2_id, product_id=None):
        """Get or create conversation between two users"""
        user1 = User.objects(id=user1_id).first()
        user2 = User.objects(id=user2_id).first()
        
        if not user1 or not user2:
            raise ValueError("Users not found")
        
        # Find existing conversation
        conversation = Conversation.objects(
            participants__all=[user1_id, user2_id],
            product_id=product_id if product_id else None
        ).first()
        
        if not conversation:
            conversation = Conversation(
                participants=[user1_id, user2_id],
                product_id=product_id
            )
            conversation.save()
        
        return conversation
    
    @staticmethod
    def get_conversations(user_id):
        """Get all conversations for a user"""
        conversations = Conversation.objects(participants=user_id).order_by('-updated_at')
        
        conversations_list = []
        for conv in conversations:
            other_user = None
            for participant in conv.participants:
                if str(participant.id) != str(user_id):
                    other_user = User.objects(id=participant.id).first()
                    break
            
            conversations_list.append({
                'id': str(conv.id),
                'conversationId': str(conv.id),
                'otherUser': {
                    'id': str(other_user.id) if other_user else '',
                    'username': other_user.username if other_user else '',
                    'profileImage': other_user.profile_image if other_user else ''
                },
                'lastMessage': conv.last_message or '',
                'lastMessageAt': conv.last_message_at.isoformat() if conv.last_message_at else None,
                'unreadCount': conv.unread_count_sender if str(conv.participants[0].id) == str(user_id) else conv.unread_count_receiver,
                'productId': str(conv.product_id.id) if conv.product_id else None
            })
        
        return conversations_list
    
    @staticmethod
    def get_messages(conversation_id, user_id, page=1, limit=50):
        """Get messages for a conversation - Aggregates messages from ALL conversations between participants
        
        This method aggregates messages from all conversations between the two participants
        because messages can be split across multiple conversations (e.g., product-specific vs general chat).
        This ensures all messages (text, offers, images) between users are returned together.
        """
        # Only fetch minimal fields from conversation to avoid loading full objects
        conversation = Conversation.objects(id=conversation_id).only('participants', 'unread_count_sender', 'unread_count_receiver').first()
        if not conversation:
            raise ValueError("Conversation not found")
        
        # Check if user is participant
        is_participant = any(str(p.id) == str(user_id) for p in conversation.participants)
        if not is_participant:
            raise ValueError("Not authorized to view this conversation")
        
        # Get messages with only required fields to prevent ReferenceField auto-dereferencing
        # Order by created_at DESC (newest first) - Page 1 = most recent messages
        # Extract participant IDs - these are the two users in the conversation
        participant_ids = [str(p.id) for p in conversation.participants]
        if len(participant_ids) != 2:
            raise ValueError("Invalid conversation: must have exactly 2 participants")
        
        # Query ALL messages between these two participants (regardless of conversation_id)
        # This aggregates messages from all conversations between the users
        # This fixes the issue where messages are split across multiple conversations
        # (e.g., product-specific conversations vs general chat)
        skip = (page - 1) * limit
        
        # Build query: messages where (sender=user1 AND receiver=user2) OR (sender=user2 AND receiver=user1)
        # This gets all messages between the two participants from ANY conversation
        from mongoengine import Q
        messages_queryset = Message.objects(
            (Q(sender_id=participant_ids[0]) & Q(receiver_id=participant_ids[1])) |
            (Q(sender_id=participant_ids[1]) & Q(receiver_id=participant_ids[0]))
        ).only(
            'id', 'text', 'sender_id', 'receiver_id', 'offer_id', 'product_id', 
            'message_type', 'attachments', 'created_at', 'is_read', 'conversation_id'
        ).order_by('-created_at').skip(skip).limit(limit)
        
        # Get total count - use estimated count for better performance on large collections
        # For exact count, use count(), but estimated_count() is faster for large datasets
        try:
            # Try to get exact count efficiently - count ALL message types (text, offer, image)
            total = Message.objects(
                (Q(sender_id=participant_ids[0]) & Q(receiver_id=participant_ids[1])) |
                (Q(sender_id=participant_ids[1]) & Q(receiver_id=participant_ids[0]))
            ).count()
        except Exception:
            # Fallback to 0 if count fails
            total = 0
        
        # Keep conversation_id_str for response consistency
        conversation_id_str = str(conversation_id)
        
        # Convert to list and extract IDs - using pattern from codebase
        from bson import ObjectId
        message_list = list(messages_queryset)
        
        # Collect all unique IDs from ReferenceFields (handle both dereferenced and DBRef)
        sender_ids = set()
        offer_ids = set()
        product_ids = set()
        
        for msg in message_list:
            # Handle sender_id ReferenceField
            if msg.sender_id:
                if hasattr(msg.sender_id, 'id'):
                    sender_ids.add(msg.sender_id.id)
                elif isinstance(msg.sender_id, ObjectId):
                    sender_ids.add(msg.sender_id)
                elif isinstance(msg.sender_id, str):
                    try:
                        sender_ids.add(ObjectId(msg.sender_id))
                    except:
                        pass
            
            # Handle offer_id ReferenceField
            if msg.offer_id:
                if hasattr(msg.offer_id, 'id'):
                    offer_ids.add(msg.offer_id.id)
                elif isinstance(msg.offer_id, ObjectId):
                    offer_ids.add(msg.offer_id)
                elif isinstance(msg.offer_id, str):
                    try:
                        offer_ids.add(ObjectId(msg.offer_id))
                    except:
                        pass
            
            # Handle product_id ReferenceField
            if msg.product_id:
                if hasattr(msg.product_id, 'id'):
                    product_ids.add(msg.product_id.id)
                elif isinstance(msg.product_id, ObjectId):
                    product_ids.add(msg.product_id)
                elif isinstance(msg.product_id, str):
                    try:
                        product_ids.add(ObjectId(msg.product_id))
                    except:
                        pass
        
        # Batch load users
        users_dict = {}
        if sender_ids:
            users = User.objects(id__in=list(sender_ids)).only('id', 'full_name')
            users_dict = {str(user.id): user for user in users}
        
        # Batch load offers
        offers_dict = {}
        offer_product_ids = set()
        if offer_ids:
            # Load all offer fields needed for complete offer object (matching WebSocket format)
            offers = Offer.objects(id__in=list(offer_ids)).only(
                'id', 'product_id', 'buyer_id', 'seller_id', 'offer_amount', 'original_price', 
                'status', 'shipping_cost', 'expiration_date', 'counter_offer_amount',
                'last_countered_by', 'buyer_counter_count', 'seller_counter_count',
                'created_at', 'updated_at'
            )
            offers_dict = {str(offer.id): offer for offer in offers}
            # Collect product IDs from offers
            for offer in offers:
                if offer.product_id:
                    offer_product_ids.add(offer.product_id.id)
        
        # Batch load products (from messages and offers) - limit images to first one only
        products_dict = {}
        all_product_ids = product_ids | offer_product_ids
        if all_product_ids:
            products = Product.objects(id__in=list(all_product_ids)).only(
                'id', 'title', 'images', 'price', 'original_price', 'currency',
                'size', 'condition', 'brand', 'category'
            )
            products_dict = {str(product.id): product for product in products}
        
        # Build messages list with cached data - optimized
        messages_list = []
        for msg in message_list:
            # Extract IDs using same pattern as rest of codebase
            sender_id = None
            receiver_id = None
            offer_id_str = None
            product_id_str = None
            
            # Extract sender_id
            if msg.sender_id:
                if hasattr(msg.sender_id, 'id'):
                    sender_id = str(msg.sender_id.id)
                elif isinstance(msg.sender_id, ObjectId):
                    sender_id = str(msg.sender_id)
                elif isinstance(msg.sender_id, str):
                    sender_id = msg.sender_id
            
            # Extract receiver_id
            if msg.receiver_id:
                if hasattr(msg.receiver_id, 'id'):
                    receiver_id = str(msg.receiver_id.id)
                elif isinstance(msg.receiver_id, ObjectId):
                    receiver_id = str(msg.receiver_id)
                elif isinstance(msg.receiver_id, str):
                    receiver_id = msg.receiver_id
            
            # Extract offer_id
            if msg.offer_id:
                if hasattr(msg.offer_id, 'id'):
                    offer_id_str = str(msg.offer_id.id)
                elif isinstance(msg.offer_id, ObjectId):
                    offer_id_str = str(msg.offer_id)
                elif isinstance(msg.offer_id, str):
                    offer_id_str = msg.offer_id
            
            # Extract product_id
            if msg.product_id:
                if hasattr(msg.product_id, 'id'):
                    product_id_str = str(msg.product_id.id)
                elif isinstance(msg.product_id, ObjectId):
                    product_id_str = str(msg.product_id)
                elif isinstance(msg.product_id, str):
                    product_id_str = msg.product_id
            
            is_sender = sender_id == str(user_id)
            sender = users_dict.get(sender_id) if sender_id else None
            
            # Ensure timestamp is in ISO format
            timestamp = msg.created_at.isoformat() if msg.created_at else None
            
            message_data = {
                'id': str(msg.id),
                'text': msg.text or '',
                'senderId': sender_id,
                'receiverId': receiver_id,
                'conversationId': str(msg.conversation_id) if hasattr(msg, 'conversation_id') and msg.conversation_id else conversation_id_str,  # Include actual conversationId from message
                'isSender': is_sender,
                'sender': 'me' if is_sender else 'other',
                'senderName': sender.full_name if sender else None,
                'timestamp': timestamp,
                'createdAt': timestamp,  # Include createdAt for consistency with requirements
                'attachments': msg.attachments or [],
                'offerId': offer_id_str,
                'productId': product_id_str,
                'messageType': msg.message_type or 'text',
                'isRead': msg.is_read if hasattr(msg, 'is_read') else False
            }
            
            # If message has an offer, include complete offer details with product information (matching WebSocket format)
            if offer_id_str:
                offer = offers_dict.get(offer_id_str)
                if offer:
                    # Extract buyer_id and seller_id safely
                    buyer_id_str = None
                    seller_id_str = None
                    if offer.buyer_id:
                        buyer_id_str = str(offer.buyer_id.id if hasattr(offer.buyer_id, 'id') else offer.buyer_id)
                    if offer.seller_id:
                        seller_id_str = str(offer.seller_id.id if hasattr(offer.seller_id, 'id') else offer.seller_id)
                    
                    # Get currency from offer (stored when offer was created from product)
                    offer_currency = offer.currency if hasattr(offer, 'currency') and offer.currency else 'SAR'
                    
                    offer_data = {
                        'id': offer_id_str,
                        'productId': str(offer.product_id.id) if offer.product_id and hasattr(offer.product_id, 'id') else (str(offer.product_id) if offer.product_id else None),
                        'buyerId': buyer_id_str,
                        'sellerId': seller_id_str,
                        'offerAmount': float(offer.offer_amount) if offer.offer_amount else 0.0,
                        'originalPrice': float(offer.original_price) if offer.original_price else 0.0,
                        'currency': offer_currency,  # Add currency from offer
                        'status': offer.status,
                        'createdAt': offer.created_at.isoformat() if offer.created_at else None,
                        'updatedAt': offer.updated_at.isoformat() if offer.updated_at else None,
                    }
                    
                    # Include counter offer if it exists
                    if offer.counter_offer_amount:
                        offer_data['counterAmount'] = float(offer.counter_offer_amount)
                    
                    # Include shipping cost if available
                    if hasattr(offer, 'shipping_cost') and offer.shipping_cost:
                        offer_data['shippingCost'] = float(offer.shipping_cost)
                    
                    # Include expiration date if available
                    if hasattr(offer, 'expiration_date') and offer.expiration_date:
                        offer_data['expirationDate'] = offer.expiration_date.isoformat()
                    
                    # Include counter tracking fields (safe access for old documents)
                    if hasattr(offer, 'last_countered_by') and offer.last_countered_by:
                        offer_data['lastCounteredBy'] = offer.last_countered_by
                    
                    if hasattr(offer, 'buyer_counter_count') and offer.buyer_counter_count is not None:
                        offer_data['buyerCounterCount'] = offer.buyer_counter_count
                    
                    if hasattr(offer, 'seller_counter_count') and offer.seller_counter_count is not None:
                        offer_data['sellerCounterCount'] = offer.seller_counter_count
                    
                    # Get product details from cached products - limit images to first 3 for performance
                    if offer.product_id:
                        product_id_from_offer = str(offer.product_id.id if hasattr(offer.product_id, 'id') else offer.product_id)
                        product = products_dict.get(product_id_from_offer)
                        if product:
                            # Limit images to first 3 to reduce payload size
                            product_images = product.images or []
                            limited_images = product_images[:3] if len(product_images) > 3 else product_images
                            
                            offer_data['product'] = {
                                'id': product_id_from_offer,
                                'title': product.title or '',
                                'image': product_images[0] if product_images else None,
                                'images': limited_images,
                                'price': float(product.price) if product.price else 0.0,
                                'originalPrice': float(product.original_price) if product.original_price else float(product.price) if product.price else 0.0,
                                'currency': offer_currency,  # Use currency from offer, not current product currency
                                'size': product.size or '',
                                'condition': product.condition or '',
                                'brand': product.brand or '',
                                'category': product.category or '',
                            }
                    
                    # Update message text if it's an offer message and needs currency correction
                    if msg.message_type == 'offer' and msg.text:
                        # Check if message text has wrong currency format and update it
                        import re
                        # Pattern to match "SAR" or currency in message
                        if 'SAR' in msg.text and offer_currency != 'SAR':
                            # Replace SAR with correct currency in message text
                            message_data['text'] = re.sub(r'SAR\s+(\d+\.?\d*)', f'{offer_currency} \\1', msg.text)
                        elif re.search(r'(\w+)\s+(\d+\.?\d*)', msg.text) and offer_currency not in msg.text:
                            # If currency is missing or wrong, regenerate message with correct currency
                            product_title = offer_data.get('product', {}).get('title', 'this product')
                            message_data['text'] = f"I've made an offer of {offer_currency} {offer.offer_amount:.2f} for \"{product_title}\"."
                    
                    message_data['offer'] = offer_data
            
            messages_list.append(message_data)
        
        # Mark-as-read operation - optimized to use exists() instead of count()
        # Mark messages as read across ALL conversations between participants
        try:
            # Check if any unread messages exist (faster than count)
            from mongoengine import Q
            has_unread = Message.objects(
                ((Q(sender_id=participant_ids[0]) & Q(receiver_id=participant_ids[1])) |
                 (Q(sender_id=participant_ids[1]) & Q(receiver_id=participant_ids[0]))) &
                Q(receiver_id=user_id) &
                Q(is_read=False)
            ).limit(1).first() is not None
            
            if has_unread:
                # Perform bulk update (single operation) - mark all unread messages between participants as read
                Message.objects(
                    ((Q(sender_id=participant_ids[0]) & Q(receiver_id=participant_ids[1])) |
                     (Q(sender_id=participant_ids[1]) & Q(receiver_id=participant_ids[0]))) &
                    Q(receiver_id=user_id) &
                    Q(is_read=False)
                ).update(set__is_read=True)
                
                # Update unread count in conversation (only if needed)
                if str(conversation.participants[0].id) == str(user_id):
                    conversation.unread_count_sender = '0'
                else:
                    conversation.unread_count_receiver = '0'
                conversation.save()
        except Exception:
            # Silently fail if update fails - don't block response
            pass
        
        return messages_list, total
    
    @staticmethod
    def send_message(sender_id, receiver_id, text, product_id=None, attachments=None, offer_id=None):
        """Send a message"""
        sender = User.objects(id=sender_id).first()
        receiver = User.objects(id=receiver_id).first()
        
        if not sender or not receiver:
            raise ValueError("Users not found")
        
        # Get or create conversation
        conversation = ChatService.get_or_create_conversation(sender_id, receiver_id, product_id)
        
        # Create message
        message = Message(
            conversation_id=str(conversation.id),
            sender_id=sender_id,
            receiver_id=receiver_id,
            product_id=product_id,
            text=text,
            attachments=attachments or [],
            offer_id=offer_id,
            message_type='offer' if offer_id else 'text'
        )
        message.save()
        
        # Update conversation
        conversation.last_message = text or 'Offer sent'
        conversation.last_message_at = datetime.utcnow()
        
        # Update unread count
        if str(conversation.participants[0].id) == str(receiver_id):
            conversation.unread_count_sender = str(int(conversation.unread_count_sender or '0') + 1)
        else:
            conversation.unread_count_receiver = str(int(conversation.unread_count_receiver or '0') + 1)
        
        conversation.updated_at = datetime.utcnow()
        conversation.save()
        
        return message

