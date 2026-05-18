# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urlparse, unquote
# import re

# def extract_image_filenames(url):
#     """
#     从网页中提取所有图片的链接，并输出文件名（不含路径、不含参数）
#     """
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
#     }
    
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status()
#         # 自动检测编码（部分网页可能不是 utf-8）
#         response.encoding = response.apparent_encoding
#     except Exception as e:
#         print(f"请求失败: {e}")
#         return []
    
#     soup = BeautifulSoup(response.text, 'html.parser')
    
#     # 查找所有 img 标签
#     img_tags = soup.find_all('img')
    
#     filenames = []
#     for img in img_tags:
#         # 获取 src 或 data-src（懒加载常见）
#         src = img.get('src') or img.get('data-src')
#         if not src:
#             continue
        
#         # 提取 URL 最后一段作为文件名（去掉查询参数）
#         parsed = urlparse(src)
#         path = unquote(parsed.path)  # 解码 %20 等字符
#         filename = path.split('/')[-1]
        
#         # 过滤掉明显不是图片文件名的（如空白、极短、无扩展名等）
#         if filename and len(filename) > 3 and re.search(r'\.(jpg|jpeg|png|gif|webp|bmp)$', filename, re.I):
#             filenames.append(filename)
    
#     # 去重并保持顺序
#     seen = set()
#     unique_filenames = []
#     for name in filenames:
#         if name not in seen:
#             seen.add(name)
#             unique_filenames.append(name)
    
#     return unique_filenames

# # 测试两个网页
# urls = [
#     # "https://wallhaven.cc/toplist?page=2",
#     "https://10wallpaper.com/"
# ]

# for url in urls:
#     print(f"\n分析网页: {url}")
#     images = extract_image_filenames(url)
#     if images:
#         # 按你示例的格式输出，用顿号或逗号分隔
#         print("输出: \n")
#         print("、".join(images[:20])+"\n")  # 只显示前20个避免太长
#     else:
#         print("没有提取到图片文件名（可能需要检查网页结构或反爬机制）")



import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
import re

def extract_image_filenames(url):
    """
    从网页中提取所有图片的链接，并输出文件名（不含路径、不含参数）
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
    except Exception as e:
        print(f"请求失败: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有 img 标签
    img_tags = soup.find_all('img')
    
    filenames = []
    for img in img_tags:
        # 获取 src 或 data-src（懒加载常见）
        src = img.get('src') or img.get('data-src')
        if not src:
            continue
        
        # 提取 URL 最后一段作为文件名（去掉查询参数）
        parsed = urlparse(src)
        path = unquote(parsed.path)  # 解码 %20 等字符
        filename = path.split('/')[-1]
        
        # 过滤掉明显不是图片文件名的（如空白、极短、无扩展名等）
        if filename and len(filename) > 3 and re.search(r'\.(jpg|jpeg|png|gif|webp|bmp)$', filename, re.I):
            filenames.append(filename)
    
    # 去重并保持顺序
    seen = set()
    unique_filenames = []
    for name in filenames:
        if name not in seen:
            seen.add(name)
            unique_filenames.append(name)
    
    return unique_filenames

def print_filenames_one_per_line(url,limit):
    """输出格式：每个文件名独占一行"""
    filenames = extract_image_filenames(url)
    if not filenames:
        print("没有提取到图片文件名（可能需要检查网页结构或反爬机制）")
        return
    
     # 如果 limit 为 None，则输出全部；否则输出前 limit 条
    output_filenames = filenames if limit is None else filenames[:limit]


    # 关键修改：每个文件名后面跟一个换行符（不是逗号）
    for name in output_filenames:
        print(name)   # 默认 print 会加换行符，正好符合你的要求

# 测试两个网页
urls = [
    # "https://wallhaven.cc/toplist?page=2",
    "https://10wallpaper.com/"
]

for url in urls:
    print(f"\n分析网页: {url}")
    # print_filenames_one_per_line(url,None)
    print_filenames_one_per_line(url,None)