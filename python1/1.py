import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import time
import random

def download_10wallpaper():
    """
    从 https://10wallpaper.com/ 下载壁纸
    """
    # 创建保存目录
    save_dir = os.path.join(os.getcwd(), 'walldown')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"创建目录: {save_dir}")
    
    # 目标网站首页
    target_url = 'https://10wallpaper.com/'
    
    # 请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("正在分析网页，寻找壁纸图片...")
    
    try:
        # 获取网页内容
        response = requests.get(target_url, headers=headers, timeout=15)
        response.raise_for_status()  # 检查请求是否成功
        response.encoding = 'utf-8'  # 设置编码
        
        # 解析网页
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有图片标签 (常见的壁纸网站图片多在 <img> 标签中)
        # 这里会尝试找到所有图片链接，并从中筛选可能是壁纸的图片
        img_tags = soup.find_all('img')
        
        # 用于存储符合条件的图片URL
        wallpaper_urls = []
        
        # 过滤出可能是壁纸的图片链接
        for img in img_tags:
            img_url = img.get('src') or img.get('data-src')  # 有些网站使用 data-src 懒加载
            if img_url:
                # 补全相对路径为完整URL
                full_img_url = urljoin(target_url, img_url)
                # 简单的过滤：排除图标、头像等小图，我们寻找较大尺寸的图片
                # 根据网页内容，很多图片文件名包含 'wallpaper' 或是较大的图片链接
                if any(keyword in full_img_url.lower() for keyword in ['wallpaper', 'upload', 'image', 'photo']):
                    if full_img_url not in wallpaper_urls:
                        wallpaper_urls.append(full_img_url)
        
        # 如果通过 img 标签没找到合适的，尝试另一种常见结构：直接在 <a> 标签中寻找图片下载链接
        if not wallpaper_urls:
            # 查找所有可能包含图片下载链接的 <a> 标签
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link['href']
                # 寻找图片文件扩展名
                if href.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp')):
                    full_url = urljoin(target_url, href)
                    wallpaper_urls.append(full_url)
        
        # 如果还是没找到，打印网页的部分内容帮助调试
        if not wallpaper_urls:
            print("提示: 未能自动解析到图片链接，可能需要检查网站结构。")
            print("网页的部分预览:", soup.prettify()[:500])
            return
        
        print(f"找到 {len(wallpaper_urls)} 个潜在的图片链接，将尝试下载前10个。")
        
        # 下载前10张图片
        downloaded = 0
        for i, img_url in enumerate(wallpaper_urls[:10], 1):
            try:
                # 获取图片文件名
                img_name = os.path.basename(img_url.split('?')[0])  # 去除URL参数
                if not img_name or '.' not in img_name:
                    img_name = f"wallpaper_{i}.jpg"
                
                filepath = os.path.join(save_dir, img_name)
                
                # 下载图片
                print(f"正在下载第 {i} 张: {img_url[:80]}...")
                img_response = requests.get(img_url, headers=headers, timeout=20, stream=True)
                img_response.raise_for_status()
                
                # 保存图片
                with open(filepath, 'wb') as f:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✓ 已保存: {img_name}")
                downloaded += 1
                
                # 礼貌等待，避免请求过快
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                print(f"✗ 下载第 {i} 张失败: {e}")
        
        print(f"\n下载完成！成功下载 {downloaded} 张壁纸，保存在: {save_dir}")
        
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
        print("请检查网络连接或目标网站是否可访问。")
    except Exception as e:
        print(f"处理过程中出现错误: {e}")

if __name__ == "__main__":
    print("="*50)
    print("10Wallpaper 壁纸下载工具")
    print("="*50)
    download_10wallpaper()