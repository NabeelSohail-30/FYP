from django.urls import path
from .views import home, upload_video, process_video, video_feed

urlpatterns = [
    path('', home, name='home'),
    path('upload/', upload_video, name='upload_video'),
    path('process/<int:video_id>/', process_video, name='process_video'),
    path('video_feed/<int:video_id>/', video_feed, name='video_feed'),
]
