import requests
from bs4 import BeautifulSoup
import os
import time
import ui
from urllib.parse import urljoin


class WallhavenScraper:
    def __init__(self, search_keyword, save_dir='wallhaven_wallpapers'):
        self.base_url = ui.url
        self.search_url = f'{self.base_url}/search?q={search_keyword}&page='
        self.save_dir = save_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def get_image_urls_from_page(self, page_url):
        """获取单页中所有壁纸详情页的链接"""
        try:
            response = requests.get(page_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # 注意：Wallhaven的图片链接通常放在 <a class="preview" href="..."> 中，如果网站改版，需调整选择器
            preview_links = soup.select('a.preview')
            image_detail_urls = [urljoin(self.base_url, link.get('href')) for link in preview_links]
            return image_detail_urls
        except Exception as e:
            print(f"获取页面 {page_url} 失败: {e}")
            return []

    def get_download_url_from_detail(self, detail_url):
        """从壁纸详情页获取实际图片下载链接（最高分辨率）"""
        try:
            response = requests.get(detail_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找包含原始图片链接的 img 标签，通常 id="wallpaper"
            img_tag = soup.select_one('img#wallpaper')
            if img_tag and img_tag.get('src'):
                # 直接获取src属性即为原始图片URL
                return img_tag['src']
            # 备用选择器：某些版本可能class不同
            img_tag = soup.select_one('img.wallpaper-img')
            if img_tag and img_tag.get('src'):
                return img_tag['src']
            return None
        except Exception as e:
            print(f"获取详情页 {detail_url} 失败: {e}")
            return None

    def download_image(self, img_url, file_name):
        """下载并保存图片"""
        try:
            response = requests.get(img_url, headers=self.headers, timeout=15, stream=True)
            response.raise_for_status()
            file_path = os.path.join(self.save_dir, file_name)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"下载成功: {file_name}")
            return True
        except Exception as e:
            print(f"下载失败 {img_url}: {e}")
            return False

    def scrape(self, max_pages=3, delay=1):
        """主流程：爬取前max_pages页，每页之间延迟delay秒"""
        for page in range(1, max_pages + 1):
            print(f"\n--- 正在爬取第 {page} 页 ---")
            current_page_url = f"{self.search_url}{page}"
            detail_urls = self.get_image_urls_from_page(current_page_url)
            if not detail_urls:
                print(f"第 {page} 页无数据，停止爬取。")
                break

            for idx, detail_url in enumerate(detail_urls):
                img_url = self.get_download_url_from_detail(detail_url)
                if img_url:
                    # 文件名使用页码_序号.jpg，实际扩展名可根据内容调整
                    file_name = f"page{page}_{idx+1}.jpg"
                    self.download_image(img_url, file_name)
                else:
                    print(f"未找到下载链接: {detail_url}")
                time.sleep(0.5)  # 下载每张图片后短暂停顿，减轻服务器压力
            time.sleep(delay)  # 每页之间延迟

if __name__ == '__main__':
    ui.root = ui.tk.Tk()
    app = ui.DownloaderApp(ui.root)
    ui.root.mainloop()

    # 使用示例：搜索关键词为“landscape”，爬取前2页
    # scraper = WallhavenScraper(search_keyword='landscape', save_dir='landscape_wallpapers')
    # scraper.scrape(max_pages=2, delay=2)