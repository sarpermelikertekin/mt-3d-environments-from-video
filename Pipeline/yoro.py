import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import csv
import cv2
from ultralytics import YOLO
from lifting_models import sye_inference

def main():
    # Paths and parameters
    model_path_yolo = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/train8/weights/last.pt'
    dataset_name = "1_realistic_chair"
    subset = "train"
    file_name = "2"
    output_folder = 'C:/Users/sakar/OneDrive/mt-datas/yolo/pose_estimation'

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Define input video path and output paths
    video_path = r'C:\Users\sakar\OneDrive\mt-datas\test\synth\test_room_1\Movie_000.mp4'
    output_video_path = os.path.join(output_folder, f'{dataset_name}_{subset}_{file_name}_tracked.mp4')
    objects_csv_path = os.path.join(output_folder, f'{dataset_name}_{subset}_{file_name}_objects.csv')

    # Initialize CSV file
    with open(objects_csv_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Frame", "Object ID", "Class ID", "Bounding Box (x1, y1, x2, y2)"])

    # Load YOLO model with ByteTrack configuration
    print("[INFO] Loading YOLO model...")
    model = YOLO(model_path_yolo)
    print("[INFO] YOLO model loaded successfully.")

    # Open video input and prepare output writer
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    print(f"[INFO] Processing video: {video_path}")
    print(f"[INFO] Video dimensions: {width}x{height} at {fps} FPS")

    frame_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] End of video reached.")
            break  # Exit loop if no more frames are available

        print(f"\n[INFO] Processing frame {frame_index}...")

        # Run YOLO inference and ByteTrack
        results = model.track(source=frame, show=False, tracker="bytetrack.yaml")
        results = results[0]  # Extract the single Results object from the list
        print(f"[INFO] Detected {len(results.boxes)} objects in frame {frame_index}.")

        with open(objects_csv_path, mode='a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)

            # Parse tracked objects and perform 3D pose estimation
            for i, box in enumerate(results.boxes):
                if box.id is None:
                    print(f"  - Object {i}: No ID assigned, skipping...")
                    continue  # Skip objects without an ID

                object_id = int(box.id.cpu().numpy())  # Get object ID
                bbox = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
                class_id = int(box.cls.cpu().numpy())  # Class ID

                print(f"  - Object {i}: ID={object_id}, BBox={bbox}, Class={class_id}")

                # Save to CSV
                csv_writer.writerow([frame_index, object_id, class_id, list(map(int, bbox))])

                # Prepare bounding box data for 3D pose estimation
                bbox_data_path = os.path.join(
                    output_folder, f'{dataset_name}_{subset}_{file_name}_frame_{frame_index}_object_{object_id}_bbox.csv'
                )
                prepare_bbox_data(bbox, bbox_data_path)
                print(f"  - Saved bounding box data to {bbox_data_path}")

                # Run 3D Pose Estimation
                print(f"  - Running 3D pose estimation for object ID={object_id}...")
                sye_inference.load_model_and_predict_3d(
                    data_2d_path=bbox_data_path,
                    output_folder=output_folder,
                    dataset_name=dataset_name,
                    subset=subset,
                    file_name=f'{file_name}_frame_{frame_index}_object_{object_id}'
                )
                print(f"  - 3D pose estimation completed for object ID={object_id}")

        # Annotate frame with tracked objects and IDs
        annotated_frame = annotate_frame_with_tracks(frame, results.boxes)

        # Write annotated frame to the output video
        out.write(annotated_frame)
        frame_index += 1

    # Release resources
    cap.release()
    out.release()
    print(f"[INFO] Tracked video saved at {output_video_path}")
    print(f"[INFO] Objects data saved at {objects_csv_path}")

def prepare_bbox_data(bbox, bbox_data_path):
    """
    Prepare data for pose estimation from the bounding box.
    """
    # Format the bounding box data as required by your pose estimation model
    with open(bbox_data_path, 'w') as f:
        f.write(f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}")

def annotate_frame_with_tracks(frame, boxes):
    """
    Annotate the frame with tracked object bounding boxes and IDs.
    """
    for box in boxes:
        if box.id is None:
            continue  # Skip objects without an ID

        bbox = box.xyxy[0].cpu().numpy()
        object_id = int(box.id.cpu().numpy())

        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"ID: {object_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

if __name__ == "__main__":
    main()
