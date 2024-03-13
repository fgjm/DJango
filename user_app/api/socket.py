import sys
from websockets.sync.client import connect
import asyncio
import socketio
from logs import get_error



def send_web_socket(send_message):
    try:
        with connect("ws://127.0.0.1:5002/") as websocket:
            websocket.send(send_message)
            message = websocket.recv()
    except:
        get_error('send_web_socket',sys.exc_info())
    return False

def send_socket(send_message):
    try:
        with socketio.SimpleClient() as sio:
            sio.connect('ws://127.0.0.1:5002/')
            sio.emit(send_message['socket_on'], send_message)
            event = sio.receive(timeout=5)
            if 'response' in event[1]:
                return event[1]['response']
    except:
        get_error('send_socket',sys.exc_info())
    return False
    