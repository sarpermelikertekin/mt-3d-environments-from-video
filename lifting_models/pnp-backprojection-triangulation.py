import numpy as np
import cv2
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Intrinsic matrix (same for both cameras)
K = np.array([
    [1108.513, 0, 640.0],
    [0, 623.5383, 360.0],
    [0, 0, 1]
])
print("Intrinsic Matrix K:\n", K)

# Base paths
base_scene_meta_path = r'C:\Users\sakar\OneDrive\mt-datas\synthetic_data\4_2_texture_door_window_household\scene_meta'
base_labels_path = r'C:\Users\sakar\OneDrive\mt-datas\synthetic_data\4_2_texture_door_window_household\labels\train'

# Define filenames for the two cameras
filename_1 = "34"    # First camera file
filename_2 = "35"  # Second camera file

# Read first camera metadata
scene_meta_path_1 = f"{base_scene_meta_path}\\{filename_1}.csv"
scene_meta_df_1 = pd.read_csv(scene_meta_path_1, header=None)
camera_position_1 = scene_meta_df_1.iloc[0, 1:4].values.astype(float)
rotation_angles_1 = scene_meta_df_1.iloc[0, 4:7].values.astype(float)
camera_position_1[2] = -camera_position_1[2]  # Right-handed adjustment

# Convert rotation angles to rotation matrix for the first camera
rotation_radians_1 = np.radians(rotation_angles_1)
rotation_matrix_1, _ = cv2.Rodrigues(rotation_radians_1)
rotation_matrix_1[:, 2] *= -1

# Read second camera metadata
scene_meta_path_2 = f"{base_scene_meta_path}\\{filename_2}.csv"
scene_meta_df_2 = pd.read_csv(scene_meta_path_2, header=None)
camera_position_2 = scene_meta_df_2.iloc[0, 1:4].values.astype(float)
rotation_angles_2 = scene_meta_df_2.iloc[0, 4:7].values.astype(float)
camera_position_2[2] = -camera_position_2[2]

# Convert rotation angles to rotation matrix for the second camera
rotation_radians_2 = np.radians(rotation_angles_2)
rotation_matrix_2, _ = cv2.Rodrigues(rotation_radians_2)
rotation_matrix_2[:, 2] *= -1

# Read 2D corner points for the first camera
label_path_1 = f"{base_labels_path}\\{filename_1}.txt"
with open(label_path_1, 'r') as file_1:
    lines_1 = file_1.readlines()

all_corner_2d_points_1 = []
for line in lines_1:
    data = line.strip().split()
    corner_2d_values_1 = list(map(float, data[5:]))  # Start from the 5th element
    corner_2d_points_1 = np.array(corner_2d_values_1).reshape(-1, 3)[:, :2]
    corner_2d_points_1 = corner_2d_points_1 * np.array([K[0, 0], K[1, 1]])  # Convert to pixel space
    all_corner_2d_points_1.append(corner_2d_points_1)

# Read 2D corner points for the second camera
label_path_2 = f"{base_labels_path}\\{filename_2}.txt"
with open(label_path_2, 'r') as file_2:
    lines_2 = file_2.readlines()

all_corner_2d_points_2 = []
for line in lines_2:
    data = line.strip().split()
    corner_2d_values_2 = list(map(float, data[5:]))  # Start from the 5th element
    corner_2d_points_2 = np.array(corner_2d_values_2).reshape(-1, 3)[:, :2]
    corner_2d_points_2 = corner_2d_points_2 * np.array([K[0, 0], K[1, 1]])  # Convert to pixel space
    all_corner_2d_points_2.append(corner_2d_points_2)

# Create projection matrices for both cameras
P1 = K @ np.hstack((rotation_matrix_1, -rotation_matrix_1 @ camera_position_1.reshape(-1, 1)))
P2 = K @ np.hstack((rotation_matrix_2, -rotation_matrix_2 @ camera_position_2.reshape(-1, 1)))

# Perform triangulation and visualize 3D coordinates for each object
all_3d_points = []
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

for i, (corner_2d_points_1, corner_2d_points_2) in enumerate(zip(all_corner_2d_points_1, all_corner_2d_points_2)):
    print(f"\nTriangulating Object {i + 1}")

    # Convert 2D points in both views to homogeneous coordinates
    corner_2d_homogeneous_1 = np.hstack((corner_2d_points_1, np.ones((corner_2d_points_1.shape[0], 1))))
    corner_2d_homogeneous_2 = np.hstack((corner_2d_points_2, np.ones((corner_2d_points_2.shape[0], 1))))

    # Perform triangulation using the projection matrices
    points_4d_homogeneous = cv2.triangulatePoints(P1, P2, corner_2d_homogeneous_1.T[:2], corner_2d_homogeneous_2.T[:2])
    points_3d = (points_4d_homogeneous[:3] / points_4d_homogeneous[3]).T  # Normalize to get 3D coordinates

    all_3d_points.append(points_3d)
    print(f"3D Corner Points for Object {i + 1}:\n", points_3d)

    # Plot the 3D points for the current object
    ax.scatter(points_3d[:, 0], points_3d[:, 1], points_3d[:, 2], label=f'Object {i + 1}')

    # Draw lines to form the cube shape by connecting corresponding points
    edges = [
        (0, 1), (1, 3), (3, 2), (2, 0),  # Bottom rectangle
        (4, 5), (5, 7), (7, 6), (6, 4),  # Top rectangle
        (0, 4), (1, 5), (2, 6), (3, 7)   # Vertical edges
    ]
    for start, end in edges:
        ax.plot([points_3d[start, 0], points_3d[end, 0]],
                [points_3d[start, 1], points_3d[end, 1]],
                [points_3d[start, 2], points_3d[end, 2]], 'k-')

# Set labels and plot parameters
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Corner Points for All Objects')
ax.legend()
plt.show()

# Output all 3D coordinates for each object's corners
for i, points_3d in enumerate(all_3d_points):
    print(f"\nObject {i + 1} 3D Coordinates:")
    for j, point in enumerate(points_3d):
        print(f"Corner {j + 1}: {point}")
