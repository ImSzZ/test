import requests
from lxml import etree
import os
import time

class WallpaperScraper:
    def __init__(self, save_dir='downloaded_wallpapers'):
        """
        初始化下载器
        :param save_dir: 图片保存的文件夹名称
        """
        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        # 直接使用固定的请求头，不需要 fake_useragent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def scrape(self, max_pages=3):
        """
        主流程：爬取壁纸网站，下载图片
        :param max_pages: 要爬取的页数
        """
        print(f"⏳ 开始爬取任务，目标页数: {max_pages}")
        img_counter = 1
        start_page = 2

        for page in range(start_page, max_pages + 1):
            print(f"\n📄 --- 正在处理第 {page} 页 ---")
            # 1. 构造每一页的网址
            url = f'https://10wallpaper.com/list-wallpapers/{page}/'
            
            try:
                # 2. 获取网页内容
                resp = requests.get(url, headers=self.headers, timeout=10)
                resp.raise_for_status()
                resp.encoding = 'utf-8'
                
                # 3. 解析网页，找到所有图片的链接
                tree = etree.HTML(resp.text)
                # 这个 XPath 是从目标网页中分析得到的，用于提取所有 <img> 标签的 'src' 属性
                img_urls = tree.xpath("//div[@class='item-img']//img/@src")
                
                if not img_urls:
                    print(f"⚠️ 在第 {page} 页没有找到任何图片链接，可能页面结构已更新或已到末尾。")
                    break
                
                print(f"✨ 在第 {page} 页发现 {len(img_urls)} 张图片，开始下载...")
                
                # 4. 遍历并下载每一张图片
                for img_path in img_urls:
                    # 将相对路径拼接成完整的图片URL
                    if img_path.startswith('/'):
                        img_url = 'https://10wallpaper.com' + img_path
                    else:
                        img_url = img_path
                    
                    # 提取图片文件名，如果无法提取则用序号命名
                    file_name = img_path.split('/')[-1]
                    if not file_name or '.' not in file_name:
                        file_name = f"wallpaper_{img_counter}.jpg"
                    
                    # 下载并保存
                    self._download_image(img_url, file_name)
                    img_counter += 1
                    time.sleep(0.5)
                
                # 每页处理完后多停顿一会
                time.sleep(1.5)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ 网络请求出错 (第{page}页): {e}")
                continue
            except Exception as e:
                print(f"❌ 解析页面时发生未知错误 (第{page}页): {e}")
                continue
        
        print(f"\n🎉 下载任务全部完成！图片已保存到 '{self.save_dir}' 文件夹中。")

    def _download_image(self, img_url, file_name):
        """
        下载单张图片的内部方法
        :param img_url: 图片的网络地址
        :param file_name: 保存到本地的文件名
        """
        try:
            # 添加 Referer 头，模拟图片的真实来源
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://10wallpaper.com/'
            }
            response = requests.get(img_url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()
            
            # 根据图片内容判断后缀
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                suffix = '.jpg'
            elif 'png' in content_type:
                suffix = '.png'
            else:
                suffix = '.jpg'
            
            # 确保文件名有正确的后缀
            if not file_name.lower().endswith(( '.jpg', '.jpeg', '.png' )):
                file_name = os.path.splitext(file_name)[0] + suffix
            
            file_path = os.path.join(self.save_dir, file_name)
            
            # 以二进制流的方式写入文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ 下载成功: {file_name}")
            return True
        except Exception as e:
            print(f"❌ 下载失败: {file_name} -> 原因: {e}")
            return False

if __name__ == '__main__':
    print("="*30)
    print("欢迎使用壁纸批量下载工具！")
    print("="*30)
    
    # 你可以通过修改下面的参数来定制下载任务
    scraper = WallpaperScraper(save_dir='my_beautiful_wallpapers')
    scraper.scrape(max_pages=2)  # 这里设置爬取2页