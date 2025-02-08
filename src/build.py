import PyInstaller.__main__
import sys
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 确定是否是 Windows 系统
is_windows = sys.platform.startswith('win')

# PyInstaller 参数
args = [
    os.path.join(current_dir, 'gui.py'),  # 使用完整路径
    '--name=PhotoOrganizer',  # 生成的可执行文件名
    '--onefile',  # 打包成单个文件
    '--windowed',  # 不显示控制台窗口
    '--clean',  # 清理临时文件
    f'--paths={current_dir}',  # 添加源代码目录到 Python 路径
]

# 运行 PyInstaller
PyInstaller.__main__.run(args) 