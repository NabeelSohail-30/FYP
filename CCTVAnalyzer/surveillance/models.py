from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to="videos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Detection(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    timestamp = models.FloatField()  # Time in seconds
    object_detected = models.CharField(max_length=100)
    confidence = models.FloatField()  # Probability
