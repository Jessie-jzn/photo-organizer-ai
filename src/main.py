from photo_organizer import PhotoOrganizer
from duplicate_detector import DuplicateDetector
from image_classifier import ImageClassifier
import os
import shutil

def count_images(directory):
    """统计目录下的图片数量"""
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                count += 1
    return count

def move_duplicates_to_folder(duplicates, dest_dir):
    """将重复图片移动到指定文件夹"""
    duplicates_dir = os.path.join(dest_dir, "duplicates")
    os.makedirs(duplicates_dir, exist_ok=True)
    
    moved_files = set()
    
    for idx, (original, duplicate) in enumerate(duplicates, 1):
        if os.path.exists(original) and original not in moved_files:
            try:
                shutil.move(original, os.path.join(duplicates_dir, os.path.basename(original)))
                moved_files.add(original)
            except Exception as e:
                print(f"移动文件 {os.path.basename(original)} 时出错: {e}")
        
        if os.path.exists(duplicate) and duplicate not in moved_files:
            try:
                shutil.move(duplicate, os.path.join(duplicates_dir, os.path.basename(duplicate)))
                moved_files.add(duplicate)
            except Exception as e:
                print(f"移动文件 {os.path.basename(duplicate)} 时出错: {e}")
    
    print(f"成功移动 {len(moved_files)} 个重复文件")
    return duplicates_dir

def main():
    # 设置源文件夹和目标文件夹
    source_dir = "/Users/jessie.chen/Desktop/photo"
    dest_dir = "/Users/jessie.chen/Desktop/photo/organized_photos"

    # 1. 先按国家分类
    print("开始按国家分类照片...")
    classifier = ImageClassifier(dest_dir)
    classifier.classify_by_country(source_dir, dest_dir)

    # 2. 在每个国家目录下按时间整理
    print("\n开始按时间整理照片...")
    for country_dir in os.listdir(dest_dir):
        country_path = os.path.join(dest_dir, country_dir)
        if os.path.isdir(country_path) and country_dir != "duplicates":
            organizer = PhotoOrganizer(country_path, country_path)
            organizer.organize_photos()

    # 3. 在时间目录下继续按城市和地区分类
    print("\n开始按城市和地区分类...")
    for country_dir in os.listdir(dest_dir):
        country_path = os.path.join(dest_dir, country_dir)
        if os.path.isdir(country_path) and country_dir != "duplicates":
            classifier.classify_by_location_details(country_path)

    # 4. 检测重复图片
    print("\n开始检测重复图片...")
    detector = DuplicateDetector(threshold=2)
    duplicates = detector.find_duplicates(dest_dir)
    
    if duplicates:
        print(f"\n找到 {len(duplicates)} 组重复图片")
        duplicates_dir = move_duplicates_to_folder(duplicates, dest_dir)
        print(f"重复图片已移动到: {duplicates_dir}")

if __name__ == "__main__":
    main() 