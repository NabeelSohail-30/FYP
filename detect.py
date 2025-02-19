from ultralytics import YOLO
import cv2

# Load the model
model = YOLO("./best.pt")  # Replace with your trained model path

# Open video file or webcam
video_path = "./8.mp4"  # Replace with your video file path
cap = cv2.VideoCapture(video_path)

# Get video properties
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
frame_fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define output video file
out = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(
    *"mp4v"), frame_fps, (frame_width, frame_height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection
    results = model(frame)

    # Plot results on frame
    for r in results:
        frame = r.plot()

    # Show and save frame
    cv2.imshow("YOLO Video Detection", frame)
    out.write(frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()
