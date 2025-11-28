#!/usr/bin/env python3
"""
PyWebView API 服务器示例
演示如何将 PyWebView 与后端 API 服务器集成，实现更复杂的业务逻辑
"""

import webview
import threading
import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sqlite3
import os

class DataDatabase:
    """数据库操作类"""

    def __init__(self):
        self.db_file = "app_data.db"
        self.init_database()

    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')

        # 创建日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_user(self, name, email, age):
        """添加用户"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                (name, email, age)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return {"success": True, "user_id": user_id}
        except sqlite3.IntegrityError:
            return {"success": False, "error": "邮箱已存在"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def get_users(self):
        """获取所有用户"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "age": row[3],
                "created_at": row[4]
            }
            for row in users
        ]

    def add_task(self, title, description, priority="medium"):
        """添加任务"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO tasks (title, description, priority) VALUES (?, ?, ?)",
                (title, description, priority)
            )
            conn.commit()
            task_id = cursor.lastrowid
            return {"success": True, "task_id": task_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def get_tasks(self):
        """获取所有任务"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "priority": row[4],
                "created_at": row[5],
                "completed_at": row[6]
            }
            for row in tasks
        ]

    def update_task_status(self, task_id, status):
        """更新任务状态"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            if status == "completed":
                cursor.execute(
                    "UPDATE tasks SET status = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (status, task_id)
                )
            else:
                cursor.execute(
                    "UPDATE tasks SET status = ?, completed_at = NULL WHERE id = ?",
                    (status, task_id)
                )
            conn.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def add_log(self, level, message):
        """添加日志"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (level, message) VALUES (?, ?)",
            (level, message)
        )
        conn.commit()
        conn.close()

    def get_logs(self, limit=50):
        """获取日志"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM logs ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        logs = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "level": row[1],
                "message": row[2],
                "created_at": row[3]
            }
            for row in logs
        ]

class ApiRequestHandler(BaseHTTPRequestHandler):
    """API 请求处理器"""

    def __init__(self, *args, database=None, **kwargs):
        self.database = database
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        if path == '/api/status':
            self.send_json_response({
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            })
        elif path == '/api/users':
            users = self.database.get_users()
            self.send_json_response(users)
        elif path == '/api/tasks':
            tasks = self.database.get_tasks()
            self.send_json_response(tasks)
        elif path == '/api/logs':
            limit = int(query_params.get('limit', [50])[0])
            logs = self.database.get_logs(limit)
            self.send_json_response(logs)
        elif path == '/api/stats':
            stats = self.get_statistics()
            self.send_json_response(stats)
        else:
            self.send_error(404, "API endpoint not found")

    def do_POST(self):
        """处理 POST 请求"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/users':
            result = self.database.add_user(
                data.get('name'),
                data.get('email'),
                data.get('age')
            )
            self.send_json_response(result)
        elif path == '/api/tasks':
            result = self.database.add_task(
                data.get('title'),
                data.get('description'),
                data.get('priority', 'medium')
            )
            self.send_json_response(result)
        elif path == '/api/logs':
            self.database.add_log(
                data.get('level', 'info'),
                data.get('message')
            )
            self.send_json_response({"success": True})
        else:
            self.send_error(404, "API endpoint not found")

    def do_PUT(self):
        """处理 PUT 请求"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/api/tasks/'):
            task_id = path.split('/')[-1]
            result = self.database.update_task_status(
                task_id,
                data.get('status')
            )
            self.send_json_response(result)
        else:
            self.send_error(404, "API endpoint not found")

    def send_json_response(self, data, status_code=200):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))

    def get_statistics(self):
        """获取统计信息"""
        users = self.database.get_users()
        tasks = self.database.get_tasks()
        logs = self.database.get_logs(10)

        task_stats = {
            "total": len(tasks),
            "pending": len([t for t in tasks if t["status"] == "pending"]),
            "in_progress": len([t for t in tasks if t["status"] == "in_progress"]),
            "completed": len([t for t in tasks if t["status"] == "completed"])
        }

        return {
            "users": {
                "total": len(users)
            },
            "tasks": task_stats,
            "recent_logs": logs
        }

def run_api_server(database, port=8080):
    """运行 API 服务器"""
    def handler(*args, **kwargs):
        return ApiRequestHandler(*args, database=database, **kwargs)

    server = HTTPServer(('localhost', port), handler)
    print(f"API 服务器启动在 http://localhost:{port}")
    server.serve_forever()

class ApiServerExample:
    """API 服务器示例主类"""

    def __init__(self):
        self.database = DataDatabase()
        self.api_port = 8080

    def create_html(self):
        """创建前端 HTML 页面"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyWebView API 服务器集成示例</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .stat-label {{
            color: #666;
            font-size: 1.1em;
        }}

        .section {{
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}

        .form-group {{
            margin-bottom: 15px;
        }}

        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }}

        .form-group input, .form-group textarea, .form-group select {{
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
        }}

        .form-group input:focus, .form-group textarea:focus, .form-group select:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .btn {{
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
        }}

        .btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}

        .btn-secondary {{
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        }}

        .btn-success {{
            background: linear-gradient(45deg, #43e97b, #38f9d7);
        }}

        .data-list {{
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: #f8f9fa;
        }}

        .data-item {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}

        .data-item h4 {{
            color: #667eea;
            margin-bottom: 8px;
        }}

        .data-item p {{
            color: #666;
            margin-bottom: 5px;
        }}

        .data-item .meta {{
            font-size: 0.9em;
            color: #999;
            margin-top: 10px;
        }}

        .task-status {{
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}

        .status-pending {{
            background: #fff3cd;
            color: #856404;
        }}

        .status-in-progress {{
            background: #cce5ff;
            color: #004085;
        }}

        .status-completed {{
            background: #d4edda;
            color: #155724;
        }}

        .priority-low {{
            background: #d1ecf1;
            color: #0c5460;
        }}

        .priority-medium {{
            background: #fff3cd;
            color: #856404;
        }}

        .priority-high {{
            background: #f8d7da;
            color: #721c24;
        }}

        .log-entry {{
            padding: 8px;
            margin-bottom: 5px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.9em;
        }}

        .log-info {{
            background: #d1ecf1;
            border-left: 4px solid #0c5460;
        }}

        .log-warning {{
            background: #fff3cd;
            border-left: 4px solid #856404;
        }}

        .log-error {{
            background: #f8d7da;
            border-left: 4px solid #721c24;
        }}

        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}

        .status-online {{
            background: #28a745;
            animation: pulse 2s infinite;
        }}

        .status-offline {{
            background: #dc3545;
        }}

        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}

        .loading {{
            text-align: center;
            padding: 20px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 PyWebView API 服务器集成示例</h1>
            <p>演示 PyWebView 与后端 API 服务器的完整集成</p>
            <div style="margin-top: 15px;">
                <span class="status-indicator" id="serverStatus"></span>
                <span id="serverStatusText">检查服务器状态...</span>
            </div>
        </div>

        <div class="stats-grid" id="statsGrid">
            <div class="loading">加载统计数据...</div>
        </div>

        <div class="grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div class="section">
                <h2>👥 用户管理</h2>
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
                <button class="btn" onclick="addUser()">添加用户</button>
                <button class="btn btn-secondary" onclick="loadUsers()">刷新用户列表</button>
                <div id="usersList" class="data-list" style="margin-top: 15px;">
                    <div class="loading">点击"刷新用户列表"加载数据</div>
                </div>
            </div>

            <div class="section">
                <h2>📋 任务管理</h2>
                <div class="form-group">
                    <label>任务标题：</label>
                    <input type="text" id="taskTitle" placeholder="请输入任务标题">
                </div>
                <div class="form-group">
                    <label>任务描述：</label>
                    <textarea id="taskDescription" rows="3" placeholder="请输入任务描述"></textarea>
                </div>
                <div class="form-group">
                    <label>优先级：</label>
                    <select id="taskPriority">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </div>
                <button class="btn" onclick="addTask()">添加任务</button>
                <button class="btn btn-secondary" onclick="loadTasks()">刷新任务列表</button>
                <div id="tasksList" class="data-list" style="margin-top: 15px;">
                    <div class="loading">点击"刷新任务列表"加载数据</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📊 系统日志</h2>
            <div style="margin-bottom: 15px;">
                <button class="btn btn-success" onclick="loadLogs()">刷新日志</button>
                <button class="btn" onclick="clearLogs()">清空日志显示</button>
            </div>
            <div id="logsList" class="data-list">
                <div class="loading">点击"刷新日志"加载数据</div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = 'http://localhost:{self.api_port}/api';

        // 页面加载时初始化
        window.onload = function() {{
            checkServerStatus();
            loadStatistics();
            loadUsers();
            loadTasks();
            loadLogs();

            // 定期更新状态
            setInterval(checkServerStatus, 5000);
            setInterval(loadStatistics, 10000);
        }};

        // 检查服务器状态
        async function checkServerStatus() {{
            try {{
                const response = await fetch(`${{API_BASE}}/status`);
                const data = await response.json();

                document.getElementById('serverStatus').className = 'status-indicator status-online';
                document.getElementById('serverStatusText').textContent = `服务器在线 (版本: ${{data.version}})`;
            }} catch (error) {{
                document.getElementById('serverStatus').className = 'status-indicator status-offline';
                document.getElementById('serverStatusText').textContent = '服务器离线';
            }}
        }}

        // 加载统计数据
        async function loadStatistics() {{
            try {{
                const response = await fetch(`${{API_BASE}}/stats`);
                const stats = await response.json();

                const statsGrid = document.getElementById('statsGrid');
                statsGrid.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${{stats.users.total}}</div>
                        <div class="stat-label">用户总数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${{stats.tasks.total}}</div>
                        <div class="stat-label">任务总数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${{stats.tasks.completed}}</div>
                        <div class="stat-label">已完成任务</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${{stats.tasks.pending}}</div>
                        <div class="stat-label">待处理任务</div>
                    </div>
                `;
            }} catch (error) {{
                console.error('加载统计数据失败:', error);
            }}
        }}

        // 用户管理
        async function addUser() {{
            const name = document.getElementById('userName').value;
            const email = document.getElementById('userEmail').value;
            const age = document.getElementById('userAge').value;

            if (!name || !email || !age) {{
                alert('请填写完整的用户信息！');
                return;
            }}

            try {{
                const response = await fetch(`${{API_BASE}}/users`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ name, email, age: parseInt(age) }})
                }});

                const result = await response.json();
                if (result.success) {{
                    alert('用户添加成功！');
                    document.getElementById('userName').value = '';
                    document.getElementById('userEmail').value = '';
                    document.getElementById('userAge').value = '';
                    loadUsers();
                    loadStatistics();
                }} else {{
                    alert('添加失败: ' + result.error);
                }}
            }} catch (error) {{
                alert('添加用户失败: ' + error.message);
            }}
        }}

        async function loadUsers() {{
            try {{
                const response = await fetch(`${{API_BASE}}/users`);
                const users = await response.json();

                const usersList = document.getElementById('usersList');
                if (users.length === 0) {{
                    usersList.innerHTML = '<div style="text-align: center; color: #666;">暂无用户数据</div>';
                    return;
                }}

                let html = '';
                users.forEach(user => {{
                    html += `
                        <div class="data-item">
                            <h4>${{user.name}}</h4>
                            <p>📧 ${{user.email}}</p>
                            <p>🎂 ${{user.age}} 岁</p>
                            <div class="meta">创建时间: ${{new Date(user.created_at).toLocaleString('zh-CN')}}</div>
                        </div>
                    `;
                }});
                usersList.innerHTML = html;
            }} catch (error) {{
                document.getElementById('usersList').innerHTML = '<div style="color: red;">加载用户列表失败</div>';
            }}
        }}

        // 任务管理
        async function addTask() {{
            const title = document.getElementById('taskTitle').value;
            const description = document.getElementById('taskDescription').value;
            const priority = document.getElementById('taskPriority').value;

            if (!title) {{
                alert('请输入任务标题！');
                return;
            }}

            try {{
                const response = await fetch(`${{API_BASE}}/tasks`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ title, description, priority }})
                }});

                const result = await response.json();
                if (result.success) {{
                    alert('任务添加成功！');
                    document.getElementById('taskTitle').value = '';
                    document.getElementById('taskDescription').value = '';
                    document.getElementById('taskPriority').value = 'medium';
                    loadTasks();
                    loadStatistics();
                }} else {{
                    alert('添加失败: ' + result.error);
                }}
            }} catch (error) {{
                alert('添加任务失败: ' + error.message);
            }}
        }}

        async function loadTasks() {{
            try {{
                const response = await fetch(`${{API_BASE}}/tasks`);
                const tasks = await response.json();

                const tasksList = document.getElementById('tasksList');
                if (tasks.length === 0) {{
                    tasksList.innerHTML = '<div style="text-align: center; color: #666;">暂无任务数据</div>';
                    return;
                }}

                let html = '';
                tasks.forEach(task => {{
                    const statusClass = `status-${{task.status.replace('_', '-')}}`;
                    const priorityClass = `priority-${{task.priority}}`;
                    const completedTime = task.completed_at ?
                        `完成时间: ${{new Date(task.completed_at).toLocaleString('zh-CN')}}` : '';

                    html += `
                        <div class="data-item">
                            <h4>${{task.title}}</h4>
                            <p>${{task.description || '无描述'}}</p>
                            <div style="margin: 10px 0;">
                                <span class="task-status ${{statusClass}}">${{getStatusLabel(task.status)}}</span>
                                <span class="task-status ${{priorityClass}}" style="margin-left: 8px;">${{getPriorityLabel(task.priority)}}</span>
                            </div>
                            <div class="meta">
                                创建时间: ${{new Date(task.created_at).toLocaleString('zh-CN')}}<br>
                                ${{completedTime}}
                            </div>
                            <div style="margin-top: 10px;">
                                ${{task.status !== 'completed' ? `<button class="btn btn-success" onclick="updateTaskStatus(${{task.id}}, 'completed')">标记完成</button>` : ''}}
                                ${{task.status === 'pending' ? `<button class="btn" onclick="updateTaskStatus(${{task.id}}, 'in_progress')">开始处理</button>` : ''}}
                            </div>
                        </div>
                    `;
                }});
                tasksList.innerHTML = html;
            }} catch (error) {{
                document.getElementById('tasksList').innerHTML = '<div style="color: red;">加载任务列表失败</div>';
            }}
        }}

        async function updateTaskStatus(taskId, status) {{
            try {{
                const response = await fetch(`${{API_BASE}}/tasks/${{taskId}}`, {{
                    method: 'PUT',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ status }})
                }});

                const result = await response.json();
                if (result.success) {{
                    loadTasks();
                    loadStatistics();
                }} else {{
                    alert('更新失败: ' + result.error);
                }}
            }} catch (error) {{
                alert('更新任务状态失败: ' + error.message);
            }}
        }}

        // 日志管理
        async function loadLogs() {{
            try {{
                const response = await fetch(`${{API_BASE}}/logs?limit=20`);
                const logs = await response.json();

                const logsList = document.getElementById('logsList');
                if (logs.length === 0) {{
                    logsList.innerHTML = '<div style="text-align: center; color: #666;">暂无日志数据</div>';
                    return;
                }}

                let html = '';
                logs.forEach(log => {{
                    const levelClass = `log-${{log.level}}`;
                    html += `
                        <div class="log-entry ${{levelClass}}">
                            <strong>[${{log.level.toUpperCase()}}]</strong> ${{log.message}}
                            <div style="font-size: 0.8em; color: #666; margin-top: 4px;">
                                ${{new Date(log.created_at).toLocaleString('zh-CN')}}
                            </div>
                        </div>
                    `;
                }});
                logsList.innerHTML = html;
            }} catch (error) {{
                document.getElementById('logsList').innerHTML = '<div style="color: red;">加载日志失败</div>';
            }}
        }}

        function clearLogs() {{
            document.getElementById('logsList').innerHTML = '<div style="text-align: center; color: #666;">日志显示已清空</div>';
        }}

        // 辅助函数
        function getStatusLabel(status) {{
            const labels = {{
                'pending': '待处理',
                'in_progress': '处理中',
                'completed': '已完成'
            }};
            return labels[status] || status;
        }}

        function getPriorityLabel(priority) {{
            const labels = {{
                'low': '低优先级',
                'medium': '中优先级',
                'high': '高优先级'
            }};
            return labels[priority] || priority;
        }}
    </script>
</body>
</html>
        """

    def run(self):
        """运行应用"""
        # 在后台线程启动 API 服务器
        api_server_thread = threading.Thread(
            target=run_api_server,
            args=(self.database, self.api_port),
            daemon=True
        )
        api_server_thread.start()

        # 等待服务器启动
        time.sleep(2)

        # 创建 WebView 窗口
        html_content = self.create_html()

        window = webview.create_window(
            'PyWebView API 服务器集成示例',
            html=html_content,
            width=1400,
            height=900,
            resizable=True,
            min_size=(800, 600)
        )

        print("正在启动 PyWebView API 服务器示例...")
        print(f"API 服务器地址: http://localhost:{self.api_port}")
        print("这个示例展示了：")
        print("1. 后端 API 服务器集成")
        print("2. SQLite 数据库操作")
        print("3. RESTful API 设计")
        print("4. 前后端分离架构")
        print("5. 实时数据更新")
        print("6. 用户和任务管理")
        print("\\n按 Ctrl+C 或关闭窗口退出应用")

        webview.start()

def main():
    """主函数"""
    app = ApiServerExample()
    app.run()

if __name__ == '__main__':
    main()