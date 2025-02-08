# Photo Organizer AI

一个智能照片整理工具，可以按照国家、时间、城市和地区对照片进行自动分类，并检测重复图片。提供图形界面，操作简单直观。

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
- 图形界面：
  - 简单直观的操作界面
  - 实时显示处理进度
  - 支持自定义选项

## 使用方法

### 方法一：直接使用可执行文件（推荐）

1. 从 [Releases](https://github.com/Jessie-jzn/photo-organizer-ai/releases) 页面下载最新版本
   - Windows 用户下载 `PhotoOrganizer.exe`
   - macOS 用户下载 `PhotoOrganizer.app.zip`

2. 运行程序
   - Windows：双击 `PhotoOrganizer.exe`
   - macOS：解压后双击 `PhotoOrganizer.app`

3. 在程序界面中：
   - 点击"浏览"选择源文件夹（包含要整理的照片的文件夹）
   - 可选：选择目标文件夹（整理后的照片存放位置）
   - 根据需要调整选项：
     - 跳过国家分类：当照片 GPS 信息不准确时建议选择
     - 跳过地点分类：只按时间整理时选择
     - 重复检测阈值：值越小检测越严格（建议范围1-5）
   - 点击"开始处理"按钮
   - 等待处理完成

### 方法二：从源码运行

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

4. 运行程序：

```bash
# 运行图形界面版本（推荐）
python src/gui.py

# 或运行命令行版本
python src/main.py --source "源文件夹路径" --dest "目标文件夹路径" [选项]
```

命令行选项：
- `--source`: 源文件夹路径（必需）
- `--dest`: 目标文件夹路径（可选）
- `--skip_country`: 跳过国家分类
- `--skip_location`: 跳过地点分类
- `--dup_threshold`: 重复检测阈值（默认2）

## 整理后的目录结构

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

## 项目结构

```
photo-organizer-ai/
├── src/
│   ├── __init__.py
│   ├── main.py              # 命令行入口
│   ├── gui.py              # 图形界面入口
│   ├── photo_organizer.py   # 照片整理模块
│   ├── image_classifier.py  # 图片分类模块
│   └── duplicate_detector.py # 重复检测模块
├── requirements.txt         # 项目依赖
└── README.md               # 项目说明
```

## 注意事项

1. 确保照片包含 GPS 信息，否则将被归类到 "unknown" 目录
2. 程序会保持原始照片的文件名
3. 重复照片会被移动到 duplicates 目录
4. 首次运行时可能需要联网获取地理信息
5. 处理大量照片时可能需要较长时间，请耐心等待
6. 建议在处理前备份重要照片

## 常见问题

1. **程序无法启动**
   - 确保已安装所有依赖
   - 检查 Python 版本（建议 3.8 及以上）
   - Windows 用户可能需要安装 Visual C++ Redistributable

2. **照片未按国家分类**
   - 检查照片是否包含 GPS 信息
   - 尝试使用"跳过国家分类"选项

3. **处理速度较慢**
   - 这是正常现象，特别是在处理大量照片时
   - 可以先处理少量照片测试

## 依赖说明

- Pillow: 图像处理
- imagehash: 图像哈希算法
- python-dateutil: 日期处理
- exifread: EXIF 数据读取
- geopy: 地理编码

## 许可证

MIT License
