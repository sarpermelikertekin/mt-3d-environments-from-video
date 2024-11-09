import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

# Intrinsic matrix from Unity output
K = np.array([
    [1108.513, 0, 640.0],
    [0, 623.5383, 360.0],
    [0, 0, 1]
])
print("Intrinsic Matrix K:\n", K)

# Base paths
base_scene_meta_path = r'C:\Users\sakar\OneDrive\mt-datas\synthetic_data\4_1_texture_door_window_household\scene_meta'
base_labels_path = r'C:\Users\sakar\OneDrive\mt-datas\synthetic_data\4_1_texture_door_window_household\labels\train'

# Define the filename (without extension) to read specific files with the same name pattern
filename = "1"  # Replace with your file name

# Read camera position and rotation from the scene metadata file (CSV)
scene_meta_path = f"{base_scene_meta_path}\\{filename}.csv"
scene_meta_df = pd.read_csv(scene_meta_path, header=None)
camera_position = scene_meta_df.iloc[0, 1:4].values.astype(float)
rotation_angles = scene_meta_df.iloc[0, 4:7].values.astype(float)

print("Camera Position:", camera_position)
print("Rotation Angles (degrees):", rotation_angles)

# Convert rotation angles to radians and then to a rotation matrix
rotation_radians = np.radians(rotation_angles)
rotation_matrix, _ = cv2.Rodrigues(rotation_radians)

print("Rotation Matrix:\n", rotation_matrix)

# Read 2D corner points from the label file (TXT)
label_path = f"{base_labels_path}\\{filename}.txt"
with open(label_path, 'r') as file:
    lines = file.readlines()

# Process each line/object in the label file
all_world_points_3d = []
for i, line in enumerate(lines):
    print(f"\nProcessing Object {i + 1}")
    
    # Parse each line to get the 2D corners (skip first 5 elements, then take x, y and ignore z for each triplet)
    data = line.strip().split()
    print("Raw Data:", data)
    
    corner_2d_values = list(map(float, data[5:]))  # Start from the 5th element
    corner_2d_points = np.array(corner_2d_values).reshape(-1, 3)[:, :2]  # Reshape to 8 (x, y, z) triplets, take x, y
    
    print("Extracted 2D Corner Points (normalized):\n", corner_2d_points)

    # Convert corner points from normalized to pixel space
    corner_2d_points = corner_2d_points * np.array([K[0, 0], K[1, 1]])
    print("2D Corner Points (pixel space):\n", corner_2d_points)

    # Convert 2D points to homogeneous coordinates
    corner_2d_homogeneous = np.hstack((corner_2d_points, np.ones((corner_2d_points.shape[0], 1))))
    print("2D Homogeneous Coordinates:\n", corner_2d_homogeneous)

    # Compute the pseudo-inverse of the camera matrix for unprojection
    K_inv = np.linalg.inv(K)
    print("Inverse Intrinsic Matrix K_inv:\n", K_inv)

    # Back-project 2D points to 3D rays
    rays_3d = K_inv @ corner_2d_homogeneous.T
    print("3D Rays in Camera Coordinates:\n", rays_3d.T)

    # Define depth (scale factor) for each point, or set it to a fixed value if depth is not known
    depth = 1  # Assuming all points lie on a plane at depth = 1
    corner_3d_points = depth * rays_3d.T
    print("3D Corner Points in Camera Coordinates (scaled by depth):\n", corner_3d_points)

    # Convert the 3D points from camera to world coordinates using the extrinsic matrix
    world_points_3d = (np.linalg.inv(rotation_matrix) @ (corner_3d_points - camera_position).T).T
    print("3D Corner Points in World Coordinates:\n", world_points_3d)
    all_world_points_3d.append(world_points_3d)

    # Plot each object in a separate 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the 3D points for the current object
    ax.scatter(world_points_3d[:, 0], world_points_3d[:, 1], world_points_3d[:, 2], color='blue', s=50)

    # Define edges to form the cube by connecting corresponding points
    edges = [
        (0, 1), (1, 3), (3, 2), (2, 0),  # Bottom rectangle
        (4, 5), (5, 7), (7, 6), (6, 4),  # Top rectangle
        (0, 4), (1, 5), (2, 6), (3, 7)   # Vertical edges
    ]

    # Draw the edges of the cube
    for start, end in edges:
        ax.plot([world_points_3d[start, 0], world_points_3d[end, 0]],
                [world_points_3d[start, 1], world_points_3d[end, 1]],
                [world_points_3d[start, 2], world_points_3d[end, 2]], 'k-')

    # Set labels and plot parameters for each object
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'3D Cube for Object {i + 1}')

plt.show()
