from django.db import models
from django.contrib.auth.models import User

class UploadedVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Detection(models.Model):
    video = models.ForeignKey(UploadedVideo, on_delete=models.CASCADE)
    frame_time = models.FloatField()  # Time in seconds
    label = models.CharField(max_length=100)
    confidence = models.FloatField()
    detected_at = models.DateTimeField(auto_now_add=True)
