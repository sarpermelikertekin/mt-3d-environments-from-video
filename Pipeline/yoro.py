# Pipeline/yoro.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions or classes from YOLOv8
from yolov8 import yolo_inference

def main():
    # Example usage of the function
    model_path = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/train/weights/last.pt'
    dataset_name = "1_realistic_chair"
    subset = "train"
    file_name = "2"
    output_folder = 'C:/Users/sakar/OneDrive/mt-datas/yolo/pose_estimation'

    yolo_inference.run_yolo_inference(model_path, dataset_name, subset, file_name, output_folder)

if __name__ == "__main__":
    main()