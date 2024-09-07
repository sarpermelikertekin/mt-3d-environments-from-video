import cv2
import numpy as np
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

    masks = results[0].masks.data.cpu().numpy()  # Get segmentation masks as a numpy array (N x H x W)
    bboxes = results[0].boxes.xyxy.cpu().tolist()  # Bounding box coordinates [x1, y1, x2, y2]
    class_ids = results[0].boxes.cls.cpu().tolist()  # Class IDs for each detection
    class_names = results[0].names  # Class names dictionary

    # Iterate over each detection
    for idx, (mask, bbox, class_id) in enumerate(zip(masks, bboxes, class_ids), start=1):
        print('Detection found, iterating...')  # Debugging print

        # Retrieve the class name
        object_name = class_names[int(class_id)]

        # Resize the mask to match the original image size
        original_height, original_width = image.shape[:2]
        resized_mask = cv2.resize(mask, (original_width, original_height), interpolation=cv2.INTER_NEAREST)

        # Find the contours of the resized mask
        mask_uint8 = (resized_mask * 255).astype(np.uint8)  # Convert mask to uint8
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw the segmentation mask and bounding box
        color = colors(idx, True)  # Assign a color based on the unique ID
        txt_color = annotator.get_txt_color(color)

        # Draw the contour (polygon around the segmented object)
        cv2.polylines(image, contours, isClosed=True, color=color, thickness=2)

        # Add class name and object ID to the image
        x1, y1, x2, y2 = map(int, bbox)  # Bounding box coordinates
        label = f"{object_name} ID:{idx}"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Apply the resized mask to the image to get the RGB values of the segmented area
        mask_bool = resized_mask.astype(bool)  # Convert resized mask to boolean array
        object_pixels = image[mask_bool]  # Get the pixels corresponding to the segmented object

        # Calculate the average RGB values of the object
        if len(object_pixels) > 0:
            avg_rgb = np.mean(object_pixels, axis=0)
            print(f"ID: {idx}, Class: {object_name}, Average RGB: {avg_rgb}")
        else:
            print(f"ID: {idx}, Class: {object_name}, No pixels found for this object.")

else:
    print("No detections or masks found.")  # Debugging print in case no objects are detected

# Get the annotated image with bounding boxes, class labels, and masks
annotated_image = annotator.result()

# Display the result image
cv2.imshow("Instance Segmentation", annotated_image)
cv2.waitKey(0)  # Wait for a key press to close the window
cv2.destroyAllWindows()

# Optionally save the result image
result_image_path = r'C:\\Users\\sakar\\OneDrive\\mt-datas\\YOLO\\Test Images\\segmented_result.jpg'
cv2.imwrite(result_image_path, annotated_image)
