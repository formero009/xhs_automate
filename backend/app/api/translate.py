from flask import Blueprint, request
from app.utils.response import success_response, error_response
from translate.tencent_translate import TencentTranslator
from app.utils.logger import logger

bp = Blueprint('translate', __name__, url_prefix='/api')

@bp.route('/translate', methods=['POST'])
def translate_text():
    try:
        logger.info("Starting translation request")
        
        data = request.json
        text = data.get('text')
        source_lang = data.get('source_lang', 'en')
        target_lang = data.get('target_lang', 'zh')
        
        logger.info(f"Translation request - from {source_lang} to {target_lang}")
        logger.info(f"Text to translate: {text[:100]}...")  # 只记录前100个字符
        
        if not text:
            logger.warning("Missing text in translation request")
            return error_response('Missing required field: text')

        logger.info("Initializing TencentTranslator")
        translator = TencentTranslator()
        
        logger.info("Sending translation request")
        translated_text = translator.translate(text, source_lang, target_lang)
        logger.info("Translation completed successfully")

        return success_response({
            'original_text': text,
            'translated_text': translated_text
        })

    except Exception as e:
        logger.exception("Error during translation")
        return error_response('Translation failed', 500) 