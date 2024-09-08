import os
import cv2
import numpy as np
import pandas as pd  # To store object data in a DataFrame
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from midas_depth_estimation import get_depth_map

# Global list to store object information across frames
objects_list = []
object_id_counter = 1

# Function to track objects between frames
def track_objects(current_frame_objects):
    global objects_list, object_id_counter
    
    # Check existing objects and try to match with the current frame objects
    for obj in current_frame_objects:
        matched = False
        
        # Try to match with already detected objects (same class, spatially close)
        for existing_obj in objects_list:
            if (existing_obj['class'] == obj['class']) and (iou(existing_obj['bbox'], obj['bbox']) > 0.3):  # Set an IoU threshold
                obj['id'] = existing_obj['id']
                matched = True
                break
        
        # If not matched, assign a new ID
        if not matched:
            obj['id'] = object_id_counter
            object_id_counter += 1
        
        # Add object to the final list (updating its ID if it was matched)
        objects_list.append(obj)

# Function to compute IoU (Intersection over Union) for bounding box matching
def iou(box1, box2):
    x1, y1, x2, y2 = box1
    x1b, y1b, x2b, y2b = box2

    inter_x1 = max(x1, x1b)
    inter_y1 = max(y1, y1b)
    inter_x2 = min(x2, x2b)
    inter_y2 = min(y2, y2b)

    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

    box1_area = (x2 - x1) * (y2 - y2)
    box2_area = (x2b - x1b) * (y2b - y1b)

    iou_value = inter_area / float(box1_area + box2_area - inter_area)
    return iou_value

# Function to perform depth estimation and instance segmentation on a single image
def process_image(image_path, output_dir, model):
    global object_id_counter
    # Load the image
    image = cv2.imread(image_path)
    
    # Get the image filename for saving results
    image_filename = os.path.basename(image_path)

    # Get the depth map for the image
    depth_map_resized = get_depth_map(image)

    # Create an empty segmented depth image (same size as the original image, 1 channel for depth)
    segmented_depth_image = np.zeros_like(depth_map_resized)

    # Perform segmentation on the image
    results = model.predict(image, save=False)

    # Create an annotator object to draw on the image
    annotator = Annotator(image, line_width=2)

    # List to store objects detected in this frame
    current_frame_objects = []

    if len(results[0].boxes) > 0 and results[0].masks is not None:
        print(f"Detections found in {image_filename}.")

        masks = results[0].masks.data.cpu().numpy()  # Get segmentation masks as a numpy array (N x H x W)
        bboxes = results[0].boxes.xyxy.cpu().tolist()  # Bounding box coordinates [x1, y1, x2, y2]
        class_ids = results[0].boxes.cls.cpu().tolist()  # Class IDs for each detection
        class_names = results[0].names  # Class names dictionary

        # Iterate over each detection
        for idx, (mask, bbox, class_id) in enumerate(zip(masks, bboxes, class_ids), start=1):
            object_name = class_names[int(class_id)]

            # Resize the mask to match the original image size
            original_height, original_width = image.shape[:2]
            resized_mask = cv2.resize(mask, (original_width, original_height), interpolation=cv2.INTER_NEAREST)

            # Convert the mask to a uint8 format for further processing
            mask_uint8 = (resized_mask * 255).astype(np.uint8)

            # Find contours of the mask to draw
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Draw the contours on the image
            color = colors(idx, True)
            cv2.drawContours(image, contours, -1, color, 2)

            # Optionally: Blend the mask with the original image
            mask_colored = np.zeros_like(image)
            mask_colored[resized_mask.astype(bool)] = color
            image = cv2.addWeighted(image, 1.0, mask_colored, 0.5, 0)

            x1, y1, x2, y2 = map(int, bbox)
            label = f"{object_name} ID:{idx}"
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Calculate the average depth values of the object
            mask_bool = resized_mask.astype(bool)
            object_depth_pixels = depth_map_resized[mask_bool]

            if len(object_depth_pixels) > 0:
                avg_depth = np.mean(object_depth_pixels)
                print(f"ID: {idx}, Class: {object_name}, Average Depth: {avg_depth}")
            else:
                avg_depth = None
                print(f"ID: {idx}, Class: {object_name}, No depth pixels found for this object.")

            # Store the object information for this frame
            current_frame_objects.append({
                'id': None,  # This will be assigned later in track_objects
                'class': object_name,
                'bbox': bbox,
                'avg_depth': avg_depth
            })

    else:
        print(f"No detections or masks found in {image_filename}.")

    # Track objects across frames
    track_objects(current_frame_objects)

    # Get the annotated image with bounding boxes, class labels, and masks
    annotated_image = annotator.result()

    # Save the result images
    result_image_path = os.path.join(output_dir, f'segmented_result_with_depth_{image_filename}')
    segmented_depth_image_path = os.path.join(output_dir, f'segmented_depth_image_{image_filename}')

    cv2.imwrite(result_image_path, annotated_image)
    cv2.imwrite(segmented_depth_image_path, segmented_depth_image)

    print(f"Results saved for {image_filename}.")

# Main function to iterate over multiple images in a directory
def process_images_in_directory(image_directory, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load the YOLO segmentation model
    model = YOLO("yolov8n-seg.pt")

    # Iterate over all images in the directory
    for image_filename in os.listdir(image_directory):
        image_path = os.path.join(image_directory, image_filename)

        # Only process image files
        if not image_path.endswith(('.jpg', '.jpeg', '.png')):
            continue

        print(f"Processing image: {image_filename}")
        process_image(image_path, output_dir, model)

    # Convert the list of objects to a pandas DataFrame
    df = pd.DataFrame(objects_list)
    
    # Print the dataframe and save to CSV
    print(df)
    df.to_csv(os.path.join(output_dir, "objects_data.csv"), index=False)

if __name__ == "__main__":
    image_directory = r'C:\\Users\\sakar\\OneDrive\\mt-datas\\V2P\\Images\\rhd'
    output_dir = r'C:\\Users\\sakar\\OneDrive\\mt-datas\\YOLO\\Results\\Images'
    
    # Process all images in the directory
    process_images_in_directory(image_directory, output_dir)
