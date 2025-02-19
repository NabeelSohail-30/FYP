from .models import Detection, Video
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ultralytics import YOLO
import cv2
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Video
from .forms import VideoUploadForm


def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = VideoUploadForm()
    return render(request, 'upload.html', {'form': form})


model = YOLO("./best.pt")  # Load your trained model


def process_video(video_id):
    video = Video.objects.get(id=video_id)
    cap = cv2.VideoCapture(video.video_file.path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)

        for r in results:
            for box in r.boxes:
                confidence = float(box.conf[0])
                label = box.cls

                # Store detection in database
                Detection.objects.create(
                    video=video,
                    timestamp=cap.get(cv2.CAP_PROP_POS_MSEC) /
                    1000,  # Time in seconds
                    object_detected=label,
                    confidence=confidence
                )

                # Send detection data via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "detections",
                    {
                        "type": "send_detection",
                        "message": f"{label} detected with {confidence:.2f} confidence."
                    }
                )

    cap.release()


def dashboard(request):
    videos = Video.objects.all()
    stats = {}

    for video in videos:
        detections = Detection.objects.filter(video=video)
        total_detections = detections.count()

        if total_detections > 0:
            avg_confidence = sum(
                d.confidence for d in detections) / total_detections
        else:
            avg_confidence = 0

        stats[video.id] = {
            "title": video.title,
            "total_detections": total_detections,
            "avg_confidence": avg_confidence
        }

    return render(request, "dashboard.html", {"stats": stats})
