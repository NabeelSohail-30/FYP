from django.db import models


class Video(models.Model):
    file = models.FileField(upload_to="videos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Detection(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    timestamp = models.FloatField()  # Time in seconds
    label = models.CharField(max_length=100)
    confidence = models.FloatField()
