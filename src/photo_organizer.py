import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from dateutil.parser import parse
import shutil

class PhotoOrganizer:
    def __init__(self, source_dir, dest_dir):
        """
        初始化照片整理器
        :param source_dir: 源文件夹路径
        :param dest_dir: 目标文件夹路径
        """
        self.source_dir = source_dir
        self.dest_dir = dest_dir

    def get_image_date(self, image_path):
        """
        获取图片的拍摄日期
        """
        try:
            image = Image.open(image_path)
            exif = image._getexif()
            if exif:
                for tag_id in exif:
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal':
                        return datetime.strptime(exif[tag_id], '%Y:%m:%d %H:%M:%S')
            
            # 如果没有EXIF数据，使用文件修改时间
            return datetime.fromtimestamp(os.path.getmtime(image_path))
        except Exception:
            return datetime.fromtimestamp(os.path.getmtime(image_path))

    def organize_photos(self):
        """
        整理照片到目标文件夹
        """
        processed = 0
        total_files = sum(1 for root, _, files in os.walk(self.source_dir)
                         for file in files
                         if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')))
        
        print(f"开始处理 {total_files} 张图片...")
        
        for root, _, files in os.walk(self.source_dir):
            for filename in files:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    file_path = os.path.join(root, filename)
                    date = self.get_image_date(file_path)
                    
                    # 创建年/月文件夹结构
                    year_dir = os.path.join(self.dest_dir, str(date.year))
                    month_dir = os.path.join(year_dir, f"{date.month:02d}")
                    
                    os.makedirs(month_dir, exist_ok=True)
                    
                    # 复制文件到目标位置
                    dest_path = os.path.join(month_dir, filename)
                    if not os.path.exists(dest_path):
                        shutil.copy2(file_path, dest_path)
                    
                    processed += 1
                    if processed % 10 == 0 or processed == total_files:  # 每处理10张图片显示一次进度
                        print(f"进度: {processed}/{total_files} ({(processed/total_files*100):.1f}%)") 