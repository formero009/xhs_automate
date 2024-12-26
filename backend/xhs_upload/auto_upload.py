from playwright.sync_api import sync_playwright
import time
from xhs import XhsClient
from conf import BASE_PATH
import os
import glob
from typing import Union, List


class XhsUploader:
    def __init__(self, cookie):
        self.playwright = sync_playwright().start()
        self.browser_context, self.context_page = self.get_context_page(self.playwright)
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

    # def get_context_page(self, playwright):
    #     chromium = playwright.chromium
    #     browser = chromium.launch(headless=True)
    #     browser_context = browser.new_context(
    #         viewport={"width": 1920, "height": 1080},
    #         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    #     )
    #     stealthPath = os.path.join(BASE_PATH, "xhs_upload", "stealth.min.js")
    #     browser_context.add_init_script(path=stealthPath)
    #     context_page = browser_context.new_page()
    #     return browser_context, context_page

    def sign(self, uri, data, a1="", web_session=""):
        # 填写自己的 flask 签名服务端口地址
        # res = requests.post("http://192.168.1.150:5005/sign",
        #                     json={"uri": uri, "data": data, "a1": a1, "web_session": web_session})
        # signs = res.json()
        # return {
        #     "x-s": signs["x-s"],
        #     "x-t": signs["x-t"]
        # }
        self.context_page.goto("https://www.xiaohongshu.com")
        cookie_list = self.browser_context.cookies()
        web_session_cookie = list(filter(lambda cookie: cookie["name"] == "web_session", cookie_list))
        if not web_session_cookie:
            self.browser_context.add_cookies([
                {'name': 'web_session', 'value': web_session, 'domain': ".xiaohongshu.com", 'path': "/"},
                {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
            )
            time.sleep(1)
        encrypt_params = self.context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
        return {
            "x-s": encrypt_params["X-s"],
            "x-t": str(encrypt_params["X-t"])
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
        # xhs_client = XhsClient(cookie=self.cookie, sign=self.sign)
        note = self.xhs_client.create_image_note(title, desc, processed_images, topics=topics, is_private=is_private)
        return note

    # def close(self):
    #     """Clean up resources"""
    #     self.browser_context.close()
    #     self.playwright.stop()

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
    test_publish_note()
    # test_search_topic("哆啦A梦")
    # test_get_emojis()
        
