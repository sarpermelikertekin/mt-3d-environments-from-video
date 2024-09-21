import cv2
import mediapipe as mp

# Initialize MediaPipe Objectron
mp_objectron = mp.solutions.objectron
mp_drawing = mp.solutions.drawing_utils

# Load the video
video_path = "C:\\Users\\sakar\\OneDrive\\mt-datas\\test\\videos\\rh_one_chair.mp4"  # Replace with your video file path
cap = cv2.VideoCapture(video_path)

# Initialize Objectron (for cup, you can change it to shoe, chair, book)
with mp_objectron.Objectron(static_image_mode=False,
                            max_num_objects=5,  # Max number of objects to detect
                            min_detection_confidence=0.5,
                            min_tracking_confidence=0.5,
                            model_name='Cup') as objectron:

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty frame.")
            break

        # Convert the image to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and detect objects
        results = objectron.process(image_rgb)

        # If objects are detected, draw them on the frame
        if results.detected_objects:
            for detected_object in results.detected_objects:
                mp_drawing.draw_landmarks(frame, 
                                          detected_object.landmarks_2d, 
                                          mp_objectron.BOX_CONNECTIONS)
                mp_drawing.draw_axis(frame, detected_object.rotation,
                                     detected_object.translation)

        # Show the result frame
        cv2.imshow('MediaPipe Objectron', frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Release video capture and close windows
cap.release()
cv2.destroyAllWindows()
