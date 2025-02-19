import asyncio
from django.shortcuts import render
import cv2
import json
import threading
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Video, Detection
from .forms import VideoUploadForm
from ultralytics import YOLO

model = YOLO("./best.pt")


def upload_video(request):
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            return redirect("process_video", video_id=video.id)
    else:
        form = VideoUploadForm()

    return render(request, "upload_video.html", {"form": form})


# def process_video_stream(video_path, video_id):
#     cap = cv2.VideoCapture(video_path)
#     channel_layer = get_channel_layer()

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         results = model(frame)
#         detections = [model.names[int(cls)]
#                       for r in results for cls in r.boxes.cls]

#         if detections:
#             detection_entry = Detection.objects.create(
#                 video_id=video_id,
#                 timestamp=cap.get(cv2.CAP_PROP_POS_MSEC),
#                 detected_objects=", ".join(detections)
#             )

#             # Send detections via WebSocket
#             async_to_sync(channel_layer.group_send)(
#                 "detections_group",  # Fix group name
#                 {"type": "send_alert", "detections": detections}
#             )

#         _, buffer = cv2.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

#     cap.release()


# def detect_objects():
#     global cap, frame
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Perform detection
#         results = model(frame)

#         # Send detected objects via WebSocket
#         detections = []
#         for r in results:
#             for box in r.boxes:
#                 detections.append({
#                     "class": r.names[int(box.cls[0])],
#                     "confidence": float(box.conf[0])
#                 })

#         if detections:
#             # Send detection data via WebSocket
#             channel_layer = get_channel_layer()
#             asyncio.run(channel_layer.group_send(
#                 "detections_group",
#                 {
#                     "type": "send_alert",
#                     "detections": detections
#                 }
#             ))

#         # Encode frame for streaming
#         _, buffer = cv2.imencode(".jpg", frame)
#         yield (b"--frame\r\n"
#                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")


def video_feed(request):
    video = Video.objects.latest('id')  # Get the latest uploaded video
    video_path = video.file.path  # Ensure correct path

    def generate_frames():
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to JPG format
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

        cap.release()

    return StreamingHttpResponse(generate_frames(), content_type="multipart/x-mixed-replace; boundary=frame")


def process_video(request, video_id):
    video = Video.objects.get(id=video_id)
    return render(request, "process_video.html", {"video": video})


def dashboard(request):
    detections = Detection.objects.all().order_by("-created_at")
    return render(request, "dashboard.html", {"detections": detections})
