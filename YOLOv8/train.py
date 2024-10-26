import ultralytics

if __name__ == "__main__":
    model = ultralytics.YOLO("yolov8n-pose.pt")  # Load the model
    model.train(
        data='C:/Users/sakar/mt-3d-environments-from-video/YOLOv8/config.yaml', 
        epochs=30, 
        imgsz=640,
    )
