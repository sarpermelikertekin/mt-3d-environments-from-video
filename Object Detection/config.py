import os

# Define the base common path for the 'V2P' project, 'YOLO', 'Midas', and 'Test'
COMMON_BASE_PATH = "C:\\Users\\sakar\\OneDrive\\mt-datas\\"

# Define the project folders for 'V2P', 'YOLO', 'Midas', and 'Test'
V2P_DIR = "v2p"
YOLO_DIR = "yolo"
MIDAS_DIR = "midas"
TEST_DIR = "test"

# Define the subfolder names
IMAGES_DIR = "images"
VIDEOS_DIR = "videos"
IMAGE_SEGMENTATION_DIR = "image_segmentation"
VIDEO_SEGMENTATION_DIR = "video_segmentation"
SINGLE_DIR = "single"

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
    return os.path.join(get_test_path(), IMAGES_DIR)

def get_test_videos_path():
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\test\\videos"""
    return os.path.join(get_test_path(), VIDEOS_DIR)

def get_v2p_images_path(subfolder):
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\v2p\\images"""
    return os.path.join(get_v2p_path(), IMAGES_DIR, subfolder)

def get_v2p_videos_path(subfolder):
    """C:\\Users\\sakar\\OneDrive\\mt-datas\\v2p\\videos"""
    return os.path.join(get_v2p_path(), VIDEOS_DIR, subfolder)

def get_midas_output_path(video_name=None):
    """
    C:\\Users\\sakar\\OneDrive\\mt-datas\\midas
    If a video_name is provided, return the path for the video.
    Otherwise, return the default 'Single' folder.
    """
    if video_name:
        return os.path.join(get_midas_path(), video_name)
    return os.path.join(get_midas_path(), SINGLE_DIR)

def get_yolo_segmentation_image_output_path(video_name=None):
    """
    C:\\Users\\sakar\\OneDrive\\mt-datas\\yolo\\image_segmentation
    If a video_name is provided, return the path in the 'image_segmentation' directory for that video.
    Otherwise, return the default 'single' folder for standalone image processing.
    """
    if video_name:
        return os.path.join(get_yolo_path(), IMAGE_SEGMENTATION_DIR, video_name)
    return os.path.join(get_yolo_path(), IMAGE_SEGMENTATION_DIR, SINGLE_DIR)

def get_yolo_segmentation_video_output_path(video_name=None):
    """
    C:\\Users\\sakar\\OneDrive\\mt-datas\\yolo\\video_segmentation
    If a video_name is provided, return the path in the 'video_segmentation' directory for that video.
    Otherwise, return the default 'single' folder for standalone image processing.
    """
    return os.path.join(get_yolo_path(), VIDEO_SEGMENTATION_DIR, video_name)