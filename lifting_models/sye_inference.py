import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd

# Define the Pose Estimation Model
class PoseEstimationNet(nn.Module):
    def __init__(self, input_size, output_size):
        super(PoseEstimationNet, self).__init__()
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
    # Load the first column of data_2d_path to determine the model variant
    try:
        df_2d = pd.read_csv(data_2d_path, header=None)
        object_id = int(df_2d.iloc[0, 0])  # Get the first value in the first column
        model_path = f"C:/Users/sakar/mt-3d-environments-from-video/lifting_models/sye{object_id}.pth"
        
        # Ensure the model file exists
        if not os.path.exists(model_path):
            print(f"Model file not found: {model_path}")
            return None

        print(f"Using model: {model_path}")
    except Exception as e:
        print(f"Error reading data or determining model path: {e}")
        return None

    # Instantiate the model architecture and load weights
    model = PoseEstimationNet(input_size=input_size, output_size=output_size)
    model.load_state_dict(torch.load(model_path))
    model.eval()  # Set the model to evaluation mode

    # Prepare data for inference by dropping the ID column
    data_2d_tensor = torch.tensor(df_2d.iloc[:, 1:].values, dtype=torch.float32)

    # Run the model to predict 3D points
    with torch.no_grad():
        predictions_3d = model(data_2d_tensor)

    # Convert predictions to a DataFrame with 2 decimal precision
    predictions_df = pd.DataFrame(predictions_3d.numpy()).round(2)
    
    # Add the ID column to the predictions DataFrame
    predictions_df.insert(0, 'ID', df_2d.iloc[:, 0])
    
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Define the output CSV file path with _sye suffix
    output_csv_path = os.path.join(output_folder, f"{file_name}_sye_result.csv")
    
    # Write the predictions DataFrame to a CSV file
    predictions_df.to_csv(output_csv_path, index=False, header=False)
    
    print(f"3D predictions have been saved to {output_csv_path}")
    return predictions_3d

# Main function (for direct execution)
def main():
    # Define paths and parameters
    base_path = r"C:\Users\sakar\OneDrive\mt-datas\yolo\pose_estimation"
    dataset_name = "1_realistic_chair"
    subset = "train"
    file_name = "2"
    data_2d_sample_path = os.path.join(base_path, f"{dataset_name}_{subset}_{file_name}_yolo_result.csv")

    # Define the output folder
    output_folder = r"C:\Users\sakar\OneDrive\mt-datas\yolo\pose_estimation"

    # Run inference and save results to CSV
    predictions_3d = load_model_and_predict_3d(
        data_2d_sample_path, output_folder, dataset_name, subset, file_name
    )
    if predictions_3d is not None:
        print("3D Predictions:", predictions_3d)

if __name__ == "__main__":
    main()
