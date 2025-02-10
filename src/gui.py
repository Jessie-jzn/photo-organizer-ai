import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from main import process_photos
import threading

class PhotoOrganizerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Photo Organizer AI")
        self.window.geometry("800x600")
        # self.window.iconphoto(False, tk.PhotoImage(file='resources/icon.ico'))  # 添加图标

        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')  # 使用现代主题
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TCheckbutton", background="#f0f0f0")
        style.configure("TLabelFrame", background="#f0f0f0", font=('Arial', 10, 'bold'))
        style.configure("TLabel", background="#f0f0f0", font=('Arial', 10))
        style.configure("TEntry", font=('Arial', 10))
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文件选择区域
        self.create_file_selection()
        
        # 创建选项区域
        self.create_options()
        
        # 创建进度显示区域
        self.create_progress_area()

    def create_file_selection(self):
        """创建文件选择区域"""
        file_frame = ttk.LabelFrame(self.main_frame, text="文件选择", padding="10")
        file_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # 源文件夹选择
        source_frame = ttk.Frame(file_frame)
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(source_frame, text="源文件夹:").pack(side=tk.LEFT)
        self.source_path = tk.StringVar()
        ttk.Entry(source_frame, textvariable=self.source_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(source_frame, text="浏览", command=self.browse_source).pack(side=tk.LEFT)
        
        # 目标文件夹选择
        dest_frame = ttk.Frame(file_frame)
        dest_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dest_frame, text="目标文件夹:").pack(side=tk.LEFT)
        self.dest_path = tk.StringVar()
        ttk.Entry(dest_frame, textvariable=self.dest_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dest_frame, text="浏览", command=self.browse_dest).pack(side=tk.LEFT)

    def create_options(self):
        """创建选项区域"""
        options_frame = ttk.LabelFrame(self.main_frame, text="选项", padding="10")
        options_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # 复选框选项
        self.skip_country = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="跳过国家分类", 
                       variable=self.skip_country).pack(side=tk.LEFT, padx=5)
        
        self.skip_location = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="跳过地点分类", 
                       variable=self.skip_location).pack(side=tk.LEFT, padx=5)
         
        # 跳过人脸识别
        self.skip_face_recognition = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="跳过人脸识别", 
                       variable=self.skip_face_recognition).pack(side=tk.LEFT, padx=5)
        
        # 重复检测阈值
        threshold_frame = ttk.Frame(options_frame)
        threshold_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(threshold_frame, text="重复检测阈值:").pack(side=tk.LEFT)
        self.dup_threshold = tk.StringVar(value="2")
        ttk.Entry(threshold_frame, textvariable=self.dup_threshold, width=5).pack(side=tk.LEFT, padx=5)
       

    def create_progress_area(self):
        """创建进度显示区域"""
        progress_frame = ttk.LabelFrame(self.main_frame, text="处理进度", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        # 进度条
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # 日志显示
        self.log_text = tk.Text(progress_frame, height=10, wrap=tk.WORD, font=('Arial', 10))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(progress_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # 开始按钮
        self.start_button = ttk.Button(progress_frame, text="开始处理", command=self.start_processing)
        self.start_button.pack(pady=5)

    def browse_source(self):
        """浏览源文件夹"""
        path = filedialog.askdirectory()
        if path:
            self.source_path.set(path)
            self.log_message(f"已选择源文件夹: {path}")

    def browse_dest(self):
        """浏览目标文件夹"""
        path = filedialog.askdirectory()
        if path:
            self.dest_path.set(path)
            self.log_message(f"已选择目标文件夹: {path}")

    def log_message(self, message):
        """显示日志消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.window.update()

    def start_processing(self):
        """开始处理照片"""
        if not self.source_path.get():
            messagebox.showwarning("警告", "请选择源文件夹！")
            return
            
        self.start_button.state(['disabled'])
        self.progress['value'] = 0
        
        # 在新线程中处理照片
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
                skip_face_recognition=self.skip_face_recognition.get(),
                gui_log_callback=self.log_message
            )
            self.window.after(0, lambda: messagebox.showinfo("完成", "照片处理完成！"))
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("错误", f"处理过程中出现错误：\n{str(e)}"))
        finally:
            self.start_button.state(['!disabled'])

    def run(self):
        """运行程序"""
        self.window.mainloop()

if __name__ == "__main__":
    app = PhotoOrganizerGUI()
    app.run() 