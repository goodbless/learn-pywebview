#!/usr/bin/env python3
"""
PyWebView Hello World 示例
这是最简单的 PyWebView 应用程序，创建一个窗口并加载网页
"""

import webview

def main():
    """
    主函数：创建并显示一个简单的 webview 窗口
    """
    # 创建一个标题为 "Hello PyWebView" 的窗口，加载 PyWebView 官网
    window = webview.create_window(
        'Hello PyWebView',
        'http://argo.philomel.netease.com/#/search/quick-search?project=H72',
        width=800,
        height=600
    )

    # 启动应用程序
    webview.start()

if __name__ == '__main__':
    main()