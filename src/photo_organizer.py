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

    def scan_photos(self):
        """扫描源文件夹中的所有照片"""
        photos = []
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                if self.is_supported_image(file):
                    file_path = os.path.join(root, file)
                    photos.append(file_path)
        return photos

    def organize_by_time(self, photo_path):
        """按时间整理单张照片"""
        try:
            date = self.get_image_date(photo_path)
            if date:
                # 创建年/月目录
                year_dir = os.path.join(self.dest_dir, str(date.year))
                month_dir = os.path.join(year_dir, f"{date.month:02d}")
                os.makedirs(month_dir, exist_ok=True)
                
                # 移动文件
                dest_path = os.path.join(month_dir, os.path.basename(photo_path))
                if os.path.exists(photo_path):  # 确保源文件存在
                    shutil.move(photo_path, dest_path)
                    return dest_path
        except Exception as e:
            print(f"处理文件 {photo_path} 时出错: {str(e)}")
        return None

    def organize_by_country(self, photo_path):
        """按国家整理单张照片"""
        try:
            # 获取照片的地理信息
            location = self.get_photo_location(photo_path)
            if location and location.get('country'):
                country_dir = os.path.join(self.dest_dir, self._sanitize_path(location['country']))
                os.makedirs(country_dir, exist_ok=True)
                
                # 移动文件
                dest_path = os.path.join(country_dir, os.path.basename(photo_path))
                if os.path.exists(photo_path):  # 确保源文件存在
                    shutil.move(photo_path, dest_path)
                    return dest_path
        except Exception as e:
            print(f"处理文件 {photo_path} 时出错: {str(e)}")
        return None

    def organize_by_location_details(self, photo_path):
        """按详细地点整理单张照片"""
        try:
            # 获取照片的地理信息
            location = self.get_photo_location(photo_path)
            if location:
                # 构建目录路径：国家/城市/区域
                path_components = []
                if location.get('country'):
                    path_components.append(self._sanitize_path(location['country']))
                if location.get('city'):
                    path_components.append(self._sanitize_path(location['city']))
                if location.get('district'):
                    path_components.append(self._sanitize_path(location['district']))
                
                if path_components:
                    location_dir = os.path.join(self.dest_dir, *path_components)
                    os.makedirs(location_dir, exist_ok=True)
                    
                    # 移动文件
                    dest_path = os.path.join(location_dir, os.path.basename(photo_path))
                    if os.path.exists(photo_path):  # 确保源文件存在
                        shutil.move(photo_path, dest_path)
                        return dest_path
        except Exception as e:
            print(f"处理文件 {photo_path} 时出错: {str(e)}")
        return None

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