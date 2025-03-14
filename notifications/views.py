from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        recent_notifications = Notification.objects.filter(
            recipient=request.user, 
        ).order_by('-created_at')[:10]
        serializer = self.get_serializer(recent_notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'])
    def delete_notification(self, request, pk=None):
        notification = self.get_object()
        notification.delete()
        return Response({'status': 'success'},status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Notification.objects.filter(recipient=request.user).delete()
        return Response({'status': 'success'},status=status.HTTP_204_NO_CONTENT)
    
    
