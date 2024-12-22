from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import csv
import os

def run_yolo_inference(model_path, image_path, output_image_path, output_csv_path):
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

        # Get the class ID for the detected object
        class_id = int(result.boxes.cls[0])  # Get the class ID as an integer

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

            # Check if there are enough keypoints for top and bottom squares
            if len(keypoints) >= 8:
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
            else:
                print(f"[WARNING] Not enough keypoints for 3D box drawing. Detected {len(keypoints)} keypoints.")

            # Normalize keypoints and prepare CSV data for this detection
            row = [class_id, round(norm_center_x, 2), round(norm_center_y, 2), round(norm_bbox_width, 2), round(norm_bbox_height, 2)]
            for x, y in keypoints[:8]:  # Only take the first 8 keypoints
                norm_x, norm_y = round(x / width, 2), round(y / height, 2)
                row.extend([norm_x, norm_y])

            # Trim row to exactly 21 elements (id, 4 bb info, 16 keypoint info)
            row = row[:21]
            csv_data.append(row)

    # Write data to CSV
    with open(output_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        for row in csv_data:
            writer.writerow(row)

    # Save the annotated image
    img.save(output_image_path)

    # Display confirmation
    print(f"Data has been saved to {output_csv_path}")
    print(f"Annotated image has been saved to {output_image_path}")

def main():
    # Define paths and parameters for YOLO inference
    model_path = 'C:/Users/sakar/mt-3d-environments-from-video/runs/pose/5_objects_and_edges/weights/last.pt'
    dataset_name = "5_objects_and_edges"
    subset = "test"
    file_name = "3007"
    output_folder = 'C:/Users/sakar/OneDrive/mt-datas/yolo/pose_estimation'

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Define image path, output image path, and output CSV path
    image_path = f'C:/Users/sakar/OneDrive/mt-datas/synthetic_data/{dataset_name}/images/{subset}/{file_name}.png'
    output_image_path = os.path.join(output_folder, f'{dataset_name}_{subset}_{file_name}_yolo_result.png')
    output_csv_path = os.path.join(output_folder, f'{dataset_name}_{subset}_{file_name}_yolo_result.csv')

    # Run YOLO inference
    run_yolo_inference(model_path, image_path, output_image_path, output_csv_path)

if __name__ == "__main__":
    main()
