from ultralytics import YOLO
import os
import shutil
import pandas as pd


def track_objects_with_yolo(video_path, model_path, output_base_dir):
    """
    Track objects in a video using YOLOv8's built-in tracking mode, saving results (bounding boxes, IDs, and poses)
    in a custom directory, while keeping original results intact and creating an annotated_frames folder.

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
        # Copy original contents to the custom output folder
        for item in os.listdir(yolo_default_track_dir):
            src_path = os.path.join(yolo_default_track_dir, item)
            dest_path = os.path.join(output_folder, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)

        # Optionally, clear YOLO's default track folder after copying
        shutil.rmtree(yolo_default_track_dir)

    # Define the annotated frames folder
    annotated_frames_folder = os.path.join(output_folder, "annotated_frames")
    os.makedirs(annotated_frames_folder, exist_ok=True)

    # Modify the label files to drop confidence values for objects and keypoints
    frame_results_dir = os.path.join(output_folder, "labels")
    if os.path.exists(frame_results_dir):
        for label_file in os.listdir(frame_results_dir):
            src_label_path = os.path.join(frame_results_dir, label_file)
            dest_label_path = os.path.join(annotated_frames_folder, label_file)

            # Modify content: drop confidence values
            with open(src_label_path, 'r') as src_file, open(dest_label_path, 'w') as dest_file:
                for line in src_file:
                    parts = line.strip().split()
                    if len(parts) > 5:
                        # Format:
                        # <class_id> <cx> <cy> <w> <h> <x1> <y1> ... <x8> <y8> <track_id>
                        class_id, cx, cy, w, h = parts[:5]
                        keypoints = parts[5:-1]
                        track_id = parts[-1]

                        # Skip objects without a valid track_id
                        if not track_id.isdigit():
                            continue

                        # Filter out confidence values for keypoints
                        keypoints_without_conf = [kp for i, kp in enumerate(keypoints) if i % 3 != 2]  # Keep x, y only

                        # Combine the required parts
                        modified_line = ' '.join([class_id, cx, cy, w, h] + keypoints_without_conf + [track_id]) + '\n'
                        dest_file.write(modified_line)

    # Process annotated_frames to create single_objects.csv
    create_single_objects_csv(annotated_frames_folder, output_folder)

    # Define the output video path
    output_video = os.path.join(output_folder, f"{video_name}_tracked.mp4")

    print(f"Processed video saved at: {output_video}")
    print(f"Original results saved in: {output_folder}")
    print(f"Annotated frames saved at: {annotated_frames_folder}")
    print(f"All results are saved in: {output_folder}")


def create_single_objects_csv(annotated_frames_folder, output_folder):
    """
    Process the annotated frames to create single_objects.csv, ensuring one row per unique object.

    Args:
        annotated_frames_folder (str): Path to the annotated_frames folder.
        output_folder (str): Path to the output folder.
    """
    center_closest_records = {}

    for label_file in os.listdir(annotated_frames_folder):
        # Extract frame number by splitting at '_' and stripping the last part
        try:
            frame_number = int(label_file.split('_')[-1].split('.')[0].strip())
        except ValueError:
            print(f"Skipping file without a valid frame number: {label_file}")
            continue

        label_path = os.path.join(annotated_frames_folder, label_file)

        with open(label_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                class_id, cx, cy, w, h = parts[:5]
                keypoints = parts[5:-1]
                track_id = parts[-1]

                # Skip objects without a valid track_id
                if not track_id.isdigit():
                    continue

                # Convert cx (center x) to a float
                cx = float(cx)

                # Check if this object is closest to the center
                if track_id not in center_closest_records or abs(cx - 0.5) < abs(center_closest_records[track_id]["cx"] - 0.5):
                    center_closest_records[track_id] = {
                        "class_id": class_id,
                        "cx": cx,
                        "cy": cy,
                        "w": w,
                        "h": h,
                        "keypoints": ' '.join(keypoints),
                        "track_id": track_id,
                        "frame_number": frame_number  # Ensure frame number is at the end
                    }

    # Save single_objects.csv
    single_objects_csv_path = os.path.join(output_folder, "single_objects.csv")
    single_objects_df = pd.DataFrame(center_closest_records.values())
    single_objects_df.to_csv(single_objects_csv_path, index=False)

    print(f"single_objects.csv saved at: {single_objects_csv_path}")


# Example usage
model_path_yolo = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/5_objects_and_edges/weights/last.pt'
video_path = r'C:/Users/sakar/OneDrive/mt-datas/test/synth/test_room_1/Movie_000.mp4'
output_base_dir = r"C:/Users/sakar/OneDrive/mt-datas/yoro"

track_objects_with_yolo(video_path, model_path_yolo, output_base_dir)
