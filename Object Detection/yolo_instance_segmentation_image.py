import os
import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import colors
from config import get_test_images_path, get_yolo_segmentation_image_output_path  # Use config.py for paths

# Function to perform instance segmentation using YOLO and apply mask contours to the image
def perform_instance_segmentation(image):
    # Load the YOLO segmentation model
    model = YOLO("yolov8n-seg.pt")
    
    # Perform segmentation on the image
    results = model.predict(image, save=False)
    
    # List to store objects detected in this frame
    detected_objects = []

    # Create a copy of the image to apply mask contours, regardless of detections
    image_with_contours = image.copy()

    # If segmentation results exist
    if len(results[0].boxes) > 0 and results[0].masks is not None:
        masks = results[0].masks.data.cpu().numpy()  # Get segmentation masks as a numpy array (N x H x W)
        bboxes = results[0].boxes.xyxy.cpu().tolist()  # Bounding box coordinates [x1, y1, x2, y2] (for tracking only)
        class_ids = results[0].boxes.cls.cpu().tolist()  # Class IDs for each detection
        class_names = results[0].names  # Class names dictionary

        # Iterate over each detection
        for idx, (mask, bbox, class_id) in enumerate(zip(masks, bboxes, class_ids), start=1):
            object_name = class_names[int(class_id)]
            detected_objects.append({
                'class': object_name,
                'bbox': bbox,
                'mask': mask
            })

            # Resize the mask to the original image size
            mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)

            # Convert the resized mask to a uint8 format
            mask_uint8 = (mask_resized * 255).astype(np.uint8)

            # Find contours of the mask
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Define a random color for the contour
            color = colors(idx, True)

            # Draw the contour of the mask
            cv2.drawContours(image_with_contours, contours, -1, color, 2)

            # Optionally, annotate with text
            x1, y1, x2, y2 = map(int, bbox)  # Coordinates of the bounding box
            label = f"{object_name} ID:{idx}"
            cv2.putText(image_with_contours, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Return the detected objects and the image with contours (even if no detections were made)
    return detected_objects, image_with_contours

def save_segmented_image(image_name, annotated_image, output_dir):
    """ Save the segmented image in the provided directory. """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save the result with the name `originalname_yolo_segmentation.png`
    output_image_name = f"{os.path.splitext(image_name)[0]}_yolo_segmentation.png"
    output_path = os.path.join(output_dir, output_image_name)

    cv2.imwrite(output_path, annotated_image)
    print(f"YOLO segmentation result saved to: {output_path}")

def main(image_name, output_dir=None):
    # Load the image
    image_directory = get_test_images_path()  # Dynamically get image path from config
    image_path = os.path.join(image_directory, image_name)
    image = cv2.imread(image_path)

    # Perform instance segmentation and apply contours
    _, image_with_contours = perform_instance_segmentation(image)

    # If output_dir is not provided, use the default path (Single folder)
    output_dir = output_dir or get_yolo_segmentation_image_output_path()

    # Save the segmented image
    save_segmented_image(image_name, image_with_contours, output_dir)

if __name__ == "__main__":
    # Only the image name is hardcoded here
    image_name = "office.jpg"
    main(image_name)
