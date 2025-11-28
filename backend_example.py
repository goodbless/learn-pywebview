#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyWebView 后端逻辑示例
演示如何实现 Python 后端逻辑，包括 JavaScript 桥接、文件操作和 API 服务
"""

import webview
import json
import os
import threading
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import uuid

class ApiHandler:
    """API 类，定义前端可以调用的方法"""

    def __init__(self):
        self.user_data = {}
        self.messages = []
        self.current_theme = "default"

    def get_system_info(self):
        """获取系统信息"""
        return {
            "platform": os.name,
            "current_time": datetime.now().isoformat(),
            "python_version": "3.10.2",
            "pywebview_version": "6.1"
        }

    def save_user_data(self, name, email, age):
        """保存用户数据"""
        try:
            user_id = str(uuid.uuid4())
            self.user_data[user_id] = {
                "id": user_id,
                "name": name,
                "email": email,
                "age": int(age),
                "created_at": datetime.now().isoformat()
            }
            return {"success": True, "user_id": user_id, "message": "用户数据保存成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_user_data(self, user_id=None):
        """获取用户数据"""
        if user_id:
            return self.user_data.get(user_id, None)
        return self.user_data

    def add_message(self, content, author="匿名用户"):
        """添加消息"""
        message = {
            "id": str(uuid.uuid4()),
            "content": content,
            "author": author,
            "timestamp": datetime.now().isoformat(),
            "likes": 0
        }
        self.messages.append(message)
        return message

    def get_messages(self):
        """获取所有消息"""
        return sorted(self.messages, key=lambda x: x["timestamp"], reverse=True)

    def like_message(self, message_id):
        """点赞消息"""
        for message in self.messages:
            if message["id"] == message_id:
                message["likes"] += 1
                return {"success": True, "likes": message["likes"]}
        return {"success": False, "error": "消息不存在"}

    def set_theme(self, theme):
        """设置主题"""
        self.current_theme = theme
        return {"success": True, "theme": theme}

    def get_theme(self):
        """获取当前主题"""
        return {"theme": self.current_theme}

    def calculate_expression(self, expression):
        """计算数学表达式"""
        try:
            # 安全计算（仅支持基本运算）
            allowed_chars = set('0123456789+-*/(). ')
            if not all(c in allowed_chars for c in expression):
                return {"success": False, "error": "表达式包含非法字符"}

            result = eval(expression)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def file_operation(self, operation, filename=None, content=None):
        """文件操作"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))

            if operation == "read":
                if not filename:
                    return {"success": False, "error": "请提供文件名"}

                file_path = os.path.join(current_dir, filename)
                if not os.path.exists(file_path):
                    return {"success": False, "error": "文件不存在"}

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"success": True, "content": content}

            elif operation == "write":
                if not filename or not content:
                    return {"success": False, "error": "请提供文件名和内容"}

                file_path = os.path.join(current_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {"success": True, "message": "文件 {} 保存成功".format(filename)}

            elif operation == "list":
                files = []
                for file in os.listdir(current_dir):
                    if file.endswith(('.txt', '.md', '.json', '.html', '.py')):
                        files.append({
                            "name": file,
                            "size": os.path.getsize(os.path.join(current_dir, file))
                        })
                return {"success": True, "files": files}

            else:
                return {"success": False, "error": "不支持的操作"}

        except Exception as e:
            return {"success": False, "error": str(e)}

class BackendExample:
    """后端示例主类"""

    def __init__(self):
        self.api = ApiHandler()

    def run(self):
        """运行应用"""

        window = webview.create_window(
            'PyWebView 后端逻辑示例',
            'backend_example.html',
            width=1200,
            height=800,
            resizable=True,
            min_size=(800, 600),
            js_api=self.api
        )

        print("正在启动 PyWebView 后端示例...")
        print("这个示例展示了：")
        print("1. JavaScript 与 Python 的桥接通信")
        print("2. 用户数据管理")
        print("3. 消息板系统")
        print("4. 文件操作")
        print("5. 主题切换")
        print("6. 数学计算器")
        print("\\n按 Ctrl+C 或关闭窗口退出应用")

        webview.start(debug=True)

def main():
    """主函数"""
    app = BackendExample()
    app.run()

if __name__ == '__main__':
    main()