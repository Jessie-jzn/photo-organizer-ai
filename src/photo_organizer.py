import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from dateutil.parser import parse
import shutil

# 支持的图片格式
SUPPORTED_FORMATS = {
    # 常见图片格式
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', 
    # RAW 格式
    '.raw', '.arw', '.cr2', '.cr3', '.nef', '.nrw', '.dng', '.orf', '.rw2', '.pef', '.raf', '.srw',
    # 其他格式
    '.tiff', '.tif', '.heic', '.heif'
}

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

    def is_supported_image(self, filename):
        """检查文件是否为支持的图片格式"""
        return filename.lower().endswith(tuple(SUPPORTED_FORMATS))

    def organize_photos(self):
        """按时间组织照片"""
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                if self.is_supported_image(file):
                    try:
                        file_path = os.path.join(root, file)
                        date = self.get_image_date(file_path)
                        
                        if date:
                            # 创建年/月目录
                            year_dir = os.path.join(self.dest_dir, str(date.year))
                            month_dir = os.path.join(year_dir, f"{date.month:02d}")
                            os.makedirs(month_dir, exist_ok=True)
                            
                            # 移动文件
                            shutil.move(file_path, os.path.join(month_dir, file))
                        else:
                            # 如果无法获取日期，移动到 unknown 目录
                            unknown_dir = os.path.join(self.dest_dir, "unknown")
                            os.makedirs(unknown_dir, exist_ok=True)
                            shutil.move(file_path, os.path.join(unknown_dir, file))
                    except Exception as e:
                        print(f"处理文件 {file} 时出错: {str(e)}")
                        # 发生错误时移动到 unknown 目录
                        unknown_dir = os.path.join(self.dest_dir, "unknown")
                        os.makedirs(unknown_dir, exist_ok=True)
                        shutil.move(file_path, os.path.join(unknown_dir, file)) 