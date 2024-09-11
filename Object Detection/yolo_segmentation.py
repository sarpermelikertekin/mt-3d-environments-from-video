import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

# Function to perform instance segmentation using YOLO
def perform_instance_segmentation(image):
    # Load the YOLO segmentation model
    model = YOLO("yolov8n-seg.pt")
    
    # Perform segmentation on the image
    results = model.predict(image, save=False)
    
    # Create an annotator object to draw on the image
    annotator = Annotator(image, line_width=2)
    
    # List to store objects detected in this frame
    detected_objects = []
    
    if len(results[0].boxes) > 0 and results[0].masks is not None:
        masks = results[0].masks.data.cpu().numpy()  # Get segmentation masks as a numpy array (N x H x W)
        bboxes = results[0].boxes.xyxy.cpu().tolist()  # Bounding box coordinates [x1, y1, x2, y2]
        class_ids = results[0].boxes.cls.cpu().tolist()  # Class IDs for each detection
        class_names = results[0].names  # Class names dictionary

        # Iterate over each detection
        for idx, (mask, bbox, class_id) in enumerate(zip(masks, bboxes, class_ids), start=1):
            object_name = class_names[int(class_id)]
            detected_objects.append({
                'class': object_name,
                'bbox': bbox,
                'mask': mask
            })

            # Annotate the image
            color = colors(idx, True)
            annotator.box_label(bbox, f"{object_name} ID:{idx}", color=color)

    return detected_objects, annotator.result()  # Return the detected objects and annotated image
