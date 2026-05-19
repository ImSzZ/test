# import os
# import re
# import sys
# import time     
# import random    
# import tkinter as tk
# from tkinter import messagebox, scrolledtext
# import threading
# from urllib.parse import urljoin, urlparse, parse_qs
# import requests
# from bs4 import BeautifulSoup

# # 模拟浏览器请求头
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# }

# class ImageSpiderGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("智能高清图片下载器 (修正最终版)")
#         self.root.geometry("620x520")

#         # 网址输入框
#         tk.Label(root, text="请输入网址:", font=("Arial", 11)).pack(anchor="w", padx=15, pady=5)
#         self.url_input = tk.Entry(root, font=("Arial", 11), width=65)
#         self.url_input.pack(padx=15, pady=5)
#         self.url_input.insert(0, "https://bing.wdbyte.com/zh-cn/")

#         # 数量控制区域
#         count_frame = tk.Frame(root)
#         count_frame.pack(anchor="w", padx=15, pady=5)
        
#         tk.Label(count_frame, text="设置下载数量 (张):", font=("Arial", 11)).pack(side=tk.LEFT)
#         self.count_input = tk.Entry(count_frame, font=("Arial", 11), width=10)
#         self.count_input.pack(side=tk.LEFT, padx=10)
#         self.count_input.insert(0, "5") 

#         # 按钮
#         self.start_btn = tk.Button(
#             root, 
#             text="开始识别并下载", 
#             font=("Arial", 11), 
#             bg="#4CAF50", 
#             fg="white", 
#             command=self.start_crawl_thread
#         )
#         self.start_btn.pack(pady=10)

#         # 日志输出框
#         tk.Label(root, text="运行日志:", font=("Arial", 10)).pack(anchor="w", padx=15)
#         self.log_text = scrolledtext.ScrolledText(root, width=72, height=16, font=("Consolas", 9))
#         self.log_text.pack(padx=15, pady=5)

#         self.downloaded_count = 0
#         self.max_count = 5

#     def log(self, message):
#         """向界面打印日志"""
#         self.log_text.insert(tk.END, message + "\n")
#         self.log_text.see(tk.END)

#     def start_crawl_thread(self):
#         url = self.url_input.get().strip()
#         limit_str = self.count_input.get().strip()
        
#         if not url:
#             messagebox.showwarning("警告", "请输入有效的网址！")
#             return
        
#         try:
#             self.max_count = int(limit_str)
#             if self.max_count <= 0:
#                 raise ValueError
#         except ValueError:
#             messagebox.showwarning("警告", "下载数量必须是大于 0 的整数！")
#             return

#         self.start_btn.config(state=tk.DISABLED)
#         self.log_text.delete(1.0, tk.END)
#         self.downloaded_count = 0 

#         thread = threading.Thread(target=self.crawl_task, args=(url,))
#         thread.daemon = True  
#         thread.start()

#     def crawl_task(self, base_url):
#         self.log(f"开始任务，目标上限: {self.max_count} 张图片")
#         self.log(f"正在分析主页: {base_url}")
#         try:
#             response = requests.get(base_url, headers=HEADERS, timeout=10)
#             response.encoding = response.apparent_encoding
#             if response.status_code != 200:
#                 self.log(f"错误: 无法访问该网站 (状态码: {response.status_code})")
#                 return

#             soup = BeautifulSoup(response.text, "lxml")
#             download_dir = "./downloaded_images"
#             os.makedirs(download_dir, exist_ok=True)

#             if "10wallpaper.com" in base_url:
#                 self.handle_10wallpaper(soup, base_url, download_dir)
#             elif "bing.wdbyte.com" in base_url:
#                 self.handle_bing_wdbyte(soup, base_url, download_dir)
#             # elif "zedge.net" in base_url:
#             #     self.handle_zedge(base_url, download_dir)
#             elif "wallpapercave.com" in base_url:
#                 self.handle_wallpapercave(soup, base_url, download_dir)
#             elif "simpledesktops.com" in base_url:
#                 self.handle_simpledesktops(soup, base_url, download_dir)
#             elif "alphacoders.com" in base_url:
#                 self.handle_alphacoders(soup, base_url, download_dir)
#             else:
#                 self.log("暂未适配该网站的特异性规则，尝试通用兜底解析...")
#                 self.handle_generic(soup, base_url, download_dir)

#             if self.downloaded_count >= self.max_count:
#                 self.log(f"\n【提示】已达到设定的下载上限 ({self.max_count}张)，任务提前结束。")
#             else:
#                 self.log(f"\n任务结束！共成功下载了 {self.downloaded_count} 张图片。")
                
#         except Exception as e:
#             self.log(f"发生异常: {str(e)}")
#         finally:
#             self.start_btn.config(state=tk.NORMAL)

#     # --- 网站 1: 10wallpaper 专属解析规则 ---
#     def handle_10wallpaper(self, soup, base_url, download_dir):
#         self.log("进入 10wallpaper 解析模式...")
#         links = soup.find_all("a", href=re.compile(r"/view/.*\.html"))
#         detail_urls = list(set([urljoin(base_url, l["href"]) for l in links]))
#         self.log(f"发现 {len(detail_urls)} 个图片详情页...")

#         for idx, detail_url in enumerate(detail_urls, 1):
#             if self.downloaded_count >= self.max_count:
#                 break
#             try:
#                 self.log(f"正在进入详情页 [{idx}]: {detail_url}")
#                 res = requests.get(detail_url, headers=HEADERS, timeout=10)
#                 detail_soup = BeautifulSoup(res.text, "lxml")

#                 main_pic_div = detail_soup.find(id="main-pic")
#                 if main_pic_div and main_pic_div.find("img"):
#                     img_src = main_pic_div.find("img")["src"]
#                     img_url = urljoin(base_url, img_src)
#                     self.download_file(img_url, download_dir)
#                 else:
#                     self.log("  --> 未能在详情页找到高清图标签")
#             except Exception as e:
#                 self.log(f"  --> 详情页解析失败: {e}")

#     # --- 网站 2: bing.wdbyte 专属解析规则 ---
#     def handle_bing_wdbyte(self, soup, base_url, download_dir):
#         self.log("进入 必应壁纸(wdbyte) 解析模式...")
#         links = soup.find_all("a", href=re.compile(r"day/\d+/.*\.html"))
#         detail_urls = list(set([urljoin(base_url, l["href"]) for l in links]))
#         self.log(f"发现 {len(detail_urls)} 个必应详情页...")

#         for idx, detail_url in enumerate(detail_urls, 1):
#             if self.downloaded_count >= self.max_count:
#                 break
#             try:
#                 self.log(f"正在进入详情页 [{idx}]: {detail_url}")
#                 res = requests.get(detail_url, headers=HEADERS, timeout=10)
#                 detail_soup = BeautifulSoup(res.text, "lxml")

#                 target_a = detail_soup.find("a", string=re.compile(r"4K|1080P"))
#                 if not target_a:
#                     target_a = detail_soup.find("a", href=re.compile(r"UHD"))

#                 if target_a and target_a.get("href"):
#                     img_url = urljoin(base_url, target_a["href"])
#                     self.download_file(img_url, download_dir)
#                 else:
#                     self.log("  --> 未找到4K或1080P下载链接")
#             except Exception as e:
#                 self.log(f"  --> 详情页解析失败: {e}")

#     # # --- 网站 3: Zedge 专属解析规则 (免翻墙API升级版) ---
#     # def handle_zedge(self, base_url, download_dir):
#     #     self.log("进入 Zedge 壁纸免翻墙解析模式...")
        
#     #     # 1. 提取 ID
#     #     match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', base_url)
        
#     #     if match:
#     #         item_id = match.group(1)
#     #         self.log(f"成功提取壁纸 ID: {item_id}")
#     #         self.log("正在通过 Zedge 备用 API 获取直链...")
            
#     #         # 2. 访问 Zedge 的公开数据网关 API
#     #         api_url = f"https://rest-api.zedge.net/v3/items/wallpaper/{item_id}"
            
#     #         try:
#     #             # 请求 API 拿到 JSON 数据
#     #             res = requests.get(api_url, headers=HEADERS, timeout=10)
#     #             if res.status_code == 200:
#     #                 data = res.json()
                    
#     #                 # 3. 从返回的 JSON 结构中精准提取 meta 里的下载链接
#     #                 # 优先取大图（lm 规格或直接 meta 里的 url）
#     #                 img_url = data.get('meta', {}).get('url')
                    
#     #                 if not img_url:
#     #                     # 备用提取：如果 meta 里没有，尝试提取 contentUrl
#     #                     img_url = data.get('contentUrl')
                        
#     #                 if img_url:
#     #                     self.log(f"成功绕过封锁，捕获原图直链!")
#     #                     # 4. 提交给下载器
#     #                     self.download_file(img_url, download_dir)
#     #                 else:
#     #                     self.log("  --> 错误: 成功解析了 API，但未在数据中找到图片直链。")
#     #             else:
#     #                 self.log(f"  --> API 请求失败 (状态码: {res.status_code})，可能该图片已被下架或需要权限。")
#     #         except Exception as e:
#     #             self.log(f"  --> 调用备用 API 出错: {e}")
#     #     else:
#     #         self.log("错误: 无法从该网址中解析出有效的 Zedge 壁纸 ID！")
#     #     self.log("进入 Zedge 壁纸解析模式...")
        
#     #     # 1. 使用正则表达式从网址中提取出 36 位的 UUID (图片ID)
#     #     match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', base_url)
        
#     #     if match:
#     #         item_id = match.group(1)
#     #         self.log(f"成功提取壁纸 ID: {item_id}")
            
#     #         # 2. 直接拼接 Zedge 的超清原图 CDN 真实下载链接
#     #         img_url = f"https://fsa.zgedge.com/v3/wallpaper/lm/{item_id}?format=jpeg"
            
#     #         # 3. 提交下载
#     #         self.download_file(img_url, download_dir)
#     #     else:
#     #         self.log("错误: 无法从该网址中解析出有效的 Zedge 壁纸 ID！")

#     # --- 网站 4: WallpaperCave 专属解析规则 ---
#     def handle_wallpapercave(self, soup, base_url, download_dir):
#         self.log("进入 WallpaperCave 壁纸解析模式...")
        
#         # 1. 寻找页面中所有走向详情页的链接，链接格式通常是 /w/xxxx
#         links = soup.find_all("a", href=re.compile(r"^/w/"))
#         detail_urls = list(set([urljoin(base_url, l["href"]) for l in links]))
#         self.log(f"发现 {len(detail_urls)} 个壁纸详情页...")

#         for idx, detail_url in enumerate(detail_urls, 1):
#             # 每次循环前检查是否达到下载上限
#             if self.downloaded_count >= self.max_count:
#                 break

#             try:
#                 self.log(f"正在进入详情页 [{idx}]: {detail_url}")
#                 res = requests.get(detail_url, headers=HEADERS, timeout=10)
#                 detail_soup = BeautifulSoup(res.text, "lxml")

#                 # 2. 定位下载按钮。该站点的下载按钮通常有 id="download" 属性
#                 download_btn = detail_soup.find("a", id="download")
                
#                 # 备用方案：如果没找到 id="download"，找文本含有 "Download" 且指向 /download/ 的链接
#                 if not download_btn:
#                     download_btn = detail_soup.find("a", href=re.compile(r"/download/"))

#                 if download_btn and download_btn.get("href"):
#                     img_url = urljoin(base_url, download_btn["href"])
#                     self.log(f"  --> 成功捕获高清大图直链，开始下载...")
#                     self.download_file(img_url, download_dir)
#                 else:
#                     self.log("  --> 未能在详情页找到高清图下载按钮")
                    
#             except Exception as e:
#                 self.log(f"  --> 详情页解析失败: {e}")

#     # --- 网站 5: SimpleDesktops 专属解析规则 ---
#     def handle_simpledesktops(self, soup, base_url, download_dir):
#         self.log("进入 SimpleDesktops 极简壁纸解析模式...")
        
#         # 1. 找到所有包含 uploads/desktops 路径的缩略图标签
#         imgs = soup.find_all("img", src=re.compile(r"uploads/desktops"))
#         self.log(f"页面上一共发现 {len(imgs)} 张壁纸卡片，开始逆向还原高清图...")

#         for idx, img in enumerate(imgs, 1):
#             if self.downloaded_count >= self.max_count:
#                 break

#             thumb_src = img.get("src")
#             if not thumb_src:
#                 continue

#             # 2. 核心逆向算法：利用正则表达式切除 .png 或 .jpg 后面的缩略图尺寸后缀
#             # 匹配到类似 .png.295x184_q100.png 时，只保留到前面的 .png
#             original_match = re.search(r"(.*?\.(?:png|jpg|jpeg|webp))", thumb_src, re.IGNORECASE)
            
#             if original_match:
#                 img_url = original_match.group(1)
                
#                 # 3. 规范化处理：将 http 强转为 https，确保下载链接稳定
#                 if img_url.startswith("http://"):
#                     img_url = img_url.replace("http://", "https://", 1)
#                 elif not img_url.startswith("http"):
#                     img_url = urljoin(base_url, img_url)

#                 self.log(f"成功逆向还原第 [{idx}] 张原图!")
#                 self.download_file(img_url, download_dir)
#             else:
#                 self.log(f"  --> 无法解析该图的源地址: {thumb_src}")

#     # --- 网站 6: AlphaCoders 专属解析规则 ---
#     def handle_alphacoders(self, soup, base_url, download_dir):
#         self.log("进入 AlphaCoders (Wallpaper Abyss) 顶级壁纸解析模式...")
        
#         # 1. 寻找页面中所有走向详情页的链接，链接格式通常是 /wallpaper/xxxx
#         links = soup.find_all("a", href=re.compile(r"/wallpaper/\d+"))
        
#         # 去重并补全绝对路径
#         detail_urls = list(set([urljoin(base_url, l["href"]) for l in links]))
#         self.log(f"发现 {len(detail_urls)} 个壁纸详情页，由于该站有严密的反爬限制，将启用微秒级限速保护...")

#         for idx, detail_url in enumerate(detail_urls, 1):
#             if self.downloaded_count >= self.max_count:
#                 break

#             try:
#                 self.log(f"正在进入详情页 [{idx}]: {detail_url}")
                
#                 # 针对 AlphaCoders 定制伪装请求头，带上 Referer
#                 custom_headers = HEADERS.copy()
#                 custom_headers["Referer"] = base_url
                
#                 # 请求详情页
#                 res = requests.get(detail_url, headers=custom_headers, timeout=10)
#                 if res.status_code == 403:
#                     self.log("  --> 糟糕，触发了网站的防爬拦截(403)，尝试跳过这一张...")
#                     continue
                    
#                 detail_soup = BeautifulSoup(res.text, "lxml")

#                 # 2. 定位大图：通常在 class="main-wallpaper" 的 img 标签中
#                 img_tag = detail_soup.find("img", class_="main-wallpaper")
                
#                 if img_tag:
#                     # 优先取 src，有些页面可能是动态加载的则取 data-src
#                     img_url = img_tag.get("src") or img_tag.get("data-src")
                    
#                     if img_url:
#                         self.log(f"  --> 成功穿透加密，捕获超清大图直链!")
#                         self.download_file(img_url, download_dir)
#                 else:
#                     self.log("  --> 未能在详情页找到高清图主标签")
                
#                 # 3. 策略性限速：随机等待 1 到 2.5 秒，防止频繁请求被封 IP
#                 if self.downloaded_count < self.max_count:
#                     sleep_time = random.uniform(1.0, 2.5)
#                     time.sleep(sleep_time)

#             except Exception as e:
#                 self.log(f"  --> 详情页解析失败: {e}")

#     # --- 通用兜底规则 ---
#     def handle_generic(self, soup, base_url, download_dir):
#         imgs = soup.find_all("img")
#         self.log(f"共发现 {len(imgs)} 张常规图片...")
#         for img in imgs:
#             if self.downloaded_count >= self.max_count:
#                 break
#             src = img.get("src") or img.get("data-src")
#             if src:
#                 self.download_file(urljoin(base_url, src), download_dir)

#     # --- 文件下载核心函数 (修正文件名逻辑) ---
#     def download_file(self, url, folder):
#         if self.downloaded_count >= self.max_count:
#             return

#         try:
#             filename = ""
#             parsed_url = urlparse(url)
#             query_params = parse_qs(parsed_url.query)
            
#             if 'id' in query_params:
#                 id_val = query_params['id'][0] 
#                 filename = id_val.replace("OHR.", "") 
            
#             if not filename:
#                 filename = url.split("/")[-1].split("?")[0]
            
#             if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp")):
#                 filename += ".jpg"

#             filepath = os.path.join(folder, filename)

#             if os.path.exists(filepath):
#                 self.log(f"  --> 已经下载过该图片，跳过: {filename}")
#                 return

#             r = requests.get(url, headers=HEADERS, stream=True, timeout=15)
#             if r.status_code == 200:
#                 with open(filepath, "wb") as f:
#                     for chunk in r.iter_content(chunk_size=8192):
#                         f.write(chunk)
                
#                 self.downloaded_count += 1
#                 self.log(f"  --> 下载成功 [进度: {self.downloaded_count}/{self.max_count}]: {filename}")
#             else:
#                 self.log(f"  --> 下载失败 (状态码: {r.status_code})")
#         except Exception as e:
#             self.log(f"  --> 下载出错: {e}")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ImageSpiderGUI(root)
#     root.mainloop()

import os
import re
import sys
import time
import random
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import subprocess  # <-- 新增：用于执行系统安装/卸载命令
import atexit      # <-- 新增：用于监听脚本关闭事件

# --- 全局自动清理注册 ---
def uninstall_drission_page():
    """临终遗嘱：当检测到程序关闭时，彻底卸载临时安装的库"""
    try:
        # 再次静默检查，防止没安装也去跑卸载命令
        __import__('drission_page')
        print("[系统自动清理] 检测到软件正在关闭，正在为您卸载临时组件 DrissionPage...")
        # -y 参数代表自动同意，无需用户在后台敲 Y 确认
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "DrissionPage", "-y"], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[系统自动清理] 卸载完成，您的电脑已恢复纯净状态。")
    except ImportError:
        pass

# 告诉操作系统：不管这脚本怎么死的（正常退出或点X关掉），死前必须执行上面这个卸载函数
atexit.register(uninstall_drission_page)

# ==========================================
# 核心配置：终极伪装浏览器请求头（兼容所有网站）
# ==========================================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

class ImageSpiderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("万能智能高清图片下载器 (多站合一版)")
        self.root.geometry("620x520")

        # 网址输入框
        tk.Label(root, text="请输入网址:", font=("Arial", 11)).pack(anchor="w", padx=15, pady=5)
        self.url_input = tk.Entry(root, font=("Arial", 11), width=65)
        self.url_input.pack(padx=15, pady=5)
        self.url_input.insert(0, "https://bing.wdbyte.com/zh-cn/")

        # 数量控制区域
        count_frame = tk.Frame(root)
        count_frame.pack(anchor="w", padx=15, pady=5)
        
        tk.Label(count_frame, text="设置下载数量 (张):", font=("Arial", 11)).pack(side=tk.LEFT)
        self.count_input = tk.Entry(count_frame, font=("Arial", 11), width=10)
        self.count_input.pack(side=tk.LEFT, padx=10)
        self.count_input.insert(0, "5") 

        # 按钮
        self.start_btn = tk.Button(
            root, 
            text="开始识别并下载", 
            font=("Arial", 11), 
            bg="#4CAF50", 
            fg="white", 
            command=self.start_crawl_thread
        )
        self.start_btn.pack(pady=10)

        # 日志输出框
        tk.Label(root, text="运行日志:", font=("Arial", 10)).pack(anchor="w", padx=15)
        self.log_text = scrolledtext.ScrolledText(root, width=72, height=16, font=("Consolas", 9))
        self.log_text.pack(padx=15, pady=5)

        self.downloaded_count = 0
        self.max_count = 5

    def log(self, message):
        """向界面打印日志"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_crawl_thread(self):
        url = self.url_input.get().strip()
        limit_str = self.count_input.get().strip()
        
        if not url:
            messagebox.showwarning("警告", "请输入有效的网址！")
            return
        
        try:
            self.max_count = int(limit_str)
            if self.max_count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("警告", "下载数量必须是大于 0 的整数！")
            return

        self.start_btn.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        self.downloaded_count = 0 

        thread = threading.Thread(target=self.crawl_task, args=(url,))
        thread.daemon = True  
        thread.start()

    # def crawl_task(self, base_url):
    #     self.log(f"开始任务，目标上限: {self.max_count} 张图片")
    #     self.log(f"正在分析主页: {base_url}")
    #     try:
    #         # 统一采用宽松的 25 秒超时，确保海外站点不轻易卡死
    #         response = requests.get(base_url, headers=HEADERS, timeout=25)
    #         response.encoding = response.apparent_encoding
    #         if response.status_code != 200:
    #             self.log(f"错误: 无法访问该网站 (状态码: {response.status_code})")
    #             return

    #         soup = BeautifulSoup(response.text, "lxml")
    #         download_dir = "./downloaded_images"
    #         os.makedirs(download_dir, exist_ok=True)

    #         # ==========================================
    #         # 智能路由分拣中心：根据网址进不同生产线
    #         # ==========================================
    #         if "10wallpaper.com" in base_url:
    #             self.handle_10wallpaper(soup, base_url, download_dir)
    #         elif "bing.wdbyte.com" in base_url:
    #             self.handle_bing_wdbyte(soup, base_url, download_dir)
    #         elif "zedge.net" in base_url:
    #             self.handle_zedge(base_url, download_dir)
    #         elif "wallpapercave.com" in base_url:
    #             self.handle_wallpapercave(soup, base_url, download_dir)
    #         elif "simpledesktops.com" in base_url:
    #             self.handle_simpledesktops(soup, base_url, download_dir)
    #         elif "alphacoders.com" in base_url:
    #             self.handle_alphacoders(soup, base_url, download_dir)
    #         elif "konachan.net" in base_url:
    #             self.handle_konachan(base_url, download_dir)
    #         else:
    #             self.log("暂未适配该网站的特异性规则，尝试通用兜底解析...")
    #             self.handle_generic(soup, base_url, download_dir)

    #         if self.downloaded_count >= self.max_count:
    #             self.log(f"\n【提示】已达到设定的下载上限 ({self.max_count}张)，任务提前结束。")
    #         else:
    #             self.log(f"\n任务结束！共成功下载了 {self.downloaded_count} 张图片。")
                
    #     except Exception as e:
    #         self.log(f"发生异常: {str(e)}")
    #     finally:
    #         self.start_btn.config(state=tk.NORMAL)

    def crawl_task(self, base_url):
        self.log(f"开始任务，目标上限: {self.max_count} 张图片")
        
        # 建立通用的下载目录
        download_dir = "./downloaded_images"
        os.makedirs(download_dir, exist_ok=True)

        # ========================================================
        # 核心修复：将路由判断前置！如果是 Konachan，彻底绕过 requests.get
        # ========================================================
        if "konachan.net" in base_url or "konachan.moe" in base_url:
            try:
                self.handle_konachan(base_url, download_dir)
            except Exception as e:
                self.log(f"发生异常: {str(e)}")
            finally:
                # 无论成功失败，恢复按钮状态
                self.start_btn.config(state=tk.NORMAL)
                if self.downloaded_count >= self.max_count:
                    self.log(f"\n【提示】已达到设定的下载上限 ({self.max_count}张)，任务提前结束。")
                else:
                    self.log(f"\n任务结束！共成功下载了 {self.downloaded_count} 张图片。")
            return # 执行完 Konachan 专属逻辑后直接退出，不走下面的常规请求

        # ========================================================
        # 其他无需特殊处理主页的网站，继续走常规的 requests 静态请求
        # ========================================================
        self.log(f"正在分析主页: {base_url}")
        try:
            response = requests.get(base_url, headers=HEADERS, timeout=25)
            response.encoding = response.apparent_encoding
            if response.status_code != 200:
                self.log(f"错误: 无法访问该网站 (状态码: {response.status_code})")
                return

            soup = BeautifulSoup(response.text, "lxml")

            if "10wallpaper.com" in base_url:
                self.handle_10wallpaper(soup, base_url, download_dir)
            elif "bing.wdbyte.com" in base_url:
                self.handle_bing_wdbyte(soup, base_url, download_dir)
            elif "zedge.net" in base_url:
                self.handle_zedge(base_url, download_dir)
            elif "wallpapercave.com" in base_url:
                self.handle_wallpapercave(soup, base_url, download_dir)
            elif "simpledesktops.com" in base_url:
                self.handle_simpledesktops(soup, base_url, download_dir)
            elif "alphacoders.com" in base_url:
                self.handle_alphacoders(soup, base_url, download_dir)
            else:
                self.log("暂未适配该网站的特异性规则，尝试通用兜底解析...")
                self.handle_generic(soup, base_url, download_dir)

            if self.downloaded_count >= self.max_count:
                self.log(f"\n【提示】已达到设定的下载上限 ({self.max_count}张)，任务提前结束。")
            else:
                self.log(f"\n任务结束！共成功下载了 {self.downloaded_count} 张图片。")
                
        except Exception as e:
            self.log(f"发生异常: {str(e)}")
        finally:
            self.start_btn.config(state=tk.NORMAL)

    # --- 网站 1: 10wallpaper 专属解析规则 ---
    def handle_10wallpaper(self, soup, base_url, download_dir):
        self.log("进入 10wallpaper 解析模式...")
        links = soup.find_all("a", href=re.compile(r"/view/.*\.html"))
        detail_urls = list(set([urljoin(base_url, l["href"]) for l in links]))
        self.log(f"发现 {len(detail_urls)} 个图片详情页...")

        for idx, detail_url in enumerate(detail_urls, 1):
            if self.downloaded_count >= self.max_count:
                break
            try:
                self.log(f"正在进入详情页 [{idx}]: {detail_url}")
                res = requests.get(detail_url, headers=HEADERS, timeout=25)
                detail_soup = BeautifulSoup(res.text, "lxml")

                main_pic_div = detail_soup.find(id="main-pic")
                if main_pic_div and main_pic_div.find("img"):
                    img_src = main_pic_div.find("img")["src"]
                    img_url = urljoin(base_url, img_src)
                    self.download_file(img_url, download_dir)
                else:
                    self.log("  --> 未能在详情页找到高清图标签")
            except Exception as e:
                self.log(f"  --> 详情页解析失败: {e}")

    # --- 网站 2: bing.wdbyte 专属解析规则 ---
    def handle_bing_wdbyte(self, soup, base_url, download_dir):
        self.log("进入 必应壁纸(wdbyte) 解析模式...")
        links = soup.find_all("a", href=re.compile(r"day/\d+/.*\.html"))
        detail_urls = list(set([urljoin(base_url, l["href"]) for l in links]))
        self.log(f"发现 {len(detail_urls)} 个必应详情页...")

        for idx, detail_url in enumerate(detail_urls, 1):
            if self.downloaded_count >= self.max_count:
                break
            try:
                self.log(f"正在进入详情页 [{idx}]: {detail_url}")
                res = requests.get(detail_url, headers=HEADERS, timeout=25)
                detail_soup = BeautifulSoup(res.text, "lxml")

                target_a = detail_soup.find("a", string=re.compile(r"4K|1080P"))
                if not target_a:
                    target_a = detail_soup.find("a", href=re.compile(r"UHD"))

                if target_a and target_a.get("href"):
                    img_url = urljoin(base_url, target_a["href"])
                    self.download_file(img_url, download_dir)
                else:
                    self.log("  --> 未找到4K或1080P下载链接")
            except Exception as e:
                self.log(f"  --> 详情页解析失败: {e}")

    # --- 网站 3: Zedge 专属解析规则 (Hosts直连版本) ---
    def handle_zedge(self, base_url, download_dir):
        self.log("进入 Zedge 壁纸 Hosts 直连解析模式...")
        match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', base_url)
        if match:
            item_id = match.group(1)
            self.log(f"成功提取壁纸 ID: {item_id}")
            api_url = f"https://rest-api.zedge.net/v3/items/wallpaper/{item_id}"
            self.log("正在请求中央数据接口...")
            try:
                res = requests.get(api_url, headers=HEADERS, timeout=25)
                if res.status_code == 200:
                    data = res.json()
                    img_url = data.get('meta', {}).get('url') or data.get('contentUrl')
                    if img_url:
                        self.log("成功获取到大图分发直链，开始下载...")
                        self.download_file(img_url, download_dir)
                        return
            except Exception as e:
                self.log(f"  --> 接口尝试失败: {e}，正在尝试第二预案...")

            self.log("执行预案：直接向静态服务器申请超清原图...")
            backup_url = f"https://fsa.zgedge.com/v3/wallpaper/lm/{item_id}?format=jpeg"
            self.download_file(backup_url, download_dir)
        else:
            self.log("错误: 无法从该网址中解析出有效的 Zedge 壁纸 ID！")

    # --- 网站 4: WallpaperCave 专属解析规则 ---
    def handle_wallpapercave(self, soup, base_url, download_dir):
        self.log("进入 WallpaperCave 壁纸解析模式...")
        links = soup.find_all("a", href=re.compile(r"^/w/"))
        detail_urls = list(set([urljoin(base_url, l["href"]) for l in links]))
        self.log(f"发现 {len(detail_urls)} 个壁纸详情页...")

        for idx, detail_url in enumerate(detail_urls, 1):
            if self.downloaded_count >= self.max_count:
                break
            try:
                self.log(f"正在进入详情页 [{idx}]: {detail_url}")
                res = requests.get(detail_url, headers=HEADERS, timeout=25)
                detail_soup = BeautifulSoup(res.text, "lxml")

                download_btn = detail_soup.find("a", id="download")
                if not download_btn:
                    download_btn = detail_soup.find("a", href=re.compile(r"/download/"))

                if download_btn and download_btn.get("href"):
                    img_url = urljoin(base_url, download_btn["href"])
                    self.download_file(img_url, download_dir)
                else:
                    self.log("  --> 未能在详情页找到高清图下载按钮")
            except Exception as e:
                self.log(f"  --> 详情页解析失败: {e}")

    # --- 网站 5: SimpleDesktops 专属解析规则 ---
    def handle_simpledesktops(self, soup, base_url, download_dir):
        self.log("进入 SimpleDesktops 极简壁纸解析模式...")
        imgs = soup.find_all("img", src=re.compile(r"uploads/desktops"))
        self.log(f"页面上一共发现 {len(imgs)} 张壁纸卡片，开始逆向还原高清图...")

        for idx, img in enumerate(imgs, 1):
            if self.downloaded_count >= self.max_count:
                break
            thumb_src = img.get("src")
            if not thumb_src:
                continue

            original_match = re.search(r"(.*?\.(?:png|jpg|jpeg|webp))", thumb_src, re.IGNORECASE)
            if original_match:
                img_url = original_match.group(1)
                if img_url.startswith("http://"):
                    img_url = img_url.replace("http://", "https://", 1)
                elif not img_url.startswith("http"):
                    img_url = urljoin(base_url, img_url)

                self.log(f"成功逆向还原第 [{idx}] 张原图!")
                self.download_file(img_url, download_dir)
            else:
                self.log(f"  --> 无法解析该图的源地址: {thumb_src}")

    # --- 网站 6: AlphaCoders 专属解析规则 (标签逆向+规范命名版) ---
    def handle_alphacoders(self, soup, base_url, download_dir):
        self.log("进入 AlphaCoders (标签深度逆向) 解析模式...")
        
        # 1. 极其精准地只抓取网页上 class 为 thumb 的壁纸标签
        img_tags = soup.find_all("img", class_="thumb")
        self.log(f"成功锁定页面上 {len(img_tags)} 张目标壁纸标签，开始强力逆向高清直链...")

        for idx, tag in enumerate(img_tags, 1):
            if self.downloaded_count >= self.max_count:
                break

            # 2. 提取缩略图地址 (如: https://images.alphacoders.com/605/thumbbig-605592.webp)
            thumb_src = tag.get("src") or tag.get("data-src")
            if not thumb_src:
                continue

            # 3. 核心算法：提取图片的核心数字 ID (如: 605592)
            id_match = re.search(r'thumbbig-(\d+)\.', thumb_src)
            if id_match:
                img_id = id_match.group(1)
                
                # 4. 逆向生成高清原图直链 (把 thumbbig- 抹掉，后缀换成大图常用的 .jpg)
                # 变成: https://images.alphacoders.com/605/605592.jpg
                high_res_url = thumb_src.replace(f"thumbbig-{img_id}.webp", f"{img_id}.jpg")
                
                # 5. 严格按照要求，将本地保存的文件名格式规范化为 thumbbig-XXXXXX.jpg
                target_filename = f"thumbbig-{img_id}.jpg"
                
                self.log(f"发现第 [{self.downloaded_count + 1}] 张壁纸 [ID: {img_id}]")
                
                # 6. 传入专属下载逻辑
                self.download_alphacoders_exact(high_res_url, download_dir, target_filename, thumb_src)
            else:
                self.log(f"  --> 无法解析该标签的图片ID: {thumb_src}")

    # --- 网站 7: Konachan 专属解析规则 (带环境动态刷新破盾版) ---
    def handle_konachan(self, base_url, download_dir):
        self.log("\n==============================================")
        self.log("[检查环境] 正在扫描本地 Python 环境...")
        
        need_uninstall_later = False
        
        # 1. 环境自检与动态刷新
        try:
            # 尝试导入
            __import__('DrissionPage')
            self.log("[检查环境] 结果：本地已满足运行条件，直接启动。")
        except ImportError:
            self.log("[检查环境] 结果：本地未检测到破盾核心组件。")
            self.log("[环境部署] 正在联网为您静默安装 DrissionPage，请稍候...")
            
            try:
                # 执行 pip 安装
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "DrissionPage"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    self.log("[环境部署] 【成功】组件动态安装成功！")
                    self.log("[环境部署] 正在强行刷新 Python 运行时环境表...")
                    
                    # 核心修复：强行刷新导入引擎的缓存，让当前进程立刻认出新安装的库！
                    import importlib
                    importlib.invalidate_caches()
                    
                    need_uninstall_later = True 
                else:
                    self.log(f"[环境部署] 【失败】安装返回错误码: {result.returncode}")
                    return
            except Exception as e:
                self.log(f"[环境部署] 【崩溃】调用安装引发异常: {e}")
                return

        # 2. 正常执行真实浏览器破盾业务
        self.log("[业务启动] 正在召唤 Chromium 真实浏览器内核...")
        try:
            # 注意：官方标准库名大小写为 DrissionPage
            from DrissionPage import ChromiumPage, ChromiumOptions
            
            self.log("[浏览器伪装] 正在初始化无痕防检测浏览器配置...")
            co = ChromiumOptions()
            co.set_argument('--headless') # 静默无头模式
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-gpu')
            
            page = ChromiumPage(co)
            
            self.log(f"[安全穿越] 真实浏览器正在强冲 Cloudflare 防线: {base_url}")
            page.get(base_url)
            
            page.wait.load_start()
            time.sleep(3) # 耐心等待安全盾自动验证并放行
            
            html_source = page.html
            page.quit() # 浏览器使命结束，及时关闭释放内存
            self.log("[安全穿越] 【大获全胜】成功拿到过盾后的干净网页源码！")
            
            # 3. 开始解析与下载
            secure_soup = BeautifulSoup(html_source, "lxml")
            links = secure_soup.find_all("a", class_="thumb")
            if not links:
                links = secure_soup.find_all("a", href=re.compile(r"/post/show/\d+"))
                
            detail_urls = list(set([urljoin(base_url, l["href"]) for l in links]))
            self.log(f"[数据提取] 成功在主页捕获到 {len(detail_urls)} 个高清壁纸详情页...")

            for idx, detail_url in enumerate(detail_urls, 1):
                if self.downloaded_count >= self.max_count:
                    break
                
                try:
                    img_id_match = re.search(r'/show/(\d+)', detail_url)
                    img_id = img_id_match.group(1) if img_id_match else str(random.randint(100000, 999999))
                    
                    self.log(f"[解析大图] 正在穿透第 [{idx}] 个详情页 [ID: {img_id}]...")
                    res = requests.get(detail_url, headers=HEADERS, timeout=15)
                    d_soup = BeautifulSoup(res.text, "lxml")
                    high_res_tag = d_soup.find("a", id="high-res") or d_soup.find("img", id="image")
                    
                    if high_res_tag:
                        img_url = high_res_tag.get("href") or high_res_tag.get("src")
                        if img_url.startswith("//"): img_url = "https:" + img_url
                        
                        ext = ".jpg"
                        if ".png" in img_url.lower(): ext = ".png"
                        target_filename = f"thumbbig-{img_id}{ext}"
                        
                        self.download_konachan_file(img_url, download_dir, target_filename)
                        time.sleep(1)
                    else:
                        self.log(f"  --> [警告] 第 [{idx}] 张图未解析到高清下载锚点")
                except Exception as e:
                    self.log(f"  --> [错误] 提取详情页失败: {e}")

        except Exception as e:
            self.log(f"[系统崩溃] 自动化流程发生未预料异常: {e}")
        finally:
            if need_uninstall_later:
                self.log("\n[温馨提示] 本次使用的 DrissionPage 库为临时部署。")
                self.log("[温馨提示] 当您关闭本下载器软件时，后台会自动帮您无痕卸载该组件。")
            self.log("==============================================\n")

    # 针对 IP 直连定制的穿透下载器
    def download_konachan_direct(self, url, folder, filename, resolved_ip):
        filepath = os.path.join(folder, filename)
        if os.path.exists(filepath):
            self.log(f"  --> 图片已存在，跳过: {filename}")
            return
        try:
            download_headers = HEADERS.copy()
            download_headers.update({"Host": "konachan.net"})
            
            r = requests.get(url, headers=download_headers, verify=False, stream=True, timeout=25)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.downloaded_count += 1
                self.log(f"  --> 【成功】壁纸无损保存为: {filename}")
            else:
                self.log(f"  --> 下载节点响应异常 (错误码: {r.status_code})")
        except Exception as e:
            self.log(f"  --> 建立下载流失败: {e}")
 
    # Konachan 专属精准下载器
    def download_konachan_file(self, url, folder, filename):
        filepath = os.path.join(folder, filename)
        if os.path.exists(filepath):
            self.log(f"  --> 该图已在硬盘中，自动跳过: {filename}")
            return
        try:
            r = requests.get(url, headers=HEADERS, stream=True, timeout=25)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.downloaded_count += 1
                self.log(f"  --> 【成功】超清原图已存为: {filename}")
            else:
                self.log(f"  --> 下载失败 (网络错误码: {r.status_code})")
        except Exception as e:
            self.log(f"  --> 建立图片下载连接失败: {e}")

    # 具备双保险的专属精确下载器
    def download_alphacoders_exact(self, url, folder, filename, fallback_url):
        filepath = os.path.join(folder, filename)
        if os.path.exists(filepath):
            self.log(f"  --> 已经下载过该图片，跳过: {filename}")
            return

        try:
            # 优先尝试下载超清 JPG 原图
            self.log(f"  --> 正在下载高清原图...")
            r = requests.get(url, headers=HEADERS, stream=True, timeout=15)
            
            # 如果原图不是 JPG 格式导致 404，自动尝试 PNG 后缀
            if r.status_code == 404:
                url = url.replace(".jpg", ".png")
                r = requests.get(url, headers=HEADERS, stream=True, timeout=15)
            
            # 如果原图真的被保护了或者找不到，降级下载网页上原本显示的那个高清缩略图(确保绝对不空手而归)
            if r.status_code != 200:
                self.log(f"  --> [提示] 原图直链未响应，启动无损降级，下载高精度缩略图...")
                url = fallback_url
                r = requests.get(url, headers=HEADERS, stream=True, timeout=15)

            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.downloaded_count += 1
                self.log(f"  --> 【成功】图片已存入: {filename}")
            else:
                self.log(f"  --> 下载失败 (错误码: {r.status_code})")
                
        except Exception as e:
            self.log(f"  --> 请求出错: {e}")

    # --- 通用兜底规则 ---
    def handle_generic(self, soup, base_url, download_dir):
        imgs = soup.find_all("img")
        self.log(f"共发现 {len(imgs)} 张常规图片...")
        for img in imgs:
            if self.downloaded_count >= self.max_count:
                break
            src = img.get("src") or img.get("data-src")
            if src:
                self.download_file(urljoin(base_url, src), download_dir)

    # --- 文件下载核心函数 (智能提取直链文件名) ---
    def download_file(self, url, folder):
        if self.downloaded_count >= self.max_count:
            return
        try:
            filename = ""
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if 'id' in query_params:
                id_val = query_params['id'][0] 
                filename = id_val.replace("OHR.", "") 
            
            if not filename:
                filename = url.split("/")[-1].split("?")[0]
            
            if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp")):
                filename += ".jpg"

            filepath = os.path.join(folder, filename)

            if os.path.exists(filepath):
                self.log(f"  --> 已经下载过该图片，跳过: {filename}")
                return

            r = requests.get(url, headers=HEADERS, stream=True, timeout=25)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.downloaded_count += 1
                self.log(f"  --> 下载成功 [进度: {self.downloaded_count}/{self.max_count}]: {filename}")
            else:
                self.log(f"  --> 下载失败 (状态码: {r.status_code})")
        except Exception as e:
            self.log(f"  --> 下载出错: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSpiderGUI(root)
    root.mainloop()