import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import time

# Define the Pose Estimation Model
class SYENet(nn.Module):
    def __init__(self, input_size, output_size):
        super(SYENet, self).__init__()
        self.fc1 = nn.Linear(input_size, 1024)
        self.bn1 = nn.BatchNorm1d(1024)
        self.dropout1 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(1024, 512)
        self.bn2 = nn.BatchNorm1d(512)
        self.dropout2 = nn.Dropout(0.5)
        self.fc3 = nn.Linear(512, output_size)

    def forward(self, x):
        x = F.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)
        x = F.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)
        x = self.fc3(x)
        return x

# Function to load the trained model, use it for inference, and write results to CSV
def load_model_and_predict_3d(data_2d_path, output_folder, file_name, input_size=20, output_size=30):
    """
    Load the model for 2D-to-3D lifting and write the results to a CSV.
    Process each row independently to determine the correct model for each object.
    """
    try:
        start_time = time.time()  # Start overall runtime measurement

        # Load the 2D data
        load_start = time.time()
        df_2d = pd.read_csv(data_2d_path, header=None)
        load_end = time.time()
        print(f"Data loading time: {load_end - load_start:.4f} seconds")

        # Prepare the output DataFrame
        all_predictions = []

        # Process each row independently
        for _, row in df_2d.iterrows():
            row_start_time = time.time()  # Start time for this row

            object_id = int(row.iloc[0])  # Extract the object ID from the first column
            model_path = f"C:/Users/sakar/mt-3d-environments-from-video/lifting_models/sye{object_id}.pth"
            if not os.path.exists(model_path):
                print(f"Model file not found for object ID {object_id}: {model_path}")
                continue

            print(f"Using model for object ID {object_id}: {model_path}")

            # Prepare the data for inference: Drop the ID column
            data_2d_tensor = torch.tensor(row.iloc[1:].values.reshape(1, -1), dtype=torch.float32)

            # Validate input dimensions
            if data_2d_tensor.shape[1] != input_size:
                print(f"Error: Model expects input size {input_size}, but got {data_2d_tensor.shape[1]} for object ID {object_id}")
                continue

            # Instantiate the model architecture and load weights
            model = SYENet(input_size=input_size, output_size=output_size)
            model_load_start = time.time()
            model.load_state_dict(torch.load(model_path))
            model.eval()  # Set the model to evaluation mode
            model_load_end = time.time()
            print(f"Model loading time for object ID {object_id}: {model_load_end - model_load_start:.4f} seconds")

            # Run the model to predict 3D points
            inference_start = time.time()
            with torch.no_grad():
                try:
                    predictions_3d = model(data_2d_tensor)
                except Exception as e:
                    print(f"Error during model inference for object ID {object_id}: {e}")
                    continue
            inference_end = time.time()
            print(f"Inference time for object ID {object_id}: {inference_end - inference_start:.4f} seconds")

            # Convert predictions to a list
            predictions = predictions_3d.numpy().flatten().tolist()

            # Add the object ID back to the predictions
            all_predictions.append([object_id] + predictions)

            row_end_time = time.time()
            print(f"Total time for row (object ID {object_id}): {row_end_time - row_start_time:.4f} seconds")

    except Exception as e:
        print(f"Error processing 2D data: {e}")
        return None

    # Convert all predictions to a DataFrame
    predictions_df = pd.DataFrame(all_predictions).round(4)

    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Define the output CSV file path with _sye suffix
    output_csv_path = os.path.join(output_folder, f"{file_name}_sye_result.csv")

    # Write the predictions DataFrame to a CSV file
    save_start = time.time()
    predictions_df.to_csv(output_csv_path, index=False, header=False)
    save_end = time.time()
    print(f"CSV saving time: {save_end - save_start:.4f} seconds")

    total_time = time.time() - start_time
    print(f"Total runtime: {total_time:.4f} seconds")

    print(f"3D predictions have been saved to {output_csv_path}")
    return predictions_df

def main():
    # Define paths and parameters
    base_path = r""
    dataset_name = "12_yoro_dataset"
    subset = "test"
    file_name = "10007"
    data_2d_sample_path = os.path.join(base_path, f"{dataset_name}_{subset}_{file_name}.csv")
#    data_2d_sample_path = os.path.join(base_path, f"{dataset_name}_{subset}_{file_name}_yolo_result.csv")


    # Define the output folder
    output_folder = r""

    # Run inference and save results to CSV
    predictions_3d = load_model_and_predict_3d(
        data_2d_sample_path, output_folder, file_name
    )
    if predictions_3d is not None:
        print("3D Predictions:", predictions_3d)

if __name__ == "__main__":
    main()
