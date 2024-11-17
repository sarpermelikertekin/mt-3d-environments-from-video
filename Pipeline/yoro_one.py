import sys
import os
import cv2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions from YOLOv8, Lifting Models, and Tracking
from yolov8 import yolo_inference
from lifting_models import sye_inference
from tracker import track_and_assign_ids

def extract_frames_from_video(video_path, frames_folder):
    """
    Extract frames from the given video and save them to the specified folder.
    """
    cap = cv2.VideoCapture(video_path)
    frame_index = 0

    if not cap.isOpened():
        print(f"[ERROR] Unable to open video file: {video_path}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video
        
        frame_path = os.path.join(frames_folder, f"frame_{frame_index:05d}.jpg")
        cv2.imwrite(frame_path, frame)
        frame_index += 1

    cap.release()
    print(f"[INFO] Extracted {frame_index} frames from the video.")

# Update the main function to include tracking
def main():
    # Paths and parameters
    model_path_yolo = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/train8/weights/last.pt'
    video_path = r'C:/Users/sakar/OneDrive/mt-datas/test/synth/test_room_1/Movie_000.mp4'
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # Define the base output repository for the video
    base_output_folder = os.path.join(r'C:/Users/sakar/OneDrive/mt-datas/yoro', video_name)
    os.makedirs(base_output_folder, exist_ok=True)

    # Define folder for frames and processed results
    frames_folder = os.path.join(base_output_folder, "frames")
    processed_folder = os.path.join(base_output_folder, "frames_processed")
    tracked_folder = os.path.join(base_output_folder, "frames_tracked")
    os.makedirs(frames_folder, exist_ok=True)
    os.makedirs(processed_folder, exist_ok=True)
    os.makedirs(tracked_folder, exist_ok=True)

    # Step 1: Extract frames from the video
    print("[INFO] Extracting frames from the video...")
    extract_frames_from_video(video_path, frames_folder)
    print(f"[INFO] Frames saved in: {frames_folder}")

    # Step 2: Process each frame in the frames folder
    print("[INFO] Processing frames for YOLO and pose estimation...")
    for file_name in os.listdir(frames_folder):
        if file_name.endswith(('.png', '.jpg', '.jpeg')):  # Process only image files
            image_path = os.path.join(frames_folder, file_name)
            
            # Generate output file names based on the frame name
            base_name = os.path.splitext(file_name)[0]
            output_image_path = os.path.join(processed_folder, f'{base_name}_yolo_result.png')
            output_yolo_path = os.path.join(processed_folder, f'{base_name}_yolo_result.csv')
            output_sye_path = os.path.join(processed_folder, f'{base_name}_sye_result.csv')

            print(f"[INFO] Processing frame: {image_path}")

            # Step 3: Run YOLO inference
            yolo_inference.run_yolo_inference(model_path_yolo, image_path, output_image_path, output_yolo_path)
            
            # Step 4: Run Pose Estimation
            predictions_3d = sye_inference.load_model_and_predict_3d(
                data_2d_path=output_yolo_path,
                output_folder=processed_folder,
                file_name=base_name
            )
            
            if predictions_3d is not None:
                print(f"[INFO] 3D Predictions from Pose Estimation saved for: {base_name}")
            else:
                print(f"[WARNING] Pose Estimation failed for: {base_name}")

    # Step 5: Track objects and assign unique IDs
    print("[INFO] Tracking objects and assigning unique IDs...")
    track_and_assign_ids(processed_folder, tracked_folder)

    print(f"[INFO] Completed processing and tracking for all frames from the video: {video_path}")

if __name__ == "__main__":
    main()
