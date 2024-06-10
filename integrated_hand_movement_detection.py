import asyncio
import cv2
import mediapipe as mp
from aiortc import VideoStreamTrack
import av
import logging

# Setup logging configuration
logging.basicConfig(level=logging.INFO)

class HandTrackingStream(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.mp_hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=4,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = cv2.VideoCapture(0)

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        success, image = self.cap.read()

        if not success:
            logging.error("Failed to capture video frame")
            return None

        # Process with MediaPipe
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.mp_hands.process(image)
        logging.info(f"MediaPipe processing complete. Multi hand landmarks detected: {bool(results.multi_hand_landmarks)}")

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    image, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
            logging.info(f"Processed frame with {len(results.multi_hand_landmarks)} hands")
        else:
            logging.info("No hands detected in the frame")

        # Convert the processed image to a video frame
        video_frame = av.VideoFrame.from_ndarray(image, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame

    async def stop(self):
        self.cap.release()