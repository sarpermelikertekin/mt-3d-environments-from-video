import os

# Define the base common path without 'V2P'
COMMON_BASE_PATH = "C:\\Users\\sakar\\OneDrive\\mt-datas\\"

# Define the project folder 'V2P'
PROJECT_DIR = "V2P"

# Define the subfolder names
VIDEOS_DIR = "Videos"
IMAGES_DIR = "Images"

def get_project_path():
    """Returns the path to the project directory."""
    return os.path.join(COMMON_BASE_PATH, PROJECT_DIR)

def get_video_path(video_name):
    """Returns the full path for a given video name."""
    return os.path.join(get_project_path(), VIDEOS_DIR, video_name)

def get_images_output_dir(pics_folder):
    """Returns the full path for the images output directory."""
    return os.path.join(get_project_path(), IMAGES_DIR, pics_folder)
