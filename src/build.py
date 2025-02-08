import PyInstaller.__main__
import os
import sys

print("当前工作目录:", os.getcwd())
print("Python版本:", sys.version)
print("操作系统:", sys.platform)

# 基本参数
args = [
    'src/gui.py',
    '--name=PhotoOrganizer',
    '--onefile',
    '--windowed',
    '--clean',
    '--distpath=./dist',
    '--workpath=./build',
    '--specpath=.',
]

# macOS 特定参数
if sys.platform == 'darwin':
    args.extend([
        '--osx-bundle-identifier=com.jessie.photoorganizer',
    ])
    
print("\n开始打包...")
print("使用参数:", " ".join(args))

try:
    PyInstaller.__main__.run(args)
    print("\n打包完成！")
    print("输出目录内容:")
    if os.path.exists('dist'):
        print(os.listdir('dist'))
    else:
        print("dist 目录不存在！")
except Exception as e:
    print("\n打包失败:", str(e)) 