from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import logging

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return "Signaling Server for Video Conference"

@socketio.on('connect')
def test_connect():
    logging.info('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    logging.info('Client disconnected')

@socketio.on('sdp')
def handle_sdp(data):
    logging.info(f'Received sdp: {data}')
    emit('sdp', data, broadcast=True, include_self=False)

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    logging.info(f'Received ICE candidate: {data}')
    emit('ice_candidate', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    try:
        socketio.run(app, debug=True)
    except Exception as e:
        logging.error("Error running the server: %s", str(e))
