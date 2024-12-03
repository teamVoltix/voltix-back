from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from voltix.models import Notification
from .serializers import NotificationSerializer
from django.utils import timezone
from rest_framework import filters

# Create your views here.

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(user=user)

        # Filtrar por fechas
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Filtrar por tipo usando 'type' directamente en el queryset
        notification_type = self.request.query_params.get('notification_type')
        if notification_type:
            queryset = queryset.filter(type=notification_type)

        return queryset
