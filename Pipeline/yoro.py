import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
from ultralytics import YOLO
from lifting_models import sye_inference

def main():
    # Paths and parameters
    model_path_yolo = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/train/weights/last.pt'
    dataset_name = "1_realistic_chair"
    subset = "train"
    file_name = "2"
    output_folder = 'C:/Users/sakar/OneDrive/mt-datas/yolo/pose_estimation'

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Define input video path and output paths
    video_path = r'C:\Users\sakar\OneDrive\mt-datas\test\synth\test_room_1\Movie_000.mp4'
    output_video_path = os.path.join(output_folder, f'{dataset_name}_{subset}_{file_name}_tracked.mp4')

    # Load YOLO model with ByteTrack configuration
    model = YOLO(model_path_yolo)

    # Open video input and prepare output writer
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    frame_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Exit loop if no more frames are available

        # Run YOLO inference and ByteTrack
        results = model.track(source=frame, show=False, tracker="bytetrack.yaml")

        # Parse tracked objects and perform 3D pose estimation
        for track in results:
            object_id = track.id
            bbox = track.boxes.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
            class_id = track.cls

            # Prepare bounding box data for 3D pose estimation
            bbox_data_path = os.path.join(
                output_folder, f'{dataset_name}_{subset}_{file_name}_frame_{frame_index}_object_{object_id}_bbox.csv'
            )
            prepare_bbox_data(bbox, bbox_data_path)

            # Run 3D Pose Estimation
            sye_inference.load_model_and_predict_3d(
                data_2d_path=bbox_data_path,
                output_folder=output_folder,
                dataset_name=dataset_name,
                subset=subset,
                file_name=f'{file_name}_frame_{frame_index}_object_{object_id}'
            )

        # Annotate frame with tracked objects and IDs
        annotated_frame = annotate_frame_with_tracks(frame, results)

        # Write annotated frame to the output video
        out.write(annotated_frame)
        frame_index += 1

    # Release resources
    cap.release()
    out.release()
    print(f"Tracked video saved at {output_video_path}")

def prepare_bbox_data(bbox, bbox_data_path):
    """
    Prepare data for pose estimation from the bounding box.
    """
    # Format the bounding box data as required by your pose estimation model
    with open(bbox_data_path, 'w') as f:
        f.write(f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}")

def annotate_frame_with_tracks(frame, results):
    """
    Annotate the frame with tracked object bounding boxes and IDs.
    """
    for track in results:
        bbox = track.boxes.xyxy[0].cpu().numpy()
        object_id = track.id

        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"ID: {object_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

if __name__ == "__main__":
    main()
