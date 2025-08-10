import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json.scanner
from .models import ChatRoom,ChatMessage
from django.core.exceptions import ObjectDoesNotExist
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):   
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

           # Add debug logging
        logger.info(f"Attempting to connect to room {self.room_id}")
        logger.info(f"User: {self.scope.get('user')}")


        if not await self.can_access_room():
            logger.info(f"Access denied to room {self.room_id}")
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Successfully connected to room {self.room_id}")
        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def can_access_room(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            user = self.scope['user']
            if user.is_anonymous:
                logger.info("Anonymous user denied access")
                return False
            has_access = user == room.tutor or user == room.student
            logger.info(f"Access check for user {user.id}: {has_access}")
            return has_access
        except ObjectDoesNotExist:
            logger.info(f"Room {self.room_id} not found") 
            return False
        except Exception as e:
            logger.error(f"Error checking room access: {e}")
            return False


    async def receive(self,text_data):
        data = json.loads(text_data)

        message_type = data.get('type')

        if message_type == 'send_message':
            message = data['message']
            chat_message = await self.save_message(message,message_type)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': str(chat_message.id),
                    'message': message,
                    'sender_id': self.scope['user'].id,
                    'sender_email': self.scope['user'].email,
                    'sender_name': f"{self.scope['user'].first_name} {self.scope['user'].last_name}",
                    'timestamp': chat_message.timestamp.isoformat(),
                    'message_type': message_type 

                }
            )
    
        
    
        elif message_type == 'delete_message':
            message_id = data.get('message_id')
            deleted = await self.delete_message(message_id)
            
            if deleted:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'delete_chat_message',
                        'message_id': message_id
                    }
                )

    async def delete_chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id']
        }))
        
    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            message = ChatMessage.objects.get(
                id=message_id, 
                room_id=self.room_id, 
                sender=self.scope['user']
            )
            message.delete()
            return True
        except ObjectDoesNotExist:
            return False

    async def chat_message(self, event):
        message_data = {
            'id': event['id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_email': event['sender_email'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
            'message_type':event['message_type']
        }
        await self.send(text_data=json.dumps(message_data))
        
      

    @database_sync_to_async
    def save_message(self, message,message_type):
        chat_room = ChatRoom.objects.get(id=self.room_id)
        return ChatMessage.objects.create(
            room=chat_room,
            sender=self.scope['user'],
            content=message,
            message_type=message_type 
        )