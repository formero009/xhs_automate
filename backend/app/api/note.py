from flask import Blueprint, request
from app.utils.response import success_response, error_response
from xhs_upload.auto_upload import XhsUploader
from conf import XHS_COOKIE, UPLOAD_FOLDER, OUTPUT_FOLDER
import os
from app.utils.logger import logger

bp = Blueprint('note', __name__, url_prefix='/api')

@bp.route('/publish', methods=['POST'])
def upload_note():
    try:
        logger.info("Starting note publish request")
        
        data = request.json
        title = data.get('title')
        desc = data.get('description')
        is_private = data.get('is_private', True)
        image_urls = data.get('images', [])
        topics = data.get('topics', [])
        
        logger.info(f"Note details - title: {title}, private: {is_private}, image count: {len(image_urls)}, topics: {topics}")
        
        if not all([title, desc, image_urls]):
            logger.warning("Missing required fields in request")
            return error_response('Missing required fields: title, description, or images')

        # 验证并转换图片路径
        image_paths = []
        for url in image_urls:
            logger.info(f"Processing image URL: {url}")
            
            if url.startswith('/images/upload/'):
                base_dir = UPLOAD_FOLDER
                filename = url.replace('/images/upload/', '', 1)
            elif url.startswith('/images/output/'):
                base_dir = OUTPUT_FOLDER
                filename = url.replace('/images/output/', '', 1)
            else:
                logger.warning(f"Invalid image path format: {url}")
                return error_response(f'Invalid image path: {url}')

            file_path = os.path.join(base_dir, filename)
            if not os.path.exists(file_path):
                logger.error(f"Image file not found: {file_path}")
                return error_response(f'Image file not found: {filename}')
                
            image_paths.append(file_path)
            logger.info(f"Validated image path: {file_path}")
        
        logger.info("Initializing XhsUploader")
        uploader = XhsUploader(cookie=XHS_COOKIE)
        
        formatted_topics = []
        desc_append_topics = []
        for topic in topics:
            ttpoc = topic.replace('#', '').strip()
            logger.info(f"Getting topic suggestions for: {ttpoc}")
            
            suggest_result = uploader.xhs_client.get_suggest_topic(ttpoc)
            topic_info = suggest_result[0]
            logger.info(f"Got topic suggestion: {topic_info.get('name')} (ID: {topic_info.get('id')})")
            
            formatted_topics.append({
                'id': topic_info.get('id'),
                'name': topic_info.get('name'),
                'type': 'topic',
                'link': topic_info.get('link')
            })
            desc_append_topics.append(f'#{topic_info.get("name")}[话题]#')
        
        logger.info("Starting note upload to XHS")
        note = uploader.upload_note(
            title=title,
            desc=desc + '\n'+' '.join(desc_append_topics),
            images=image_paths,
            topics=formatted_topics,
            is_private=is_private
        )
        logger.info(f"Successfully published note to XHS with result: {note}")
        
        return success_response(note)

    except Exception as e:
        logger.exception("Error during note publishing")
        return error_response('Failed to publish note', 500) 