from flask import Blueprint, request
from app.utils.response import success_response, error_response
import openai
import json
import os
from conf import (
    OPENAI_API_KEY, 
    OPENAI_API_BASE, 
    BASE_PATH, 
    OPENAI_ENHANCE_MODEL,
    OPENAI_CAPTION_MODEL
)
from app.utils.logger import logger

bp = Blueprint('prompt', __name__, url_prefix='/api')

@bp.route('/enhance-prompt', methods=['POST'])
def enhance_prompt():
    try:
        logger.info("Starting prompt enhancement request")
        
        prompt = request.json.get('prompt')
        if not prompt:
            logger.warning("Missing prompt in request")
            return error_response('Missing required field: prompt')

        logger.info(f"Processing prompt: {prompt[:100]}...")
        
        system_message = """I am an expert in avatar prompt generation. 
        I expand and enrich user-provided prompts by focusing on aspects like lighting, composition, atmosphere, details, and theme to generate an enhanced version of the prompt. 
        I return only the enhanced prompt without any extra commentary, and I communicate exclusively in English.
        """
        
        client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE
        )
        
        logger.info(f"Sending request to OpenAI API using model: {OPENAI_ENHANCE_MODEL}")
        response = client.chat.completions.create(
            model=OPENAI_ENHANCE_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"original image prompt：{prompt}"}
            ],
            temperature=0.65
        )
        
        content = response.choices[0].message.content.strip()
        logger.info("Successfully enhanced prompt")
        return success_response({'prompt': content})
            
    except Exception as e:
        logger.exception("Error during prompt enhancement")
        return error_response('Prompt enhancement failed', 500)

@bp.route('/generate-caption', methods=['POST'])
def generate_caption():
    try:
        logger.info("Starting caption generation request")
        
        prompt = request.json.get('prompt')
        if not prompt:
            logger.warning("Missing prompt in request")
            return error_response('Missing required field: prompt')

        logger.info(f"Processing prompt for caption: {prompt[:100]}...")
        
        system_message = """你是一个专业的小红书文案生成专家。请根据用户的描述生成小红书文案。
        返回格式必须是JSON格式，包含以下三个字段：
        1. title: 爆炸性的简短标题，很有吸引力，善于下钩子，要很有梗，不要直接描述图片内容
        2. content: 简洁有趣的正文内容，突出头像和壁纸的分享，要有故事性和互动性
        3. topics: 话题标签数组，每个标签前都要加#号，长度不超过10个字符，数量不少于5个
        """
        
        client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE
        )
        
        logger.info(f"Sending request to OpenAI API using model: {OPENAI_CAPTION_MODEL}")
        response = client.chat.completions.create(
            model=OPENAI_CAPTION_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"请根据以下描述生成小红书文案，记住必须返回JSON格式：{prompt}"}
            ],
            temperature=0.85,
            response_format={ "type": "json_object" }
        )
        
        content = json.loads(response.choices[0].message.content.strip())
        logger.info("Successfully generated caption")
        return success_response(content)
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {str(e)}")
        return error_response(f'Invalid response format from OpenAI: {str(e)}', 500)
    except Exception as e:
        logger.exception("Error during caption generation")
        return error_response('Caption generation failed', 500)