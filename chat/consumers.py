"""
WebSocket consumers for chat and notifications
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.services import ChatService
from chat.models import Message, Conversation
from authentication.models import User
from notifications.models import UserNotification


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for chat"""
    
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
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
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'notifications_{self.user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
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

