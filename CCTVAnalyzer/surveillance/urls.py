from django.urls import path
from .views import upload_video, dashboard, video_detections

urlpatterns = [
    path("upload/", upload_video, name="upload_video"),
    path("dashboard/", dashboard, name="dashboard"),
    path("detections/<int:video_id>/", video_detections, name="video_detections"),
]
