import os
import cv2
import numpy as np
from ultralytics.utils.plotting import Annotator, colors
from midas_depth_estimation import get_depth_map  # Import the depth estimation function
from yolo_instance_segmentation_video import construct_video_paths  # Import video path construction function
from ultralytics import YOLO

# Load the YOLO segmentation model
model = YOLO("yolov8n-seg.pt")  # segmentation model

# Load the video
video_name_with_extension = "rh_one_chair.mp4"
input_video_path, output_video_dir = construct_video_paths(video_name_with_extension)

# Open the video for reading
cap = cv2.VideoCapture(input_video_path)
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# Specify the output video path
output_video_path = os.path.join(output_video_dir, f"{os.path.splitext(video_name_with_extension)[0]}_instance_segmentation_depth.avi")

# Create the video writer object
out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*"MJPG"), fps, (w, h))

# Process video frames
while True:
    ret, im0 = cap.read()
    if not ret:
        print("Video frame is empty or video processing has been successfully completed.")
        break

    # Perform depth estimation for the current frame
    depth_map_resized = get_depth_map(im0)

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

            # Iterate over the mask coordinates and ensure they are within bounds
            for i in range(len(mask[0])):
                x = min(max(int(mask[0][i]), 0), w - 1)  # Ensure x is within bounds [0, w-1]
                y = min(max(int(mask[1][i]), 0), h - 1)  # Ensure y is within bounds [0, h-1]
                mask_bool[y, x] = True

            # Extract depth information within the mask region
            object_depth_pixels = depth_map_resized[mask_bool]  # Get depth values for masked area
            if len(object_depth_pixels) > 0:
                avg_depth = np.mean(object_depth_pixels)  # Average depth within the masked area
            else:
                avg_depth = -1  # If no depth pixels are found

            # Print the ID, bbox center, and depth in the console
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            print(f"ID: {track_id}, Center: ({center_x:.2f}, {center_y:.2f}), Average Depth: {avg_depth:.2f}")

            # Overlay the mask on the frame as a semi-transparent region
            mask_overlay = np.zeros_like(im0, dtype=np.uint8)
            mask_overlay[mask_bool] = [0, 255, 0]  # Green mask for the object
            im0 = cv2.addWeighted(im0, 1.0, mask_overlay, 0.5, 0)  # Blend the mask into the frame

            # Add depth information to the annotation
            label_with_depth = f"ID: {track_id} Depth: {avg_depth:.2f}"
            annotator.box_label((x1, y1, x2, y2), label_with_depth, color=color)

    # Write the annotated frame to the output video
    out.write(im0)

    # Display the result frame with masks and depth
    cv2.imshow("instance-segmentation-object-tracking", im0)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the video capture and writer objects
out.release()
cap.release()
cv2.destroyAllWindows()

print(f"Video saved to {output_video_path}")
