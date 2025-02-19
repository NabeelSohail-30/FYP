import cv2
import json
import os
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ultralytics import YOLO
from .models import Video, Detection

model = YOLO("./best.pt")


def home(request):
    videos = Video.objects.all().order_by('-uploaded_at')
    return render(request, 'home.html', {'videos': videos})


def upload_video(request):
    if request.method == "POST":
        video = Video.objects.create(file=request.FILES['video'])
        return redirect('process_video', video.id)
    return render(request, 'upload.html')


def process_video(request, video_id):
    video = Video.objects.get(id=video_id)
    return render(request, 'process.html', {'video': video})


def generate_frames(video_path, video_id):
    cap = cv2.VideoCapture(video_path)
    channel_layer = get_channel_layer()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        detections = [model.names[int(cls)]
                      for r in results for cls in r.boxes.cls]

        if detections:
            Detection.objects.create(video_id=video_id, timestamp=cap.get(
                cv2.CAP_PROP_POS_MSEC), detected_objects=", ".join(detections))
            async_to_sync(channel_layer.group_send)("detections_group", {
                "type": "send_alert", "detections": detections})

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

    cap.release()


def video_feed(request, video_id):
    video = Video.objects.get(id=video_id)  # Get the video object using the ID
    video_path = video.file.path  # Use the video file's path

    cap = cv2.VideoCapture(video_path)

    def generate_frames():
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)
            detections = [model.names[int(cls)]
                          for r in results for cls in r.boxes.cls]

            if detections:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "detections_group",
                    {
                        "type": "send_alert",
                        "detections": detections
                    }
                )

            _, buffer = cv2.imencode(".jpg", frame)
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

        cap.release()

    return StreamingHttpResponse(generate_frames(), content_type="multipart/x-mixed-replace; boundary=frame")
