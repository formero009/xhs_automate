from flask import Blueprint
from app.utils.response import success_response
import websocket
from conf import COMFYUI_SERVER_ADDRESS

bp = Blueprint('health', __name__, url_prefix='/api')

def check_comfyui_status():
    try:
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId=health_check".format(COMFYUI_SERVER_ADDRESS))
        ws.close()
        return True, "ComfyUI is running"
    except Exception as e:
        return False, "ComfyUI is not running. Please start ComfyUI first."

@bp.route('/health', methods=['GET'])
def health_check():
    comfyui_running, comfyui_message = check_comfyui_status()
    
    return success_response({
        'status': 'healthy' if comfyui_running else 'warning',
        'message': 'Service is running',
        'comfyui_status': {
            'running': comfyui_running,
            'message': comfyui_message
        }
    }) 