import cv2
import mediapipe as mp
import pandas as pd

# Initialize MediaPipe Hand solution
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)

# Initialize video capture
cap = cv2.VideoCapture(0)  # Use 0 for webcam

hand_data = []

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    # Flip and convert the image to RGB
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    
    # Process the image and draw hand landmarks
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            hand_data.append(landmarks)
    # Display the image
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27: # exit with esc key
        break

df = pd.DataFrame(hand_data)
df.to_csv('hand_movements.csv', index=False)
# Release resources
cap.release()
cv2.destroyAllWindows()
