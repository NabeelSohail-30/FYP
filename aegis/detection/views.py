from django.shortcuts import render, redirect
from .forms import VideoUploadForm
from .models import UploadedVideo, Detection
from django.contrib.auth.decorators import login_required
from ultralytics import YOLO
import cv2
import os

@login_required
def dashboard(request):
    videos = UploadedVideo.objects.filter(user=request.user)
    return render(request, 'detection/dashboard.html', {'videos': videos})

@login_required
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
            process_video(video)
            return redirect('dashboard')
    else:
        form = VideoUploadForm()
    return render(request, 'detection/upload.html', {'form': form})

def process_video(video):
    model = YOLO("best.pt")  # Replace with your model path
    video_path = video.video.path
    cap = cv2.VideoCapture(video_path)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        results = model(frame)
        
        for r in results:
            for box in r.boxes.data.tolist():
                x1, y1, x2, y2, confidence, class_id = box
                label = model.names[int(class_id)]
                Detection.objects.create(video=video, frame_time=cap.get(cv2.CAP_PROP_POS_MSEC) / 1000, label=label, confidence=confidence)
        
    cap.release()
