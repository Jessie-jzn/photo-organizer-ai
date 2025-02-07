import os
import exifread
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import shutil
from PIL import Image
import numpy as np

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

    def classify_by_country(self, source_dir, dest_dir):
        """首先按国家分类"""
        print("\n开始按国家分类...")
        processed = 0
        total_files = sum(1 for root, _, files in os.walk(source_dir)
                         for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')))
        
        for root, _, files in os.walk(source_dir):
            for filename in files:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
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

    def classify_by_location_details(self, country_dir):
        """在时间目录下按城市和地区进行分类"""
        print(f"\n开始对 {country_dir} 进行城市和地区分类...")
        for year_dir in os.listdir(country_dir):
            year_path = os.path.join(country_dir, year_dir)
            if os.path.isdir(year_path) and year_dir.isdigit():
                for month_dir in os.listdir(year_path):
                    month_path = os.path.join(year_path, month_dir)
                    if os.path.isdir(month_path) and month_dir.isdigit():
                        self._classify_month_by_location(month_path)

    def _classify_month_by_location(self, month_dir):
        """对月份目录下的照片按城市和地区分类"""
        processed = 0
        files = [f for f in os.listdir(month_dir) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        total_files = len(files)
        
        for filename in files:
            file_path = os.path.join(month_dir, filename)
            location_info = self.get_location_info(file_path)
            
            # 构建城市和地区目录
            city_dir = os.path.join(month_dir, self._sanitize_path(location_info['city']))
            district_dir = os.path.join(city_dir, self._sanitize_path(location_info['district'])) if location_info['district'] else city_dir
            
            # 创建目录
            os.makedirs(district_dir, exist_ok=True)
            
            # 移动文件
            dest_path = os.path.join(district_dir, filename)
            if not os.path.exists(dest_path):
                shutil.move(file_path, dest_path)
            
            processed += 1
            if processed % 10 == 0 or processed == total_files:
                print(f"进度: {processed}/{total_files} ({(processed/total_files*100):.1f}%)")
    
    def _sanitize_path(self, path_component):
        """清理路径组件，移除或替换非法字符"""
        if not path_component:
            return "unknown"
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            path_component = path_component.replace(char, '_')
        return path_component.strip() or "unknown"

    def classify_by_people(self, year_month_dir):
        """按人物数量对指定目录下的图片进行分类"""
        print(f"\n暂时跳过人物分类: {year_month_dir}")
        return 