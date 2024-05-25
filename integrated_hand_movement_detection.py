import cv2
import mediapipe as mp
from aiortc import VideoStreamTrack
# from av import VideoFrame
import av

class HandTrackingStream(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.mp_hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = cv2.VideoCapture(0)  # Initialize video capture

    async def recv(self):
        frame = await self.get_frame()
        return frame

    async def get_frame(self):
        success, image = self.cap.read()
        if not success:
            raise Exception("Could not capture video frame")

        # Process with MediaPipe
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        results = self.mp_hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        # Convert the image to VideoFrame to send via WebRTC
        video_frame = av.VideoFrame.from_ndarray(image, format="bgr24")
        video_frame.pts = None
        video_frame.time_base = None

        return video_frame

    def __del__(self):
        self.cap.release()
