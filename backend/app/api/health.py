from flask import Blueprint
from app.utils.response import success_response

bp = Blueprint('health', __name__, url_prefix='/api')

@bp.route('/health', methods=['GET'])
def health_check():
    return success_response({
        'status': 'healthy',
        'message': 'Service is running'
    }) 