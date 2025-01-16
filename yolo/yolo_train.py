import ultralytics

if __name__ == "__main__":
    model = ultralytics.YOLO("yolo11n-pose.pt")
    model.train(
        data='C:/Users/sakar/mt-3d-environments-from-video/yolo/config.yaml', 
        epochs=30, 
        imgsz=640,
    )
