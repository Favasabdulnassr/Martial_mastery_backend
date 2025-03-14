import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            print(f"WebSocket connection rejected: User not authenticated")
            await self.close(code=4003) 
            return
            
        self.notification_group_name = f'notifications_{self.user.id}'
        
        # Join notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        recent_notifications = await self.get_recent_notifications()
        if recent_notifications:
            await self.send(text_data=json.dumps({
                'type': 'recent_notifications',
                'notifications': recent_notifications
            }))
    
    async def disconnect(self, close_code):
        # Leave notification group
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data.get('command') == 'delete_notification':
            notification_id = data.get('notification_id')
            if notification_id:
                success = await self.delete_notification(notification_id)
                
                if success:
                    await self.channel_layer.group_send(
                        self.notification_group_name,
                        {
                            'type':'notification_deleted',
                            'notification_id':notification_id
                        }
                    )
        
        elif data.get('command') == 'delete_all':
            await self.delete_all_notifications()

            await self.channel_layer.group_send(
                self.notification_group_name,
                {
                    'type':'all_notification_deleted'
                }
                )
    
    # Handler for notification message from channel layer
    async def notification_message(self, event):
        # Send notification to WebSocket
        if 'notification' in event and 'id' in event['notification']:
            await self.send(text_data=json.dumps({
                'type': 'new_notification',
                'notification': event['notification']
            }))



    # Handler for deleted notification
    async def notification_deleted(self,event):
        await self.send(text_data=json.dumps({
            'type':'notification_deleted',
            'notification_id': event['notification_id']


        }))    


    # Handler for all notifications deleted
    async def all_notification_deleted(self,event):
        await self.send(text_data=json.dumps({
            'type':'all_notification_deleted'

        }))      


    
    @database_sync_to_async
    def get_recent_notifications(self):
        notifications = Notification.objects.filter(
            recipient=self.user, 
        ).order_by('-created_at')[:10]
        
        return [
            {
                'id': notification.id,
                'type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'created_at': notification.created_at.isoformat(),
                'course_id': notification.course.id if notification.course else None
            }
            for notification in notifications
        ]
    
    @database_sync_to_async
    def delete_notification(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, recipient=self.user)
            notification.delete()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def delete_all_notifications(self):
        Notification.objects.filter(recipient=self.user, read=False).delete()
