import json
from channels.generic.websocket import AsyncWebsocketConsumer


class DetectionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("detections_group", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("detections_group", self.channel_name)

    async def send_alert(self, event):
        await self.send(text_data=json.dumps({"detections": event["detections"]}))
