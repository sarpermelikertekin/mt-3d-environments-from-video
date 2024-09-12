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
VIDEO_SEGMENTATION_DIR = "Video Segmentation"
SINGLE_DIR = "Single"

def get_v2p_path():
    """Returns the full path to the V2P directory."""
    return os.path.join(COMMON_BASE_PATH, V2P_DIR)

def get_yolo_path():
    """Returns the full path to the YOLO directory."""
    return os.path.join(COMMON_BASE_PATH, YOLO_DIR)

def get_midas_path():
    """Returns the full path to the Midas directory."""
    return os.path.join(COMMON_BASE_PATH, MIDAS_DIR)

def get_test_path():
    """Returns the full path to the Test directory."""
    return os.path.join(COMMON_BASE_PATH, TEST_DIR)

def get_v2p_images_path(subfolder):
    """Returns the full path to the images folder inside V2P."""
    return os.path.join(get_v2p_path(), IMAGES_DIR, subfolder)

def get_yolo_segmentation_single_output_path():
    """Returns the full path to the 'Single' directory inside the Image Segmentation folder in YOLO."""
    return os.path.join(get_yolo_path(), IMAGE_SEGMENTATION_DIR, SINGLE_DIR)

def get_yolo_segmentation_output_path(video_name=None):
    """
    Returns the YOLO segmentation output path.
    If a video_name is provided, return the path for the video.
    Otherwise, return the default 'Single' folder.
    """
    if video_name:
        return os.path.join(get_yolo_path(), VIDEO_SEGMENTATION_DIR, SINGLE_DIR, video_name)
    return get_yolo_segmentation_single_output_path()

def get_midas_single_output_path():
    """Returns the full path to the 'Single' directory in the Midas folder."""
    return os.path.join(get_midas_path(), SINGLE_DIR)

def get_midas_output_path(video_name=None):
    """
    Returns the Midas output path.
    If a video_name is provided, return the path for the video.
    Otherwise, return the default 'Single' folder.
    """
    if video_name:
        return os.path.join(get_midas_path(), video_name)
    return get_midas_single_output_path()

def get_video_input_path(video_name_with_extension):
    """Returns the full path to the input video in the Test folder with the provided filename and extension."""
    return os.path.join(get_test_path(), VIDEOS_DIR, video_name_with_extension)

def get_video_segmentation_output_path(video_name):
    """Returns the full path to the output directory for video segmentation."""
    return os.path.join(get_yolo_path(), VIDEO_SEGMENTATION_DIR, SINGLE_DIR, video_name)

# Adding the missing function to get the Test Images path
def get_test_images_path():
    """Returns the full path to the 'Images' directory inside the 'Test' folder."""
    return os.path.join(get_test_path(), IMAGES_DIR)
