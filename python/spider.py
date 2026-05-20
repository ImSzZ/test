import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

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

class ImageSpider:
    """图片爬虫核心逻辑类"""
    
    def __init__(self, log_callback=None):
        """
        初始化爬虫
        :param log_callback: 日志回调函数，用于将日志输出到UI
        """
        self.log_callback = log_callback
        self.downloaded_count = 0
        self.max_count = 5
        
    def log(self, message):
        """输出日志"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def crawl(self, base_url, max_count):
        """
        开始爬取图片
        :param base_url: 目标网址
        :param max_count: 最大下载数量
        :return: 下载成功的图片数量
        """
        self.downloaded_count = 0
        self.max_count = max_count
        
        self.log(f"开始任务，目标上限: {self.max_count} 张图片")
        self.log(f"正在分析主页: {base_url}")
        
        try:
            # 统一采用宽松的 25 秒超时，确保海外站点不轻易卡死
            response = requests.get(base_url, headers=HEADERS, timeout=25)
            response.encoding = response.apparent_encoding
            if response.status_code != 200:
                self.log(f"错误: 无法访问该网站 (状态码: {response.status_code})")
                return 0

            soup = BeautifulSoup(response.text, "lxml")
            download_dir = "./downloaded_images"
            os.makedirs(download_dir, exist_ok=True)

            # ==========================================
            # 智能路由分拣中心：根据网址进不同生产线
            # ==========================================
            if "10wallpaper.com" in base_url:
                self.handle_10wallpaper(soup, base_url, download_dir)
            elif "bing.wdbyte.com" in base_url:
                self.handle_bing_wdbyte(soup, base_url, download_dir)
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
                
            return self.downloaded_count
            
        except Exception as e:
            self.log(f"发生异常: {str(e)}")
            return self.downloaded_count

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

    # --- 网站 3: WallpaperCave 专属解析规则 ---
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

    # --- 网站 4: SimpleDesktops 专属解析规则 ---
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

    # --- 网站 5: AlphaCoders 专属解析规则 ---
    def handle_alphacoders(self, soup, base_url, download_dir):
        self.log("进入 AlphaCoders (标签深度逆向) 解析模式...")
        
        img_tags = soup.find_all("img", class_="thumb")
        self.log(f"成功锁定页面上 {len(img_tags)} 张目标壁纸标签，开始强力逆向高清直链...")

        for idx, tag in enumerate(img_tags, 1):
            if self.downloaded_count >= self.max_count:
                break

            thumb_src = tag.get("src") or tag.get("data-src")
            if not thumb_src:
                continue

            id_match = re.search(r'thumbbig-(\d+)\.', thumb_src)
            if id_match:
                img_id = id_match.group(1)
                high_res_url = thumb_src.replace(f"thumbbig-{img_id}.webp", f"{img_id}.jpg")
                target_filename = f"thumbbig-{img_id}.jpg"
                
                self.log(f"发现第 [{self.downloaded_count + 1}] 张壁纸 [ID: {img_id}]")
                self.download_alphacoders_exact(high_res_url, download_dir, target_filename, thumb_src)
            else:
                self.log(f"  --> 无法解析该标签的图片ID: {thumb_src}")
    
    # 具备双保险的专属精确下载器
    def download_alphacoders_exact(self, url, folder, filename, fallback_url):
        filepath = os.path.join(folder, filename)
        if os.path.exists(filepath):
            self.log(f"  --> 已经下载过该图片，跳过: {filename}")
            return

        try:
            self.log(f"  --> 正在下载高清原图...")
            r = requests.get(url, headers=HEADERS, stream=True, timeout=15)
            
            if r.status_code == 404:
                url = url.replace(".jpg", ".png")
                r = requests.get(url, headers=HEADERS, stream=True, timeout=15)
            
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

    # --- 文件下载核心函数 ---
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
