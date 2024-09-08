import pandas as pd
import random
import sys
import json

def write_detection_data_to_csv(results, class_names, width, height, csv_file_path):
    # Create a list to store the detection data
    data = []

    # Extract detection details and format them
    for result in results:
        for box in result['boxes']:
            # Extract coordinates and convert to float
            x1, y1, x2, y2 = box['xyxy']
            # Calculate center coordinates and normalize them between 0 and 10
            pos_x = ((x1 + x2) / 2 / width) * 10
            pos_y = ((y1 + y2) / 2 / height) * 10
            pos_z = random.uniform(0, 10)
            
            # Extract class label
            class_id = int(box['cls'])
            object_name = class_names[class_id]
            
            # Generate random rotations and sizes
            rot_x = random.uniform(0, 360)
            rot_y = random.uniform(0, 360)
            rot_z = random.uniform(0, 360)
            size_x = 1
            size_y = 1
            size_z = 1
            
            # Append data to list
            data.append([object_name, class_id, pos_x, pos_y, pos_z, rot_x, rot_y, rot_z, size_x, size_y, size_z])

    # Create a DataFrame
    columns = ['object_name', 'id', 'pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z', 'size_x', 'size_y', 'size_z']
    df = pd.DataFrame(data, columns=columns)

    # Save the DataFrame to a CSV file
    df.to_csv(csv_file_path, index=False)

    print(f"Detection results saved to {csv_file_path}")

if __name__ == "__main__":
    # Parse the JSON passed from subprocess
    results_json = sys.argv[1]
    csv_file_path = sys.argv[2]
    
    # Convert JSON back to a dictionary
    results_data = json.loads(results_json)
    results = results_data['results']
    class_names = results_data['class_names']
    width = results_data['width']
    height = results_data['height']

    # Write the detection data to CSV
    write_detection_data_to_csv(results, class_names, width, height, csv_file_path)
