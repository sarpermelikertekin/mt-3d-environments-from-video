import cv2
from ultralytics import YOLO
import os
import sys

sys.path.append(r'C:\\Users\\sakar\\mt-3d-environments-from-video\\Utils')
from data_to_csv import write_detection_data_to_csv

def perform_detection(image_path, result_image_path, csv_file_path):
    # Load the pre-trained YOLOv8 model
    model = YOLO('yolov8s.pt')

    # Get the names of the classes from the model
    class_names = model.names

    image = cv2.imread(image_path)
    height, width, _ = image.shape

    # Perform object detection
    results = model.predict(source=image_path)

    # Draw the results on the image
    result_image = results[0].plot()

    # Display the result image
    cv2.imshow('Detection Results', result_image)
    print("Press any key to close the image window.")
    cv2.waitKey(0)  # Wait for a key press
    cv2.destroyAllWindows()  # Close the image window

    # Save the result image
    cv2.imwrite(result_image_path, result_image)

    # Write detection data to CSV
    write_detection_data_to_csv(results, class_names, width, height, csv_file_path)

def main():
    # Define the common path
    common_path = r'C:\\Users\\sakar\\mt-3d-environments-from-video\\Object Detection\\'

    # File paths
    image_file_name = 'frame_0140.jpg'
    result_file_name = image_file_name.split('.')[0] + '_result.jpg'
    csv_file_name = 'detection_results.csv'

    image_path = os.path.join(common_path, image_file_name)
    result_image_path = os.path.join(common_path, result_file_name)
    csv_file_path = os.path.join(common_path, csv_file_name)

    # Perform detection
    perform_detection(image_path, result_image_path, csv_file_path)

if __name__ == "__main__":
    main()
