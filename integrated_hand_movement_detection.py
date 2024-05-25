# Integrate MediaPipe with the VideoStream

import cv2
import mediapipe as mp
from aiortc import VideoStreamTrack
from av import VideoFrame

class MediaPipeVideoStream(VideoStreamTrack):
    def __init__(self):
        super().__init__()  # Initialize the base class
        self.cap = cv2.VideoCapture(0)  # Open the default camera
        self.mp_hands = mp.solutions.hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    async def recv(self):
        frame = await self.get_frame()
        return frame

    async def get_frame(self):
        success, image = self.cap.read()
        if not success:
            return None

        # Process with MediaPipe
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.mp_hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Draw the hand annotations on the image
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    image, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

        # Convert the image to VideoFrame to send via WebRTC
        video_frame = VideoFrame.from_ndarray(image, format="bgr24")
        video_frame.pts = None
        video_frame.time_base = None

        return video_frame

    def __del__(self):
        self.cap.release()
