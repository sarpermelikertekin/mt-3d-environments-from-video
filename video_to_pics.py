import cv2
import os

def sample_frames_from_video(video_path, output_dir, interval=30):
    """
    Samples frames from a video at a specified interval and saves them as images.

    Args:
    - video_path (str): Path to the input video file.
    - output_dir (str): Directory to save the sampled images.
    - interval (int): The interval at which frames are sampled. Default is every 30 frames.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    frame_count = 0
    saved_image_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Save the frame if it is at the specified interval
        if frame_count % interval == 0:
            image_path = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
            cv2.imwrite(image_path, frame)
            saved_image_count += 1

        frame_count += 1
    
    cap.release()
    print(f"Saved {saved_image_count} images to {output_dir}")

if __name__ == "__main__":
    video_path = "example.mp4"  # Replace with the path to your video file
    output_dir = "pics"          # Replace with your desired output directory
    interval = 5                          # Adjust the interval as needed

    sample_frames_from_video(video_path, output_dir, interval)
