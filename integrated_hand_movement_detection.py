import asyncio
import os
import cv2
import mediapipe as mp
from aiortc import VideoStreamTrack
import av
import pandas as pd
import logging

# Setup logging configuration
logging.basicConfig(level=logging.INFO)

class HandTrackingStream(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.mp_hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.hand_data = []

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        # Initialize camera capture
        cap = cv2.VideoCapture(0)
        success, image = cap.read()
        cap.release()

        if not success:
            logging.error("Failed to capture video frame")
            return None

        logging.info("Video frame captured successfully")

        # Process with MediaPipe
        image = cv2.cvtColor(cv2.flip(image, 0), cv2.COLOR_BGR2RGB)
        results = self.mp_hands.process(image)
        logging.info(f"MediaPipe processing complete. Multi hand landmarks detected: {bool(results.multi_hand_landmarks)}")

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                # Extract and store landmark data for movement analysis
                landmarks = [landmark for lm in hand_landmarks.landmark for landmark in (lm.x, lm.y, lm.z)]
                self.hand_data.append(landmarks)
            logging.info(f"Processed frame with {len(results.multi_hand_landmarks)} hands")
        else:
            logging.info("No hands detected in the frame")

        # Convert the processed image to a video frame
        video_frame = av.VideoFrame.from_ndarray(image, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        logging.info("VideoFrame created and returned")
        return video_frame

    def save_hand_data(self):
        if len(self.hand_data) > 0:
            df = pd.DataFrame(self.hand_data)
            df.to_csv('hand_movements.csv', index=False, mode='a', header=not os.path.exists('hand_movements.csv'))
            logging.info(f"Saved {len(self.hand_data)} hand movement data points to CSV")
            self.hand_data = []  # Clear hand data after saving
        else:
            logging.info("No hand movement data to save")

    def __del__(self):
        self.save_hand_data()  # Ensure hand data is saved before the object is destroyed
        self.mp_hands.close()