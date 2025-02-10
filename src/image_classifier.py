import os
import exifread
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import shutil
from PIL import Image
import numpy as np
from photo_organizer import SUPPORTED_FORMATS

class ImageClassifier:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.geolocator = Nominatim(user_agent="my_photo_organizer")
        
    def get_location_info(self, image_path):
        """获取图片的详细地理位置信息"""
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f)
                
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                lat = self._convert_to_degrees(tags['GPS GPSLatitude'])
                lon = self._convert_to_degrees(tags['GPS GPSLongitude'])
                
                # 获取地理位置名称
                location = self.geolocator.reverse(f"{lat}, {lon}", language='zh')
                if location:
                    address = location.raw['address']
                    return {
                        'country': address.get('country', 'unknown_country'),
                        'state': address.get('state', ''),
                        'city': address.get('city', address.get('county', '')),
                        'district': address.get('suburb', address.get('district', ''))
                    }
            
            # 如果没有 GPS 信息，尝试从文件名或目录名推测位置
            guessed_location = self.guess_location_from_filename(image_path)
            if guessed_location:
                return guessed_location
            
            return {
                'country': 'unknown_country',
                'state': 'unknown_state',
                'city': 'unknown_city',
                'district': 'unknown_district'
            }
        except Exception as e:
            print(f"获取位置信息失败 {image_path}: {e}")
            return {
                'country': 'unknown_country',
                'state': 'unknown_state',
                'city': 'unknown_city',
                'district': 'unknown_district'
            }
    
    def _convert_to_degrees(self, value):
        """将GPS坐标转换为度数"""
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)
        return d + (m / 60.0) + (s / 3600.0)

    def guess_location_from_filename(self, image_path):
        """尝试从文件名或目录名推测位置"""
        # 示例：从文件名或目录名中提取可能的地名
        # 这里假设文件名或目录名中可能包含地名信息
        # 例如：/path/to/photos/Paris_2023/photo1.jpg
        path_parts = os.path.normpath(image_path).split(os.sep)
        for part in path_parts:
            try:
                location = self.geolocator.geocode(part, language='zh')
                if location:
                    address = location.raw['address']
                    return {
                        'country': address.get('country', 'unknown_country'),
                        'state': address.get('state', ''),
                        'city': address.get('city', address.get('county', '')),
                        'district': address.get('suburb', address.get('district', ''))
                    }
            except GeocoderTimedOut:
                continue
        return None

    def is_supported_image(self, filename):
        """检查文件是否为支持的图片格式"""
        return filename.lower().endswith(tuple(SUPPORTED_FORMATS))

    def classify_by_country(self, source_dir, dest_dir):
        """首先按国家分类"""
        print("\n开始按国家分类...")
        processed = 0
        total_files = sum(1 for root, _, files in os.walk(source_dir)
                         for f in files if self.is_supported_image(f))
        
        for root, _, files in os.walk(source_dir):
            for filename in files:
                if self.is_supported_image(filename):
                    file_path = os.path.join(root, filename)
                    location_info = self.get_location_info(file_path)
                    
                    # 创建国家目录
                    country_dir = os.path.join(dest_dir, self._sanitize_path(location_info['country']))
                    os.makedirs(country_dir, exist_ok=True)
                    
                    # 移动文件到国家目录
                    dest_path = os.path.join(country_dir, filename)
                    if not os.path.exists(dest_path):
                        shutil.move(file_path, dest_path)
                    
                    processed += 1
                    if processed % 10 == 0 or processed == total_files:
                        print(f"进度: {processed}/{total_files} ({(processed/total_files*100):.1f}%)")

    def classify_by_location_details(self, source_dir):
        """在时间目录下按城市和地区分类"""
        for root, _, files in os.walk(source_dir):
            # 跳过 duplicates 文件夹
            if "duplicates" in root:
                continue
            
            # 只处理年/月目录下的文件
            if not any(p.isdigit() for p in os.path.split(root)):
                continue
            
            for file in files:
                if self.is_supported_image(file):
                    try:
                        file_path = os.path.join(root, file)
                        location = self.get_location_info(file_path)
                        
                        if location and location.get('city') and location['city'] != 'unknown_city':
                            # 如果有城市信息，按城市分类
                            city_dir = os.path.join(root, location['city'])
                            if location.get('district') and location['district'] != 'unknown_district':
                                # 如果有区域信息，在城市目录下创建区域子目录
                                dest_dir = os.path.join(city_dir, location['district'])
                            else:
                                dest_dir = city_dir
                        else:
                            # 如果没有地理信息，直接放在 unknown 目录
                            dest_dir = os.path.join(root, 'unknown')
                        
                        # 创建目标目录并移动文件
                        os.makedirs(dest_dir, exist_ok=True)
                        shutil.move(file_path, os.path.join(dest_dir, file))
                    except Exception as e:
                        print(f"处理文件 {file} 时出错: {str(e)}")
                        # 发生错误时，将文件移动到 unknown 目录
                        unknown_dir = os.path.join(root, 'unknown')
                        os.makedirs(unknown_dir, exist_ok=True)
                        shutil.move(file_path, os.path.join(unknown_dir, file))

    def classify_by_people(self, year_month_dir):
        """按人物数量对指定目录下的图片进行分类"""
        print(f"\n暂时跳过人物分类: {year_month_dir}")
        return 

    def _sanitize_path(self, path_component):
        """清理路径组件，移除或替换非法字符"""
        if not path_component:
            return "unknown"
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            path_component = path_component.replace(char, '_')
        return path_component.strip() or "unknown"

    def get_photo_location(self, image_path):
        # This method is mentioned in classify_by_location_details but not implemented in the provided code block
        # It's assumed to exist as it's called in the classify_by_location_details method
        # If this method is needed, it should be implemented here
        pass

    def classify_by_location_details(self, country_dir):
        # This method is mentioned in classify_by_location_details but not implemented in the provided code block
        # It's assumed to exist as it's called in the classify_by_location_details method
        # If this method is needed, it should be implemented here
        pass 