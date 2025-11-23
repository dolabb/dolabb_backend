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


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for chat"""
    
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
                logger.warning("WebSocket connection rejected - no token provided")
                await self.accept()  # Accept first, then close
                await self.close(code=4001)  # Unauthorized
                return
            
            try:
                user = await self.authenticate_user(token)
                if not user:
                    logger.warning("WebSocket authentication failed - invalid token")
                    await self.accept()  # Accept first, then close
                    await self.close(code=4001)  # Unauthorized
                    return
                self.user = user
                logger.info(f"WebSocket authenticated - user_id: {str(user.id)}")
            except Exception as e:
                logger.error(f"WebSocket authentication error: {str(e)}", exc_info=True)
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
            try:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as e:
                logger.error(f"Failed to join channel layer group: {str(e)}", exc_info=True)
                # Still accept connection even if Redis fails
                # Messages won't be broadcasted but direct messages will work
                logger.warning("Continuing without channel layer group (Redis may be unavailable)")
            
            await self.accept()
            logger.info(f"WebSocket connected successfully - conversation_id: {self.conversation_id}")
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
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
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
                    'message': f'Unknown message type: {message_type}'
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
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
                'message': 'receiverId is required'
            }))
            return
        
        # Save message to database
        message = await self.save_message(sender_id, receiver_id, text, product_id, attachments, offer_id)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': str(message.id),
                    'text': message.text,
                    'sender': 'me',
                    'timestamp': message.created_at.isoformat(),
                    'attachments': message.attachments,
                    'offerId': str(message.offer_id.id) if message.offer_id else None,
                    'productId': str(message.product_id.id) if message.product_id else None
                }
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
                'message': 'productId, offerAmount, and receiverId are required'
            }))
            return
        
        try:
            # Create offer
            offer = await self.create_offer_async(
                buyer_id, product_id, float(offer_amount),
                shipping_address, zip_code, house_number
            )
            
            # Save message with offer
            message = await self.save_message(
                buyer_id, receiver_id, text or f"Made an offer of ${offer_amount}",
                product_id, [], str(offer.id)
            )
            
            # Broadcast offer to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'offer_sent',
                    'offer': {
                        'id': str(offer.id),
                        'productId': str(offer.product_id.id),
                        'buyerId': str(offer.buyer_id.id),
                        'sellerId': str(offer.seller_id.id),
                        'offerAmount': offer.offer_amount,
                        'originalPrice': offer.original_price,
                        'status': offer.status,
                        'createdAt': offer.created_at.isoformat()
                    },
                    'message': {
                        'id': str(message.id),
                        'text': message.text,
                        'timestamp': message.created_at.isoformat()
                    }
                }
            )
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def handle_counter_offer(self, data):
        """Handle counter offer via WebSocket"""
        from products.services import OfferService
        
        seller_id = str(self.user.id)
        offer_id = data.get('offerId')
        counter_amount = data.get('counterAmount')
        receiver_id = data.get('receiverId')
        text = data.get('text', '')  # Optional message with counter offer
        
        # Validate required fields
        if not offer_id or not counter_amount or not receiver_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'offerId, counterAmount, and receiverId are required'
            }))
            return
        
        try:
            # Counter the offer
            offer = await self.counter_offer_async(offer_id, seller_id, float(counter_amount))
            
            # Save message with counter offer
            message = await self.save_message(
                seller_id, receiver_id,
                text or f"Countered with ${counter_amount}",
                str(offer.product_id.id) if offer.product_id else None,
                [], str(offer.id)
            )
            
            # Broadcast counter offer to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'offer_countered',
                    'offer': {
                        'id': str(offer.id),
                        'counterAmount': offer.counter_offer_amount,
                        'status': offer.status,
                        'updatedAt': offer.updated_at.isoformat()
                    },
                    'message': {
                        'id': str(message.id),
                        'text': message.text,
                        'timestamp': message.created_at.isoformat()
                    }
                }
            )
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
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
                'message': 'offerId and receiverId are required'
            }))
            return
        
        try:
            # Get offer to check status and determine who can accept
            offer = await self.get_offer_async(offer_id)
            if not offer:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Offer not found'
                }))
                return
            
            # Determine if user is buyer or seller
            is_buyer = str(offer.buyer_id.id) == user_id
            is_seller = str(offer.seller_id.id) == user_id
            
            # Validate who can accept based on offer status
            if offer.status == 'pending' and not is_seller:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Only seller can accept a pending offer'
                }))
                return
            elif offer.status == 'countered' and not is_buyer:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Only buyer can accept a counter offer'
                }))
                return
            elif offer.status not in ['pending', 'countered']:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Cannot accept offer with status: {offer.status}'
                }))
                return
            
            # Accept the offer (seller accepts original, buyer accepts counter)
            if offer.status == 'pending':
                # Seller accepting buyer's offer
                offer = await self.accept_offer_async(offer_id, user_id)
            else:
                # Buyer accepting seller's counter offer
                offer = await self.accept_counter_offer_async(offer_id, user_id)
            
            # Save message
            message = await self.save_message(
                user_id, receiver_id,
                text or "Offer accepted",
                str(offer.product_id.id) if offer.product_id else None,
                [], str(offer.id)
            )
            
            # Broadcast offer acceptance to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'offer_accepted',
                    'offer': {
                        'id': str(offer.id),
                        'status': offer.status,
                        'updatedAt': offer.updated_at.isoformat()
                    },
                    'message': {
                        'id': str(message.id),
                        'text': message.text,
                        'timestamp': message.created_at.isoformat()
                    }
                }
            )
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
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
                'message': 'offerId and receiverId are required'
            }))
            return
        
        try:
            # Reject the offer
            offer = await self.reject_offer_async(offer_id, seller_id)
            
            # Save message
            message = await self.save_message(
                seller_id, receiver_id,
                text or "Offer rejected",
                str(offer.product_id.id) if offer.product_id else None,
                [], str(offer.id)
            )
            
            # Broadcast offer rejection to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'offer_rejected',
                    'offer': {
                        'id': str(offer.id),
                        'status': offer.status,
                        'updatedAt': offer.updated_at.isoformat()
                    },
                    'message': {
                        'id': str(message.id),
                        'text': message.text,
                        'timestamp': message.created_at.isoformat()
                    }
                }
            )
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def chat_message(self, event):
        """Send message to WebSocket"""
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))
    
    async def offer_sent(self, event):
        """Send offer sent event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'offer_sent',
            'offer': event['offer'],
            'message': event['message']
        }))
    
    async def offer_countered(self, event):
        """Send offer countered event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'offer_countered',
            'offer': event['offer'],
            'message': event['message']
        }))
    
    async def offer_accepted(self, event):
        """Send offer accepted event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'offer_accepted',
            'offer': event['offer'],
            'message': event['message']
        }))
    
    async def offer_rejected(self, event):
        """Send offer rejected event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'offer_rejected',
            'offer': event['offer'],
            'message': event['message']
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
    def counter_offer_async(self, offer_id, seller_id, counter_amount):
        """Counter offer asynchronously"""
        from products.services import OfferService
        return OfferService.counter_offer(offer_id, seller_id, counter_amount)
    
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
    def accept_counter_offer_async(self, offer_id, buyer_id):
        """Buyer accepts seller's counter offer"""
        from products.models import Offer
        offer = Offer.objects(id=offer_id, buyer_id=buyer_id).first()
        if not offer:
            raise ValueError("Offer not found")
        if offer.status != 'countered':
            raise ValueError("Offer is not in countered status")
        
        offer.status = 'accepted'
        offer.updated_at = datetime.utcnow()
        offer.save()
        return offer


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for notifications"""
    
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
            try:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as e:
                logger.error(f"Failed to join channel layer group: {str(e)}", exc_info=True)
                logger.warning("Continuing without channel layer group (Redis may be unavailable)")
            
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
        await self.channel_layer.group_discard(
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

