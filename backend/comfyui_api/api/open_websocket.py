import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
from conf import COMFYUI_SERVER_ADDRESS

def open_websocket_connection():
  client_id=str(uuid.uuid4())

  ws = websocket.WebSocket()
  ws.connect("ws://{}/ws?clientId={}".format(COMFYUI_SERVER_ADDRESS, client_id))
  return ws, COMFYUI_SERVER_ADDRESS, client_id