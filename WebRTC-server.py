import asyncio
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from integrated_hand_movement_detection import HandTrackingStream

pcs = set()


async def index(request):
    with open('index.html', 'r') as f:
        return web.Response(content_type='text/html', text=f.read())


async def save_hand_data_periodically(hand_tracking_stream):
    while True:
        await asyncio.sleep(10)  # Save data every 10 seconds
        hand_tracking_stream.save_hand_data()


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

    local_video = HandTrackingStream()
    pc.addTrack(local_video)
    asyncio.ensure_future(save_hand_data_periodically(local_video))  # Start periodic saving

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
