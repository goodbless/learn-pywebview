#!/usr/bin/env python3
"""
PyWebView 本地 HTML 文件示例
演示如何加载本地 HTML 文件并创建功能丰富的桌面应用
"""

import webview
import os

def main():
    """
    主函数：创建窗口并加载本地 HTML 文件
    """

    # 创建窗口配置
    window = webview.create_window(
        'PyWebView 本地文件示例 - 桌面应用',
        'index.html',
        width=1000,
        height=700,
        resizable=True,
        min_size=(800, 600)
    )

    # 启动应用程序
    print("正在启动 PyWebView 应用...")
    print("按 Ctrl+C 或关闭窗口退出应用")

    # 启动 webview
    webview.start()

if __name__ == '__main__':
    main()