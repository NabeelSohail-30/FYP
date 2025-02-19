import threading
from ultralytics import YOLO
from .models import Video, Detection
from django.shortcuts import render
import cv2
from django.shortcuts import render, redirect
from .forms import VideoUploadForm
from .models import Video


def upload_video(request):
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            return redirect("play_video", video_id=video.id)
    else:
        form = VideoUploadForm()

    return render(request, "upload.html", {"form": form})


model = YOLO("./best.pt")  # Load YOLO Model


def process_video(video_id):
    video = Video.objects.get(id=video_id)
    video_path = video.file.path

    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)  # Run detection
        for r in results:
            for box in r.boxes:
                Detection.objects.create(
                    video=video,
                    timestamp=cap.get(cv2.CAP_PROP_POS_MSEC) /
                    1000.0,  # Convert to seconds
                    label=r.names[int(box.cls)],
                    confidence=float(box.conf)
                )

    cap.release()


def play_video(request, video_id):
    video = Video.objects.get(id=video_id)

    # Start processing in background
    thread = threading.Thread(target=process_video, args=(video_id,))
    thread.start()

    return render(request, "play_video.html", {"video": video})


def dashboard(request):
    videos = Video.objects.prefetch_related("detection_set").all()
    
    # Exclude detections where label is "person"
    for video in videos:
        video.filtered_detections = video.detection_set.exclude(label="person")
    
    return render(request, "dashboard.html", {"videos": videos})