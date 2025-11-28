#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWebView 文件管理器打包脚本
使用 PyInstaller 将应用打包为单一可执行文件
"""

import os
import sys
import subprocess
import shutil

def main():
    """主打包函数"""
    print("PyWebView 文件管理器打包工具")
    print("=" * 50)

    # 检查虚拟环境
    if not os.path.exists('.venv'):
        print("错误: 未找到虚拟环境 .venv")
        print("请先创建虚拟环境: python -m venv .venv")
        return False

    # 激活虚拟环境路径
    if sys.platform == 'win32':
        python_exe = os.path.join('.venv', 'Scripts', 'python.exe')
        pip_exe = os.path.join('.venv', 'Scripts', 'pip.exe')
    else:
        python_exe = os.path.join('.venv', 'bin', 'python')
        pip_exe = os.path.join('.venv', 'bin', 'pip')

    # 检查 Python 可执行文件
    if not os.path.exists(python_exe):
        print(f"错误: 未找到 Python 可执行文件: {python_exe}")
        return False

    print(f"使用 Python: {python_exe}")

    # 检查是否安装了 pyinstaller
    print("检查 PyInstaller...")
    try:
        result = subprocess.run([pip_exe, 'show', 'pyinstaller'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("安装  安装 PyInstaller...")
            install_result = subprocess.run([pip_exe, 'install', 'pyinstaller'],
                                          capture_output=True, text=True)
            if install_result.returncode != 0:
                print("错误 PyInstaller 安装失败:")
                print(install_result.stderr)
                return False
            print("成功 PyInstaller 安装成功")
        else:
            print("成功 PyInstaller 已安装")
    except Exception as e:
        print(f"错误 检查 PyInstaller 时出错: {e}")
        return False

    # 清理之前的构建
    print("清理之前的构建文件...")
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   删除 {folder}/")

    # 运行 PyInstaller
    print("开始打包...")
    print("   这可能需要几分钟时间...")

    try:
        cmd = [python_exe, '-m', 'PyInstaller', 'file_operations_example.spec', '--clean']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("成功 打包成功！")

            # 检查生成的文件
            exe_path = os.path.join('dist', 'PyWebViewFileManager.exe')
            if os.path.exists(exe_path):
                file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
                print(f"可执行文件: {exe_path}")
                print(f"文件大小: {file_size:.1f} MB")
                print("\n打包完成！")
                print("提示:")
                print("   - 首次运行可能需要一些时间")
                print("   - 文件大小较大是正常的（包含了所有依赖）")
                print("   - 可以将 exe 文件复制到其他 Windows 电脑上运行")
            else:
                print("警告  警告: 找不到生成的可执行文件")
                return False
        else:
            print("错误 打包失败:")
            print(result.stdout)
            print(result.stderr)
            return False

    except Exception as e:
        print(f"错误 打包过程中出错: {e}")
        return False

    return True

if __name__ == '__main__':
    success = main()
    if success:
        input("\n按 Enter 键退出...")
    else:
        input("\n打包失败，按 Enter 键退出...")
        sys.exit(1)