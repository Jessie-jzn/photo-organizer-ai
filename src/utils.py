import os
from PIL import Image

def is_valid_image(file_path):
    """
    检查文件是否为有效的图片文件
    """
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def get_file_size(file_path):
    """
    获取文件大小（MB）
    """
    return os.path.getsize(file_path) / (1024 * 1024)

def create_directory_if_not_exists(directory):
    """
    如果目录不存在则创建
    """
    if not os.path.exists(directory):
        os.makedirs(directory) 