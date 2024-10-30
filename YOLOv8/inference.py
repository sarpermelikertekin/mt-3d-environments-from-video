from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import os

# Paths
model_path = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/train/weights/last.pt'
image_path = 'C:/Users/sakar/OneDrive/mt-datas/synthetic_data/1_black_chair/images/test/1008.png'

# Load the YOLO model
model = YOLO(model_path)

# Load the image with PIL
img = Image.open(image_path)
draw = ImageDraw.Draw(img)
width, height = img.size
font = ImageFont.load_default()

# Run inference on the image
results = model(image_path)[0]

for result in results:
    # Get the bounding box in xyxy format
    box = result.boxes.xyxy[0]
    x1, y1, x2, y2 = map(int, box)

    # Draw the bounding box in red
    draw.rectangle([x1, y1, x2, y2], outline="red", width=2)

    # Calculate the center of the bounding box and mark it in red
    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
    draw.ellipse([center_x - 3, center_y - 3, center_x + 3, center_y + 3], fill="red", outline="red")

    # Get and draw keypoints with their indices, using different colors for corners and edges
    keypoints = result.keypoints.xy.tolist()
    
    if keypoints:  # Ensure keypoints are available
        # Convert all keypoints to integer tuples
        keypoints = [(int(x), int(y)) for x, y in keypoints[0] if x != 0 and y != 0]

        for keypoint_index, (x, y) in enumerate(keypoints):
            # Draw keypoints in blue with labels in white
            text = str(keypoint_index)
            
            # Draw a blue circle at each keypoint
            draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill="blue", outline="blue")

            # Draw label with white text on a blue background
            bbox = draw.textbbox((x, y), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.rectangle([x, y, x + text_width + 6, y + text_height + 4], fill="blue")
            draw.text((x + 3, y + 2), text, fill="white", font=font)

        # Divide keypoints into top and bottom squares
        top_square = keypoints[:4]
        bottom_square = keypoints[4:8]

        # Draw edges of the top and bottom squares in green and connect corresponding top and bottom points
        for i in range(4):
            # Draw lines for the top square
            pt1, pt2 = top_square[i], top_square[(i + 1) % 4]
            draw.line([pt1, pt2], fill="green", width=2)

            # Draw lines for the bottom square
            pt1, pt2 = bottom_square[i], bottom_square[(i + 1) % 4]
            draw.line([pt1, pt2], fill="green", width=2)

            # Draw vertical lines connecting top and bottom squares
            draw.line([top_square[i], bottom_square[i]], fill="green", width=2)

# Show the annotated image
img.show()
