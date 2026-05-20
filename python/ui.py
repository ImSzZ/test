# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# import threading
# # import spider

# class DownloaderApp:
#     def __init__(self, root):
#         self.root = root
#         root.title("图片下载器")
#         root.geometry("800x600")
#         root.resizable(False, False)

#         # 下载链接输入框
#         tk.Label(root, text="下载链接:").pack(pady=5)
#         self.url_entry = tk.Entry(root, width=70)
#         self.url_entry.pack(pady=5)

#         # 保存路径
#         path_frame = tk.Frame(root)
#         path_frame.pack(pady=5)
#         self.path_var = tk.StringVar(value="./downloads")
#         tk.Entry(path_frame, textvariable=self.path_var, width=50).pack(side=tk.LEFT, padx=5)
#         tk.Button(path_frame, text="浏览...", command=self.select_path).pack(side=tk.LEFT)

#         # 下载按钮
#         self.download_btn = tk.Button(root, text="开始下载", command=self.start_download, bg="#4CAF50", fg="white")
#         self.download_btn.pack(pady=10)

#         # 进度条
#         self.progress = ttk.Progressbar(root, length=500, mode='determinate')
#         self.progress.pack(pady=5)

#         # 状态标签
#         self.status_label = tk.Label(root, text="就绪", fg="gray")
#         self.status_label.pack()

#     def select_path(self):
#         path = filedialog.askdirectory()
#         if path:
#             self.path_var.set(path)

#     def start_download(self):
#         url = self.url_entry.get().strip()
#         if not url:
#             messagebox.showwarning("警告", "请输入下载链接")
#             return

#     #     self.download_btn.config(state=tk.DISABLED)
#     #     self.progress['value'] = 0
#     #     self.status_label.config(text="下载中...", fg="blue")

#     #     # 启动下载线程（避免界面卡死）
#     #     thread = threading.Thread(target=self.do_download, args=(url,))
#     #     thread.start()

#     # def do_download(self, url):
#     #     try:
#     #         # 这里是下载逻辑的占位符
#     #         # 实际应该用 requests + 多线程分块下载
#     #         import time
#     #         for i in range(101):
#     #             time.sleep(0.02)  # 模拟下载进度
#     #             self.progress['value'] = i
#     #             self.root.update_idletasks()

#     #         self.status_label.config(text="下载完成！", fg="green")
#     #         messagebox.showinfo("完成", "文件下载成功")

#     #     except Exception as e:
#     #         self.status_label.config(text=f"错误: {str(e)}", fg="red")
#     #         messagebox.showerror("错误", f"下载失败：{e}")

#     #     finally:
#     #         self.download_btn.config(state=tk.NORMAL)

# if __name__ == '__main__':
#     root = tk.Tk()
#     app = DownloaderApp(root)
#     root.mainloop()

import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from spider import ImageSpider

class ImageSpiderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("万能智能高清图片下载器 (多站合一版)")
        self.root.geometry("620x520")
        
        # 初始化爬虫实例
        self.spider = None
        self.crawl_thread = None

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
            command=self.start_crawl
        )
        self.start_btn.pack(pady=10)

        # 日志输出框
        tk.Label(root, text="运行日志:", font=("Arial", 10)).pack(anchor="w", padx=15)
        self.log_text = scrolledtext.ScrolledText(root, width=72, height=16, font=("Consolas", 9))
        self.log_text.pack(padx=15, pady=5)

    def log(self, message):
        """向界面打印日志"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_crawl(self):
        """开始爬取任务"""
        url = self.url_input.get().strip()
        limit_str = self.count_input.get().strip()
        
        if not url:
            messagebox.showwarning("警告", "请输入有效的网址！")
            return
        
        try:
            max_count = int(limit_str)
            if max_count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("警告", "下载数量必须是大于 0 的整数！")
            return

        # 禁用开始按钮，防止重复点击
        self.start_btn.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        
        # 创建爬虫实例，传入日志回调函数
        self.spider = ImageSpider(log_callback=self.log)
        
        # 在新线程中执行爬取任务
        self.crawl_thread = threading.Thread(
            target=self._crawl_task,
            args=(url, max_count)
        )
        self.crawl_thread.daemon = True
        self.crawl_thread.start()
    
    def _crawl_task(self, url, max_count):
        """爬取任务（在后台线程中运行）"""
        try:
            self.spider.crawl(url, max_count)
        except Exception as e:
            self.log(f"任务执行出错: {str(e)}")
        finally:
            # 任务完成后重新启用开始按钮
            self.start_btn.config(state=tk.NORMAL)

def main():
    root = tk.Tk()
    app = ImageSpiderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
