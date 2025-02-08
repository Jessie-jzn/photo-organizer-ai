import os
import imagehash
from PIL import Image
import numpy as np
from collections import defaultdict
import shutil
from photo_organizer import SUPPORTED_FORMATS

class DuplicateDetector:
    def __init__(self, threshold=2, fuzzy_match=True, log_callback=print):
        """
        初始化重复检测器
        :param threshold: 哈希差异阈值，越小越严格（0表示完全相同）
        :param fuzzy_match: 是否启用模糊匹配
        :param log_callback: 日志输出回调函数
        """
        self.threshold = threshold
        self.fuzzy_match = fuzzy_match
        self.hash_dict = defaultdict(list)
        self.log = log_callback

    def calculate_hash(self, image_path):
        """
        计算图片的感知哈希值，使用多个哈希算法提高准确性
        """
        try:
            image = Image.open(image_path)
            # 使用多个哈希算法组合
            avg_hash = imagehash.average_hash(image)
            dhash = imagehash.dhash(image)
            phash = imagehash.phash(image)
            # 组合哈希值
            return (str(avg_hash), str(dhash), str(phash))
        except Exception as e:
            print(f"处理图片 {image_path} 时出错: {e}")
            return None

    def get_image_quality(self, image_path):
        """获取图片质量信息"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                resolution = width * height
                format_quality = {
                    'PNG': 5,
                    'JPEG': 4,
                    'TIFF': 5,
                    'RAW': 6,
                    'HEIC': 4
                }.get(img.format.upper(), 3)
                
                # 检查是否经过编辑
                exif = img.getexif() if hasattr(img, 'getexif') else None
                is_edited = bool(exif and any(tag for tag in exif if str(tag).startswith('Software')))
                
                return {
                    'resolution': resolution,
                    'format_quality': format_quality,
                    'is_edited': is_edited,
                    'file_size': os.path.getsize(image_path)
                }
        except Exception as e:
            print(f"获取图片质量信息失败 {image_path}: {e}")
            return None

    def compare_images(self, img1_path, img2_path):
        """比较两张图片的相似度"""
        try:
            # 基本哈希比较
            hash1 = self.calculate_hash(img1_path)
            hash2 = self.calculate_hash(img2_path)
            
            if not hash1 or not hash2:
                return False, 0
            
            # 计算哈希相似度
            hash_similarity = all(self._hamming_distance(h1, h2) <= self.threshold 
                                for h1, h2 in zip(hash1, hash2))
            
            if not self.fuzzy_match:
                return hash_similarity, 1.0 if hash_similarity else 0.0
            
            # 模糊匹配：考虑图片大小、亮度等因素
            with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
                # 统一大小进行比较
                size = (300, 300)  # 缩小图片加快比较速度
                img1_resized = img1.resize(size, Image.Resampling.LANCZOS)
                img2_resized = img2.resize(size, Image.Resampling.LANCZOS)
                
                # 转换为灰度图进行比较
                img1_gray = img1_resized.convert('L')
                img2_gray = img2_resized.convert('L')
                
                # 计算亮度直方图相似度
                hist1 = img1_gray.histogram()
                hist2 = img2_gray.histogram()
                hist_similarity = sum(min(h1, h2) for h1, h2 in zip(hist1, hist2)) / sum(hist1)
                
                # 综合评分
                similarity = (hash_similarity * 0.7 + hist_similarity * 0.3)
                return similarity >= 0.8, similarity
                
        except Exception as e:
            print(f"比较图片失败: {e}")
            return False, 0

    def suggest_better_version(self, img1_path, img2_path):
        """建议保留质量更好的版本"""
        quality1 = self.get_image_quality(img1_path)
        quality2 = self.get_image_quality(img2_path)
        
        if not quality1 or not quality2:
            return img1_path  # 默认保留第一张
        
        # 评分系统
        score1 = (quality1['resolution'] * 0.4 + 
                 quality1['format_quality'] * 0.3 + 
                 quality1['file_size'] * 0.2 + 
                 quality1['is_edited'] * 0.1)
        
        score2 = (quality2['resolution'] * 0.4 + 
                 quality2['format_quality'] * 0.3 + 
                 quality2['file_size'] * 0.2 + 
                 quality2['is_edited'] * 0.1)
        
        return img1_path if score1 >= score2 else img2_path

    def find_duplicates(self, directory):
        """在指定目录中查找重复图片"""
        duplicate_groups = []
        hash_dict = defaultdict(list)  # 用于存储哈希值到文件路径的映射
        total_files = sum(1 for root, _, files in os.walk(directory)
                         for f in files if f.lower().endswith(tuple(SUPPORTED_FORMATS)))
        
        self.log(f"\n开始扫描文件夹: {directory}")
        self.log(f"共发现 {total_files} 个图片文件")
        
        # 第一步：计算所有图片的哈希值
        processed_count = 0
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.lower().endswith(tuple(SUPPORTED_FORMATS)):
                    file_path = os.path.join(root, filename)
                    processed_count += 1
                    
                    if processed_count % 10 == 0:  # 每处理10个文件输出一次进度
                        self.log(f"计算哈希值进度: {processed_count}/{total_files} "
                               f"({processed_count/total_files*100:.1f}%)")
                    
                    try:
                        # 计算图片哈希值
                        image_hash = self.calculate_hash(file_path)
                        if image_hash:
                            # 使用第一个哈希值作为主键（通常是 average_hash）
                            hash_dict[image_hash[0]].append((file_path, image_hash))
                    except Exception as e:
                        self.log(f"处理文件 {filename} 时出错: {str(e)}")
        
        # 第二步：查找相似图片
        self.log("\n开始查找相似图片...")
        processed_files = set()
        
        for hash_value, files in hash_dict.items():
            if len(files) > 1:  # 如果有多个文件共享相同的主哈希值
                for i, (file1, hash1) in enumerate(files):
                    if file1 in processed_files:
                        continue
                        
                    current_group = [file1]
                    
                    # 只比较具有相同主哈希值的文件
                    for file2, hash2 in files[i+1:]:
                        if file2 not in processed_files:
                            # 使用所有哈希值进行详细比较
                            is_similar, similarity = self.compare_hashes(hash1, hash2)
                            if is_similar:
                                self.log(f"发现相似图片: \n  - {file1}\n  - {file2}"
                                       f"\n  相似度: {similarity:.2f}")
                                current_group.append(file2)
                                processed_files.add(file2)
                    
                    if len(current_group) > 1:
                        # 对组内照片进行排序，保证最好的版本在前面
                        current_group.sort(key=lambda x: self.get_image_quality(x)['resolution'], 
                                         reverse=True)
                        duplicate_groups.append(current_group)
                        self.log(f"\n找到一组重复照片，共 {len(current_group)} 张")
                    
                    processed_files.add(file1)
        
        self.log(f"\n扫描完成，共找到 {len(duplicate_groups)} 组重复照片")
        return duplicate_groups

    def compare_hashes(self, hash1, hash2):
        """比较两组哈希值的相似度"""
        # 计算所有哈希算法的平均相似度
        distances = [self._hamming_distance(h1, h2) for h1, h2 in zip(hash1, hash2)]
        avg_distance = sum(distances) / len(distances)
        similarity = 1 - (avg_distance / 64)  # 64 是哈希值的位数
        return avg_distance <= self.threshold, similarity

    def _hamming_distance(self, hash1, hash2):
        """
        计算两个哈希值之间的汉明距离
        """
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

    def move_duplicates_to_folder(self, duplicates, base_dir):
        """将重复的照片移动到特定文件夹"""
        duplicates_dir = os.path.join(base_dir, "duplicates")
        os.makedirs(duplicates_dir, exist_ok=True)
        
        self.log(f"\n开始移动重复照片到: {duplicates_dir}")
        moved_files = []
        duplicate_info = []
        
        for i, group in enumerate(duplicates, 1):
            self.log(f"\n处理第 {i} 组重复照片:")
            kept_file = group[0]
            self.log(f"保留文件: {kept_file}")
            
            group_info = {
                'kept': kept_file,
                'duplicates': []
            }
            
            for file_path in group[1:]:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(duplicates_dir, filename)
                    
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        dest_path = os.path.join(duplicates_dir, f"{base}_{counter}{ext}")
                        counter += 1
                    
                    self.log(f"移动文件: {file_path} -> {dest_path}")
                    shutil.move(file_path, dest_path)
                    moved_files.append(file_path)
                    group_info['duplicates'].append({
                        'original_path': file_path,
                        'moved_to': dest_path
                    })
            
            duplicate_info.append(group_info)
        
        self.log(f"\n重复照片处理完成，共移动 {len(moved_files)} 张照片")
        return duplicates_dir, moved_files, duplicate_info 