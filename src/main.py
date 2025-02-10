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

def process_photos(source_dir, dest_dir=None, skip_country=False, skip_location=False, 
                  dup_threshold=2, skip_face_recognition=False, gui_log_callback=print, preview_callback=None):
    """
    处理照片的主函数
    :param source_dir: 源文件夹
    :param dest_dir: 目标文件夹（如果不指定，则在源文件夹旁创建）
    :param skip_country: 是否跳过国家分类
    :param skip_location: 是否跳过地点分类
    :param dup_threshold: 重复检测阈值
    :param skip_face_recognition: 是否跳过人脸识别
    :param gui_log_callback: GUI日志回调函数
    :param preview_callback: 预览回调函数，接收 (image_path, status) 参数
    """
    try:
        # 设置目标文件夹
        if not dest_dir:
            dest_dir = os.path.join(os.path.dirname(source_dir), 
                                  os.path.basename(source_dir) + "_organized")
        
        # 创建目标文件夹
        os.makedirs(dest_dir, exist_ok=True)
        
        # 创建照片整理器和重复检测器
        organizer = PhotoOrganizer(source_dir, dest_dir)
        detector = DuplicateDetector(threshold=dup_threshold, log_callback=gui_log_callback)
        
        # 扫描所有照片
        gui_log_callback("\n开始扫描照片...")
        photos = organizer.scan_photos()
        
        # 检测重复照片
        gui_log_callback("\n开始检测重复照片...")
        for photo in photos:
            if preview_callback:
                preview_callback(photo, "检测重复")
                
        duplicates = detector.find_duplicates(source_dir)
        
        if duplicates:
            # 移动重复照片
            gui_log_callback("\n开始处理重复照片...")
            duplicates_dir, moved_files, _ = detector.move_duplicates_to_folder(duplicates, dest_dir)
            
            # 从照片列表中移除已移动的重复照片
            photos = [p for p in photos if p not in moved_files]
        
        # 按时间整理照片
        gui_log_callback("\n开始按时间整理照片...")
        for photo in photos:
            if preview_callback:
                preview_callback(photo, "按时间整理")
            organizer.organize_by_time(photo)
        
        if not skip_country:
            # 按国家整理照片
            gui_log_callback("\n开始按国家整理照片...")
            for photo in photos:
                if preview_callback:
                    preview_callback(photo, "按国家整理")
                organizer.organize_by_country(photo)
        
        if not skip_location:
            # 按地点整理照片
            gui_log_callback("\n开始按地点整理照片...")
            for photo in photos:
                if preview_callback:
                    preview_callback(photo, "按地点整理")
                organizer.organize_by_location_details(photo)
        
        if not skip_face_recognition:
            # 人脸识别分类
            gui_log_callback("\n开始按人脸分类...")
            classifier = ImageClassifier(base_dir=dest_dir)
            classifier.classify_by_people(dest_dir)
        
        gui_log_callback("\n照片处理完成！")
        return dest_dir
        
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
    parser = argparse.ArgumentParser(description="智能照片整理工具")
    parser.add_argument('--source', required=True, help='源文件夹路径')
    parser.add_argument('--dest', help='目标文件夹路径')
    parser.add_argument('--skip_country', action='store_true', help='跳过国家分类')
    parser.add_argument('--skip_location', action='store_true', help='跳过地点分类')
    parser.add_argument('--dup_threshold', type=int, default=2, help='重复检测阈值')
    parser.add_argument('--skip_face_recognition', action='store_true', help='跳过人脸识别')
    
    args = parser.parse_args()
    
    try:
        process_photos(
            source_dir=args.source,
            dest_dir=args.dest,
            skip_country=args.skip_country,
            skip_location=args.skip_location,
            dup_threshold=args.dup_threshold,
            skip_face_recognition=args.skip_face_recognition
        )
        return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 