"""
WebSocket consumers for chat and notifications
"""
import json
import logging
from datetime import datetime
from urllib.parse import parse_qs
from bson import ObjectId
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.services import ChatService
from chat.models import Message, Conversation
from authentication.models import User
from authentication.services import JWTService
from notifications.models import UserNotification

logger = logging.getLogger(__name__)

# Track online users per conversation: {conversation_id: {user_id: count}}
online_users = {}


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for chat"""
    
    async def safe_channel_layer_operation(self, operation, *args, **kwargs):
        """Safely execute channel layer operations with error handling"""
        if not self.channel_layer:
            logger.warning("Channel layer not available - skipping operation")
            return False
        
        try:
            await operation(*args, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Channel layer operation failed: {str(e)}", exc_info=True)
            return False
    
    async def connect(self):
        try:
            # Get token from query parameters
            query_string = self.scope.get('query_string', b'').decode()
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]
            
            conversation_id = self.scope['url_route']['kwargs'].get('conversation_id')
            logger.info(f"WebSocket connection attempt - conversation_id: {conversation_id}, has_token: {bool(token)}")
            
            # Authentication is REQUIRED - reject connections without tokens
            if not token:
                logger.warning(f"WebSocket connection rejected - no token provided for conversation_id: {conversation_id}")
                await self.accept()  # Accept first, then close
                await self.close(code=4001)  # Unauthorized
                return
            
            try:
                user = await self.authenticate_user(token)
                if not user:
                    logger.warning(f"WebSocket authentication failed - invalid token for conversation_id: {conversation_id}")
                    await self.accept()  # Accept first, then close
                    await self.close(code=4001)  # Unauthorized
                    return
                self.user = user
                logger.info(f"WebSocket authenticated - user_id: {str(user.id)}, conversation_id: {conversation_id}")
            except Exception as e:
                logger.error(f"WebSocket authentication error for conversation_id {conversation_id}: {str(e)}", exc_info=True)
                await self.accept()
                await self.close(code=4001)
                return
            
            self.conversation_id = conversation_id
            self.room_group_name = f'chat_{self.conversation_id}'
            
            # Check if channel_layer is available
            if not self.channel_layer:
                logger.error("Channel layer is not configured - Redis connection may be missing")
                await self.accept()
                await self.close(code=1011)  # Internal error
                return
            
            # Join room group
            await self.safe_channel_layer_operation(
                self.channel_layer.group_add,
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Track user as online
            await self.mark_user_online()
            
            # Send current online users to the newly connected user
            await self.send_current_online_users()
            
            logger.info(f"WebSocket connected successfully - conversation_id: {self.conversation_id}, user_id: {str(self.user.id)}")
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}", exc_info=True)
            # Try to accept and close gracefully
            try:
                await self.accept()
                await self.close(code=1011)  # Internal error
            except:
                pass
    
    @database_sync_to_async
    def authenticate_user(self, token):
        """Authenticate user from JWT token"""
        try:
            payload = JWTService.verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get('user_id')
            user_type = payload.get('user_type', 'user')
            
            # Convert string ID to ObjectId if needed
            try:
                if isinstance(user_id, str):
                    user_id = ObjectId(user_id)
            except Exception:
                return None
            
            if user_type == 'admin':
                from authentication.models import Admin
                return Admin.objects(id=user_id).first()
            elif user_type == 'affiliate':
                from authentication.models import Affiliate
                return Affiliate.objects(id=user_id).first()
            else:
                return User.objects(id=user_id).first()
        except Exception:
            return None
    
    async def disconnect(self, close_code):
        # Mark user as offline before disconnecting
        if hasattr(self, 'user') and self.user and hasattr(self, 'conversation_id'):
            await self.mark_user_offline()
        
        # Leave room group
        await self.safe_channel_layer_operation(
            self.channel_layer.group_discard,
            self.room_group_name,
            self.channel_name
        )
    
    async def mark_user_online(self):
        """Mark user as online and broadcast status"""
        if not hasattr(self, 'conversation_id') or not self.user:
            return
        
        user_id = str(self.user.id)
        conversation_id = self.conversation_id
        
        # Track online users
        if conversation_id not in online_users:
            online_users[conversation_id] = {}
        
        # Increment connection count for this user
        if user_id not in online_users[conversation_id]:
            online_users[conversation_id][user_id] = 0
        online_users[conversation_id][user_id] += 1
        
        # Get conversation participants to determine who to notify
        participants = await self.get_conversation_participants(conversation_id)
        
        # Broadcast user online status
        await self.safe_channel_layer_operation(
            self.channel_layer.group_send,
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': user_id,
                'status': 'online',
                'participants': participants
            }
        )
    
    async def mark_user_offline(self):
        """Mark user as offline and broadcast status"""
        if not hasattr(self, 'conversation_id') or not self.user:
            return
        
        user_id = str(self.user.id)
        conversation_id = self.conversation_id
        
        # Decrement connection count
        if conversation_id in online_users and user_id in online_users[conversation_id]:
            online_users[conversation_id][user_id] -= 1
            
            # If count reaches 0, user is offline
            if online_users[conversation_id][user_id] <= 0:
                del online_users[conversation_id][user_id]
                
                # Get conversation participants
                participants = await self.get_conversation_participants(conversation_id)
                
                # Broadcast user offline status
                await self.safe_channel_layer_operation(
                    self.channel_layer.group_send,
                    self.room_group_name,
                    {
                        'type': 'user_status',
                        'user_id': user_id,
                        'status': 'offline',
                        'participants': participants
                    }
                )
    
    async def send_current_online_users(self):
        """Send current online users list to the connected user with user details"""
        if not hasattr(self, 'conversation_id'):
            return
        
        conversation_id = self.conversation_id
        online_user_ids = []
        
        if conversation_id in online_users:
            online_user_ids = list(online_users[conversation_id].keys())
        
        # Get user details for online users
        online_users_details = await self.get_users_details(online_user_ids)
        
        # Get conversation participants
        participants = await self.get_conversation_participants(conversation_id)
        
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'onlineUsers': online_user_ids,  # Keep IDs for backward compatibility
            'onlineUsersDetails': online_users_details,  # New: includes username and profile_image
            'participants': participants
        }))
    
    @database_sync_to_async
    def get_conversation_participants(self, conversation_id):
        """Get conversation participant IDs"""
        try:
            conversation = Conversation.objects(id=conversation_id).first()
            if conversation and conversation.participants:
                return [str(p.id) for p in conversation.participants]
            return []
        except Exception as e:
            logger.error(f"Error getting conversation participants: {str(e)}")
            return []
    
    @database_sync_to_async
    def get_users_details(self, user_ids):
        """Get user details (username and profile_image) for given user IDs"""
        if not user_ids:
            return []
        
        try:
            from bson import ObjectId
            # Convert string IDs to ObjectId
            object_ids = []
            for user_id in user_ids:
                try:
                    if isinstance(user_id, str):
                        object_ids.append(ObjectId(user_id))
                    else:
                        object_ids.append(user_id)
                except Exception:
                    continue
            
            if not object_ids:
                return []
            
            # Batch load users with only required fields
            users = User.objects(id__in=object_ids).only('id', 'username', 'profile_image')
            
            # Build user details list
            users_details = []
            for user in users:
                users_details.append({
                    'id': str(user.id),
                    'username': user.username or '',
                    'profileImage': user.profile_image or ''
                })
            
            return users_details
        except Exception as e:
            logger.error(f"Error getting users details: {str(e)}", exc_info=True)
            return []
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        # Ensure user is authenticated
        if not self.user:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Authentication required'
            }))
            return
        
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'send_offer':
                await self.handle_send_offer(data)
            elif message_type == 'counter_offer':
                await self.handle_counter_offer(data)
            elif message_type == 'accept_offer':
                await self.handle_accept_offer(data)
            elif message_type == 'reject_offer':
                await self.handle_reject_offer(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}',
                    'error': 'UNKNOWN_MESSAGE_TYPE',
                    'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format',
                'error': 'INVALID_JSON',
                'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
            }))
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def handle_chat_message(self, data):
        """Handle regular chat message"""
        sender_id = str(self.user.id)
        receiver_id = data.get('receiverId')
        text = data.get('text', '')
        attachments = data.get('attachments', [])
        offer_id = data.get('offerId')
        product_id = data.get('productId')
        
        # Validate receiver
        if not receiver_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'receiverId is required',
                'error': 'MISSING_RECEIVER_ID',
                'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
            }))
            return
        
        # Save message to database
        message = await self.save_message(sender_id, receiver_id, text, product_id, attachments, offer_id)
        
        # Get message details with sender/receiver info
        message_data = await self.get_message_data(message, sender_id)
        
        # Send message to room group
        await self.safe_channel_layer_operation(
            self.channel_layer.group_send,
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )
    
    async def handle_send_offer(self, data):
        """Handle sending a new offer via WebSocket"""
        from products.services import OfferService
        
        buyer_id = str(self.user.id)
        product_id = data.get('productId')
        offer_amount = data.get('offerAmount')
        receiver_id = data.get('receiverId')
        shipping_address = data.get('shippingAddress')
        zip_code = data.get('zipCode')
        house_number = data.get('houseNumber')
        text = data.get('text', '')  # Optional message with offer
        
        # Validate required fields
        if not product_id or not offer_amount or not receiver_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'productId, offerAmount, and receiverId are required',
                'error': 'MISSING_REQUIRED_FIELDS',
                'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
            }))
            return
        
        try:
            # Create offer
            offer = await self.create_offer_async(
                buyer_id, product_id, float(offer_amount),
                shipping_address, zip_code, house_number
            )
            
            # Reload offer immediately to ensure we have the latest data including currency
            # This is critical because the offer was just created and currency is stored in the database
            try:
                reloaded_offer = await self.reload_offer_async(str(offer.id))
                if reloaded_offer:
                    offer = reloaded_offer  # Use reloaded offer for currency retrieval
            except Exception as e:
                logger.warning(f"Could not reload offer: {str(e)}")
            
            # Get currency from offer FIRST (offer stores currency from product at creation time)
            # This is the source of truth since offer.currency was set when offer was created
            offer_currency = 'SAR'  # Default fallback
            if hasattr(offer, 'currency') and offer.currency:
                offer_currency = offer.currency
            else:
                # Fallback: get currency from product if offer doesn't have it
                if offer.product_id:
                    from products.models import Product
                    product = Product.objects(id=offer.product_id.id).only('currency', 'title').first()
                    if product and hasattr(product, 'currency') and product.currency:
                        offer_currency = product.currency
            
            # Get product title for the message
            product_title = ""
            if offer.product_id:
                from products.models import Product
                product = Product.objects(id=offer.product_id.id).only('title').first()
                if product:
                    product_title = product.title or ""
            
            # Get offer details with product information
            offer_data = await self.get_offer_details_async(offer)
            
            # Generate message text with correct currency
            if not text:
                if product_title:
                    message_text = f"I've made an offer of {offer_currency} {offer_amount:.2f} for \"{product_title}\"."
                else:
                    message_text = f"I've made an offer of {offer_currency} {offer_amount:.2f}."
            else:
                message_text = text
            
            # Save message with offer
            message = await self.save_message(
                buyer_id, receiver_id, message_text,
                product_id, [], str(offer.id)
            )
            
            # Get complete message data with all fields
            message_data = await self.get_message_data(message, buyer_id)
            
            # Broadcast offer to room group
            await self.safe_channel_layer_operation(
                self.channel_layer.group_send,
                self.room_group_name,
                {
                    'type': 'offer_sent',
                    'offer': offer_data,
                    'message': message_data,
                    'conversationId': message.conversation_id
                }
            )
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e),
                'error': 'OFFER_CREATION_ERROR',
                'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
            }))
    
    async def handle_counter_offer(self, data):
        """Handle counter offer via WebSocket - allows both buyer and seller to counter"""
        from products.services import OfferService
        
        user_id = str(self.user.id)
        offer_id = data.get('offerId')
        counter_amount = data.get('counterAmount')
        receiver_id = data.get('receiverId')
        text = data.get('text', '')  # Optional message with counter offer
        
        # Validate required fields
        if not offer_id or not counter_amount or not receiver_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'offerId, counterAmount, and receiverId are required',
                'error': 'MISSING_REQUIRED_FIELDS',
                'offerId': offer_id,
                'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
            }))
            return
        
        try:
            # Get offer first to determine receiver
            offer = await self.get_offer_async(offer_id)
            if not offer:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Offer not found. It may have been deleted or already processed.',
                    'error': 'OFFER_NOT_FOUND',
                    'offerId': offer_id,
                    'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
                }))
                return
            
            # Determine if user is buyer or seller
            is_buyer = str(offer.buyer_id.id) == user_id
            is_seller = str(offer.seller_id.id) == user_id
            
            if not is_buyer and not is_seller:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You are not authorized to counter this offer',
                    'error': 'UNAUTHORIZED_ACTION',
                    'offerId': offer_id,
                    'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
                }))
                return
            
            # Counter the offer (now accepts both buyer and seller)
            offer = await self.counter_offer_async(offer_id, user_id, float(counter_amount))
            
            # Save message with counter offer
            message = await self.save_message(
                user_id, receiver_id,
                text or f"Countered with ${counter_amount}",
                str(offer.product_id.id) if offer.product_id else None,
                [], str(offer.id)
            )
            
            # Get offer details with product information and counter offer
            offer_data = await self.get_offer_details_async(offer, include_counter=True)
            
            # Get complete message data with all fields
            message_data = await self.get_message_data(message, user_id)
            
            # Broadcast counter offer to room group
            await self.safe_channel_layer_operation(
                self.channel_layer.group_send,
                self.room_group_name,
                {
                    'type': 'offer_countered',
                    'offer': offer_data,
                    'message': message_data,
                    'conversationId': message.conversation_id
                }
            )
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e),
                'error': 'COUNTER_OFFER_ERROR',
                'offerId': offer_id,
                'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
            }))
    
    async def handle_accept_offer(self, data):
        """Handle accepting an offer via WebSocket
        - Seller can accept buyer's original offer (status: pending)
        - Buyer can accept seller's counter offer (status: countered)
        """
        from products.services import OfferService
        from products.models import Offer
        
        user_id = str(self.user.id)
        offer_id = data.get('offerId')
        receiver_id = data.get('receiverId')
        text = data.get('text', '')  # Optional message
        
        # Validate required fields
        if not offer_id or not receiver_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'offerId and receiverId are required',
                'error': 'MISSING_REQUIRED_FIELDS',
                'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
            }))
            return
        
        try:
            # Get offer to check status and determine who can accept
            offer = await self.get_offer_async(offer_id)
            if not offer:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Offer not found',
                    'error': 'OFFER_NOT_FOUND',
                    'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
                }))
                return
            
            # Determine if user is buyer or seller
            is_buyer = str(offer.buyer_id.id) == user_id
            is_seller = str(offer.seller_id.id) == user_id
            
            # Validate who can accept based on offer status
            if offer.status == 'pending' and not is_seller:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Only seller can accept a pending offer',
                    'error': 'UNAUTHORIZED_ACTION',
                    'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
                }))
                return
            elif offer.status == 'countered' and not is_buyer:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Only buyer can accept a counter offer',
                    'error': 'UNAUTHORIZED_ACTION',
                    'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
                }))
                return
            elif offer.status not in ['pending', 'countered']:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Cannot accept offer with status: {offer.status}',
                    'error': 'INVALID_OFFER_STATUS',
                    'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
                }))
                return
            
            # Accept the offer (seller accepts original, buyer accepts counter)
            if offer.status == 'pending':
                # Seller accepting buyer's offer
                offer = await self.accept_offer_async(offer_id, user_id)
            else:
                # Buyer accepting seller's counter offer
                offer = await self.accept_counter_offer_async(offer_id, user_id)
            
            # Get complete offer details with product information
            offer_data = await self.get_offer_details_async(offer, include_counter=True)
            
            # Save message
            message = await self.save_message(
                user_id, receiver_id,
                text or "Offer accepted",
                str(offer.product_id.id) if offer.product_id else None,
                [], str(offer.id)
            )
            
            # Get complete message data with all fields
            message_data = await self.get_message_data(message, user_id)
            
            # Broadcast offer acceptance to room group
            await self.safe_channel_layer_operation(
                self.channel_layer.group_send,
                self.room_group_name,
                {
                    'type': 'offer_accepted',
                    'offer': offer_data,
                    'message': message_data,
                    'conversationId': message.conversation_id
                }
            )
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e),
                'error': 'REJECT_OFFER_ERROR',
                'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
            }))
    
    async def handle_reject_offer(self, data):
        """Handle rejecting an offer via WebSocket"""
        from products.services import OfferService
        
        seller_id = str(self.user.id)
        offer_id = data.get('offerId')
        receiver_id = data.get('receiverId')
        text = data.get('text', '')  # Optional message
        
        # Validate required fields
        if not offer_id or not receiver_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'offerId and receiverId are required',
                'error': 'MISSING_REQUIRED_FIELDS',
                'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
            }))
            return
        
        try:
            # Reject the offer
            offer = await self.reject_offer_async(offer_id, seller_id)
            
            # Get complete offer details with product information
            offer_data = await self.get_offer_details_async(offer, include_counter=True)
            
            # Save message
            message = await self.save_message(
                seller_id, receiver_id,
                text or "Offer rejected",
                str(offer.product_id.id) if offer.product_id else None,
                [], str(offer.id)
            )
            
            # Get complete message data with all fields
            message_data = await self.get_message_data(message, seller_id)
            
            # Broadcast offer rejection to room group
            await self.safe_channel_layer_operation(
                self.channel_layer.group_send,
                self.room_group_name,
                {
                    'type': 'offer_rejected',
                    'offer': offer_data,
                    'message': message_data,
                    'conversationId': message.conversation_id
                }
            )
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e),
                'error': 'REJECT_OFFER_ERROR',
                'conversationId': self.conversation_id if hasattr(self, 'conversation_id') else None
            }))
    
    @database_sync_to_async
    def get_message_data(self, message, current_user_id):
        """Get message data with sender/receiver information"""
        sender_id = str(message.sender_id.id) if message.sender_id else None
        receiver_id = str(message.receiver_id.id) if message.receiver_id else None
        is_sender = sender_id == str(current_user_id)
        
        # Get sender user info
        sender = None
        if message.sender_id:
            sender = User.objects(id=message.sender_id.id).first()
        
        # Ensure timestamp is in ISO format
        timestamp = message.created_at.isoformat() if message.created_at else datetime.utcnow().isoformat()
        
        message_data = {
            'id': str(message.id),
            'text': message.text or '',
            'senderId': sender_id,
            'receiverId': receiver_id,
            'conversationId': message.conversation_id,  # Add conversation_id for frontend query refetch
            'isSender': is_sender,  # True if current user sent this message
            'sender': 'me' if is_sender else 'other',  # For backward compatibility
            'senderName': sender.full_name if sender else None,
            'timestamp': timestamp,
            'createdAt': timestamp,  # Include createdAt for consistency
            'attachments': message.attachments or [],
            'offerId': str(message.offer_id.id) if message.offer_id else None,
            'productId': str(message.product_id.id) if message.product_id else None,
            'messageType': message.message_type or 'text',
            'isRead': message.is_read if hasattr(message, 'is_read') else False
        }
        
        # If message has an offer, include complete offer details with product information
        if message.offer_id:
            from products.models import Offer, Product
            offer = Offer.objects(id=message.offer_id.id).first()
            if offer:
                offer_data = {
                    'id': str(offer.id),
                    'productId': str(offer.product_id.id) if offer.product_id else None,
                    'buyerId': str(offer.buyer_id.id) if offer.buyer_id else None,
                    'sellerId': str(offer.seller_id.id) if offer.seller_id else None,
                    'offerAmount': float(offer.offer_amount) if offer.offer_amount else 0.0,
                    'originalPrice': float(offer.original_price) if offer.original_price else 0.0,
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
                
                # Get complete product details
                if offer.product_id:
                    product = Product.objects(id=offer.product_id.id).first()
                    if product:
                        product_images = product.images or []
                        # Use first image as main image, or fallback to image field
                        main_image = product_images[0] if product_images else (product.image if hasattr(product, 'image') else None)
                        
                        offer_data['product'] = {
                            'id': str(product.id),
                            'title': product.title or '',
                            'image': main_image,
                            'images': product_images,
                            'price': float(product.price) if product.price else 0.0,
                            'originalPrice': float(product.original_price) if product.original_price else float(product.price) if product.price else 0.0,
                            'currency': product.currency or 'SAR',
                            'size': product.size or '',
                            'condition': product.condition or '',
                            'brand': product.brand or '' if hasattr(product, 'brand') else '',
                            'category': product.category or '' if hasattr(product, 'category') else '',
                        }
                
                message_data['offer'] = offer_data
        
        return message_data
    
    async def chat_message(self, event):
        """Send message to WebSocket"""
        message = event['message']
        
        # Determine if current user is sender (for frontend display)
        if hasattr(self, 'user') and self.user:
            current_user_id = str(self.user.id)
            message['isSender'] = message.get('senderId') == current_user_id
            message['sender'] = 'me' if message['isSender'] else 'other'
        
        # Ensure conversation_id is included in the response
        if 'conversationId' not in message and hasattr(self, 'conversation_id'):
            message['conversationId'] = self.conversation_id
        
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'conversationId': message.get('conversationId')  # Include at top level for easy access
        }))
    
    async def user_status(self, event):
        """Send user online/offline status to WebSocket"""
        user_id = event['user_id']
        status = event['status']
        participants = event.get('participants', [])
        
        # Get current online users for this conversation
        conversation_id = self.conversation_id
        online_user_ids = []
        if conversation_id in online_users:
            online_user_ids = list(online_users[conversation_id].keys())
        
        # Get user details for the user who changed status
        user_details = await self.get_users_details([user_id])
        user_detail = user_details[0] if user_details else {
            'id': user_id,
            'username': '',
            'profileImage': ''
        }
        
        # Get user details for all online users
        online_users_details = await self.get_users_details(online_user_ids)
        
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': user_id,
            'status': status,  # 'online' or 'offline'
            'user': user_detail,  # New: includes username and profile_image for the user who changed status
            'onlineUsers': online_user_ids,  # Keep IDs for backward compatibility
            'onlineUsersDetails': online_users_details,  # New: includes username and profile_image for all online users
            'participants': participants
        }))
    
    async def offer_sent(self, event):
        """Send offer sent event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'offer_sent',
            'offer': event['offer'],
            'message': event['message'],
            'conversationId': event.get('conversationId') or event['message'].get('conversationId')
        }))
    
    async def offer_countered(self, event):
        """Send offer countered event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'offer_countered',
            'offer': event['offer'],
            'message': event['message'],
            'conversationId': event.get('conversationId') or event['message'].get('conversationId')
        }))
    
    async def offer_accepted(self, event):
        """Send offer accepted event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'offer_accepted',
            'offer': event['offer'],
            'message': event['message'],
            'conversationId': event.get('conversationId') or event['message'].get('conversationId')
        }))
    
    async def offer_rejected(self, event):
        """Send offer rejected event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'offer_rejected',
            'offer': event['offer'],
            'message': event['message'],
            'conversationId': event.get('conversationId') or event['message'].get('conversationId')
        }))
    
    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, text, product_id, attachments, offer_id):
        """Save message to database"""
        return ChatService.send_message(sender_id, receiver_id, text, product_id, attachments, offer_id)
    
    @database_sync_to_async
    def create_offer_async(self, buyer_id, product_id, offer_amount, shipping_address=None, zip_code=None, house_number=None):
        """Create offer asynchronously"""
        from products.services import OfferService
        return OfferService.create_offer(buyer_id, product_id, offer_amount, shipping_address, zip_code, house_number)
    
    @database_sync_to_async
    def counter_offer_async(self, offer_id, user_id, counter_amount):
        """Counter offer asynchronously - accepts both buyer and seller"""
        from products.services import OfferService
        return OfferService.counter_offer(offer_id, user_id, counter_amount)
    
    @database_sync_to_async
    def accept_offer_async(self, offer_id, seller_id):
        """Accept offer asynchronously"""
        from products.services import OfferService
        return OfferService.accept_offer(offer_id, seller_id)
    
    @database_sync_to_async
    def reject_offer_async(self, offer_id, seller_id):
        """Reject offer asynchronously"""
        from products.services import OfferService
        return OfferService.reject_offer(offer_id, seller_id)
    
    @database_sync_to_async
    def get_offer_async(self, offer_id):
        """Get offer asynchronously"""
        from products.models import Offer
        return Offer.objects(id=offer_id).first()
    
    @database_sync_to_async
    def reload_offer_async(self, offer_id):
        """Reload offer asynchronously to get latest data including currency"""
        from products.models import Offer
        offer = Offer.objects(id=offer_id).first()
        if offer:
            offer.reload()
        return offer
    
    @database_sync_to_async
    def get_offer_details_async(self, offer, include_counter=False):
        """Get complete offer details with product information"""
        from products.models import Product
        
        offer_data = {
            'id': str(offer.id),
            'productId': str(offer.product_id.id) if offer.product_id else None,
            'buyerId': str(offer.buyer_id.id) if offer.buyer_id else None,
            'sellerId': str(offer.seller_id.id) if offer.seller_id else None,
            'offerAmount': float(offer.offer_amount) if offer.offer_amount else 0.0,
            'originalPrice': float(offer.original_price) if offer.original_price else 0.0,
            'status': offer.status,
            'createdAt': offer.created_at.isoformat() if offer.created_at else None,
            'updatedAt': offer.updated_at.isoformat() if offer.updated_at else None,
        }
        
        # Include counter offer if it exists (always include if requested, or if offer has counter)
        if offer.counter_offer_amount:
            offer_data['counterAmount'] = float(offer.counter_offer_amount)
        
        # Include shipping cost if available
        if hasattr(offer, 'shipping_cost') and offer.shipping_cost:
            offer_data['shippingCost'] = float(offer.shipping_cost)
        
        # Include expiration date if available
        if hasattr(offer, 'expiration_date') and offer.expiration_date:
            offer_data['expirationDate'] = offer.expiration_date.isoformat()
        
        # Get complete product details
        if offer.product_id:
            product = Product.objects(id=offer.product_id.id).first()
            if product:
                product_images = product.images or []
                # Use first image as main image, or fallback to image field
                main_image = product_images[0] if product_images else (product.image if hasattr(product, 'image') else None)
                
                offer_data['product'] = {
                    'id': str(product.id),
                    'title': product.title or '',
                    'image': main_image,
                    'images': product_images,
                    'price': float(product.price) if product.price else 0.0,
                    'originalPrice': float(product.original_price) if product.original_price else float(product.price) if product.price else 0.0,
                    'currency': product.currency or 'SAR',
                    'size': product.size or '',
                    'condition': product.condition or '',
                    'brand': product.brand or '' if hasattr(product, 'brand') else '',
                    'category': product.category or '' if hasattr(product, 'category') else '',
                }
        
        return offer_data
    
    @database_sync_to_async
    def accept_counter_offer_async(self, offer_id, buyer_id):
        """Buyer accepts seller's counter offer"""
        from products.models import Offer, Product
        offer = Offer.objects(id=offer_id, buyer_id=buyer_id).first()
        if not offer:
            raise ValueError("Offer not found")
        if offer.status != 'countered':
            raise ValueError("Offer is not in countered status")
        
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
        
        return offer


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for notifications"""
    
    async def safe_channel_layer_operation(self, operation, *args, **kwargs):
        """Safely execute channel layer operations with error handling"""
        if not self.channel_layer:
            logger.warning("Channel layer not available - skipping operation")
            return False
        
        try:
            await operation(*args, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Channel layer operation failed: {str(e)}", exc_info=True)
            return False
    
    async def connect(self):
        try:
            # Get token from query parameters
            query_string = self.scope.get('query_string', b'').decode()
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]
            
            logger.info(f"Notification WebSocket connection attempt - user_id: {self.scope['url_route']['kwargs'].get('user_id')}, has_token: {bool(token)}")
            
            # Authentication is REQUIRED - reject connections without tokens
            if not token:
                logger.warning("Notification WebSocket connection rejected - no token provided")
                await self.accept()
                await self.close(code=4001)  # Unauthorized
                return
            
            try:
                user = await self.authenticate_user(token)
                if not user:
                    logger.warning("Notification WebSocket authentication failed - invalid token")
                    await self.accept()
                    await self.close(code=4001)  # Unauthorized
                    return
                self.user = user
                logger.info(f"Notification WebSocket authenticated - user_id: {str(user.id)}")
            except Exception as e:
                logger.error(f"Notification WebSocket authentication error: {str(e)}")
                await self.accept()
                await self.close(code=4001)
                return
            
            self.user_id = self.scope['url_route']['kwargs']['user_id']
            self.room_group_name = f'notifications_{self.user_id}'
            
            # Check if channel_layer is available
            if not self.channel_layer:
                logger.error("Channel layer is not configured - Redis connection may be missing")
                await self.accept()
                await self.close(code=1011)  # Internal error
                return
            
            # Join room group
            await self.safe_channel_layer_operation(
                self.channel_layer.group_add,
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"Notification WebSocket connected successfully - user_id: {self.user_id}")
        except Exception as e:
            logger.error(f"Notification WebSocket connection error: {str(e)}", exc_info=True)
            try:
                await self.accept()
                await self.close(code=1011)  # Internal error
            except:
                pass
    
    @database_sync_to_async
    def authenticate_user(self, token):
        """Authenticate user from JWT token"""
        try:
            payload = JWTService.verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get('user_id')
            user_type = payload.get('user_type', 'user')
            
            # Convert string ID to ObjectId if needed
            try:
                if isinstance(user_id, str):
                    user_id = ObjectId(user_id)
            except Exception:
                return None
            
            if user_type == 'admin':
                from authentication.models import Admin
                return Admin.objects(id=user_id).first()
            elif user_type == 'affiliate':
                from authentication.models import Affiliate
                return Affiliate.objects(id=user_id).first()
            else:
                return User.objects(id=user_id).first()
        except Exception:
            return None
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.safe_channel_layer_operation(
            self.channel_layer.group_discard,
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        pass
    
    async def send_notification(self, event):
        """Send notification to WebSocket"""
        notification = event['notification']
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification
        }))

