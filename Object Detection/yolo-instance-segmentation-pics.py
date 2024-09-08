import os
import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from midas_depth_estimation import get_depth_map  # Import the depth estimation function

# Function to perform depth estimation and instance segmentation on a single image
def process_image(image_path, output_dir, model):
    # Load the image
    image = cv2.imread(image_path)
    
    # Get the image filename for saving results
    image_filename = os.path.basename(image_path)

    # Get the depth map for the image
    depth_map_resized = get_depth_map(image)  # Modified to use the array

    # Create an empty segmented depth image (same size as the original image, 1 channel for depth)
    segmented_depth_image = np.zeros_like(depth_map_resized)

    # Perform segmentation on the image
    results = model.predict(image, save=False)

    # Create an annotator object to draw on the image
    annotator = Annotator(image, line_width=2)

    # Check if we have boxes and masks in the results
    if len(results[0].boxes) > 0 and results[0].masks is not None:
        print(f"Detections found in {image_filename}.")

        masks = results[0].masks.data.cpu().numpy()  # Get segmentation masks as a numpy array (N x H x W)
        bboxes = results[0].boxes.xyxy.cpu().tolist()  # Bounding box coordinates [x1, y1, x2, y2]
        class_ids = results[0].boxes.cls.cpu().tolist()  # Class IDs for each detection
        class_names = results[0].names  # Class names dictionary

        # Iterate over each detection
        for idx, (mask, bbox, class_id) in enumerate(zip(masks, bboxes, class_ids), start=1):
            print(f'Detection {idx}: Bounding Box: {bbox}, Class: {class_names[int(class_id)]}')

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

            # Apply the resized mask to the depth map to get the depth values of the segmented area
            mask_bool = resized_mask.astype(bool)  # Convert resized mask to boolean array
            object_depth_pixels = depth_map_resized[mask_bool]  # Get the depth values corresponding to the segmented object

            # Add the depth values of the segmented object to the segmented depth image
            segmented_depth_image[mask_bool] = depth_map_resized[mask_bool]

            # Calculate the average depth values of the object
            if len(object_depth_pixels) > 0:
                avg_depth = np.mean(object_depth_pixels)
                print(f"ID: {idx}, Class: {object_name}, Average Depth: {avg_depth}")
            else:
                print(f"ID: {idx}, Class: {object_name}, No depth pixels found for this object.")

    else:
        print(f"No detections or masks found in {image_filename}.")

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
    model = YOLO("yolov8n-seg.pt")  # Ensure you have the correct path to your YOLOv8 segmentation model

    # Iterate over all images in the directory
    for image_filename in os.listdir(image_directory):
        # Construct full image path
        image_path = os.path.join(image_directory, image_filename)

        # Only process files that are images (jpg, jpeg, png)
        if not image_path.endswith(('.jpg', '.jpeg', '.png')):
            continue

        print(f"Processing image: {image_filename}")
        # Call the function to process each image
        process_image(image_path, output_dir, model)

if __name__ == "__main__":
    # Set the directory containing your images
    image_directory = r'C:\\Users\\sakar\\OneDrive\\mt-datas\\V2P\\Images\\rhd'

    # Set the output directory
    output_dir = r'C:\\Users\\sakar\\OneDrive\\mt-datas\\YOLO\\Results'

    # Process all images in the directory
    process_images_in_directory(image_directory, output_dir)