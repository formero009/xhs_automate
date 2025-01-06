# from playwright.sync_api import sync_playwright
# import time
from app.utils.logger import logger
import requests
from xhs import XhsClient
from conf import BASE_PATH
import os
import glob
from typing import Union, List
import json
import random
import openai
from conf import OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_ENHANCE_MODEL, PROMPT_ENHANCE_SYSTEM_MESSAGE, OPENAI_CAPTION_MODEL, PROMPT_CAPTION_SYSTEM_MESSAGE
import asyncio
from app.models.user import User
from app.extensions import db
from app.models.workflow import Workflow
from app.models.workflow_variable import WorkflowVariable
from app.models.variable_definitions import VariableDefinitions
from comfyui_api.utils.actions.prompt_to_image import prompt_to_image
from comfyui_api.utils.actions.load_workflow import load_workflow
from app.models.image import Image


class XhsUploader:
    def __init__(self, cookie):
        # self.playwright = sync_playwright().start()
        # self.browser_context, self.context_page = self.get_context_page(self.playwright)
        self.cookie = cookie
        self.xhs_client = self.initXhsClient()

    def initXhsClient(self):
        return XhsClient(cookie=self.cookie, sign=self.sign)

    def get_images_from_directory(self, directory: str) -> List[str]:
        """
        Get all jpg and png images from a directory
        
        Args:
            directory (str): Directory path to scan for images
            
        Returns:
            List[str]: List of image file paths
        """
        if not os.path.isdir(directory):
            raise Exception(f"Directory not found: {directory}")
            
        # Get all jpg and png files (case insensitive, but avoid duplicates)
        image_files = set()  # 使用 set 来避免重复
        for ext in ('*.jpg', '*.jpeg', '*.png'):
            # Windows 是大小写不敏感的，所以不需要重复的大写模式
            image_files.update(glob.glob(os.path.join(directory, ext)))
            
        if not image_files:
            raise Exception(f"No jpg or png images found in directory: {directory}")
            
        print('image files:', sorted(image_files))
        return sorted(image_files)  # 转换回列表并排序
    

    def process_images(self, images: Union[str, List[str]]) -> List[str]:
        """
        Process images input which can be:
        - A single directory path (str)
        - A list of image file paths
        
        Args:
            images: Directory path or list of image paths
            
        Returns:
            List[str]: List of processed local image paths
        """
        print('检测到多个图片上传到小红书：', images)
        # Handle directory input
        if isinstance(images, str):
            if os.path.isdir(images):
                return self.get_images_from_directory(images)
            else:
                # Single image path
                images = [images]
        
        # Handle list of images
        if not isinstance(images, (list, tuple)):
            raise Exception(f"Invalid images format. Expected string or list, got {type(images)}")
            
        # Validate all images
        processed_images = []
        for image in images:
            if not isinstance(image, str):
                raise Exception(f"Invalid image format. Expected string, got {type(image)}")
            
            # Handle if the item is a directory
            if os.path.isdir(image):
                processed_images.extend(self.get_images_from_directory(image))
            else:
                # Verify file exists and has correct extension
                if not os.path.exists(image):
                    raise Exception(f"Image file not found: {image}")
                
                ext = os.path.splitext(image)[1].lower()
                if ext not in ('.jpg', '.jpeg', '.png'):
                    raise Exception(f"Unsupported image format: {image}. Only jpg and png are supported.")
                    
                processed_images.append(image)
                
        return processed_images

    def sign(self, uri, data, a1="", web_session=""):
        # 填写自己的 flask 签名服务端口地址
        res = requests.post("http://192.168.1.150:5005/sign",
                            json={"uri": uri, "data": data, "a1": a1, "web_session": web_session})
        signs = res.json()
        return {
            "x-s": signs["x-s"],
            "x-t": signs["x-t"]
        }

    def upload_note(self, title, desc, images, topics, is_private=True):
        """
        Upload note with images. Images can be local file paths or directory paths.
        
        Args:
            title (str): Note title
            desc (str): Note description
            images (Union[str, List[str]]): Directory path or list of image paths
            is_private (bool): Whether the note is private
            post_time (str, optional): Post time
        """
        processed_images = self.process_images(images)
        note = self.xhs_client.create_image_note(title, desc, processed_images, topics=topics, is_private=is_private)
        return note

def _generate_prompts(prompt_template: str, topic: str, image_count: int, image_style: str) -> List[str]:
    """Generate image prompts using OpenAI API"""
    logger.info('Generating prompts with params: topic=%s, count=%d, style=%s', topic, image_count, image_style)
    
    base_prompt = "input parameters, topic:{}, style:{}, count:{}".format(
        topic if topic else "",
        image_style if image_style else "",
        image_count
    )
    logger.debug('Base prompt: %s', base_prompt)
    
    client = openai.OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE
    )
    
    batch_prompt = base_prompt.format(style=image_style)
    logger.info('System message: %s', prompt_template)
    
    response = client.chat.completions.create(
        model=OPENAI_ENHANCE_MODEL,
        messages=[
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": batch_prompt}
        ],
        temperature=0.65,
        max_tokens=4096,
    )
    
    if not response.choices or not response.choices[0].message.content:
        raise Exception("Failed to generate prompts from OpenAI")
        
    prompts = [p.strip() for p in response.choices[0].message.content.strip().split('\n') if p.strip()]
    prompts = prompts[:image_count]
    
    if len(prompts) < image_count:
        raise Exception(f"Only generated {len(prompts)} prompts, but {image_count} were requested")
    
    logger.info('Generated prompts: %s', prompts)
    return prompts

def _get_workflow_info(workflow_id: int) -> tuple:
    """Get workflow information and variables"""
    logger.info('Getting workflow info for ID: %d', workflow_id)
    
    workflow = Workflow.query.get(workflow_id)
    if not workflow:
        raise Exception(f"Workflow not found with id: {workflow_id}")
    logger.debug('Found workflow: %s', workflow.name)

    workflow_path = os.path.join(BASE_PATH, workflow.file_path.replace('\\', '/'))
    if not os.path.exists(workflow_path):
        raise Exception(f"Workflow file not found at path: {workflow_path}")
    logger.debug('Workflow path: %s', workflow_path)

    workflow_data = load_workflow(workflow_path)
    logger.debug('Loaded workflow data')

    workflow_vars = WorkflowVariable.query.filter_by(workflow_id=workflow_id).all()
    logger.debug('Found %d workflow variables', len(workflow_vars))
    
    prompt_var = next((var for var in workflow_vars 
                    if var.variable_definition.param_type == 'input' 
                    and 'prompt' in var.title.lower()), None)
    seed_var = next((var for var in workflow_vars
                    if var.variable_definition.param_type == 'input'
                    and 'seed' in var.variable_definition.value_path.lower()), None)
    output_var = next((var for var in workflow_vars 
                    if var.variable_definition.param_type == 'output'), None)

    if not prompt_var:
        raise Exception("Workflow missing required prompt input variable")
    if not output_var:
        raise Exception("Workflow missing required output variable")
        
    return workflow, workflow_data, prompt_var, seed_var, output_var

def _generate_images(workflow_data: dict, prompt_var: WorkflowVariable, seed_var: WorkflowVariable, 
                    output_var: WorkflowVariable, prompts: List[str], workflow: Workflow, 
                    image_style: str, topic: str) -> List[str]:
    """Generate images using the workflow"""
    logger.info('Starting image generation for %d prompts', len(prompts))
    generated_images = []
    
    for prompt in prompts:
        variable_mapping = {
            prompt_var.node_id: {
                prompt_var.variable_definition.value_path: prompt
            }
        }
        
        seed_value = None
        if seed_var:
            seed_value = random.randint(100000000, 9999999999)
            variable_mapping[seed_var.node_id] = {
                seed_var.variable_definition.value_path: seed_value
            }
        logger.debug('Variable mapping: %s', variable_mapping)

        result = prompt_to_image(
            workflow=workflow_data,
            variable_values=variable_mapping,
            output_node_ids=[output_var.node_id],
            save_previews=True
        )
        logger.debug('Generation result: %s', result)

        if result:
            image_path = os.path.join(BASE_PATH, 'output', 'images', result[0])
            generated_images.append(image_path)
            logger.info('Generated image: %s', image_path)

            image = Image(
                filename=result[0],
                workflow_name=workflow.name,
                file_path=os.path.join('output', 'images', result[0]),
                workflow_id=workflow.id,
                variables={
                    'prompt': prompt,
                    'seed': seed_value,
                    'style': image_style,
                    'topic': topic
                }
            )
            db.session.add(image)
            db.session.commit()
            logger.info('Saved image record to database: %d', image.id)

    return generated_images

def _generate_caption(image_style: str, topic: str, prompts: List[str]) -> dict:
    """Generate caption for Xiaohongshu note using GPT-4"""
    logger.info('Generating caption for Xiaohongshu note')
    
    # Prepare input for caption generation
    
    client = openai.OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE
    )
    
    logger.info('Sending request to OpenAI for caption generation')
    response = client.chat.completions.create(
        model=OPENAI_CAPTION_MODEL,
        messages=[
            {"role": "system", "content": PROMPT_CAPTION_SYSTEM_MESSAGE},
            {"role": "user", "content": "请生成一个小红书文案，记住必须返回JSON格式"}
        ],
        temperature=0.85,
        response_format={ "type": "json_object" }
    )
    
    try:
        content = json.loads(response.choices[0].message.content.strip())
        logger.info('Successfully generated caption')
        return content
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {str(e)}")
        raise Exception(f"Failed to generate caption: {str(e)}")

def _upload_to_xiaohongshu(generated_images: List[str], image_style: str, topic: str, 
                          account_id: int, prompts: List[str]) -> dict:
    """Upload generated images to Xiaohongshu"""
    logger.info('Uploading %d images to Xiaohongshu', len(generated_images))
    
    # Generate caption using GPT-4
    caption = _generate_caption(image_style, topic, prompts)
    logger.info('Generated caption: %s', caption)
    
    note = None
    user = User.query.get(account_id)
    if not user:
        raise Exception(f"User not found with id: {account_id}")

    uploader = XhsUploader(cookie=user.cookie)
    
    # Process and format topics
    formatted_topics = []
    desc_append_topics = []
    
    for topic in caption.get('topics', [topic] if topic else []):
        topic_text = topic.replace('#', '').strip()
        logger.info(f"Getting topic suggestions for: {topic_text}")
        
        suggest_result = uploader.xhs_client.get_suggest_topic(topic_text)
        if not suggest_result:
            logger.warning(f"No topic suggestions found for: {topic_text}")
            continue
            
        topic_info = suggest_result[0]
        logger.info(f"Got topic suggestion: {topic_info.get('name')} (ID: {topic_info.get('id')})")
        
        formatted_topics.append({
            'id': topic_info.get('id'),
            'name': topic_info.get('name'),
            'type': 'topic',
            'link': topic_info.get('link')
        })
        desc_append_topics.append(f'#{topic_info.get("name")}[话题]#')
    
    # Upload note with formatted topics
    note = uploader.upload_note(
        title=caption.get('title', "又是一些精美的壁纸"),
        desc=' '.join(desc_append_topics),  # Add formatted topics to description
        images=generated_images,
        topics=formatted_topics,
        is_private=True
    )
    
    logger.info('Successfully uploaded note to Xiaohongshu')
    return note

def auto_gen_and_upload(topic, image_count, prompt_template, image_style, account_id, workflow_id):
    """Main function to generate images and upload to Xiaohongshu"""
    try:
        logger.info('Starting auto generation and upload process')
        logger.info('Parameters: topic=%s, count=%d, style=%s, account=%s, workflow=%d', 
                    topic, image_count, image_style, account_id, workflow_id)
        
        # Limit image count to maximum 15
        image_count = min(image_count, 15)

        # 1. Generate prompts
        prompts = _generate_prompts(prompt_template, topic, image_count, image_style)

        try:
            # 2. Get workflow information
            workflow, workflow_data, prompt_var, seed_var, output_var = _get_workflow_info(workflow_id)

            # 3. Generate images
            generated_images = _generate_images(
                workflow_data, prompt_var, seed_var, output_var, 
                prompts, workflow, image_style, topic
            )

            # 4. Upload to Xiaohongshu
            if generated_images:
                note = _upload_to_xiaohongshu(generated_images, image_style, topic, account_id, prompts)
                
                return {
                    "success": True,
                    "message": "Successfully generated and uploaded images",
                    "data": {
                        "note": note,
                        "prompts": prompts,
                        "images": generated_images
                    }
                }
            else:
                raise Exception("No images were generated")

        except Exception as e:
            logger.error("Error during image generation: %s", str(e), exc_info=True)
            raise e

    except Exception as e:
        logger.error("Error in auto_gen_and_upload: %s", str(e), exc_info=True)
        return {
            "success": False,
            "message": str(e),
            "data": None
        }

def get_self_info():
    cookie = ""
    uploader = XhsUploader(cookie=cookie)
    data = uploader.xhs_client.get_self_info()
    assert isinstance(data, dict)
    return data

def test_publish_note():
    # Example usage
    title = "可爱的头像来袭"
    desc = "下面我说两点"
    
    # Example 1: Using a directory path
    images = os.path.join(BASE_PATH, "datas")
    
    # Example 2: Using a list of file paths
    images = [
        'xhs_automate\\backend\\upload\\images\\test.png'
    ]
    topics = [
        {
            "id": "5be00fafcfc9bd000193136d", "name": "头像", "type": "topic",
            "link": "https://www.xiaohongshu.com/page/topics/5be00faf758b8000015cd349?naviHidden=yes"
        }
    ]
    
    cookie = ""

    uploader = XhsUploader(cookie=cookie)
    # try:
    note = uploader.upload_note(title=title, desc=desc, images=images, topics=topics, is_private=True)
    print(note)
    # finally:
    #     uploader.close()

def test_search_topic(topic_keyword):
    cookie = ""
    uploader = XhsUploader(cookie=cookie)
    topics = uploader.xhs_client.get_suggest_topic(topic_keyword)
    print(topics)

def test_get_emojis():
    cookie = ""
    uploader = XhsUploader(cookie=cookie)
    emojis = uploader.xhs_client.get_emojis()
    print(emojis)


if __name__ == "__main__":
    pass
    # 其他测试函数
    # get_self_info()
    # test_publish_note()
    # test_search_topic("哆啦A梦")
    # test_get_emojis()