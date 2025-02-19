from django.shortcuts import render, redirect
from .models import Video, Detection
from .forms import VideoUploadForm
from .tasks import process_video_task


def upload_video(request):
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            process_video_task.delay(video.id)  # Run in background
            return redirect("dashboard")
    else:
        form = VideoUploadForm()
    return render(request, "upload.html", {"form": form})


def dashboard(request):
    videos = Video.objects.all()
    return render(request, "dashboard.html", {"videos": videos})


def video_detections(request, video_id):
    video = Video.objects.get(id=video_id)
    detections = Detection.objects.filter(video=video)
    return render(request, "detections.html", {"video": video, "detections": detections})
