from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Detection(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    timestamp = models.FloatField()  # Frame timestamp
    detected_objects = models.TextField()  # JSON list of detected objects
    created_at = models.DateTimeField(auto_now_add=True)
