import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

# Load the segmentation model
model = YOLO("yolov8n-seg.pt")  # Ensure you have the correct path to your YOLOv8 segmentation model

# Load the image
image_path = r'C:\\Users\\sakar\\OneDrive\\mt-datas\\YOLO\\Test Images\\office.jpg'
image = cv2.imread(image_path)

# Check if the image was loaded successfully
if image is None:
    print(f"Error: Unable to load image at {image_path}")
    exit(1)

# Perform segmentation on the image
results = model.predict(image, save=False)

# Print the raw output for debugging
print(f"Model Results: {results}")

# Create an annotator object to draw on the image
annotator = Annotator(image, line_width=2)

# Check if we have boxes and masks in the results
if len(results[0].boxes) > 0 and results[0].masks is not None:
    print("Detections found.")

    masks = results[0].masks.xy  # List of masks for each detection
    bboxes = results[0].boxes.xyxy.cpu().tolist()  # Bounding box coordinates [x1, y1, x2, y2]
    class_ids = results[0].boxes.cls.cpu().tolist()  # Class IDs for each detection
    class_names = results[0].names  # Class names dictionary

    # Assign unique IDs manually (since boxes.id is None)
    num_detections = len(results[0].boxes)
    track_ids = list(range(1, num_detections + 1))  # IDs: 1, 2, 3, ...

    # Iterate over each detection
    for idx, (mask, bbox, class_id, track_id) in enumerate(zip(masks, bboxes, class_ids, track_ids), start=1):
        print('Detection found, iterating...')  # Debugging print

        # Retrieve the class name
        object_name = class_names[int(class_id)]

        # Draw the segmentation mask and bounding box
        color = colors(track_id, True)  # Assign a color based on the unique ID
        txt_color = annotator.get_txt_color(color)
        annotator.seg_bbox(mask=mask, mask_color=color, label=f"{object_name} ID:{track_id}", txt_color=txt_color)

        # Calculate the center of the bounding box (bbox format: [x1, y1, x2, y2])
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        # Print the ID, class, and center coordinates of the bounding box
        print(f"ID: {track_id}, Class: {object_name}, Bounding Box Center: ({center_x:.2f}, {center_y:.2f})")

else:
    print("No detections or masks found.")  # Debugging print in case no objects are detected

# Get the annotated image with bounding boxes and masks
annotated_image = annotator.result()

# Display the result image
cv2.imshow("Instance Segmentation", annotated_image)
cv2.waitKey(0)  # Wait for a key press to close the window
cv2.destroyAllWindows()

# Optionally save the result image
result_image_path = r'C:\\Users\\sakar\\OneDrive\\mt-datas\\YOLO\\Test Images\\segmented_result.jpg'
cv2.imwrite(result_image_path, annotated_image)
