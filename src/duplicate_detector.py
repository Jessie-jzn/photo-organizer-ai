import os
import imagehash
from PIL import Image
from collections import defaultdict

class DuplicateDetector:
    def __init__(self, threshold=2):
        """
        初始化重复检测器
        :param threshold: 哈希差异阈值，越小越严格（0表示完全相同）
        """
        self.threshold = threshold
        self.hash_dict = defaultdict(list)

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

    def find_duplicates(self, directory):
        """
        在指定目录中查找重复图片
        """
        duplicates = []
        processed_files = set()  # 记录已处理的文件
        
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    file_path = os.path.join(root, filename)
                    
                    # 跳过已处理的文件
                    if file_path in processed_files:
                        continue
                        
                    file_size = os.path.getsize(file_path)
                    image_hash = self.calculate_hash(file_path)
                    
                    if image_hash:
                        # 检查是否与现有图片相似
                        for existing_path, (existing_hash, existing_size) in self.hash_dict.items():
                            # 首先比较文件大小，如果相差太大就跳过
                            if abs(file_size - existing_size) / max(file_size, existing_size) > 0.01:  # 允许1%的大小差异
                                continue
                                
                            # 检查所有哈希值是否都相似
                            if all(self._hamming_distance(h1, h2) <= self.threshold 
                                   for h1, h2 in zip(image_hash, existing_hash)):
                                duplicates.append((existing_path, file_path))
                                processed_files.add(file_path)
                                break
                        else:
                            self.hash_dict[file_path] = (image_hash, file_size)
        
        return duplicates

    def _hamming_distance(self, hash1, hash2):
        """
        计算两个哈希值之间的汉明距离
        """
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2)) 