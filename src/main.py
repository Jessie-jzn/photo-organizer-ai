from photo_organizer import PhotoOrganizer
from duplicate_detector import DuplicateDetector
from image_classifier import ImageClassifier
import os
import shutil
import argparse

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

def process_photos(source_dir, dest_dir=None, skip_country=False, 
                  skip_location=False, dup_threshold=2, gui_log_callback=print):
    """处理照片的核心函数，支持 GUI 和命令行调用"""
    
    # 如果没有指定目标目录，在源目录下创建
    if not dest_dir:
        dest_dir = os.path.join(source_dir, "organized_photos")
    
    # 确保目录存在
    os.makedirs(dest_dir, exist_ok=True)
    
    gui_log_callback(f"源文件夹: {source_dir}")
    gui_log_callback(f"目标文件夹: {dest_dir}")
    gui_log_callback(f"开始处理，共发现 {count_images(source_dir)} 张图片\n")

    try:
        # 1. 按国家分类
        if not skip_country:
            gui_log_callback("开始按国家分类照片...")
            classifier = ImageClassifier(dest_dir)
            classifier.classify_by_country(source_dir, dest_dir)
        
        # 2. 在每个国家目录下按时间整理
        gui_log_callback("\n开始按时间整理照片...")
        for country_dir in os.listdir(dest_dir):
            country_path = os.path.join(dest_dir, country_dir)
            if os.path.isdir(country_path) and country_dir != "duplicates":
                organizer = PhotoOrganizer(country_path, country_path)
                organizer.organize_photos()

        # 3. 在时间目录下继续按城市和地区分类
        if not skip_location:
            gui_log_callback("\n开始按城市和地区分类...")
            for country_dir in os.listdir(dest_dir):
                country_path = os.path.join(dest_dir, country_dir)
                if os.path.isdir(country_path) and country_dir != "duplicates":
                    classifier.classify_by_location_details(country_path)

        # 4. 检测重复图片
        gui_log_callback("\n开始检测重复图片...")
        detector = DuplicateDetector(threshold=dup_threshold)
        duplicates = detector.find_duplicates(dest_dir)
        
        if duplicates:
            gui_log_callback(f"\n找到 {len(duplicates)} 组重复图片")
            duplicates_dir = move_duplicates_to_folder(duplicates, dest_dir)
            gui_log_callback(f"重复图片已移动到: {duplicates_dir}")
            
        gui_log_callback("\n照片整理完成！")
        
    except Exception as e:
        gui_log_callback(f"\n处理过程中出现错误: {str(e)}")
        raise

def main():
    # 原来的命令行处理代码
    parser = argparse.ArgumentParser(description="照片智能整理工具")
    parser.add_argument("--source", type=str, required=True, help="源文件夹路径")
    parser.add_argument("--dest", type=str, help="目标文件夹路径")
    parser.add_argument("--skip_country", action="store_true", help="跳过国家分类")
    parser.add_argument("--skip_location", action="store_true", help="跳过地点分类")
    parser.add_argument("--dup_threshold", type=int, default=2, help="重复检测阈值")
    args = parser.parse_args()
    
    try:
        process_photos(
            source_dir=args.source,
            dest_dir=args.dest,
            skip_country=args.skip_country,
            skip_location=args.skip_location,
            dup_threshold=args.dup_threshold
        )
        return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 