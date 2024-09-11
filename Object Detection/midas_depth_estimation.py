import os
import torch
import cv2
import numpy as np
from PIL import Image
from torchvision.transforms import Compose, Resize, ToTensor
from config import get_test_images_path, get_midas_output_path  # Use config.py for paths

# Function to perform depth estimation
def get_depth_map(image):
    # Load the pre-trained model (MiDaS_small)
    model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
    model.eval()

    # Convert OpenCV image (numpy array) to PIL image for depth estimation
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Preprocess the image: Convert the image to the appropriate format for the model
    depth_transform = Compose([
        Resize((384, 384)),  # Resize image to 384x384 pixels
        ToTensor()  # Convert the image to tensor format for PyTorch
    ])

    # Apply the transformation to the PIL image
    img_transformed = depth_transform(img_pil).unsqueeze(0)  # Add a batch dimension

    # Run depth estimation
    with torch.no_grad():  # Disable gradient calculation for inference
        depth_map = model(img_transformed)

    # Post-process the depth map
    depth_map = depth_map.squeeze().cpu().numpy()  # Convert the output to numpy
    depth_map = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)  # Normalize depth values
    depth_map = np.uint8(depth_map)  # Convert to 8-bit format

    # Resize the depth map to match the original image size
    depth_map_resized = cv2.resize(depth_map, (image.shape[1], image.shape[0]))

    return depth_map_resized

def main(image_name):
    # Load the image
    image_directory = get_test_images_path()  # Dynamically get image path from config
    image_path = os.path.join(image_directory, image_name)
    image = cv2.imread(image_path)

    # Perform depth estimation
    depth_map_resized = get_depth_map(image)

    # Get output directory from config
    output_dir = get_midas_output_path()
    
    # Ensure the /Single directory exists in the output folder
    os.makedirs(output_dir, exist_ok=True)

    # Save the result with the name `originalname_midas_depth.png`
    output_image_name = f"{os.path.splitext(image_name)[0]}_midas_depth.png"
    output_path = os.path.join(output_dir, output_image_name)

    cv2.imwrite(output_path, depth_map_resized)
    
    # Print the saved path
    print(f"Depth estimation result saved to: {output_path}")

if __name__ == "__main__":
    # Only the image name is hardcoded here
    image_name = "office.jpg"
    main(image_name)
