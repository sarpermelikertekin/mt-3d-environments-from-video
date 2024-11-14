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
def load_model_and_predict_3d(data_2d_path, model_path, output_folder, input_size=20, output_size=30):
    # Instantiate the model architecture and load weights
    model = PoseEstimationNet(input_size=input_size, output_size=output_size)
    model.load_state_dict(torch.load(model_path))
    model.eval()  # Set the model to evaluation mode

    # Load the 2D data for inference
    try:
        df_2d = pd.read_csv(data_2d_path, header=None)
        df_2d = df_2d.iloc[:, 1:]  # Drop the ID column
        data_2d_tensor = torch.tensor(df_2d.values, dtype=torch.float32)
    except Exception as e:
        print(f"Error loading or processing 2D data: {e}")
        return None

    # Run the model to predict 3D points
    with torch.no_grad():
        predictions_3d = model(data_2d_tensor)

    # Convert predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions_3d.numpy())
    
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Define the output CSV file path
    output_csv_path = os.path.join(output_folder, "predictions_3d.csv")
    
    # Write the predictions DataFrame to a CSV file
    predictions_df.to_csv(output_csv_path, index=False, header=False)
    
    print(f"3D predictions have been saved to {output_csv_path}")
    return predictions_3d

# Main function (for direct execution)
def main():
    # Define paths
    base_path = r"C:\Users\sakar\OneDrive\mt-datas\yolo\pose_estimation"
    filename = "1_realistic_chair_train_2_yolo_result.csv"
    data_2d_sample_path = os.path.join(base_path, filename)

    # Define the model path and output folder
    model_path = r"C:\Users\sakar\mt-3d-environments-from-video\lifting_models\sye0.pth"
    output_folder = r"C:\Users\sakar\OneDrive\mt-datas\yolo\pose_estimation"
    
    # Run inference and save results to CSV
    predictions_3d = load_model_and_predict_3d(data_2d_sample_path, model_path, output_folder)
    if predictions_3d is not None:
        print("3D Predictions:", predictions_3d)

if __name__ == "__main__":
    main()
