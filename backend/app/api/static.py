from flask import Blueprint, send_from_directory
from app.utils.response import error_response
from conf import UPLOAD_FOLDER, OUTPUT_FOLDER
from app.utils.logger import logger

bp = Blueprint('static', __name__)

@bp.route('/images/<path:filename>')
def serve_image(filename):
    try:
        logger.info(f"Serving image request: {filename}")
        
        if filename.startswith('upload/'):
            actual_filename = filename.replace('upload/', '', 1)
            logger.info(f"Serving upload image: {actual_filename}")
            return send_from_directory(UPLOAD_FOLDER, actual_filename)
        elif filename.startswith('output/'):
            actual_filename = filename.replace('output/', '', 1)
            logger.info(f"Serving output image: {actual_filename}")
            return send_from_directory(OUTPUT_FOLDER, actual_filename)
        else:
            logger.warning(f"Invalid image path requested: {filename}")
            return error_response('Invalid image path', 400)
    except Exception as e:
        logger.exception(f"Error serving image: {filename}")
        return error_response('Image not found', 404) 