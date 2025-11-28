#!/usr/bin/env python3
"""
PyWebView 本地 HTML Hello World 示例
使用本地 HTML 文件创建桌面应用
"""

import webview
import os

def main():
    """
    主函数：创建窗口并加载本地 HTML 文件
    """
    # 创建本地 HTML 内容
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hello PyWebView</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: white;
            }
            .container {
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                font-size: 3em;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            p {
                font-size: 1.2em;
                margin-bottom: 30px;
            }
            .btn {
                background: #ff6b6b;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 25px;
                font-size: 1em;
                cursor: pointer;
                transition: background 0.3s;
            }
            .btn:hover {
                background: #ff5252;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Hello PyWebView!</h1>
            <p>这是你的第一个 PyWebView 桌面应用程序</p>
            <button class="btn" onclick="showMessage()">点击我</button>
        </div>

        <script>
            function showMessage() {
                alert('你好！欢迎使用 PyWebView！');
            }
        </script>
    </body>
    </html>
    """

    # 创建窗口并加载 HTML 内容
    window = webview.create_window(
        '本地 Hello World',
        html=html_content,
        width=600,
        height=500,
        resizable=True
    )

    # 启动应用程序
    webview.start()

if __name__ == '__main__':
    main()