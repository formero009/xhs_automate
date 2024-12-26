import os
import time
import asyncio
import requests
from playwright.async_api import async_playwright
import sys
import re
from concurrent.futures import ThreadPoolExecutor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf import IMAGE_DIR

class PinterestSpider:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.all_image_urls = set()  # 存储所有发现的图片URL
        
    async def initialize(self):
        """初始化 Playwright"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def collect_current_images(self):
        """收集当前页面上的图片"""
        new_images = await self.page.query_selector_all('img.hCL.kVc.L4E.MIw')
        new_urls = set()
        for img in new_images:
            src = await img.get_attribute('src')
            if src and 'i.pinimg.com' in src:
                new_urls.add(src)
        
        # 计算新增的URL数量
        new_added = len(new_urls - self.all_image_urls)
        self.all_image_urls.update(new_urls)
        
        return new_added

    async def auto_scroll(self, scroll_times=5):
        """自动滚动页面指定次数"""
        last_height = await self.page.evaluate('document.body.scrollHeight')
        no_new_images_count = 0  # 连续没有新图片的次数
        
        for i in range(scroll_times):
            # 滚动到页面底部
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            print(f"第 {i+1}/{scroll_times} 次滚动")
            
            # 等待新内容加载
            await self.page.wait_for_timeout(2000)
            
            # 收集新图片
            new_images_count = await self.collect_current_images()
            print(f"本次滚动新增 {new_images_count} 张图片，当前总共 {len(self.all_image_urls)} 张")
            
            # 检查是否有新内容加载
            new_height = await self.page.evaluate('document.body.scrollHeight')
            if new_height == last_height:
                print("页面高度未变化，等待更长时间...")
                await self.page.wait_for_timeout(3000)
                new_height = await self.page.evaluate('document.body.scrollHeight')
                
                if new_height == last_height and new_images_count == 0:
                    no_new_images_count += 1
                    if no_new_images_count >= 3:  # 连续3次没有新图片就退出
                        print("连续多次没有新图片，停止滚动")
                        break
                else:
                    no_new_images_count = 0
            
            last_height = new_height

    def convert_to_original_url(self, url):
        """将Pinterest缩略图URL转换为原始图片URL"""
        pattern = r'https://i\.pinimg\.com/\w+/(\w{2}/\w{2}/\w{2}/\w+\.\w+)'
        match = re.match(pattern, url)
        if match:
            image_path = match.group(1)
            return f'https://i.pinimg.com/originals/{image_path}'
        return None

    def download_image(self, img_url):
        """使用requests下载单个图片"""
        try:
            original_url = self.convert_to_original_url(img_url)
            if not original_url:
                return
            
            file_name = original_url.split('/')[-1]
            file_path = os.path.join(IMAGE_DIR, file_name)
            
            if os.path.exists(file_path):
                print(f"文件已存在，跳过: {file_name}")
                return
            
            response = requests.get(original_url, timeout=10)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"成功下载图片: {file_name}")
            else:
                print(f"下载失败，状态码: {response.status_code}, URL: {original_url}")
                    
        except Exception as e:
            print(f"下载图片失败: {str(e)}, URL: {img_url}")

    async def scrape_images(self, url, scroll_times=5):
        """爬取指定Pinterest页面的图片"""
        try:
            await self.page.goto(url)
            await self.page.wait_for_timeout(3000)
            
            # 收集初始页面的图片
            await self.collect_current_images()
            print(f"初始页面找到 {len(self.all_image_urls)} 张图片")
            
            # 开始滚动收集
            await self.auto_scroll(scroll_times)
            
            print(f"滚动完成，共收集到 {len(self.all_image_urls)} 张独特图片")
            
            # 使用线程池并发下载所有收集到的图片
            with ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.download_image, self.all_image_urls)
            
        except Exception as e:
            print(f"爬取失败: {str(e)}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """清理资源"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

async def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    
    spider = PinterestSpider()
    await spider.initialize()
    
    target_url = "https://jp.pinterest.com/pin/34199278415950999/"
    await spider.scrape_images(target_url, scroll_times=2)

if __name__ == "__main__":
    asyncio.run(main())
