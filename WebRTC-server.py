import aiohttp
from aiohttp import web
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack

from integrated_hand_movement_detection import MediaPipeVideoStream

pcs = set()

class VideoStream(VideoStreamTrack):
    def __init__(self, source):
        super().__init__()
        self.source = source  # This is your video source integrated with MediaPipe

    async def recv(self):
        frame = await self.source.get_frame()
        return frame

async def index(request):
    with open('index.html', 'r') as f:
        return web.Response(content_type='text/html', text=f.read())

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % id(pc)
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)


    local_video = MediaPipeVideoStream()
    pc.addTrack(local_video)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/offer', offer)

web.run_app(app, port=8080)
