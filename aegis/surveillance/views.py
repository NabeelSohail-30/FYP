import os
import json
import cv2
from django.shortcuts import render, redirect
from .models import Video, Detection
from .forms import VideoUploadForm
from ultralytics import YOLO

# Load YOLO model
model = YOLO("./best.pt")  # Replace with your trained model path


def upload_video(request):
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            return redirect("process_video", video_id=video.id)
    else:
        form = VideoUploadForm()

    return render(request, "upload_video.html", {"form": form})


def process_video(request, video_id):
    video = Video.objects.get(id=video_id)
    video_path = video.file.path

    cap = cv2.VideoCapture(video_path)
    frame_fps = int(cap.get(cv2.CAP_PROP_FPS))

    detections = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)

        for r in results:
            detected_objects = [model.names[int(cls)] for cls in r.boxes.cls]
            detection = Detection(video=video, timestamp=cap.get(
                cv2.CAP_PROP_POS_MSEC), detected_objects=json.dumps(detected_objects))
            detection.save()
            detections.append(detection)

        frame = results[0].plot()
        cv2.imshow("YOLO Video Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return redirect("video_detections", video_id=video.id)


def video_detections(request, video_id):
    video = Video.objects.get(id=video_id)
    detections = Detection.objects.filter(video=video)
    return render(request, "video_detections.html", {"video": video, "detections": detections})


def dashboard(request):
    videos = Video.objects.all()
    return render(request, "dashboard.html", {"videos": videos})
