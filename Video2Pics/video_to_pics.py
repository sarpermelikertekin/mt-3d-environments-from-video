import cv2
import os

def sample_frames_from_video(video_path, output_dir, fps=1):
    """
    Samples frames from a video at a specified rate (frames per second) and saves them as images.

    Args:
    - video_path (str): Path to the input video file.
    - output_dir (str): Directory to save the sampled images.
    - fps (int): The number of frames to capture per second. Default is 1 fps.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Check if the video file exists
    if not os.path.isfile(video_path):
        print(f"Error: Video file {video_path} does not exist.")
        return
    
    # Print the video path to ensure it's correct
    print(f"Processing video: {video_path}")

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    video_frame_rate = cap.get(cv2.CAP_PROP_FPS)  # Get the video's frame rate
    interval = int(video_frame_rate / fps)  # Calculate the interval between frames to capture

    frame_count = 0
    saved_image_count = 0
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Save the frame if it is at the specified interval
        if frame_count % interval == 0:
            image_path = os.path.join(output_dir, f"{video_name}_frame_{frame_count:04d}.jpg")
            cv2.imwrite(image_path, frame)
            saved_image_count += 1

        frame_count += 1
    
    cap.release()
    print(f"Saved {saved_image_count} images from {video_name} to {output_dir}")

if __name__ == "__main__":
    # Define the common path
    common_path = "C:\\Users\\sakar\\mt-3d-environments-from-video\\Video2Pics\\"
    video_file_names = ["example1.mp4", "example2.mp4", "example3.mp4"]  # Add your video file names here
    
    # Define the output directory for all images
    images_output_dir = os.path.join(common_path, "all_videos_pics")
    
    fps = 1  # Number of frames per second to capture

    # Process each video
    for video_file_name in video_file_names:
        video_path = os.path.join(common_path, video_file_name)
        sample_frames_from_video(video_path, images_output_dir, fps)