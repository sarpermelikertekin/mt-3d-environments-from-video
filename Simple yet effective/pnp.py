import cv2
import numpy as np
import os
import glob
import pandas as pd

# Define paths for 2D and 3D data
path_2d = r'C:\Users\sakar\OneDrive\mt-datas\synthetic_data\4_texture_door_window_household\2d_data'
path_3d = r'C:\Users\sakar\OneDrive\mt-datas\synthetic_data\4_texture_door_window_household\3d_data'
image_path = r'C:\Users\sakar\OneDrive\mt-datas\synthetic_data\4_texture_door_window_household\images\train'  # Adjust this to the correct image folder

# Get the first 10 CSV files from each directory
csv_files_2d = sorted(glob.glob(os.path.join(path_2d, "*.csv")))[:10]
csv_files_3d = sorted(glob.glob(os.path.join(path_3d, "*.csv")))[:10]

# Assume that images are named correspondingly to the CSV files (e.g., same name or index)
image_files = sorted(glob.glob(os.path.join(image_path, "*.png")))  # or "*.jpg", depending on your image format
if len(image_files) == 0:
    raise FileNotFoundError("No images found in the specified directory.")

# Read the first image to get image size
image = cv2.imread(image_files[0])
if image is None:
    raise FileNotFoundError(f"Image {image_files[0]} could not be loaded.")
image_size = (image.shape[1], image.shape[0])  # (width, height)
print("Image size (width, height):", image_size)

# Initialize the intrinsic matrix with an estimated focal length and principal point
focal_length = image_size[0]  # Rough estimate using image width
camera_matrix = np.array([[focal_length, 0, image_size[0] / 2],
                          [0, focal_length, image_size[1] / 2],
                          [0, 0, 1]], dtype=np.float32)

# Prepare lists to store all points from each object in each image
all_object_points = []
all_image_points = []

# Iterate through each pair of 2D and 3D CSV files
for file_2d, file_3d in zip(csv_files_2d, csv_files_3d):
    # Load each CSV file
    data_2d_df = pd.read_csv(file_2d)
    data_3d_df = pd.read_csv(file_3d)
    
    # Process each row as a separate object
    for row_2d, row_3d in zip(data_2d_df.itertuples(index=False), data_3d_df.itertuples(index=False)):
        # Convert the row to a list and ignore the first 5 elements for 2D, use the last 16 as 8 (x, y) pairs
        data_2d = list(row_2d)[5:]  # Skip the first 5 elements
        if len(data_2d) != 16:
            print(f"Skipping row in {file_2d}: Expected 16 values for 2D points, but got {len(data_2d)}.")
            continue
        image_points = np.array(data_2d).reshape(-1, 2)  # Reshape into (x, y) pairs

        # Convert the row to a list and ignore the first 7 elements for 3D, use the last 24 as 8 (X, Y, Z) triples
        data_3d = list(row_3d)[7:]  # Skip the first 7 elements
        if len(data_3d) != 24:
            print(f"Skipping row in {file_3d}: Expected 24 values for 3D points, but got {len(data_3d)}.")
            continue
        object_points = np.array(data_3d).reshape(-1, 3)  # Reshape into (X, Y, Z) triples

        # Append points for this object
        all_image_points.append(image_points.astype(np.float32))
        all_object_points.append(object_points.astype(np.float32))

# Perform camera calibration if enough data is available
if len(all_object_points) > 0 and len(all_image_points) > 0:
    # Perform calibration with the specified initial intrinsic matrix
    ret, K, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        all_object_points, all_image_points, image_size, camera_matrix, None,
        flags=cv2.CALIB_USE_INTRINSIC_GUESS
    )

    # Output results
    print("Intrinsic Matrix K:\n", K)
    print("Distortion Coefficients:\n", dist_coeffs)

    # Optionally print rotation and translation vectors for each view
    for i, (rvec, tvec) in enumerate(zip(rvecs, tvecs)):
        print(f"View {i+1}:")
        print("Rotation Vector:\n", rvec)
        print("Translation Vector:\n", tvec)
else:
    print("Insufficient valid data for calibration.")
