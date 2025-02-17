from ultralytics import YOLO

model = YOLO("C:/Users/Me/Downloads/new_Model-20250117T100617Z-001/new_Model/yolo11n.pt") 

# Train the model
results = model.train(data="C:/Users/Me/Downloads/new_Model-20250117T100617Z-001/new_Model/dataset.yaml", epochs=10, simgsz=640)