import os
from collections import defaultdict
import cv2
import pandas as pd  # For DataFrame handling
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from config import get_test_videos_path, get_yolo_segmentation_video_output_path  # Import paths from config.py

# Function to perform instance segmentation with tracking on a video
def process_video(video_name_with_extension):
    """Process the input video and perform instance segmentation with tracking."""
    
    # Track history stores the trajectory of each object
    track_history = defaultdict(lambda: [])

    # A dictionary to store unique object IDs and their class names
    tracked_objects = {}

    # Construct the input and output paths
    input_video_path, output_video_dir = construct_video_paths(video_name_with_extension)

    # YOLO segmentation model
    model = YOLO("yolov8n-seg.pt")  # segmentation model
    cap = cv2.VideoCapture(input_video_path)

    # Get video properties
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    # Output video path (inside the output directory)
    output_video_path = os.path.join(output_video_dir, f"{os.path.splitext(video_name_with_extension)[0]}_instance_segmentation_tracking.avi")
    print(f"Output video path: {output_video_path}")

    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*"MJPG"), fps, (w, h))

    # Process video frames
    while True:
        ret, im0 = cap.read()
        if not ret:
            print("Video frame is empty or video processing has been successfully completed.")
            break

        annotator = Annotator(im0, line_width=2)

        # Perform tracking
        results = model.track(im0, persist=True)

        if results[0].boxes.id is not None and results[0].masks is not None:
            masks = results[0].masks.xy
            track_ids = results[0].boxes.id.int().cpu().tolist()
            bboxes = results[0].boxes.xyxy.cpu().tolist()  # Extract bounding boxes
            class_ids = results[0].boxes.cls.int().cpu().tolist()  # Class IDs
            class_names = results[0].names  # Get class names from the model

            for mask, track_id, bbox, class_id in zip(masks, track_ids, bboxes, class_ids):
                color = colors(int(track_id), True)
                txt_color = annotator.get_txt_color(color)
                annotator.seg_bbox(mask=mask, mask_color=color, label=str(track_id), txt_color=txt_color)

                # Calculate the center of the bounding box (bbox format: [x1, y1, x2, y2])
                x1, y1, x2, y2 = bbox
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                # Add the track ID and center coordinates to track_history
                track_history[track_id].append((center_x, center_y))

                # Add the track ID and its corresponding class name to tracked_objects
                if track_id not in tracked_objects:
                    tracked_objects[track_id] = class_names[class_id]

                # Print the ID and center coordinates (optional)
                print(f"ID: {track_id}, Class: {class_names[class_id]}, Center: ({center_x:.2f}, {center_y:.2f})")

        out.write(im0)
        cv2.imshow("instance-segmentation-object-tracking", im0)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release resources
    out.release()
    cap.release()
    cv2.destroyAllWindows()

    # After processing the video, create a DataFrame from the tracked objects
    df = pd.DataFrame(list(tracked_objects.items()), columns=["Object ID", "Class Name"])

    # Print the DataFrame
    print("\nFinal DataFrame of tracked objects:")
    print(df)

    # Output CSV path
    csv_output_path = os.path.join(output_video_dir, f"{os.path.splitext(video_name_with_extension)[0]}_tracked_objects.csv")
    print(f"Output CSV path: {csv_output_path}")

    # Save the DataFrame to a CSV file inside the output directory
    df.to_csv(csv_output_path, index=False)

    # Print the CSV save location
    print(f"Tracked objects saved to: {csv_output_path}")

def construct_video_paths(video_name_with_extension):
    """Construct the input video path and output video directory."""
    # Get input video path using the video name
    input_video_path = os.path.join(get_test_videos_path(), video_name_with_extension)
    
    # Get output video directory path for YOLO segmentation
    video_name = os.path.splitext(video_name_with_extension)[0]  # Extract video name without extension
    output_video_dir = get_yolo_segmentation_video_output_path(video_name)

    # Ensure output directory exists
    os.makedirs(output_video_dir, exist_ok=True)

    # Print the constructed paths for debugging
    print(f"Input video path: {input_video_path}")
    print(f"Output video directory: {output_video_dir}")

    return input_video_path, output_video_dir


def main():
    # Define the video file to be processed
    video_name_with_extension = "rh_one_chair.mp4"  # Update this to your target video name

    # Process the video
    process_video(video_name_with_extension)


if __name__ == "__main__":
    main()
