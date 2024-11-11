from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import csv
import os

# Paths
model_path = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/train/weights/last.pt'
image_path = 'C:/Users/sakar/OneDrive/mt-datas/synthetic_data/1_realistic_chair/images/train/1.png'
output_folder = 'C:/Users/sakar/OneDrive/mt-datas/yolo/pose_estimation'
output_image_path = os.path.join(output_folder, 'result.png')
output_csv_path = os.path.join(output_folder, 'result.csv')

# Load the YOLO model
model = YOLO(model_path)

# Load the image with PIL
img = Image.open(image_path)
draw = ImageDraw.Draw(img)
width, height = img.size
font = ImageFont.load_default()

# Run inference on the image
results = model(image_path)[0]

# Prepare data for CSV
csv_data = []

for result in results:
    # Get the bounding box in xyxy format
    box = result.boxes.xyxy[0]
    x1, y1, x2, y2 = map(int, box)

    # Normalize bounding box values by image width and height
    norm_x1, norm_y1 = x1 / width, y1 / height
    norm_x2, norm_y2 = x2 / width, y2 / height

    # Draw the bounding box in red
    draw.rectangle([x1, y1, x2, y2], outline="red", width=2)

    # Calculate the center of the bounding box and mark it in red
    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
    norm_center_x, norm_center_y = center_x / width, center_y / height
    draw.ellipse([center_x - 3, center_y - 3, center_x + 3, center_y + 3], fill="red", outline="red")

    # Calculate normalized bounding box width and height
    bbox_width, bbox_height = x2 - x1, y2 - y1
    norm_bbox_width, norm_bbox_height = bbox_width / width, bbox_height / height

    # Get keypoints and normalize them
    keypoints = result.keypoints.xy.tolist() if result.keypoints else []
    if keypoints:
        keypoints = [(int(x), int(y)) for x, y in keypoints[0] if x != 0 and y != 0]

        # Draw keypoints with labels
        for keypoint_index, (x, y) in enumerate(keypoints):
            text = str(keypoint_index)
            draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill="blue", outline="blue")
            bbox = draw.textbbox((x, y), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.rectangle([x, y, x + text_width + 6, y + text_height + 4], fill="blue")
            draw.text((x + 3, y + 2), text, fill="white", font=font)

        # Draw top and bottom squares and connecting lines
        top_square = keypoints[:4]
        bottom_square = keypoints[4:8]
        for i in range(4):
            draw.line([top_square[i], top_square[(i + 1) % 4]], fill="green", width=2)
            draw.line([bottom_square[i], bottom_square[(i + 1) % 4]], fill="green", width=2)
            draw.line([top_square[i], bottom_square[i]], fill="green", width=2)

        # Normalize keypoints and prepare CSV data for this detection
        row = [norm_center_x, norm_center_y, norm_bbox_width, norm_bbox_height]
        for x, y in keypoints[:8]:
            norm_x, norm_y = x / width, y / height
            row.extend([norm_x, norm_y])
        
        # Ensure row has 21 elements (1 for ID + 4 bbox values + 16 keypoints)
        while len(row) < 21:
            row.extend([None, None])
        csv_data.append(row)

# Write data to CSV
with open(output_csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    for idx, row in enumerate(csv_data, start=1):
        writer.writerow([idx] + row)

# Save the annotated image
img.save(output_image_path)

# Display confirmation
print(f"Data has been saved to {output_csv_path}")
print(f"Annotated image has been saved to {output_image_path}")

# Show the annotated image
img.show()
