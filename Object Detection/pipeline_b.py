import os
import cv2
import numpy as np
import pandas as pd
import math
from ultralytics.utils.plotting import Annotator, colors
from midas_depth_estimation import get_depth_map, save_depth_map  # Import the depth estimation function and save function
from ultralytics import YOLO
from config import get_test_videos_path, get_yolo_segmentation_video_output_path, get_midas_output_path  # Adjust the import as per your config module

def construct_video_paths(video_name_with_extension):
    """
    Constructs input and output video paths using the config settings.
    """
    video_name_without_extension = os.path.splitext(video_name_with_extension)[0]
    input_video_path = os.path.join(get_test_videos_path(), video_name_with_extension)
    output_folder = os.path.join(get_yolo_segmentation_video_output_path(video_name_without_extension))
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    output_video_path = os.path.join(output_folder, f"{video_name_without_extension}.avi")
    
    return input_video_path, output_video_path

def calculate_camera_angle(frame_num, total_frames, total_angle=90):
    """
    Calculates the camera's angle based on the frame number.
    The total angle is defined by the `total_angle` parameter, with a default of 90 degrees.
    """
    return (frame_num / total_frames) * total_angle  # Linear progression from 0 to total_angle

def calculate_distance_from_camera(angle, room_x=4, room_y=2):
    """
    Calculate the distance from the camera at (0, 0) to the furthest point visible in the center of the frame,
    considering non-square rooms where room_x and room_y may differ.
    """
    transition_angle = math.degrees(math.atan2(room_y, room_x))
    angle_radians = math.radians(angle)

    if angle <= transition_angle:
        # Calculate distance along the x-axis
        distance = room_x / math.cos(angle_radians)
    else:
        # Calculate distance along the y-axis
        distance = room_y / math.sin(angle_radians)
    
    return distance

def extract_deepest_wall_depth(depth_map, h, w):
    """
    Extract the deepest depth value along the center of the frame (vertical line on the y-axis).
    """
    center_x = w // 2
    center_column_depths = depth_map[:, center_x]  # Get depth values along the center y-axis line
    deepest_depth = np.max(center_column_depths)  # Deepest point in that line
    return deepest_depth

def calculate_cartesian_coordinates(angle, distance):
    """
    Calculate Cartesian coordinates (x, y) from polar coordinates (angle, distance).
    The camera is at the origin (0, 0).
    """
    angle_radians = math.radians(angle)
    x = distance * math.cos(angle_radians)
    y = distance * math.sin(angle_radians)
    return (x, y)

def main():
    # Set the total camera rotation angle (default to 90 degrees)
    total_angle = 90  # You can adjust this value as needed

    # Room dimensions (in meters)
    room_x, room_y = 4, 2  # Example: room size is 4 meters by 2 meters

    # Load the YOLO segmentation model
    model = YOLO("yolov8n-seg.pt")  # segmentation model

    # Load the video
    video_name_with_extension = "rh_one_chair.mp4"
    input_video_path, output_video_path = construct_video_paths(video_name_with_extension)

    # Set up directories to save depth maps
    midas_output_dir = get_midas_output_path(video_name_with_extension.replace('.mp4', ''))

    # Open the video for reading
    cap = cv2.VideoCapture(input_video_path)
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create the video writer object
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*"MJPG"), fps, (w, h))

    # DataFrames to store angles, center coordinates, and depth
    video_df = pd.DataFrame(columns=['Timestamp', 'Angle', 'Distance from Camera', 'Deepest Wall Depth', 'Cartesian Coordinates'])
    object_dfs = {}  # Dictionary to store a DataFrame for each detected object
    deepest_depths = []  # List to store deepest wall depth per frame

    # Frame center on the x-axis
    frame_center_x = w / 2

    # Dictionary to store the closest frames for each object (based on x-coordinate)
    closest_frame_by_object = {}

    # Process video frames
    frame_num = 0
    while True:
        ret, im0 = cap.read()
        if not ret:
            print("Video frame is empty or video processing has been successfully completed.")
            break

        # Calculate the timestamp and camera angle
        timestamp = frame_num / fps
        camera_angle = calculate_camera_angle(frame_num, total_frames, total_angle)

        # Calculate distance to the center of the frame based on camera angle
        distance_from_camera = calculate_distance_from_camera(camera_angle, room_x, room_y)

        # Perform depth estimation for the current frame
        depth_map_resized = get_depth_map(im0)

        # Save depth map as an image
        save_depth_map(f"frame_{frame_num}.png", depth_map_resized, midas_output_dir)

        # Extract the deepest depth at the center vertical line
        deepest_depth = extract_deepest_wall_depth(depth_map_resized, h, w)
        deepest_depths.append(deepest_depth)

        # Calculate the Cartesian coordinates for the deepest point
        cartesian_coords = calculate_cartesian_coordinates(camera_angle, distance_from_camera)

        # Add data to the video-wide DataFrame
        video_df = pd.concat([video_df, pd.DataFrame([{
            'Timestamp': timestamp,
            'Angle': camera_angle,
            'Distance from Camera': distance_from_camera,
            'Deepest Wall Depth': deepest_depth,
            'Cartesian Coordinates': cartesian_coords
        }])], ignore_index=True)

        # Perform YOLO segmentation on the frame
        results = model.track(im0, persist=True)

        # Annotator for drawing masks and labels
        annotator = Annotator(im0, line_width=2)

        # Check if there are detected boxes with IDs and segmentation masks
        if results[0].boxes.id is not None and results[0].masks is not None:
            masks = results[0].masks.xy  # Segmentation masks
            track_ids = results[0].boxes.id.int().cpu().tolist()  # Track IDs
            bboxes = results[0].boxes.xyxy.cpu().tolist()  # Bounding boxes

            # Iterate over the detected objects
            for mask, track_id, bbox in zip(masks, track_ids, bboxes):
                color = colors(int(track_id), True)

                # Draw segmentation mask and label with ID
                annotator.seg_bbox(mask=mask, mask_color=color, label=str(track_id))

                # Extract the bounding box coordinates
                x1, y1, x2, y2 = bbox

                # Initialize mask_bool array with False values
                mask_bool = np.zeros((h, w), dtype=bool)

                for i in range(len(mask[0])):
                    x = min(max(int(mask[0][i]), 0), w - 1)  # Ensure x is within bounds [0, w-1]
                    y = min(max(int(mask[1][i]), 0), h - 1)  # Ensure y is within bounds [0, h-1]
                    mask_bool[y, x] = True

                # Extract depth information within the mask region
                object_depth_pixels = depth_map_resized[mask_bool]
                avg_depth = np.mean(object_depth_pixels) if len(object_depth_pixels) > 0 else -1

                # Estimate the object's distance using the depth ratio
                if deepest_depth > 0:  # Ensure that the deepest depth is valid
                    object_distance = distance_from_camera * (avg_depth / deepest_depth)
                else:
                    object_distance = -1  # Invalid depth ratio if deepest_depth is zero

                # Calculate object center
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                # Check if the object's center_x is closest to the frame center_x
                if track_id not in closest_frame_by_object or abs(center_x - frame_center_x) < abs(closest_frame_by_object[track_id]['center_x'] - frame_center_x):
                    # Update closest frame information for the object
                    closest_frame_by_object[track_id] = {
                        'frame_num': frame_num,
                        'center_x': center_x,
                        'center_y': center_y,
                        'avg_depth': avg_depth,
                        'object_distance': object_distance  # Store the estimated object distance
                    }

                # Add data to the object-specific DataFrame
                if track_id not in object_dfs:
                    object_dfs[track_id] = pd.DataFrame(columns=['Timestamp', 'Angle', 'Center X', 'Center Y', 'Average Depth', 'Estimated Distance'])

                object_data = {'Timestamp': timestamp, 'Angle': camera_angle, 'Center X': center_x, 'Center Y': center_y, 'Average Depth': avg_depth, 'Estimated Distance': object_distance}
                object_dfs[track_id] = pd.concat([object_dfs[track_id], pd.DataFrame([object_data])], ignore_index=True)

        # Write the annotated frame to the output video
        out.write(im0)

        # Display the processed frame
        cv2.imshow("Processed Video", im0)

        # Increment frame number
        frame_num += 1

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the video capture and writer objects
    out.release()
    cap.release()
    cv2.destroyAllWindows()

    # Save the video_df as a CSV file in the same directory as the segmentation video
    video_df_csv_path = os.path.join(os.path.dirname(output_video_path), 'video_data_with_cartesian_coordinates.csv')
    video_df.to_csv(video_df_csv_path, index=False)

    # Save each object-specific DataFrame as a CSV file
    for track_id, df in object_dfs.items():
        object_csv_path = os.path.join(os.path.dirname(output_video_path), f'object_{track_id}_data.csv')
        df.to_csv(object_csv_path, index=False)

    # Final output for closest frames, average, and median values
    print("\n--- Final Output ---")

    # Print the frame where each object's center_x is closest to the center of the frame
    print("\nFrame numbers where each object is closest to the center of the frame (X-axis):")
    for track_id, data in closest_frame_by_object.items():
        print(f"Object ID {track_id}: Frame {data['frame_num']}, Center X: {data['center_x']:.2f}, Center Y: {data['center_y']:.2f}, Avg Depth: {data['avg_depth']:.2f}, Estimated Distance: {data['object_distance']:.2f} meters")

    # Print the whole video DataFrame
    print("\nWhole Video DataFrame:")
    print(video_df)

    # Print DataFrames for each object and calculate statistics
    for track_id, df in object_dfs.items():
        print(f"\nDataFrame for Object ID {track_id}:")
        print(df)

        # Calculate and print average and median values for 'Center Y' and 'Average Depth'
        avg_depth = df['Average Depth'].mean()
        median_depth = df['Average Depth'].median()
        avg_center_y = df['Center Y'].mean()
        median_center_y = df['Center Y'].median()

        print(f"\nStatistics for Object ID {track_id}:")
        print(f"Average Depth: {avg_depth:.2f}, Median Depth: {median_depth:.2f}")
        print(f"Average Center Y: {avg_center_y:.2f}, Median Center Y: {median_center_y:.2f}")

if __name__ == "__main__":
    main()
