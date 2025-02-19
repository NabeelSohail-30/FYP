from django.urls import re_path
from .consumers import DetectionConsumer

websocket_urlpatterns = [
    re_path(r"ws/detections/(?P<video_id>\d+)/$", DetectionConsumer.as_asgi()),
]
