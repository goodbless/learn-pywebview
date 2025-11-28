#!/usr/bin/env python3
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
                return {"success": True, "message": f"文件 {filename} 保存成功"}

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

    def create_html(self):
        """创建包含后端逻辑的 HTML 页面"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyWebView 后端逻辑示例</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }

        .section {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }

        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
        }

        .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin-right: 10px;
            margin-bottom: 10px;
            transition: all 0.3s ease;
        }

        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        }

        .result {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            max-height: 300px;
            overflow-y: auto;
        }

        .message-list {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: #f8f9fa;
        }

        .message {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        .message-header {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }

        .message-content {
            margin-bottom: 10px;
        }

        .message-footer {
            font-size: 0.9em;
            color: #666;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .like-btn {
            background: #ff6b6b;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 0.8em;
        }

        .like-btn:hover {
            background: #ff5252;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .status {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }

        .error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 PyWebView 后端逻辑示例</h1>
            <p>演示 Python 后端与前端 JavaScript 的交互</p>
            <div id="systemInfo" style="margin-top: 20px; text-align: left;"></div>
        </div>

        <div class="grid">
            <div class="section">
                <h2>👤 用户管理</h2>
                <div class="form-group">
                    <label>姓名：</label>
                    <input type="text" id="userName" placeholder="请输入姓名">
                </div>
                <div class="form-group">
                    <label>邮箱：</label>
                    <input type="email" id="userEmail" placeholder="请输入邮箱">
                </div>
                <div class="form-group">
                    <label>年龄：</label>
                    <input type="number" id="userAge" placeholder="请输入年龄">
                </div>
                <button class="btn" onclick="saveUser()">保存用户</button>
                <button class="btn btn-secondary" onclick="getUsers()">查看用户</button>
                <div id="userResult" class="result"></div>
            </div>

            <div class="section">
                <h2>💬 消息板</h2>
                <div class="form-group">
                    <label>你的名字：</label>
                    <input type="text" id="messageAuthor" placeholder="请输入你的名字">
                </div>
                <div class="form-group">
                    <label>消息内容：</label>
                    <textarea id="messageContent" rows="3" placeholder="请输入消息内容..."></textarea>
                </div>
                <button class="btn" onclick="addMessage()">发送消息</button>
                <button class="btn btn-secondary" onclick="loadMessages()">刷新消息</button>
                <div id="messageList" class="message-list"></div>
            </div>
        </div>

        <div class="grid">
            <div class="section">
                <h2>🧮 计算器</h2>
                <div class="form-group">
                    <label>数学表达式：</label>
                    <input type="text" id="expression" placeholder="例如: (10 + 5) * 2 / 3">
                </div>
                <button class="btn" onclick="calculate()">计算</button>
                <div id="calcResult" class="result"></div>
            </div>

            <div class="section">
                <h2>🎨 主题设置</h2>
                <div class="form-group">
                    <label>选择主题：</label>
                    <select id="themeSelect">
                        <option value="default">默认渐变</option>
                        <option value="pink">粉色渐变</option>
                        <option value="blue">蓝色渐变</option>
                        <option value="green">绿色渐变</option>
                    </select>
                </div>
                <button class="btn" onclick="changeTheme()">应用主题</button>
                <div id="themeResult" class="result"></div>
            </div>
        </div>

        <div class="section">
            <h2>📁 文件操作</h2>
            <div class="form-group">
                <label>操作类型：</label>
                <select id="fileOperation">
                    <option value="list">列出文件</option>
                    <option value="read">读取文件</option>
                    <option value="write">写入文件</option>
                </select>
            </div>
            <div class="form-group">
                <label>文件名：</label>
                <input type="text" id="fileName" placeholder="例如: test.txt">
            </div>
            <div class="form-group">
                <label>文件内容（写入时使用）：</label>
                <textarea id="fileContent" rows="5" placeholder="请输入文件内容..."></textarea>
            </div>
            <button class="btn" onclick="fileOperation()">执行操作</button>
            <div id="fileResult" class="result"></div>
        </div>
    </div>

    <script>
        let currentUser = null;

        // 页面加载时获取系统信息
        window.onload = function() {
            getSystemInfo();
            loadMessages();
        };

        // 获取系统信息
        function getSystemInfo() {
            pywebview.api.get_system_info().then(function(result) {
                const info = `
系统信息：
• 平台: ${result.platform}
• 当前时间: ${result.current_time}
• Python版本: ${result.python_version}
• PyWebView版本: ${result.pywebview_version}
                `;
                document.getElementById('systemInfo').innerHTML = `<pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; text-align: left; display: inline-block;">${info}</pre>`;
            });
        }

        // 用户管理
        function saveUser() {
            const name = document.getElementById('userName').value;
            const email = document.getElementById('userEmail').value;
            const age = document.getElementById('userAge').value;

            if (!name || !email || !age) {
                showResult('userResult', '请填写完整信息！', true);
                return;
            }

            pywebview.api.save_user_data(name, email, age).then(function(result) {
                if (result.success) {
                    currentUser = result.user_id;
                    showResult('userResult', `保存成功！用户ID: ${result.user_id}`, false);
                    // 清空表单
                    document.getElementById('userName').value = '';
                    document.getElementById('userEmail').value = '';
                    document.getElementById('userAge').value = '';
                } else {
                    showResult('userResult', `保存失败: ${result.error}`, true);
                }
            });
        }

        function getUsers() {
            pywebview.api.get_user_data().then(function(result) {
                if (Object.keys(result).length === 0) {
                    showResult('userResult', '暂无用户数据', false);
                } else {
                    let output = '用户列表：\\n\\n';
                    for (const [id, user] of Object.entries(result)) {
                        output += `ID: ${id}\\n`;
                        output += `姓名: ${user.name}\\n`;
                        output += `邮箱: ${user.email}\\n`;
                        output += `年龄: ${user.age}\\n`;
                        output += `创建时间: ${user.created_at}\\n\\n`;
                    }
                    showResult('userResult', output, false);
                }
            });
        }

        // 消息板
        function addMessage() {
            const content = document.getElementById('messageContent').value;
            const author = document.getElementById('messageAuthor').value || '匿名用户';

            if (!content) {
                showResult('messageList', '请输入消息内容！', true);
                return;
            }

            pywebview.api.add_message(content, author).then(function(message) {
                document.getElementById('messageContent').value = '';
                loadMessages();
            });
        }

        function loadMessages() {
            pywebview.api.get_messages().then(function(messages) {
                const messageList = document.getElementById('messageList');

                if (messages.length === 0) {
                    messageList.innerHTML = '<p style="text-align: center; color: #666;">暂无消息</p>';
                    return;
                }

                let html = '';
                messages.forEach(msg => {
                    const time = new Date(msg.timestamp).toLocaleString('zh-CN');
                    html += `
                        <div class="message">
                            <div class="message-header">${msg.author}</div>
                            <div class="message-content">${msg.content}</div>
                            <div class="message-footer">
                                <span>${time}</span>
                                <button class="like-btn" onclick="likeMessage('${msg.id}')">👍 ${msg.likes}</button>
                            </div>
                        </div>
                    `;
                });
                messageList.innerHTML = html;
            });
        }

        function likeMessage(messageId) {
            pywebview.api.like_message(messageId).then(function(result) {
                if (result.success) {
                    loadMessages(); // 重新加载消息以更新点赞数
                }
            });
        }

        // 计算器
        function calculate() {
            const expression = document.getElementById('expression').value;

            if (!expression) {
                showResult('calcResult', '请输入数学表达式！', true);
                return;
            }

            pywebview.api.calculate_expression(expression).then(function(result) {
                if (result.success) {
                    showResult('calcResult', `表达式: ${expression}\\n结果: ${result.result}`, false);
                } else {
                    showResult('calcResult', `计算错误: ${result.error}`, true);
                }
            });
        }

        // 主题设置
        function changeTheme() {
            const theme = document.getElementById('themeSelect').value;

            pywebview.api.set_theme(theme).then(function(result) {
                if (result.success) {
                    const themes = {
                        'default': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        'pink': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                        'blue': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                        'green': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
                    };

                    document.body.style.background = themes[theme];
                    showResult('themeResult', `主题已切换为: ${result.theme}`, false);
                }
            });
        }

        // 文件操作
        function fileOperation() {
            const operation = document.getElementById('fileOperation').value;
            const fileName = document.getElementById('fileName').value;
            const fileContent = document.getElementById('fileContent').value;

            if (operation === 'read' && !fileName) {
                showResult('fileResult', '请输入要读取的文件名！', true);
                return;
            }

            if (operation === 'write' && (!fileName || !fileContent)) {
                showResult('fileResult', '请输入文件名和文件内容！', true);
                return;
            }

            pywebview.api.file_operation(operation, fileName, fileContent).then(function(result) {
                if (result.success) {
                    let output = '';
                    if (operation === 'list') {
                        output = '文件列表：\\n\\n';
                        result.files.forEach(file => {
                            output += `• ${file.name} (${file.size} bytes)\\n`;
                        });
                    } else if (operation === 'read') {
                        output = `文件内容：\\n\\n${result.content}`;
                    } else {
                        output = result.message;
                    }
                    showResult('fileResult', output, false);
                } else {
                    showResult('fileResult', `操作失败: ${result.error}`, true);
                }
            });
        }

        // 通用结果显示函数
        function showResult(elementId, message, isError = false) {
            const element = document.getElementById(elementId);
            element.textContent = message;
            element.className = isError ? 'result error' : 'result';
        }

        // 添加键盘快捷键支持
        document.addEventListener('keydown', function(event) {
            if (event.ctrlKey && event.key === 'Enter') {
                // 根据当前焦点元素执行相应操作
                const activeElement = document.activeElement;
                if (activeElement.id === 'expression') {
                    calculate();
                } else if (activeElement.id === 'messageContent') {
                    addMessage();
                } else if (activeElement.id === 'fileContent') {
                    fileOperation();
                }
            }
        });
    </script>
</body>
</html>
        """

    def run(self):
        """运行应用"""
        html_content = self.create_html()

        window = webview.create_window(
            'PyWebView 后端逻辑示例',
            html=html_content,
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

        webview.start()

def main():
    """主函数"""
    app = BackendExample()
    app.run()

if __name__ == '__main__':
    main()