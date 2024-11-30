from ultralytics import YOLO
import os
import shutil

def track_objects_with_yolo(video_path, model_path, output_base_dir):
    """
    Track objects in a video using YOLOv8's built-in tracking mode, saving results (bounding boxes and IDs)
    in a custom directory. Clears and manages the default YOLO output directory.

    Args:
        video_path (str): Path to the input video file.
        model_path (str): Path to the YOLOv8 model file.
        output_base_dir (str): Base directory to save the results.
    """
    # YOLO's default results folder
    yolo_default_track_dir = os.path.join('runs', 'pose', 'track')

    # Load YOLOv8 model
    model = YOLO(model_path)

    # Get video name without extension
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # Define the custom output folder for this video with "_track" appended
    output_folder = os.path.join(output_base_dir, f"{video_name}_track")

    # Ensure output folder exists
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)  # Clear old results
    os.makedirs(output_folder)

    # Clear YOLO's default tracking folder if it exists
    if os.path.exists(yolo_default_track_dir):
        shutil.rmtree(yolo_default_track_dir)

    # Perform tracking with YOLO
    model.track(
        source=video_path,
        show=True,
        save=True,
        save_txt=True,
        save_conf=True
    )

    # Verify that YOLO's default track directory exists after processing
    if os.path.exists(yolo_default_track_dir):
        # Copy contents to the custom output folder
        for item in os.listdir(yolo_default_track_dir):
            src_path = os.path.join(yolo_default_track_dir, item)
            dest_path = os.path.join(output_folder, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)

        # Optionally, clear YOLO's default track folder after copying
        shutil.rmtree(yolo_default_track_dir)

    # Define the output video path
    output_video = os.path.join(output_folder, f"{video_name}_tracked.mp4")

    print(f"Processed video saved at: {output_video}")

    # Frame-by-frame text results
    frame_results_dir = os.path.join(output_folder, "labels")
    if os.path.exists(frame_results_dir):
        print(f"Frame-by-frame results saved at: {frame_results_dir}")
    else:
        print("Could not find frame results. Check the save directory.")

    print(f"All results are saved in: {output_folder}")


# Example usage
model_path_yolo = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/train8/weights/last.pt'
video_path = r'C:/Users/sakar/OneDrive/mt-datas/test/synth/test_room_1/Movie_000.mp4'
output_base_dir = r"C:/Users/sakar/OneDrive/mt-datas/yoro"

track_objects_with_yolo(video_path, model_path_yolo, output_base_dir)
