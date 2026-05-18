# integrated_app.py

import requests
from bs4 import BeautifulSoup
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import urljoin
from PIL import Image, ImageTk
from io import BytesIO
import re


class WallhavenScraper:
    def __init__(self, base_url, search_keyword, save_dir='wallhaven_wallpapers'):
        self.base_url = base_url.rstrip('/')  # 移除末尾的斜杠
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
            img_tag = soup.select_one('img#wallpaper')
            if img_tag and img_tag.get('src'):
                return img_tag['src']
            img_tag = soup.select_one('img.wallpaper-img')
            if img_tag and img_tag.get('src'):
                return img_tag['src']
            return None
        except Exception as e:
            print(f"获取详情页 {detail_url} 失败: {e}")
            return None

    def download_image(self, img_url, file_name, callback=None):
        """下载并保存图片"""
        try:
            response = requests.get(img_url, headers=self.headers, timeout=15, stream=True)
            response.raise_for_status()
            file_path = os.path.join(self.save_dir, file_name)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            if callback:
                callback(file_name, True, None)
            return True
        except Exception as e:
            if callback:
                callback(file_name, False, str(e))
            return False

    def get_page_count(self):
        """获取搜索结果的总页数"""
        try:
            response = requests.get(self.search_url + '1', headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            last_page_link = soup.select('a[data-page]')
            if last_page_link:
                pages = [int(link.get('data-page')) for link in last_page_link if link.get('data-page')]
                if pages:
                    return max(pages)
            # 尝试另一种方式获取总页数
            page_info = soup.select('.pages')
            if page_info:
                text = page_info[0].get_text()
                numbers = re.findall(r'(\d+)', text)
                if len(numbers) >= 2:
                    return int(numbers[-1])
            return 1
        except:
            return 1


class ImageDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片下载器 - Wallhaven爬虫")
        self.root.geometry("1200x800")
        
        # 数据存储
        self.current_page = 1
        self.total_pages = 1
        self.current_images = []  # 存储当前页的图片信息 [(url, filename, preview_img), ...]
        self.checkboxes = []  # 存储复选框变量
        self.scraper = None
        self.is_loading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # 顶部框架 - 搜索设置
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        # 网址输入
        tk.Label(top_frame, text="输入壁纸网址:").pack(side=tk.LEFT, padx=5)
        self.keyword_URL = tk.Entry(top_frame, width=25)
        self.keyword_URL.pack(side=tk.LEFT, padx=5)
        self.keyword_URL.insert(0, "https://10wallpaper.com/")  # 设置默认网址  https://wallhaven.cc
        
        # 关键词输入
        tk.Label(top_frame, text="搜索关键词:").pack(side=tk.LEFT, padx=5)
        self.keyword_entry = tk.Entry(top_frame, width=20)
        self.keyword_entry.pack(side=tk.LEFT, padx=5)
        self.keyword_entry.insert(0, "landscape")

        # 搜索按钮
        self.search_btn = tk.Button(top_frame, text="搜索", command=self.search_images, 
                                     bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        self.search_btn.pack(side=tk.LEFT, padx=10)
        
        # 保存路径
        tk.Label(top_frame, text="保存路径:").pack(side=tk.LEFT, padx=5)
        self.path_var = tk.StringVar(value="./wallhaven_downloads")
        self.path_entry = tk.Entry(top_frame, textvariable=self.path_var, width=25)
        self.path_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="浏览...", command=self.select_path).pack(side=tk.LEFT, padx=2)
        
        # 全选/取消全选框架
        select_frame = tk.Frame(self.root)
        select_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.select_all_var = tk.BooleanVar()
        self.select_all_cb = tk.Checkbutton(select_frame, text="全选", variable=self.select_all_var,
                                             command=self.toggle_select_all)
        self.select_all_cb.pack(side=tk.LEFT, padx=5)
        
        self.selected_count_label = tk.Label(select_frame, text="已选择: 0 张")
        self.selected_count_label.pack(side=tk.LEFT, padx=10)
        
        # 下载按钮
        self.download_btn = tk.Button(select_frame, text="下载选中图片", command=self.download_selected,
                                       bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.download_btn.pack(side=tk.LEFT, padx=10)
        
        # 状态标签
        self.status_label = tk.Label(select_frame, text="就绪", fg="gray")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress.pack(pady=5)
        
        # 创建画布和滚动条用于显示图片网格
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 鼠标滚轮滚动
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        
        # 底部翻页框架
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.prev_btn = tk.Button(bottom_frame, text="◀ 上一页", command=self.prev_page, 
                                    state=tk.DISABLED, font=("Arial", 10))
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.page_label = tk.Label(bottom_frame, text="第 1 / 1 页", font=("Arial", 10))
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = tk.Button(bottom_frame, text="下一页 ▶", command=self.next_page,
                                    state=tk.DISABLED, font=("Arial", 10))
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.page_entry_label = tk.Label(bottom_frame, text="跳转到:")
        self.page_entry_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.page_entry = tk.Entry(bottom_frame, width=6)
        self.page_entry.pack(side=tk.LEFT, padx=5)
        
        self.go_btn = tk.Button(bottom_frame, text="GO", command=self.go_to_page, width=5)
        self.go_btn.pack(side=tk.LEFT, padx=5)
    
    def select_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
    
    def toggle_select_all(self):
        select_all = self.select_all_var.get()
        for var in self.checkboxes:
            var.set(select_all)
        self.update_selected_count()
    
    def update_selected_count(self):
        selected_count = sum(1 for var in self.checkboxes if var.get())
        self.selected_count_label.config(text=f"已选择: {selected_count} 张")
        
        # 更新全选复选框状态
        if selected_count == 0:
            self.select_all_var.set(False)
        elif selected_count == len(self.checkboxes) and len(self.checkboxes) > 0:
            self.select_all_var.set(True)
        else:
            self.select_all_var.set(False)
    
    def search_images(self):
        if self.is_loading:
            return
        
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning("警告", "请输入搜索关键词")
            return
        
        base_url = self.keyword_URL.get().strip()
        if not base_url:
            messagebox.showwarning("警告", "请输入壁纸网站地址")
            return
        
        save_dir = self.path_var.get()
        if not save_dir:
            save_dir = "./wallhaven_downloads"
            self.path_var.set(save_dir)
        
        # 清空当前显示
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.checkboxes.clear()
        self.current_images.clear()
        self.current_page = 1
        
        # 创建爬虫实例（传入base_url）
        self.scraper = WallhavenScraper(base_url, keyword, save_dir)
        
        # 获取总页数
        self.status_label.config(text="正在获取总页数...", fg="blue")
        self.root.update()
        
        # 在新线程中获取页数
        thread = threading.Thread(target=self.fetch_total_pages)
        thread.daemon = True
        thread.start()
    
    def fetch_total_pages(self):
        try:
            self.total_pages = self.scraper.get_page_count()
            self.root.after(0, self.load_page, 1)
        except Exception as e:
            self.root.after(0, self.show_error, f"获取页数失败: {e}")
    
    def load_page(self, page_num):
        if self.is_loading:
            return
        
        self.is_loading = True
        self.search_btn.config(state=tk.DISABLED)
        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.status_label.config(text=f"正在加载第 {page_num} 页...", fg="blue")
        self.progress['value'] = 0
        self.root.update()
        
        # 在新线程中加载页面
        thread = threading.Thread(target=self.load_page_thread, args=(page_num,))
        thread.daemon = True
        thread.start()
    
    def load_page_thread(self, page_num):
        try:
            current_page_url = f"{self.scraper.search_url}{page_num}"
            detail_urls = self.scraper.get_image_urls_from_page(current_page_url)
            
            if not detail_urls:
                self.root.after(0, self.show_error, f"第 {page_num} 页没有找到图片")
                self.root.after(0, self.loading_finished)
                return
            
            images_data = []
            total = len(detail_urls)
            
            for idx, detail_url in enumerate(detail_urls):
                img_url = self.scraper.get_download_url_from_detail(detail_url)
                if img_url:
                    # 获取图片扩展名
                    ext = img_url.split('.')[-1].split('?')[0]
                    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                        ext = 'jpg'
                    file_name = f"page{page_num}_{idx+1}.{ext}"
                    images_data.append({
                        'url': img_url,
                        'filename': file_name,
                        'preview_url': img_url  # 使用原图链接作为预览
                    })
                
                # 更新进度
                progress_value = (idx + 1) / total * 50
                self.root.after(0, self.update_progress, progress_value)
            
            self.root.after(0, self.display_images, images_data, page_num)
            self.root.after(0, self.loading_finished)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"加载失败: {e}")
            self.root.after(0, self.loading_finished)
    
    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()
    
    def display_images(self, images_data, page_num):
        # 清空之前的内容
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.checkboxes.clear()
        self.current_images = images_data
        
        if not images_data:
            tk.Label(self.scrollable_frame, text="没有找到图片", font=("Arial", 14), fg="gray").pack(pady=50)
            return
        
        # 创建网格布局 (每行4个)
        cols = 4
        for idx, img_data in enumerate(images_data):
            row = idx // cols
            col = idx % cols
            
            # 创建图片框架
            frame = tk.Frame(self.scrollable_frame, relief=tk.RAISED, bd=1)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # 复选框变量
            var = tk.BooleanVar()
            self.checkboxes.append(var)
            
            # 复选框
            cb = tk.Checkbutton(frame, variable=var, command=self.update_selected_count)
            cb.pack(anchor="nw", padx=2, pady=2)
            
            # 图片标签（先显示占位符）
            img_label = tk.Label(frame, text="加载中...", bg="gray", width=20, height=15)
            img_label.pack(padx=5, pady=5)
            
            # 文件名标签
            name_label = tk.Label(frame, text=img_data['filename'][:20], font=("Arial", 8), wraplength=150)
            name_label.pack(pady=2)
            
            # 在新线程中加载预览图
            thread = threading.Thread(target=self.load_preview_image, 
                                       args=(img_data['preview_url'], img_label))
            thread.daemon = True
            thread.start()
        
        # 设置网格列权重
        for i in range(cols):
            self.scrollable_frame.columnconfigure(i, weight=1)
        
        # 更新翻页按钮状态
        self.current_page = page_num
        self.page_label.config(text=f"第 {self.current_page} / {self.total_pages} 页")
        
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)
        
        self.progress['value'] = 100
        self.status_label.config(text=f"加载完成 - 共找到 {len(images_data)} 张图片", fg="green")
    
    def load_preview_image(self, url, label):
        """异步加载预览图"""
        try:
            response = requests.get(url, headers=self.scraper.headers, timeout=10, stream=True)
            response.raise_for_status()
            
            # 读取图片数据并缩放
            img_data = response.content
            image = Image.open(BytesIO(img_data))
            
            # 缩放图片以适应显示区域
            image.thumbnail((200, 150), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            
            # 在主线程中更新UI
            def update_label():
                label.config(image=photo, text="")
                label.image = photo  # 保持引用
            
            self.root.after(0, update_label)
            
        except Exception as e:
            def show_error():
                label.config(text="加载失败", bg="red")
            self.root.after(0, show_error)
    
    def loading_finished(self):
        self.is_loading = False
        self.search_btn.config(state=tk.NORMAL)
    
    def show_error(self, error_msg):
        messagebox.showerror("错误", error_msg)
        self.status_label.config(text=f"错误: {error_msg}", fg="red")
    
    def prev_page(self):
        if self.current_page > 1 and not self.is_loading:
            self.load_page(self.current_page - 1)
    
    def next_page(self):
        if self.current_page < self.total_pages and not self.is_loading:
            self.load_page(self.current_page + 1)
    
    def go_to_page(self):
        try:
            page = int(self.page_entry.get())
            if 1 <= page <= self.total_pages and not self.is_loading:
                self.load_page(page)
            else:
                messagebox.showwarning("警告", f"页码必须在 1 到 {self.total_pages} 之间")
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的页码")
    
    def download_selected(self):
        selected_indices = [i for i, var in enumerate(self.checkboxes) if var.get()]
        
        if not selected_indices:
            messagebox.showwarning("警告", "请先选择要下载的图片")
            return
        
        save_dir = self.path_var.get()
        if not save_dir:
            save_dir = "./wallhaven_downloads"
            self.path_var.set(save_dir)
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # 更新爬虫的保存目录
        self.scraper.save_dir = save_dir
        
        # 禁用下载按钮，防止重复点击
        self.download_btn.config(state=tk.DISABLED)
        self.status_label.config(text=f"正在下载 {len(selected_indices)} 张图片...", fg="blue")
        self.progress['value'] = 0
        
        # 在新线程中下载
        thread = threading.Thread(target=self.download_images_thread, args=(selected_indices,))
        thread.daemon = True
        thread.start()
    
    def download_images_thread(self, selected_indices):
        total = len(selected_indices)
        success_count = 0
        failed_list = []
        
        for idx, i in enumerate(selected_indices):
            img_data = self.current_images[i]
            
            def callback(filename, success, error):
                nonlocal success_count
                if success:
                    success_count += 1
                else:
                    failed_list.append(filename)
            
            self.scraper.download_image(img_data['url'], img_data['filename'], callback)
            
            # 更新进度
            progress_value = (idx + 1) / total * 100
            self.root.after(0, self.update_progress, progress_value)
            self.root.after(0, lambda i=idx+1, t=total: self.status_label.config(
                text=f"正在下载... ({i}/{t})", fg="blue"))
            
            time.sleep(0.3)  # 避免请求过快
        
        # 下载完成
        def download_finished():
            self.download_btn.config(state=tk.NORMAL)
            self.progress['value'] = 100
            
            result_msg = f"下载完成！成功: {success_count} 张"
            if failed_list:
                result_msg += f"，失败: {len(failed_list)} 张"
            
            self.status_label.config(text=result_msg, fg="green")
            messagebox.showinfo("完成", result_msg)
        
        self.root.after(0, download_finished)


def main():
    root = tk.Tk()
    app = ImageDownloaderApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()


    # https://www.52pojie.cn/thread-1815691-1-1.html