# Photo Organizer AI

一个智能照片整理工具，可以按照国家、时间、城市和地区对照片进行自动分类，并检测重复图片。

## 功能特点

- 多维度照片分类：
  - 首先按国家分类
  - 然后按时间（年/月）整理
  - 最后按城市和地区细分
- 智能地理信息提取：
  - 从照片的 EXIF 数据中提取 GPS 信息
  - 自动解析为具体的地理位置信息
- 重复照片检测：
  - 使用图像哈希算法检测重复照片
  - 自动将重复照片移动到特定文件夹

## 目录结构

整理后的照片将按以下结构组织：

```
organized_photos/
├── China/
│   ├── 2024/
│   │   ├── 01/
│   │   │   ├── Shenzhen/
│   │   │   │   ├── Nanshan/
│   │   │   │   └── Futian/
│   │   │   └── Guangzhou/
│   │   └── 02/
│   └── 2023/
├── Japan/
│   └── 2024/
│       └── 01/
│           └── Tokyo/
└── duplicates/
```

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/Jessie-jzn/photo-organizer-ai.git
cd photo-organizer-ai
```

2. 创建虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

## 使用方法

1. 修改 `src/main.py` 中的源文件夹和目标文件夹路径：

```python
source_dir = "你的照片文件夹路径"
dest_dir = "整理后的目标文件夹路径"
```

2. 运行程序：

```bash
python src/main.py
```

## 项目结构

```
photo-organizer-ai/
├── src/
│   ├── __init__.py
│   ├── main.py              # 主程序入口
│   ├── photo_organizer.py   # 照片整理模块
│   ├── image_classifier.py  # 图片分类模块
│   └── duplicate_detector.py # 重复检测模块
├── requirements.txt         # 项目依赖
└── README.md               # 项目说明
```

## 依赖说明

- Pillow: 图像处理
- imagehash: 图像哈希算法
- python-dateutil: 日期处理
- exifread: EXIF 数据读取
- geopy: 地理编码

## 注意事项

1. 确保照片包含 GPS 信息，否则将被归类到 "unknown" 目录
2. 程序会保持原始照片的文件名
3. 重复照片会被移动到 duplicates 目录

## 许可证

MIT License
