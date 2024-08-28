import cv2
from ultralytics import YOLO
import pandas as pd
import random
import os

def perform_detection(image_path, result_image_path, csv_file_path):
    # COCO class names (for YOLOv8)
    COCO_CLASSES = [
        'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
        'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
        'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
        'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag',
        'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
        'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
        'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana',
        'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
        'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table',
        'toilet', 'TV', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
        'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
        'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
    ]
    
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    # Load the pre-trained YOLOv8 model
    model = YOLO('yolov8s.pt')

    # Perform object detection
    results = model.predict(source=image_path)

    # Draw the results on the image
    result_image = results[0].plot()

    # Display the result image
    cv2.imshow('Detection Results', result_image)
    print("Press any key to close the image window.")
    cv2.waitKey(0)  # Wait for a key press
    cv2.destroyAllWindows()  # Close the image window

    # Save the result image
    cv2.imwrite(result_image_path, result_image)

    # Create a list to store the detection data
    data = []

    # Extract detection details and format them
    for result in results:
        for box in result.boxes:
            # Extract coordinates and convert to float
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            # Calculate center coordinates and normalize them between 0 and 10
            pos_x = ((x1 + x2) / 2 / width) * 10
            pos_y = ((y1 + y2) / 2 / height) * 10
            pos_z = random.uniform(0, 10)
            
            # Extract class label and confidence score
            class_id = int(box.cls)
            object_name = COCO_CLASSES[class_id]
            
            # Generate random rotations and sizes
            rot_x = random.uniform(0, 360)
            rot_y = random.uniform(0, 360)
            rot_z = random.uniform(0, 360)
            size_x = 1
            size_y = 1
            size_z = 1
            
            # Append data to list
            data.append([object_name, class_id, pos_x, pos_y, pos_z, rot_x, rot_y, rot_z, size_x, size_y, size_z])

    # Create a DataFrame
    columns = ['object_name', 'id', 'pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z', 'size_x', 'size_y', 'size_z']
    df = pd.DataFrame(data, columns=columns)

    # Save the DataFrame to a CSV file
    df.to_csv(csv_file_path, index=False)

    print(f"Detection results saved to {csv_file_path}")

def main():
    # Define the common path
    common_path = 'C:\\Users\\sakar\\mt-3d-environments-from-video\\YoloV8 Object Detection\\'

    # File paths
    image_file_name = 'frame_0140.jpg'
    result_file_name = image_file_name.split('.')[0] + '_result.jpg'
    csv_file_name = 'detection_results.csv'

    image_path = os.path.join(common_path, image_file_name)
    result_image_path = os.path.join(common_path, result_file_name)
    csv_file_path = os.path.join(common_path, csv_file_name)

    # Perform detection
    perform_detection(image_path, result_image_path, csv_file_path)

if __name__ == "__main__":
    main()
