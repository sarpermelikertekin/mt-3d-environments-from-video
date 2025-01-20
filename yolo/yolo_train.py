import ultralytics

if __name__ == "__main__":
    model = ultralytics.YOLO("yolov8n-pose.pt")
    model.train(
        data='../config.yaml', 
        epochs=30, 
        imgsz=640,
    )
