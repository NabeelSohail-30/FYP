import cv2
from ultralytics import YOLO
from celery import shared_task
from .models import Video, Detection

model = YOLO("./best.pt")  # Load trained YOLO model


@shared_task
def process_video_task(video_id):
    video = Video.objects.get(id=video_id)
    cap = cv2.VideoCapture(video.video_file.path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)

        for r in results:
            for box in r.boxes:
                confidence = float(box.conf[0])
                label = box.cls

                Detection.objects.create(
                    video=video,
                    timestamp=cap.get(cv2.CAP_PROP_POS_MSEC) / 1000,
                    object_detected=label,
                    confidence=confidence
                )

    cap.release()
    return "Processing Complete"
