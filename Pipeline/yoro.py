import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions from YOLOv8 and Lifting Models
from yolov8 import yolo_inference
from lifting_models import sye_inference

def main():
    # Paths and parameters
    model_path_yolo = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/train/weights/last.pt'
    dataset_name = "1_realistic_chair"
    subset = "train"
    file_name = "2"
    output_folder = 'C:/Users/sakar/OneDrive/mt-datas/yolo/pose_estimation'
    
    # Step 1: Run YOLO inference
    yolo_inference.run_yolo_inference(model_path_yolo, dataset_name, subset, file_name, output_folder)
    
    # Step 2: Run Pose Estimation
    # Construct the path to the YOLO output file which serves as input for pose estimation
    data_2d_sample_path = os.path.join(output_folder, f"{dataset_name}_{subset}_{file_name}_yolo_result.csv")
    model_path_pose = r"C:\Users\sakar\mt-3d-environments-from-video\lifting_models\sye0.pth"
    
    # Define the output folder for 3D predictions
    output_3d_folder = os.path.join(output_folder, "3d_predictions")

    # Run pose estimation and save the predictions to the specified output folder
    predictions_3d = sye_inference.load_model_and_predict_3d(data_2d_sample_path, model_path_pose, output_3d_folder)
    if predictions_3d is not None:
        print("3D Predictions from Pose Estimation saved in:", output_3d_folder)

if __name__ == "__main__":
    main()