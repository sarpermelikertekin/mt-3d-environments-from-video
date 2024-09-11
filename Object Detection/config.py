import os

# Define the base common path for the 'V2P' project, 'YOLO', 'Midas', and 'Test'
COMMON_BASE_PATH = "C:\\Users\\sakar\\OneDrive\\mt-datas\\"

# Define the project folders for 'V2P', 'YOLO', 'Midas', and 'Test'
V2P_DIR = "V2P"
YOLO_DIR = "YOLO"
MIDAS_DIR = "Midas"
TEST_DIR = "Test"

# Define the subfolder names
IMAGES_DIR = "Images"
VIDEOS_DIR = "Videos"
IMAGE_SEGMENTATION_DIR = "Image Segmentation"

def get_v2p_path():
    """Returns the full path to the V2P directory."""
    return os.path.join(COMMON_BASE_PATH, V2P_DIR)

def get_yolo_path():
    """Returns the full path to the YOLO directory."""
    return os.path.join(COMMON_BASE_PATH, YOLO_DIR)

def get_midas_path():
    """Returns the full path to the Midas directory."""
    return os.path.join(COMMON_BASE_PATH, MIDAS_DIR)

def get_test_images_path():
    """Returns the full path to the Test Images directory."""
    return os.path.join(COMMON_BASE_PATH, TEST_DIR, IMAGES_DIR)

def get_v2p_images_path(subfolder):
    """Returns the full path to the images folder inside V2P."""
    return os.path.join(get_v2p_path(), IMAGES_DIR, subfolder)

def get_yolo_segmentation_output_path():
    """Returns the full path to the 'Single' directory inside the Image Segmentation folder in YOLO."""
    return os.path.join(get_yolo_path(), IMAGE_SEGMENTATION_DIR, "Single")

def get_midas_output_path():
    """Returns the full path to the Midas output folder."""
    return os.path.join(get_midas_path(), "Single")
