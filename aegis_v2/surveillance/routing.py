from django.urls import re_path
from .consumers import DetectionConsumer

websocket_urlpatterns = [
    re_path(r'ws/detections/$', DetectionConsumer.as_asgi()),
]
