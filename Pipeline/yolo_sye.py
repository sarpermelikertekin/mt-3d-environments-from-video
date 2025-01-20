import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Simple 6D Pose Estimator from a monocular image

# Import functions from YOLOv8 and Lifting Models
from yolo import yolo_inference
from lifting_models import sye_inference

def main():
    # Paths and parameters
    model_path_yolo = ''
    dataset_name = ""
    subset = ""
    file_name = ""
    output_folder = ''

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Define input image path and output paths for YOLO results
    image_path = f''
    output_image_path = os.path.join(output_folder, f'{dataset_name}_{subset}_{file_name}_yolo_result.png')
    output_yolo_path = os.path.join(output_folder, f'{dataset_name}_{subset}_{file_name}_yolo_result.csv')

    # Step 1: Run YOLO inference
    yolo_inference.run_yolo_inference(model_path_yolo, image_path, output_image_path, output_yolo_path)
    
    # Step 2: Run Pose Estimation with dynamic model selection based on object ID
    predictions_3d = sye_inference.load_model_and_predict_3d(
        data_2d_path=output_yolo_path,
        output_folder=output_folder,
        file_name=file_name
    )
    
    if predictions_3d is not None:
        print(f"3D Predictions from Pose Estimation saved with '_sye' suffix in: {output_folder}")

if __name__ == "__main__":
    main()
