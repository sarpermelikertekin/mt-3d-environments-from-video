# depth_estimation.py

import torch
import cv2
import numpy as np
from PIL import Image
from torchvision.transforms import Compose, Resize, ToTensor

def get_depth_map(image_path):
    # Load the pre-trained model (MiDaS_small)
    model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
    model.eval()

    # Load the image using OpenCV
    img = cv2.imread(image_path)

    # Convert OpenCV image (numpy array) to PIL image for depth estimation
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

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
    depth_map_resized = cv2.resize(depth_map, (img.shape[1], img.shape[0]))

    return depth_map_resized
