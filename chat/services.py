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
        """Get messages for a conversation"""
        conversation = Conversation.objects(id=conversation_id).first()
        if not conversation:
            raise ValueError("Conversation not found")
        
        # Check if user is participant
        is_participant = any(str(p.id) == str(user_id) for p in conversation.participants)
        if not is_participant:
            raise ValueError("Not authorized to view this conversation")
        
        messages = Message.objects(conversation_id=conversation_id).order_by('-created_at')
        
        total = messages.count()
        skip = (page - 1) * limit
        messages = messages.skip(skip).limit(limit)
        
        messages_list = []
        for msg in reversed(messages):  # Reverse to show oldest first
            sender = User.objects(id=msg.sender_id.id).first()
            is_sender = str(msg.sender_id.id) == str(user_id)
            
            sender_id = str(msg.sender_id.id) if msg.sender_id else None
            receiver_id = str(msg.receiver_id.id) if msg.receiver_id else None
            
            message_data = {
                'id': str(msg.id),
                'text': msg.text or '',
                'senderId': sender_id,
                'receiverId': receiver_id,
                'isSender': is_sender,  # True if current user sent this message
                'sender': 'me' if is_sender else 'other',  # For backward compatibility
                'senderName': sender.full_name if sender else None,
                'timestamp': msg.created_at.isoformat(),
                'attachments': msg.attachments or [],
                'offerId': str(msg.offer_id.id) if msg.offer_id else None,
                'productId': str(msg.product_id.id) if msg.product_id else None,
                'messageType': msg.message_type or 'text'
            }
            
            # If message has an offer, include full offer details with product information
            if msg.offer_id:
                offer = Offer.objects(id=msg.offer_id.id).first()
                if offer:
                    offer_data = {
                        'id': str(offer.id),
                        'offerAmount': float(offer.offer_amount) if offer.offer_amount else 0.0,
                        'originalPrice': float(offer.original_price) if offer.original_price else 0.0,
                        'status': offer.status,
                        'shippingCost': float(offer.shipping_cost) if offer.shipping_cost else 0.0,
                        'expirationDate': offer.expiration_date.isoformat() if offer.expiration_date else None,
                    }
                    
                    # Include counter offer if it exists
                    if offer.counter_offer_amount:
                        offer_data['counterAmount'] = float(offer.counter_offer_amount)
                    
                    # Get product details
                    if offer.product_id:
                        product = Product.objects(id=offer.product_id.id).first()
                        if product:
                            offer_data['product'] = {
                                'id': str(product.id),
                                'title': product.title or '',
                                'image': product.images[0] if product.images and len(product.images) > 0 else None,
                                'images': product.images or [],
                                'price': float(product.price) if product.price else 0.0,
                                'originalPrice': float(product.original_price) if product.original_price else float(product.price) if product.price else 0.0,
                                'currency': product.currency or 'SAR',
                                'size': product.size or '',
                                'condition': product.condition or '',
                                'brand': product.brand or '',
                                'category': product.category or '',
                            }
                    
                    message_data['offer'] = offer_data
            
            messages_list.append(message_data)
        
        # Mark messages as read
        Message.objects(conversation_id=conversation_id, receiver_id=user_id, is_read=False).update(set__is_read=True)
        
        # Update unread count
        if str(conversation.participants[0].id) == str(user_id):
            conversation.unread_count_sender = '0'
        else:
            conversation.unread_count_receiver = '0'
        conversation.save()
        
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

