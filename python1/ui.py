import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
# import spider

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        root.title("图片下载器")
        root.geometry("800x600")
        root.resizable(False, False)

        # 下载链接输入框
        tk.Label(root, text="下载链接:").pack(pady=5)
        self.url_entry = tk.Entry(root, width=70)
        self.url_entry.pack(pady=5)

        # 保存路径
        path_frame = tk.Frame(root)
        path_frame.pack(pady=5)
        self.path_var = tk.StringVar(value="./downloads")
        tk.Entry(path_frame, textvariable=self.path_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(path_frame, text="浏览...", command=self.select_path).pack(side=tk.LEFT)

        # 下载按钮
        self.download_btn = tk.Button(root, text="开始下载", command=self.start_download, bg="#4CAF50", fg="white")
        self.download_btn.pack(pady=10)

        # 进度条
        self.progress = ttk.Progressbar(root, length=500, mode='determinate')
        self.progress.pack(pady=5)

        # 状态标签
        self.status_label = tk.Label(root, text="就绪", fg="gray")
        self.status_label.pack()

    def select_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("警告", "请输入下载链接")
            return

    #     self.download_btn.config(state=tk.DISABLED)
    #     self.progress['value'] = 0
    #     self.status_label.config(text="下载中...", fg="blue")

    #     # 启动下载线程（避免界面卡死）
    #     thread = threading.Thread(target=self.do_download, args=(url,))
    #     thread.start()

    # def do_download(self, url):
    #     try:
    #         # 这里是下载逻辑的占位符
    #         # 实际应该用 requests + 多线程分块下载
    #         import time
    #         for i in range(101):
    #             time.sleep(0.02)  # 模拟下载进度
    #             self.progress['value'] = i
    #             self.root.update_idletasks()

    #         self.status_label.config(text="下载完成！", fg="green")
    #         messagebox.showinfo("完成", "文件下载成功")

    #     except Exception as e:
    #         self.status_label.config(text=f"错误: {str(e)}", fg="red")
    #         messagebox.showerror("错误", f"下载失败：{e}")

    #     finally:
    #         self.download_btn.config(state=tk.NORMAL)

if __name__ == '__main__':
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()