import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions from YOLOv8 and Lifting Models
from yolov8 import yolo_inference
from lifting_models import sye_inference

def main():
    # Paths and parameters
    model_path_yolo = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/train8/weights/last.pt'
    dataset_name = "5_Edges"
    subset = "test"
    input_folder = f'C:/Users/sakar/OneDrive/mt-datas/synthetic_data/{dataset_name}/images/{subset}'
    output_folder = 'C:/Users/sakar/OneDrive/mt-datas/yolo/pose_estimation'

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through all images in the folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith(('.png', '.jpg', '.jpeg')):  # Process only image files
            image_path = os.path.join(input_folder, file_name)
            
            # Generate output file names based on input file
            base_name = os.path.splitext(file_name)[0]
            output_image_path = os.path.join(output_folder, f'{dataset_name}_{subset}_{base_name}_yolo_result.png')
            output_yolo_path = os.path.join(output_folder, f'{dataset_name}_{subset}_{base_name}_yolo_result.csv')

            print(f"[INFO] Processing image: {image_path}")

            # Step 1: Run YOLO inference
            yolo_inference.run_yolo_inference(model_path_yolo, image_path, output_image_path, output_yolo_path)
            
            # Step 2: Run Pose Estimation
            predictions_3d = sye_inference.load_model_and_predict_3d(
                data_2d_path=output_yolo_path,
                output_folder=output_folder,
                dataset_name=dataset_name,
                subset=subset,
                file_name=base_name
            )
            
            if predictions_3d is not None:
                print(f"[INFO] 3D Predictions from Pose Estimation saved for: {base_name}")
            else:
                print(f"[WARNING] Pose Estimation failed for: {base_name}")

    print(f"[INFO] Completed processing all images in {input_folder}")

if __name__ == "__main__":
    main()
