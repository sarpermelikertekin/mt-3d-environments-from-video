import os
import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from config import get_test_images_path, get_yolo_segmentation_output_path  # Use config.py for paths

# Function to perform instance segmentation using YOLO
def perform_instance_segmentation(image):
    # Load the YOLO segmentation model
    model = YOLO("yolov8n-seg.pt")
    
    # Perform segmentation on the image
    results = model.predict(image, save=False)
    
    # Create an annotator object to draw on the image
    annotator = Annotator(image, line_width=2)
    
    # List to store objects detected in this frame
    detected_objects = []
    
    if len(results[0].boxes) > 0 and results[0].masks is not None:
        masks = results[0].masks.data.cpu().numpy()  # Get segmentation masks as a numpy array (N x H x W)
        bboxes = results[0].boxes.xyxy.cpu().tolist()  # Bounding box coordinates [x1, y1, x2, y2]
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

            # Annotate the image
            color = colors(idx, True)
            annotator.box_label(bbox, f"{object_name} ID:{idx}", color=color)

    return detected_objects, annotator.result()  # Return the detected objects and annotated image

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

    # Perform instance segmentation
    _, annotated_image = perform_instance_segmentation(image)

    # If output_dir is not provided, use the default path (Single folder)
    output_dir = output_dir or get_yolo_segmentation_output_path()

    # Save the segmented image
    save_segmented_image(image_name, annotated_image, output_dir)

if __name__ == "__main__":
    # Only the image name is hardcoded here
    image_name = "office.jpg"
    main(image_name)
