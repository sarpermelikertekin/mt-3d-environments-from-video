import sys
import os
import shutil
import pandas as pd
import numpy as np
from ultralytics import YOLO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lifting_models import sye_inference  # Import the provided module and function


def track_objects_with_yolo(video_path, model_path, output_base_dir):
    """
    Track objects in a video using YOLOv8's built-in tracking mode, saving results (bounding boxes, IDs, and poses)
    in a custom directory, while keeping original results intact and creating an annotated_frames folder.
    """
    yolo_default_track_dir = os.path.join('runs', 'pose', 'track')

    # Load YOLOv8 model
    model = YOLO(model_path)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = os.path.join(output_base_dir, f"{video_name}_track")

    # Clear and recreate output folder
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    # Clear YOLO's default output directory
    if os.path.exists(yolo_default_track_dir):
        shutil.rmtree(yolo_default_track_dir)

    # Run YOLO tracking on the video
    model.track(source=video_path, show=True, save=True, save_txt=True, save_conf=True)

    # Copy YOLO's output to the custom directory
    if os.path.exists(yolo_default_track_dir):
        for item in os.listdir(yolo_default_track_dir):
            src_path = os.path.join(yolo_default_track_dir, item)
            dest_path = os.path.join(output_folder, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)
        shutil.rmtree(yolo_default_track_dir)  # Clear YOLO's directory after copying

    # Create annotated_frames folder
    annotated_frames_folder = os.path.join(output_folder, "annotated_frames")
    os.makedirs(annotated_frames_folder, exist_ok=True)

    # Process YOLO's labels to remove confidence values
    frame_results_dir = os.path.join(output_folder, "labels")
    if os.path.exists(frame_results_dir):
        for label_file in os.listdir(frame_results_dir):
            src_label_path = os.path.join(frame_results_dir, label_file)
            dest_label_path = os.path.join(annotated_frames_folder, label_file)

            with open(src_label_path, 'r') as src_file, open(dest_label_path, 'w') as dest_file:
                for line in src_file:
                    parts = line.strip().split()
                    if len(parts) > 5:
                        # YOLO format: <class_id> <cx> <cy> <w> <h> <x1> <y1> <conf1> ... <x8> <y8> <conf8> <total_confidence> <track_id>
                        class_id, cx, cy, w, h = parts[:5]
                        keypoints_and_conf = parts[5:-2]  # Exclude total_confidence and track_id
                        track_id = parts[-1]

                        if not track_id.isdigit():
                            continue

                        # Remove every third value (confidence) from keypoints_and_conf
                        keypoints_without_conf = [kp for i, kp in enumerate(keypoints_and_conf) if (i % 3) != 2]

                        # Combine data into the new line
                        modified_line = ' '.join([class_id, cx, cy, w, h] + keypoints_without_conf + [track_id]) + '\n'
                        dest_file.write(modified_line)

    # Generate single_objects.csv and lift 2D keypoints to 3D
    single_objects_csv_path = create_single_objects_csv(annotated_frames_folder, output_folder)
    if single_objects_csv_path is None:
        print("Error: single_objects.csv was not generated.")
        return

    lift_objects_to_3d(single_objects_csv_path, output_folder)

    # Apply transformations to align to 0-degree frame
    transformed_csv_path = align_3d_to_zero_degree(output_folder, video_path)
    print(f"Generated transformed CSV: {transformed_csv_path}")

    # Split the transformed CSV into edges and objects
    split_csv_by_id(transformed_csv_path, output_folder)

    # Log final output
    print(f"Annotated frames saved at: {annotated_frames_folder}")
    print(f"All results saved in: {output_folder}")


def split_csv_by_id(transformed_csv_path, output_folder):
    """
    Split the transformed CSV into two separate files based on the ID in the 0th column.
    """
    # Read the transformed 3D data
    df_transformed = pd.read_csv(transformed_csv_path, header=None)

    # Filter rows where ID is 8 (edges) and others (objects)
    edges_df = df_transformed[df_transformed[0] == 8]
    objects_df = df_transformed[df_transformed[0] != 8]

    # Save the edges and objects CSV files
    edges_csv_path = os.path.join(output_folder, "edges.csv")
    objects_csv_path = os.path.join(output_folder, "objects.csv")

    edges_df.to_csv(edges_csv_path, index=False, header=False)
    objects_df.to_csv(objects_csv_path, index=False, header=False)

    print(f"Generated edges CSV: {edges_csv_path}")
    print(f"Generated objects CSV: {objects_csv_path}")


def create_single_objects_csv(annotated_frames_folder, output_folder):
    """
    Process the annotated frames to create single_objects.csv, ensuring one row per unique object.
    """
    center_closest_records = {}
    for label_file in os.listdir(annotated_frames_folder):
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

                # Skip objects without valid track_id
                if not track_id.isdigit():
                    continue
                cx = float(cx)
                if track_id not in center_closest_records or abs(cx - 0.5) < abs(center_closest_records[track_id]["cx"] - 0.5):
                    center_closest_records[track_id] = {
                        "class_id": class_id,
                        "cx": cx,
                        "cy": cy,
                        "w": w,
                        "h": h,
                        "keypoints": ' '.join(keypoints),
                        "track_id": track_id,
                        "frame_number": frame_number
                    }

    if not center_closest_records:
        print("Error: No valid data to save in single_objects.csv.")
        return None

    single_objects_csv_path = os.path.join(output_folder, "single_objects.csv")
    single_objects_df = pd.DataFrame(center_closest_records.values())
    single_objects_df.to_csv(single_objects_csv_path, index=False)
    print(f"Generated CSV: {single_objects_csv_path}")
    return single_objects_csv_path


def lift_objects_to_3d(objects_csv_path, output_folder):
    """
    Use the `load_model_and_predict_3d` function to lift 2D keypoints to 3D.
    Create a separate CSV that includes frame number information after predictions are generated.
    """
    # Read the objects.csv file
    objects_df = pd.read_csv(objects_csv_path)
    if objects_df.empty:
        print("Error: Objects CSV is empty. Cannot perform 3D lifting.")
        return

    # Expand keypoints into separate columns
    keypoints_split = objects_df["keypoints"].str.split(expand=True)

    # Convert all expanded keypoints to numeric
    keypoints_split = keypoints_split.apply(pd.to_numeric, errors="coerce")

    # Drop rows with invalid or missing keypoints
    if keypoints_split.isnull().any(axis=None):
        print("Warning: Detected invalid keypoints. Dropping affected rows.")
        print(keypoints_split[keypoints_split.isnull().any(axis=1)])  # Debug: Print invalid rows
        keypoints_split = keypoints_split.dropna()

    # Drop the original keypoints column and merge the numeric keypoints back
    data_2d = objects_df.drop(columns=["keypoints", "track_id", "frame_number"])  # Keep `frame_number` separate
    data_2d = pd.concat([data_2d.reset_index(drop=True), keypoints_split.reset_index(drop=True)], axis=1)

    # Save validated 2D data to a temporary CSV
    data_2d_path = os.path.join(output_folder, "objects_2d_temp.csv")
    data_2d.to_csv(data_2d_path, index=False, header=False)
    print(f"Generated 2D CSV for lifting: {data_2d_path}")

    # Perform 2D-to-3D lifting
    try:
        # Use the lifting model to generate 3D data
        sye_inference.load_model_and_predict_3d(data_2d_path, output_folder, "objects_3d")
        final_csv_path = os.path.join(output_folder, "objects_3d_sye_result.csv")
        print(f"Generated 3D CSV: {final_csv_path}")

        # Validate the generated 3D file
        if not os.path.exists(final_csv_path):
            print(f"Error: 3D CSV {final_csv_path} was not created.")
            return

        # After predictions, create a 3D CSV with frame numbers
        create_3d_with_frame(objects_csv_path, final_csv_path, output_folder)

    except Exception as e:
        print(f"Error during 3D lifting: {e}")


def create_3d_with_frame(objects_csv_path, predictions_3d_path, output_folder):
    """
    Append frame number information to the 3D predictions CSV.
    """
    # Read the original 2D data and the generated 3D data
    objects_df = pd.read_csv(objects_csv_path)
    predictions_3d_df = pd.read_csv(predictions_3d_path, header=None)

    # Ensure the row counts match
    if len(objects_df) != len(predictions_3d_df):
        print("Error: Mismatch between 2D objects and 3D predictions row counts.")
        return

    # Add the `frame_number` column from the original 2D data to the 3D data
    predictions_3d_df["frame_number"] = objects_df["frame_number"].values

    # Save the updated 3D data with frame numbers
    enhanced_3d_path = os.path.join(output_folder, "objects_3d_with_frame.csv")
    predictions_3d_df.to_csv(enhanced_3d_path, index=False, header=False)
    print(f"Generated 3D CSV with frame numbers: {enhanced_3d_path}")


import cv2  # Required for video processing

def align_3d_to_zero_degree(output_folder, video_path):
    """
    Transform the 3D points and rotation to the 0-degree frame based on frame numbers.
    Ensures all transformed coordinates remain positive.
    """
    # Path to the generated 3D CSV with frame numbers
    input_csv_path = os.path.join(output_folder, "objects_3d_with_frame.csv")
    if not os.path.exists(input_csv_path):
        print("Error: 3D CSV with frame information not found.")
        return None

    # Get the total number of frames from the video
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print(f"Error: Cannot open video file: {video_path}")
        return None
    num_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    video_capture.release()

    # Read the 3D data
    df_3d = pd.read_csv(input_csv_path, header=None)

    # Define constants for transformation
    max_angle = 90.0  # Maximum rotation angle in degrees

    # Find the minimum X, Y, Z across all points for translation to positive space
    min_coords = np.inf * np.ones(3)  # [min_x, min_y, min_z]

    # Transform each row based on its frame number
    transformed_rows = []
    for _, row in df_3d.iterrows():
        object_id = row[0]  # The first column is the object ID
        frame_number = row.iloc[-1]  # Frame number is the last column
        angle = (frame_number / num_frames) * max_angle  # Calculate rotation angle
        angle_rad = np.radians(angle)  # Convert angle to radians

        # Create rotation matrix for the angle (rotating around Y-axis)
        rotation_matrix = np.array([
            [np.cos(angle_rad), 0, np.sin(angle_rad)],
            [0, 1, 0],
            [-np.sin(angle_rad), 0, np.cos(angle_rad)]
        ])

        # Transform position (columns 1, 2, 3 for x, y, z)
        pos = np.array(row.iloc[1:4])  # x, y, z
        transformed_pos = rotation_matrix @ pos

        # Update min_coords for translation
        min_coords = np.minimum(min_coords, transformed_pos)

        # Transform keypoints (columns 7 to 30 for 8 keypoints)
        keypoints = np.array(row.iloc[7:31]).reshape(-1, 3)  # Reshape to 8x3
        transformed_keypoints = (rotation_matrix @ keypoints.T).T  # Transform keypoints

        # Update min_coords for keypoints
        min_coords = np.minimum(min_coords, transformed_keypoints.min(axis=0))

        # Combine transformed data
        transformed_row = (
            [object_id] + transformed_pos.tolist() + row.iloc[4:7].tolist() +
            transformed_keypoints.flatten().tolist() + [frame_number]
        )
        transformed_rows.append(transformed_row)

    # Translate all coordinates to ensure positivity
    translated_rows = []
    for row in transformed_rows:
        object_id = row[0]  # Preserve the object ID
        # Translate position
        translated_pos = np.array(row[1:4]) - min_coords

        # Translate keypoints
        keypoints = np.array(row[7:31]).reshape(-1, 3)
        translated_keypoints = (keypoints - min_coords).flatten()

        # Combine translated data
        translated_row = (
            [object_id] + translated_pos.tolist() + row[4:7] +
            translated_keypoints.tolist() + [row[-1]]
        )
        translated_rows.append(translated_row)

    # Create a new DataFrame for the translated data
    translated_df = pd.DataFrame(translated_rows).round(4)

    # Save the translated data to a new CSV
    translated_csv_path = os.path.join(output_folder, "objects_3d_transformed.csv")
    translated_df.to_csv(translated_csv_path, index=False, header=False)

    print(f"Generated transformed CSV: {translated_csv_path}")
    return translated_csv_path


# Example usage
model_path_yolo = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/5_objects_and_edges/weights/last.pt'
video_path = r'C:/Users/sakar/OneDrive/mt-datas/test/synth/Movie_009.mp4'
output_base_dir = r"C:/Users/sakar/OneDrive/mt-datas/yoro"

track_objects_with_yolo(video_path, model_path_yolo, output_base_dir)
