from django.urls import path

from waste_reports.consumers import NotificationConsumer


websocket_urlpatterns = [
    path(
        'ws/notifications/',
        NotificationConsumer.as_asgi()
    ),
]