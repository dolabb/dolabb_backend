"""
WebSocket consumers for chat and notifications
"""
import json
import logging
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
            
            # Authenticate user if token is provided
            if token:
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
            else:
                # If no token, still allow connection but user will be None
                logger.warning("WebSocket connection without token")
                self.user = None
            
            self.conversation_id = conversation_id
            self.room_group_name = f'chat_{self.conversation_id}'
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
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
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            sender_id = data.get('senderId')
            receiver_id = data.get('receiverId')
            text = data.get('text', '')
            attachments = data.get('attachments', [])
            offer_id = data.get('offerId')
            product_id = data.get('productId')
            
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
                        'attachments': message.attachments
                    }
                }
            )
    
    async def chat_message(self, event):
        """Send message to WebSocket"""
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))
    
    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, text, product_id, attachments, offer_id):
        """Save message to database"""
        return ChatService.send_message(sender_id, receiver_id, text, product_id, attachments, offer_id)


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for notifications"""
    
    async def connect(self):
        try:
            # Get token from query parameters
            query_string = self.scope.get('query_string', b'').decode()
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]
            
            logger.info(f"Notification WebSocket connection attempt - user_id: {self.scope['url_route']['kwargs'].get('user_id')}, has_token: {bool(token)}")
            
            # Authenticate user if token is provided
            if token:
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
            else:
                logger.warning("Notification WebSocket connection without token")
                self.user = None
            
            self.user_id = self.scope['url_route']['kwargs']['user_id']
            self.room_group_name = f'notifications_{self.user_id}'
            
            # Join room group
            await self.channel_layer.group_add(
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

