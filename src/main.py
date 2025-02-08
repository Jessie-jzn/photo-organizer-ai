from photo_organizer import PhotoOrganizer, SUPPORTED_FORMATS
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
            if file.lower().endswith(tuple(SUPPORTED_FORMATS)):
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
    
    if not dest_dir:
        dest_dir = os.path.join(source_dir, "organized_photos")
    
    os.makedirs(dest_dir, exist_ok=True)
    
    gui_log_callback(f"源文件夹: {source_dir}")
    gui_log_callback(f"目标文件夹: {dest_dir}")
    
    total_images = count_images(source_dir)
    gui_log_callback(f"开始处理，共发现 {total_images} 张图片\n")

    if total_images == 0:
        gui_log_callback("未找到任何图片文件！")
        return

    try:
        # 1. 检测重复图片（移到最前面）
        gui_log_callback("\n开始检测重复图片...")
        detector = DuplicateDetector(threshold=dup_threshold, log_callback=gui_log_callback)
        duplicate_pairs = detector.find_duplicates(source_dir)  # 这里改为 source_dir
        
        if duplicate_pairs:
            gui_log_callback(f"\n找到 {len(duplicate_pairs)} 组重复图片")
            duplicates_dir, moved_files, duplicate_info = detector.move_duplicates_to_folder(duplicate_pairs, dest_dir)
            
            # 显示每组重复照片的信息
            for i, group in enumerate(duplicate_info, 1):
                gui_log_callback(f"\n重复组 {i}:")
                gui_log_callback(f"保留的照片: {group['kept']}")
                for dup in group['duplicates']:
                    gui_log_callback(f"移动的重复照片: {dup['original_path']} -> {dup['moved_to']}")
            
            gui_log_callback(f"\n共移动了 {len(moved_files)} 张重复照片到: {duplicates_dir}")

        # 2. 按国家分类（对剩余的照片）
        if not skip_country:
            gui_log_callback("\n开始按国家分类照片...")
            classifier = ImageClassifier(dest_dir)
            classifier.classify_by_country(source_dir, dest_dir)
            
            moved_images = count_images(dest_dir)
            gui_log_callback(f"按国家分类完成，移动了 {moved_images} 张图片")
        
        # 3. 在每个国家目录下按时间整理
        gui_log_callback("\n开始按时间整理照片...")
        for country_dir in os.listdir(dest_dir):
            country_path = os.path.join(dest_dir, country_dir)
            if os.path.isdir(country_path) and country_dir != "duplicates":
                gui_log_callback(f"正在处理 {country_dir} 目录...")
                organizer = PhotoOrganizer(country_path, country_path)
                organizer.organize_photos()

        # 4. 在时间目录下继续按城市和地区分类
        if not skip_location:
            gui_log_callback("\n开始按城市和地区分类...")
            for country_dir in os.listdir(dest_dir):
                country_path = os.path.join(dest_dir, country_dir)
                if os.path.isdir(country_path) and country_dir != "duplicates":
                    gui_log_callback(f"正在处理 {country_dir} 目录的地理位置...")
                    classifier.classify_by_location_details(country_path)

        # 最后清理空文件夹
        remove_empty_dirs(dest_dir)
        gui_log_callback("\n已清理空文件夹")
        
        # 最终统计
        final_count = count_images(dest_dir)
        gui_log_callback(f"\n照片整理完成！共处理 {final_count} 张照片")
        
    except Exception as e:
        gui_log_callback(f"\n处理过程中出现错误: {str(e)}")
        raise

def remove_empty_dirs(directory):
    """递归删除空文件夹"""
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in dirs:
            try:
                dir_path = os.path.join(root, name)
                # 检查目录是否为空（不包含文件和子目录）
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
            except Exception as e:
                print(f"删除空文件夹 {name} 时出错: {str(e)}")

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