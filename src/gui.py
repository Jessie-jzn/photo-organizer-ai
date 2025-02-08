import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import sys
import os
from main import process_photos

class PhotoOrganizerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("照片智能整理工具")
        self.window.geometry("800x600")
        
        # 检查必要的依赖
        self.check_dependencies()
        
        # 设置整体样式
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TLabelframe', padding=10)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.window, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题和说明
        title_label = ttk.Label(self.main_frame, 
                              text="照片智能整理工具",
                              font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        description = """本工具将按以下策略整理您的照片：
1. 首先按照拍摄国家分类（基于照片GPS信息）
2. 然后在每个国家文件夹下按拍摄时间整理（年/月）
3. 最后在时间文件夹下按城市和地区细分
4. 自动检测并归类重复照片"""
        
        desc_label = ttk.Label(self.main_frame, 
                             text=description,
                             wraplength=700,
                             justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # 文件夹选择框架
        folder_frame = ttk.LabelFrame(self.main_frame, text="文件夹选择", padding=10)
        folder_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 源文件夹选择
        ttk.Label(folder_frame, text="源文件夹:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_path = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.source_path, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(folder_frame, text="浏览", command=self.choose_source).grid(row=0, column=2)
        
        # 目标文件夹选择
        ttk.Label(folder_frame, text="目标文件夹:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dest_path = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.dest_path, width=60).grid(row=1, column=1, padx=5)
        ttk.Button(folder_frame, text="浏览", command=self.choose_dest).grid(row=1, column=2)
        
        # 选项框架
        options_frame = ttk.LabelFrame(self.main_frame, text="处理选项", padding=10)
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 复选框
        self.skip_country = tk.BooleanVar()
        ttk.Checkbutton(options_frame, 
                       text="跳过国家分类（适用于GPS信息不准确的情况）", 
                       variable=self.skip_country).grid(row=0, column=0, sticky=tk.W)
        
        self.skip_location = tk.BooleanVar()
        ttk.Checkbutton(options_frame, 
                       text="跳过地点分类（仅按时间整理）", 
                       variable=self.skip_location).grid(row=1, column=0, sticky=tk.W)
        
        # 重复检测阈值
        threshold_frame = ttk.Frame(options_frame)
        threshold_frame.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        ttk.Label(threshold_frame, text="重复检测阈值:").pack(side=tk.LEFT)
        self.dup_threshold = tk.StringVar(value="2")
        ttk.Entry(threshold_frame, textvariable=self.dup_threshold, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(threshold_frame, 
                 text="（值越小检测越严格，建议范围1-5）").pack(side=tk.LEFT)
        
        # 开始按钮
        self.start_button = ttk.Button(self.main_frame, 
                                text="开始处理", 
                                command=self.start_process,
                                style='TButton')
        self.start_button.grid(row=4, column=0, columnspan=3, pady=15)
        
        # 日志框架
        log_frame = ttk.LabelFrame(self.main_frame, text="处理日志", padding=10)
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, height=12, width=80)
        self.log_text.grid(row=0, column=0, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # 设置窗口大小可调整
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
    def check_dependencies(self):
        """检查必要的依赖是否已安装"""
        try:
            import PIL
            # 在这里添加其他必要的依赖检查
        except ImportError as e:
            messagebox.showerror("错误", f"缺少必要的依赖: {str(e)}\n请确保所有依赖都已正确安装。")
            sys.exit(1)
    
    def resource_path(self, relative_path):
        """获取资源文件的绝对路径"""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    
    def choose_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_path.set(folder)
            
    def choose_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_path.set(folder)
            
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.window.update()
        
    def start_process(self):
        if not self.source_path.get():
            messagebox.showwarning("警告", "请选择源文件夹！")
            return
            
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 禁用开始按钮，避免重复点击
        self.start_button.configure(state='disabled')
        
        # 在新线程中运行处理过程
        thread = threading.Thread(target=self.process_with_progress)
        thread.start()
        
    def process_with_progress(self):
        """处理照片并显示进度"""
        try:
            process_photos(
                source_dir=self.source_path.get(),
                dest_dir=self.dest_path.get(),
                skip_country=self.skip_country.get(),
                skip_location=self.skip_location.get(),
                dup_threshold=int(self.dup_threshold.get()),
                gui_log_callback=self.log_message
            )
            # 处理完成后显示成功消息
            self.window.after(0, lambda: messagebox.showinfo("完成", "照片处理完成！"))
        except Exception as error:  # 将 'e' 改为 'error'
            # 显示错误消息
            error_msg = str(error)  # 在这里保存错误信息
            self.window.after(0, lambda: messagebox.showerror("错误", f"处理过程中出现错误：\n{error_msg}"))
        finally:
            # 重新启用开始按钮
            self.window.after(0, lambda: self.start_button.configure(state='normal'))
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    try:
        app = PhotoOrganizerGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("错误", f"程序启动失败：\n{str(e)}") 