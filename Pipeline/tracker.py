import os
import pandas as pd
import numpy as np

def track_and_assign_ids(input_csv_folder, output_csv_folder, max_distance_threshold=0.5):
    """
    Track objects across frames and assign unique IDs.
    """
    # Ensure the output folder exists
    os.makedirs(output_csv_folder, exist_ok=True)
    
    # Initialize a dictionary to hold object tracking data
    previous_objects = {}
    current_id = 0  # Start the unique ID counter
    
    # Process CSVs in sorted order by frame number
    csv_files = sorted([f for f in os.listdir(input_csv_folder) if f.endswith('_yolo_result.csv')])
    for csv_file in csv_files:
        frame_path = os.path.join(input_csv_folder, csv_file)
        output_path = os.path.join(output_csv_folder, csv_file.replace('_yolo_result.csv', '_yolo_result_tracked.csv'))
        
        # Load the current frame's data
        data = pd.read_csv(frame_path, header=None)
        if data.empty:
            print(f"[WARNING] Empty CSV: {csv_file}")
            continue

        # Extract center positions of bounding boxes
        centers = data.iloc[:, [1, 2]].values  # BB center x, y
        ids = []
        
        for center in centers:
            matched_id = None
            # Compare with previous objects
            for obj_id, prev_center in previous_objects.items():
                distance = np.linalg.norm(np.array(center) - np.array(prev_center))
                if distance < max_distance_threshold:
                    matched_id = obj_id
                    break

            if matched_id is not None:
                ids.append(matched_id)
            else:
                ids.append(current_id)
                previous_objects[current_id] = center
                current_id += 1
        
        # Update previous_objects with the current frame's objects
        previous_objects = {id_: center for id_, center in zip(ids, centers)}
        
        # Add IDs to the data
        data['ID'] = ids
        
        # Save the updated CSV
        data.to_csv(output_path, index=False, header=False)
        print(f"[INFO] Processed and saved: {output_path}")
