import os

# Define the base common path for the 'V2P' project and 'YOLO'
COMMON_BASE_PATH = "C:\\Users\\sakar\\OneDrive\\mt-datas\\"

# Define the project folder for 'V2P' and 'YOLO'
V2P_DIR = "V2P"
YOLO_DIR = "YOLO"

# Define the subfolder names
IMAGES_DIR = "Images"
VIDEOS_DIR = "Videos"
IMAGE_DETECTION_DIR = "Image Segmentation"

def get_v2p_path():
    """Returns the full path to the V2P directory."""
    return os.path.join(COMMON_BASE_PATH, V2P_DIR)

def get_yolo_path():
    """Returns the full path to the YOLO directory."""
    return os.path.join(COMMON_BASE_PATH, YOLO_DIR)

def get_v2p_images_path(subfolder):
    """Returns the full path to the images folder inside V2P."""
    return os.path.join(get_v2p_path(), IMAGES_DIR, subfolder)

def get_yolo_detection_output_path():
    """Returns the full path to the image detection folder inside YOLO."""
    return os.path.join(get_yolo_path(), IMAGE_DETECTION_DIR)
