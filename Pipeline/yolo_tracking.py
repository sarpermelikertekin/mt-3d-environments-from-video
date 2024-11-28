from ultralytics import YOLO
import os

def track_objects_with_yolo(video_path, model_path):
    """
    Track objects in a video using YOLOv8's built-in tracking mode.

    Args:
        video_path (str): Path to the input video file.
        model_path (str): Path to the YOLOv8 model file.
    """
    # Load YOLOv8 model
    model = YOLO(model_path)

    # Generate output video path
    base_name, ext = os.path.splitext(video_path)
    output_video = f"{base_name}_tracked{ext}"

    # Perform tracking
    results = model.track(source=video_path, show=True, save=True, save_txt=False, save_conf=True)

    # Move the output video to match the desired output path
    save_dir = model.overrides.get("save_dir")  # YOLO saves results in a directory
    default_output = os.path.join(save_dir, "tracked.mp4")
    if os.path.exists(default_output):
        os.rename(default_output, output_video)
        print(f"Processed video saved at: {output_video}")
    else:
        print("Could not find the tracked video. Check the save directory.")

# Example usage
model_path_yolo = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/train8/weights/last.pt'
video_path = r'C:/Users/sakar/OneDrive/mt-datas/test/synth/test_room_1/Movie_000.mp4'

track_objects_with_yolo(video_path, model_path_yolo)
