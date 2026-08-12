from rest_framework import viewsets, mixins, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer

class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        
        notification_type = self.request.query_params.get('notification_type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
            
        is_read_param = self.request.query_params.get('is_read')
        if is_read_param is not None:
            is_read = is_read_param.lower() in ['true', '1', 't', 'y', 'yes']
            queryset = queryset.filter(is_read=is_read)
            
        return queryset

    def get_queryset(self):
        # Authenticated users must only be able to access their own notifications
        if getattr(self.request, 'user', None) and self.request.user.is_authenticated:
            return Notification.objects.filter(recipient=self.request.user)
        return Notification.objects.none()

    @action(detail=False, methods=['get'])
    def unread(self, request):
        queryset = self.get_queryset().filter(is_read=False)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marked as read'})

    @action(detail=False, methods=['patch'], url_path='read-all')
    def read_all(self, request):
        queryset = self.get_queryset().filter(is_read=False)
        count = queryset.update(is_read=True)
        return Response({'status': f'{count} notifications marked as read'})

    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.get_queryset()
        total_notifications = queryset.count()
        unread_notifications = queryset.filter(is_read=False).count()
        read_notifications = total_notifications - unread_notifications
        
        return Response({
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'read_notifications': read_notifications
        })

    @action(detail=False, methods=['get', 'patch'])
    def preferences(self, request):
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = NotificationPreferenceSerializer(preference)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = NotificationPreferenceSerializer(preference, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
