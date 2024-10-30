from ultralytics import YOLO
import cv2

# Paths
model_path = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/train/weights/last.pt'
image_path = 'C:/Users/sakar/OneDrive/mt-datas/synthetic_data/1_black_chair/images/test/1008.png'

# Load the image
img = cv2.imread(image_path)

# Load the YOLO model
model = YOLO(model_path)

# Run inference on the image
results = model(img)[0]

for result in results:
    # Get the bounding box in xyxy format
    box = result.boxes.xyxy[0]
    
    print(result)

    x1, y1, x2, y2 = map(int, box)
    print(box)
    
    # Draw the bounding box on the image
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    # Get and draw keypoints with their indices
    keypoints = result.keypoints.xy.tolist()
    print(keypoints)
    
    for keypoint_index, (x, y) in enumerate(keypoints[0]):
        if x != 0 and y != 0:  # Check if keypoint is valid
            # Draw a small circle at the keypoint
            cv2.circle(img, (int(x), int(y)), 3, (255, 0, 0), -1)
            
            # Label the keypoint with its index
            cv2.putText(img, str(keypoint_index), (int(x), int(y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Display the image
cv2.imshow('Keypoints and Bounding Box', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
