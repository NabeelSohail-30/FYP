import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Detection


class DetectionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.video_id = self.scope["url_route"]["kwargs"]["video_id"]
        await self.channel_layer.group_add(f"video_{self.video_id}", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(f"video_{self.video_id}", self.channel_name)

    async def send_detection(self, event):
        await self.send(text_data=json.dumps(event["data"]))
