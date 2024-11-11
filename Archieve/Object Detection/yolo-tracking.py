from ultralytics import YOLO
import cv2

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Get the names of the classes
class_names = model.names

# Load video using absolute path
video_path = r'C:\\Users\\sakar\\OneDrive\\mt-datas\\YOLO\\Test Videos\\example.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Could not open video at {video_path}")
    exit()

print('Video opened successfully.')

# Read frames
while cap.isOpened():
    ret, frame = cap.read()
    
    if ret:
        print('Processing frame...')
        print('==' * 20)  # Separator before each frame's output

        # Detect and track objects
        results = model.track(frame, persist=True)

        # Print bounding box information with class names
        for result in results[0].boxes:
            box = result.xyxy[0].cpu().numpy()  # Extract bounding box coordinates
            cls = int(result.cls[0])  # Extract class index and convert to int
            conf = result.conf[0]  # Extract confidence score
            class_name = class_names[cls]  # Get the class name
            print(f"Class: {class_name}, Confidence: {conf:.2f}, BBox: {box}")

        print('==' * 20)  # Separator after each frame's output

        # Plot results on the frame
        frame_ = results[0].plot()

        # Visualize the frame
        cv2.imshow('frame', frame_)
        key = cv2.waitKey(25)
        if key & 0xFF == ord('q') or key == 27:  # 'q' or 'Esc' key
            break
    else:
        print("No more frames to read or error in reading frame.")
        break

cap.release()
cv2.destroyAllWindows()
