#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编辑器依赖检查和安装脚本
"""

import sys
import subprocess
import os

def check_python_version():
    """检查 Python 版本"""
    print("检查 Python 版本...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        print(f"✅ {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ 需要 Python 3.6+，当前版本: {version.major}.{version.minor}")
        return False

def check_package(package_name, import_name=None):
    """检查包是否安装"""
    if import_name is None:
        import_name = package_name
    
    print(f"检查 {package_name}...", end=" ")
    try:
        __import__(import_name)
        print(f"✅ 已安装")
        return True
    except ImportError:
        print(f"❌ 未安装")
        return False

def install_package(package_name):
    """安装包"""
    print(f"安装 {package_name}...", end=" ")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print("✅ 安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ 安装失败")
        return False

def check_pyqt6():
    """检查 PyQt6"""
    return check_package("PyQt6", "PyQt6.QtWidgets")

def check_pygame():
    """检查 Pygame"""
    return check_package("Pygame", "pygame")

def main():
    print("=" * 50)
    print("地图编辑器依赖检查工具")
    print("=" * 50)
    print()
    
    # 检查 Python 版本
    if not check_python_version():
        print("\n❌ Python 版本过低，请升级到 3.6+")
        sys.exit(1)
    
    print()
    print("检查依赖...")
    print()
    
    # 检查必需的包
    pyqt6_ok = check_pyqt6()
    pygame_ok = check_package("json")  # json 是内置的
    
    print()
    
    if not pyqt6_ok:
        print("PyQt6 未安装（推荐安装以使用新编辑器）")
        choice = input("是否现在安装 PyQt6？(y/n): ").strip().lower()
        if choice == 'y':
            install_package("PyQt6")
    
    print()
    print("检查 Pygame（仅在使用旧版编辑器时需要）...")
    pygame_ok = check_pygame()
    
    if not pygame_ok:
        print("Pygame 未安装")
        # 不强制安装 Pygame，因为推荐使用 PyQt6
    
    print()
    print("=" * 50)
    print("依赖检查完成")
    print("=" * 50)
    print()
    
    if pyqt6_ok:
        print("✅ 可以运行 PyQt6 版本编辑器")
        print("   python3 mapEditorQT.py")
        print()
    
    if pygame_ok:
        print("✅ 可以运行 Pygame 版本编辑器")
        print("   python3 mapEditorAdvanced.py")
        print()
    else:
        print("⚠️  如果需要 Pygame 版本，请运行:")
        print("   pip install pygame")
        print()
    
    if pyqt6_ok or pygame_ok:
        print("推荐使用编辑器启动器：")
        print("   python3 editor_launcher.py")
        return 0
    else:
        print("❌ 没有安装任何编辑器依赖")
        return 1

if __name__ == "__main__":
    sys.exit(main())
