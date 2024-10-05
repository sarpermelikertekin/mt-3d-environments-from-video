import os

# Define the base common path for the 'V2P' project, 'YOLO', 'Midas', and 'Test'
COMMON_BASE_PATH = "C:\\Users\\sakar\\OneDrive\\mt-datas\\"

# Define the project folders for 'V2P', 'YOLO', 'Midas', and 'Test'
V2P_DIR = "v2p"
YOLO_DIR = "yolo"
MIDAS_DIR = "midas"
TEST_DIR = "test"
SYNTHETIC_DATA_DIR = "synthetic_data"
SYNTH_VALIDATION_DATA_DIR = "synth_validation_data"

# Define the subfolder names
IMAGES_SUBFOLDER = "images"
VIDEOS_SUBFOLDER = "videos"
IMAGE_SEGMENTATION_SUBFOLDER = "image_segmentation"
VIDEO_SEGMENTATION_SUBFOLDER = "video_segmentation"
SINGLE_SUBFOLDER = "single"
TEST_SUBFOLDER = "0_test"


def get_v2p_path():
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\v2p"""
    return os.path.join(COMMON_BASE_PATH, V2P_DIR)

def get_yolo_path():
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\yolo"""
    return os.path.join(COMMON_BASE_PATH, YOLO_DIR)

def get_midas_path():
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\midas"""
    return os.path.join(COMMON_BASE_PATH, MIDAS_DIR)

def get_test_path():
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\test"""
    return os.path.join(COMMON_BASE_PATH, TEST_DIR)

def get_test_images_path():
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\test\\images"""
    return os.path.join(get_test_path(), IMAGES_SUBFOLDER)

def get_test_videos_path():
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\test\\videos"""
    return os.path.join(get_test_path(), VIDEOS_SUBFOLDER)

def get_v2p_images_path(subfolder):
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\v2p\\images"""
    return os.path.join(get_v2p_path(), IMAGES_SUBFOLDER, subfolder)

def get_v2p_videos_path(subfolder):
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\v2p\\videos"""
    return os.path.join(get_v2p_path(), VIDEOS_SUBFOLDER, subfolder)

def get_midas_output_path(video_name=None):
    """
    C:\\Users\\sakar\\OneDrive\\mt-datas\\midas
    If a video_name is provided, return the path for the video.
    Otherwise, return the default 'Single' folder.
    """
    if video_name:
        return os.path.join(get_midas_path(), video_name)
    return os.path.join(get_midas_path(), SINGLE_SUBFOLDER)

def get_yolo_segmentation_image_output_path(video_name=None):
    """
    C:\\Users\\sakar\\OneDrive\\mt-datas\\yolo\\image_segmentation
    If a video_name is provided, return the path in the 'image_segmentation' directory for that video.
    Otherwise, return the default 'single' folder for standalone image processing.
    """
    if video_name:
        return os.path.join(get_yolo_path(), IMAGE_SEGMENTATION_SUBFOLDER, video_name)
    return os.path.join(get_yolo_path(), IMAGE_SEGMENTATION_SUBFOLDER, SINGLE_SUBFOLDER)

def get_yolo_segmentation_video_output_path(video_name=None):
    """
    C:\\Users\\sakar\\OneDrive\\mt-datas\\yolo\\video_segmentation
    If a video_name is provided, return the path in the 'video_segmentation' directory for that video.
    Otherwise, return the default 'single' folder for standalone image processing.
    """
    return os.path.join(get_yolo_path(), VIDEO_SEGMENTATION_SUBFOLDER, video_name)

def get_synthetic_data_test_path():
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\synthetic_data\\0_test"""
    return os.path.join(COMMON_BASE_PATH, SYNTHETIC_DATA_DIR, TEST_SUBFOLDER)

def get_synth_validation_test_path():
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\synth_validation_data\\0_test"""
    return os.path.join(COMMON_BASE_PATH, SYNTH_VALIDATION_DATA_DIR, TEST_SUBFOLDER)
