import os
import cv2
import numpy as np
import pandas as pd
from yolo_instance_segmentation_image import perform_instance_segmentation, save_segmented_image
from midas_depth_estimation import get_depth_map, save_depth_map
from config import get_v2p_images_path, get_yolo_segmentation_image_output_path, get_midas_output_path  # Import paths from config.py

# Global list to store object information across frames
objects_list = []
object_id_counter = 1

# Function to track objects between frames
def track_objects(current_frame_objects):
    global objects_list, object_id_counter

    # Check existing objects and try to match with the current frame objects
    for obj in current_frame_objects:
        matched = False
        for existing_obj in objects_list:
            if existing_obj['class'] == obj['class'] and iou(existing_obj['bbox'], obj['bbox']) > 0.3:
                obj['id'] = existing_obj['id']
                matched = True
                break

        if not matched:
            obj['id'] = object_id_counter
            object_id_counter += 1

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
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x2b - x1b) * (y2b - y1b)
    return inter_area / float(box1_area + box2_area - inter_area)

# Main pipeline function
def process_image_pipeline(image_path, output_dir_yolo, output_dir_midas):
    global object_id_counter

    # Load the image
    image = cv2.imread(image_path)

    # Perform depth estimation
    depth_map_resized = get_depth_map(image)

    # Perform instance segmentation
    detected_objects, annotated_image = perform_instance_segmentation(image)

    # Save depth map and segmented image
    image_name = os.path.basename(image_path)
    save_depth_map(image_name, depth_map_resized, output_dir_midas)
    save_segmented_image(image_name, annotated_image, output_dir_yolo)

    # Track objects and calculate depth
    current_frame_objects = []

    for obj in detected_objects:
        bbox = obj['bbox']
        mask = obj['mask']
        class_name = obj['class']

        # Resize the mask to match the original image size (depth map size)
        original_height, original_width = image.shape[:2]
        resized_mask = cv2.resize(mask, (original_width, original_height), interpolation=cv2.INTER_NEAREST)

        # Calculate the average depth values of the object
        mask_bool = resized_mask.astype(bool)  # Ensure mask is a boolean array
        object_depth_pixels = depth_map_resized[mask_bool]

        avg_depth = np.mean(object_depth_pixels) if len(object_depth_pixels) > 0 else None

        current_frame_objects.append({
            'id': None,
            'class': class_name,
            'bbox': bbox,
            'avg_depth': avg_depth
        })

    # Track objects across frames
    track_objects(current_frame_objects)

    print(f"Results saved for {image_name}.")


# Main function to iterate over multiple images in a directory
def process_images_in_directory(image_directory, output_dir_yolo, output_dir_midas):
    os.makedirs(output_dir_yolo, exist_ok=True)
    os.makedirs(output_dir_midas, exist_ok=True)

    for image_filename in os.listdir(image_directory):
        if not image_filename.endswith(('.jpg', '.jpeg', '.png')):
            continue
        image_path = os.path.join(image_directory, image_filename)
        process_image_pipeline(image_path, output_dir_yolo, output_dir_midas)

    # Save the object information to CSV
    df = pd.DataFrame(objects_list)
    print(df)
    df.to_csv(os.path.join(output_dir_yolo, "objects_data.csv"), index=False)

if __name__ == "__main__":
    images_folder_name = "rh_one_chair"  # This is the "video name"
    image_directory = get_v2p_images_path(images_folder_name)

    # Set YOLO and Midas output directories using the video name (no Single folder in main script)
    output_dir_yolo = get_yolo_segmentation_image_output_path(images_folder_name)
    output_dir_midas = get_midas_output_path(images_folder_name)

    process_images_in_directory(image_directory, output_dir_yolo, output_dir_midas)
