import sys
import os
import shutil
import pandas as pd
import numpy as np
from ultralytics import YOLO
import cv2
from scipy.spatial.transform import Rotation as R


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lifting_models import sye_inference  # Import the provided module and function

# Use track_objects_with_yolo to complete the task
# Use YOLO to predict and process output
# Track and create a single csv containing object with distinct id's create_single_objects_csv
# Use lift_objects_to_3d to do 2D-3D lifting with SYE
# Use align_3d_to_zero_degree to transform camera angles into camera's initial zero position facing z in Unity coordinates
# Use transform_objects_to_origin_from_camera to transform camera coordinates into origin coordinates
# Use split_csv_by_id to create object and edges csv's
    
def track_objects_with_yolo(video_path, model_path, output_base_dir, camera_position, camera_rotation, start_angle, end_angle, forward_rotation, file_name, position_suffix, rotation_suffix):
    """ 
    Track objects in a video using YOLOv8's built-in tracking mode, saving results (bounding boxes, IDs, and poses)
    in a custom directory, while keeping original results intact and creating an annotated_frames folder.

    Args:
        video_path (str): Path to the video file.
        model_path (str): Path to the YOLO model weights.
        output_base_dir (str): Directory to save outputs.
        camera_position (np.ndarray): Camera's 3D position.
        camera_rotation (list): Euler angles for camera rotation in degrees.
        start_angle (float): Starting angle of camera rotation.
        end_angle (float): Ending angle of camera rotation.

    Output:
        Saves multiple files, including 2D-to-3D transformations, transformed CSVs, and split CSVs.
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

    print(f"Annotated frames saved at: {annotated_frames_folder}")
    print(f"All results saved in: {output_folder}")
    
    # Generate single_objects.csv
    single_objects_csv_path = create_single_objects_csv(annotated_frames_folder, output_folder)

    # lift 2D keypoints to 3D
    all_3d_objects_csv_path = lift_objects_to_3d(single_objects_csv_path, output_folder)

    # Apply transformations to align to 0-degree frame of the camera
    camera_transformed_csv_path = align_3d_to_zero_degree(all_3d_objects_csv_path, output_folder, start_angle, end_angle, forward_rotation)
    
    # Apply transformations to align to origin frame
    world_transformed_objects_csv_path = transform_objects_to_origin_from_camera(camera_transformed_csv_path, output_folder, camera_position, camera_rotation)

    # Split the transformed CSV into edges and objects
    split_csv_by_id(world_transformed_objects_csv_path, output_folder, file_name, position_suffix, rotation_suffix)


def create_single_objects_csv(annotated_frames_folder, output_folder):
    """
    Create a CSV containing unique objects by processing YOLO's annotated frames.

    Args:
        annotated_frames_folder (str): Path to the YOLO annotated frames folder.
        output_folder (str): Directory to save the single_objects.csv file.

    Output:
        Path to the saved single_objects.csv file.
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

    single_objects_csv_path = os.path.join(output_folder, single_objects_csv)
    single_objects_df = pd.DataFrame(center_closest_records.values())
    single_objects_df.to_csv(single_objects_csv_path, index=False)
    print(f"Generated CSV: {single_objects_csv_path}")
    return single_objects_csv_path


def lift_objects_to_3d(objects_csv_path, output_folder):
    """
    Convert 2D keypoints to 3D using a SYE model.
    Use create_3d_with_frame to create frame information

    Args:
        objects_csv_path (str): Path to the single_objects.csv file.
        output_folder (str): Directory to save the 3D predictions.

    Output:
        Saves the file objects_3d_sye_result.csv in the output folder.
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
    data_2d_path = os.path.join(output_folder, objects_2d_temp_csv)
    data_2d.to_csv(data_2d_path, index=False, header=False)
    print(f"Generated 2D CSV for lifting: {data_2d_path}")

    # Perform 2D-to-3D lifting
    try:
        # Use the lifting model to generate 3D data
        sye_inference.load_model_and_predict_3d(data_2d_path, output_folder, objects_3d_csv)
        final_csv_path = os.path.join(output_folder, objects_3d_sye_result_csv)
        print(f"Generated 3D CSV: {final_csv_path}")

        # Validate the generated 3D file
        if not os.path.exists(final_csv_path):
            print(f"Error: 3D CSV {final_csv_path} was not created.")
            return

        # After predictions, create a 3D CSV with frame numbers
        return create_3d_with_frame(objects_csv_path, final_csv_path, output_folder)

    except Exception as e:
        print(f"Error during 3D lifting: {e}")


def create_3d_with_frame(objects_csv_path, predictions_3d_path, output_folder):
    """
    Append frame numbers to the 3D predictions.
    Helper Function in lift_objects_to_3d

    Args:
        objects_csv_path (str): Path to the 2D objects file.
        predictions_3d_path (str): Path to the 3D predictions file.
        output_folder (str): Directory to save the enhanced 3D file.

    Output:
        Saves objects_3d_with_frame.csv with appended frame numbers.
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
    enhanced_3d_path = os.path.join(output_folder, objects_3d_with_frame_csv)
    predictions_3d_df.to_csv(enhanced_3d_path, index=False, header=False)
    
    print(f"Generated 3D CSV with frame numbers: {enhanced_3d_path}")
    return enhanced_3d_path

def align_3d_to_zero_degree(input_csv, output_folder, start_angle, end_angle, forward_rotation):
    """
    Align 3D points and rotations to the 0-degree frame based on camera angles.

    Args:
        input_csv (str): Path to the input 3D data CSV file.
        output_folder (str): Directory to save the transformed CSV.
        video_path (str): Path to the video file.
        start_angle (float): Starting camera rotation angle.
        end_angle (float): Ending camera rotation angle.
        forward_rotation (bool): Whether the camera rotates forward.

    Returns:
        str: Path to the generated transformed CSV file.
    """
    # Get the total number of frames from the video
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print(f"Error: Cannot open video file: {video_path}")
        return None
    num_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    video_capture.release()

    # Read the 3D data
    df_3d = pd.read_csv(input_csv, header=None)

    # Compute the rotation angle increment per frame
    angle_increment = abs(end_angle - start_angle) / (num_frames - 1)

    # Transform each row based on its frame number
    transformed_rows = []
    for _, row in df_3d.iterrows():
        object_id = row[0]  # The first column is the object ID
        pos = np.array(row.iloc[1:4])  # x, y, z position
        frame_number = row.iloc[-1]  # Frame number
        rot = np.array(row.iloc[4:7])  # Rotation as Euler angles (rx, ry, rz)

        # Calculate the current frame's rotation angle
        if forward_rotation:
            angle = start_angle + frame_number * angle_increment
        else:
            angle = start_angle - frame_number * angle_increment  # Reverse direction

        angle_rad = np.radians(angle)

        # Create the rotation matrix for aligning to 0°
        rotation_to_zero = np.array([
            [np.cos(-angle_rad), 0, np.sin(-angle_rad)],
            [0, 1, 0],
            [-np.sin(-angle_rad), 0, np.cos(-angle_rad)]
        ])

        # Transform position to the 0° frame
        aligned_pos = rotation_to_zero @ pos

        # Transform keypoints to the 0° frame (if keypoints exist)
        keypoints = np.array(row.iloc[7:31]).reshape(-1, 3)  # Reshape to 8x3 (assuming 8 keypoints)
        aligned_keypoints = []
        for kp in keypoints:
            aligned_kp = rotation_to_zero @ kp
            aligned_keypoints.append(aligned_kp)
        aligned_keypoints = np.array(aligned_keypoints)

        # Transform rotation to the 0° frame
        object_rotation_matrix = R.from_euler('xyz', rot, degrees=True).as_matrix()  # Original rotation matrix
        aligned_rotation_matrix = rotation_to_zero @ object_rotation_matrix  # Apply the inverse rotation
        aligned_rot = R.from_matrix(aligned_rotation_matrix).as_euler('xyz', degrees=True)  # Back to Euler angles

        # Combine transformed data
        transformed_row = (
            [object_id] + aligned_pos.tolist() + aligned_rot.tolist() +
            aligned_keypoints.flatten().tolist() + [frame_number]
        )
        transformed_rows.append(transformed_row)

    # Create a new DataFrame for the transformed data
    transformed_df = pd.DataFrame(transformed_rows).round(4)

    # Save the transformed data to a new CSV
    transformed_csv_path = os.path.join(output_folder, "objects_3d_transformed.csv")
    transformed_df.to_csv(transformed_csv_path, index=False, header=False)

    print(f"Generated transformed CSV: {transformed_csv_path}")
    return transformed_csv_path


def transform_objects_to_origin_from_camera(input_csv, output_folder, camera_position, camera_rotation):
    """
    Transform object positions and rotations to the camera's reference frame.

    Args:
        output_folder (str): Directory containing the transformed CSV.
        input_csv (str): Path to the aligned 3D CSV file.
        camera_position (np.ndarray): Camera's 3D position.
        camera_rotation (list): Euler angles of the camera's rotation.

    Output:
        Saves transformed_objects.csv with positions relative to the camera's world frame.
    """
    # Load the 3D object data
    df = pd.read_csv(input_csv, header=None)

    # Initialize the list for transformed data
    transformed_data = []

    # Compute the inverse of the camera's rotation matrix
    camera_rotation_matrix = R.from_euler('xyz', camera_rotation, degrees=True).as_matrix()
    inverse_camera_rotation = np.linalg.inv(camera_rotation_matrix)

    for _, row in df.iterrows():
        object_id = row[0]  # Object ID
        pos = np.array(row[1:4])  # Original position (x, y, z)
        rot = np.array(row[4:7])  # Original rotation (rx, ry, rz)

        # Transform position relative to the camera's position
        relative_pos = pos - camera_position

        # Rotate the position into the camera's reference frame
        transformed_pos = inverse_camera_rotation @ relative_pos

        # Reflect the position relative to the camera's x-coordinate
        transformed_pos = reflect_position_x(transformed_pos, camera_position)

        # Rotate the object's orientation into the camera's reference frame
        object_rotation_matrix = R.from_euler('xyz', rot, degrees=True).as_matrix()
        transformed_rotation_matrix = inverse_camera_rotation @ object_rotation_matrix
        transformed_rot = R.from_matrix(transformed_rotation_matrix).as_euler('xyz', degrees=True)

        # Combine transformed data into a new row
        transformed_row = [object_id] + transformed_pos.tolist() + transformed_rot.tolist() + row[7:].tolist()
        transformed_data.append(transformed_row)

    # Save the transformed data to a CSV
    transformed_csv_path = os.path.join(output_folder, "transformed_objects.csv")
    transformed_df = pd.DataFrame(transformed_data).round(4)
    transformed_df.to_csv(transformed_csv_path, index=False, header=False)

    print(f"Transformed objects CSV created at: {transformed_csv_path}")
    return transformed_csv_path


def reflect_position_x(position, camera_position):
    """
    Reflects the x-coordinate of a position relative to the vertical line
    passing through the camera's x-coordinate.

    Args:
        position (np.ndarray): A 3D point as [x, y, z].
        camera_position (np.ndarray): The camera's position as [x, y, z].

    Returns:
        np.ndarray: The reflected 3D position.
    """
    reflected_position = position.copy()
    reflected_position[0] = 2 * camera_position[0] - position[0]  # Reflect x-coordinate
    return reflected_position


def split_csv_by_id(transformed_csv_path, output_folder, file_name, position_suffix, rotation_suffix):
    """
    Split the transformed CSV into two separate files based on the ID in the 0th column.

    Args:
        transformed_csv_path (str): Path to the transformed 3D data CSV.
        output_folder (str): Directory to save the split CSV files.

    Output:
        Two files: edges.csv and objects.csv.
    """
    # Read the transformed 3D data
    df_transformed = pd.read_csv(transformed_csv_path, header=None)

    # Filter rows where ID is 8 (edges) and others (objects)
    edges_df = df_transformed[df_transformed[0] == 8]
    objects_df = df_transformed[df_transformed[0] != 8]
    # Save the edges and objects CSV files
    edges_csv_path = os.path.join(output_folder, f"{file_name}_{position_suffix}_{rotation_suffix}_edges.csv")
    objects_csv_path = os.path.join(output_folder, f"{file_name}_{position_suffix}_{rotation_suffix}_objects.csv")

    edges_df.to_csv(edges_csv_path, index=False, header=False)
    objects_df.to_csv(objects_csv_path, index=False, header=False)

    print(f"Generated edges CSV: {edges_csv_path}")
    print(f"Generated objects CSV: {objects_csv_path}")

# Generated files
single_objects_csv = "single_objects.csv"
objects_2d_temp_csv = "objects_2d_temp.csv"
objects_3d_csv = "objects_3d" #Temp file for SYE not visible
objects_3d_sye_result_csv = "objects_3d_sye_result.csv"
objects_3d_with_frame_csv = "objects_3d_with_frame.csv"
objects_3d_transformed_csv = "objects_3d_world_transformed.csv"
transformed_objects_csv = "transformed_objects.csv"

# Example usage
model_path_yolo = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/5_objects_and_edges/weights/last.pt'
video_base_path = r'C:/Users/sakar/OneDrive/mt-datas/test/synth'
output_base_dir = r"C:/Users/sakar/OneDrive/mt-datas/yoro"

##### Origin Camera #####

# Define the camera position
camera_position_1 = np.array([0, 0, 0])
camera_rotation_1 = [0, 0, 0]

# Modes
file_name_1 = "Movie_028"
start_angle_1 = 0
end_angle_1 = 90
forward_rotation_1 = start_angle_1 < end_angle_1
position_suffix_1 = "_o"
rotation_suffix_1 = "_f" if forward_rotation_1 else "_b"

video_path = os.path.join(video_base_path, f"{file_name_1}.mp4")
track_objects_with_yolo(video_path, model_path_yolo, output_base_dir, camera_position_1, camera_rotation_1, start_angle_1, end_angle_1, forward_rotation_1, position_suffix_1, rotation_suffix_1)

#########################

##### Corner Camera #####

# Define the camera position
camera_position_2 = np.array([5.43, 0, 7.65])
camera_rotation_2 = [0, 180, 0]

# Modes
file_name_2 = "Movie_028"
start_angle_2 = 0
end_angle_2 = 90
forward_rotation_2 = start_angle_2 < end_angle_2
position_suffix_2 = "_c"
rotation_suffix_2 = "_f" if forward_rotation_1 else "_b"

video_path = os.path.join(video_base_path, f"{file_name_2}.mp4")
track_objects_with_yolo(video_path, model_path_yolo, output_base_dir, camera_position_2, camera_rotation_2, start_angle_2, end_angle_2, forward_rotation_2, position_suffix_2, rotation_suffix_2)

#########################