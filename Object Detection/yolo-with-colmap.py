import os
import numpy as np
import cv2  # Import OpenCV for image processing
import torch
from ultralytics import YOLO

# Importing the necessary functions from read_write_model
from read_write_model import read_model, qvec2rotmat

# Path to your COLMAP sparse model directory
output_dir = r"C:\Users\sakar\Downloads\Colmap Output\D21 2\sparse\0"

# Path to the directory containing all video images
images_dir = r"C:\Users\sakar\Downloads\Colmap Output\D21 2\dense\0\images"

# Load the YOLOv8 model (assuming the model is pre-trained)
model = YOLO('yolov8n.pt')  # Replace 'yolov8n.pt' with your model path if different

def main():
    # Read the model data from the output directory
    cameras, images, points3D = read_model(path=output_dir, ext=".bin")
    
    results_per_frame = []  # Store results for all frames
    
    for image_id, image in images.items():
        # Construct the full path to the image using the image name from COLMAP
        img_path = os.path.join(images_dir, image.name)
        
        # Check if the image exists
        if not os.path.exists(img_path):
            print(f"Image not found: {img_path}")
            continue
        
        # Load the image using OpenCV
        img = cv2.imread(img_path)
        
        # Perform object detection with YOLOv8
        results = model(img)
        
        frame_results = {"image_id": image_id, "image_name": image.name, "objects": []}
        
        if results and len(results) > 0:
            # YOLOv8 results: Extract bounding boxes (in xyxy format) and process each detected object
            bboxes = results[0].boxes.xyxy.cpu().numpy()  # Get bounding boxes

            for bbox in bboxes:
                u = (bbox[0] + bbox[2]) / 2  # Calculate center u
                v = (bbox[1] + bbox[3]) / 2  # Calculate center v

                # Get Camera Parameters
                camera = cameras[image.camera_id]
                K = np.array([[camera.params[0], 0, camera.params[2]],
                              [0, camera.params[1], camera.params[3]],
                              [0, 0, 1]])

                # Convert quaternion to rotation matrix
                R = image.qvec2rotmat()
                T = image.tvec

                # Solve for λ and world coordinates (X_w, Y_w, Z_w)
                uv1 = np.array([u, v, 1])
                inv_K = np.linalg.inv(K)
                inv_R = np.linalg.inv(R)

                # Assuming Z_w (depth) is 1 (you might need to estimate this)
                Z_w = 1.0  # This should be calculated or estimated appropriately
                lambda_uv1 = inv_K @ (R @ np.array([0, 0, Z_w]) + T)

                X_w = lambda_uv1[0] / lambda_uv1[2]
                Y_w = lambda_uv1[1] / lambda_uv1[2]
                Z_w = Z_w  # Given or estimated depth

                # Store the results for this object
                frame_results["objects"].append({
                    "u": u,
                    "v": v,
                    "3D_position": {"X_w": X_w, "Y_w": Y_w, "Z_w": Z_w}
                })

        results_per_frame.append(frame_results)
        
        # Print results for this frame
        print(f"Image ID: {image_id}")
        print(f"Image Name: {image.name}")
        for obj in frame_results["objects"]:
            print(f"Object Detected at: (u, v) = ({obj['u']}, {obj['v']})")
            print(f"Estimated 3D Position (X_w, Y_w, Z_w): ({obj['3D_position']['X_w']}, {obj['3D_position']['Y_w']}, {obj['3D_position']['Z_w']})")
        print("="*50)  # Separator for readability

    # After processing all frames, you can further handle results_per_frame
    # For example, you could save them to a JSON file, process further, etc.
    # Example: saving to a JSON file
    # import json
    # with open('detection_results.json', 'w') as f:
    #     json.dump(results_per_frame, f, indent=4)

if __name__ == "__main__":
    main()
