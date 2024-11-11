import cv2
import mediapipe as mp

# Initialize MediaPipe Objectron
mp_objectron = mp.solutions.objectron
mp_drawing = mp.solutions.drawing_utils

# Load the video
video_path = "C:\\Users\\sakar\\OneDrive\\mt-datas\\test\\videos\\example.mp4"  # Replace with your video file path
cap = cv2.VideoCapture(video_path)

# Initialize Objectron (for cup, you can change it to shoe, chair, book)
with mp_objectron.Objectron(static_image_mode=False,
                            max_num_objects=5,  # Max number of objects to detect
                            min_detection_confidence=0.5,
                            min_tracking_confidence=0.5,
                            model_name='Cup') as objectron:

    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty frame.")
            break

        # Convert the image to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and detect objects
        results = objectron.process(image_rgb)

        # Increment frame count
        frame_count += 1
        print(f"\nProcessing Frame: {frame_count}")

        # If objects are detected, draw them on the frame and print details
        if results.detected_objects:
            print(f"Number of objects detected: {len(results.detected_objects)}")
            
            for i, detected_object in enumerate(results.detected_objects):
                # Draw the 2D landmarks and 3D bounding box
                mp_drawing.draw_landmarks(frame, 
                                          detected_object.landmarks_2d, 
                                          mp_objectron.BOX_CONNECTIONS)
                mp_drawing.draw_axis(frame, detected_object.rotation,
                                     detected_object.translation)

                # Print detailed information about the detected object
                print(f"Object {i+1}:")
                print(f"  - 2D Landmarks: {detected_object.landmarks_2d.landmark}")
                print(f"  - 3D Translation (Object Position): {detected_object.translation}")
                print(f"  - 3D Rotation (Object Orientation): {detected_object.rotation}")
        else:
            print("No objects detected.")

        # Show the result frame
        cv2.imshow('MediaPipe Objectron', frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Release video capture and close windows
cap.release()
cv2.destroyAllWindows()
