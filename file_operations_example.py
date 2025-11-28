#!/usr/bin/env python3
"""
PyWebView 文件操作示例
演示如何在 PyWebView 应用中实现文件读写、目录管理等功能
"""

import webview
import os
import json
import shutil
import threading
from datetime import datetime
from pathlib import Path
import mimetypes

class FileManager:
    """文件管理器类"""

    def __init__(self):
        self.current_directory = os.getcwd()
        self.bookmarks = []
        self.recent_files = []
        self.max_recent_files = 10

    def get_current_directory(self):
        """获取当前目录"""
        return {
            "path": self.current_directory,
            "name": os.path.basename(self.current_directory) or self.current_directory
        }

    def list_directory(self, path=None):
        """列出目录内容"""
        try:
            if path:
                if not os.path.exists(path):
                    return {"success": False, "error": "路径不存在"}
                if not os.path.isdir(path):
                    return {"success": False, "error": "不是目录"}
                self.current_directory = path

            items = []
            try:
                for item in os.listdir(self.current_directory):
                    item_path = os.path.join(self.current_directory, item)
                    stat = os.stat(item_path)

                    items.append({
                        "name": item,
                        "path": item_path,
                        "is_directory": os.path.isdir(item_path),
                        "size": stat.st_size if not os.path.isdir(item_path) else 0,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "extension": os.path.splitext(item)[1].lower() if not os.path.isdir(item_path) else ""
                    })
            except PermissionError:
                return {"success": False, "error": "没有访问权限"}

            # 排序：目录在前，然后按名称排序
            items.sort(key=lambda x: (not x["is_directory"], x["name"].lower()))

            return {
                "success": True,
                "directory": self.current_directory,
                "items": items
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def navigate_to_parent(self):
        """导航到父目录"""
        parent = os.path.dirname(self.current_directory)
        if parent and parent != self.current_directory:
            return self.list_directory(parent)
        return self.list_directory()

    def create_directory(self, name):
        """创建目录"""
        try:
            new_dir_path = os.path.join(self.current_directory, name)
            if os.path.exists(new_dir_path):
                return {"success": False, "error": "目录已存在"}

            os.makedirs(new_dir_path)
            return {"success": True, "message": f"目录 '{name}' 创建成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_file(self, name, content=""):
        """创建文件"""
        try:
            file_path = os.path.join(self.current_directory, name)
            if os.path.exists(file_path):
                return {"success": False, "error": "文件已存在"}

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.add_to_recent_files(file_path)
            return {"success": True, "message": f"文件 '{name}' 创建成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_file(self, path):
        """读取文件内容"""
        try:
            if not os.path.exists(path):
                return {"success": False, "error": "文件不存在"}
            if not os.path.isfile(path):
                return {"success": False, "error": "不是文件"}

            # 检查文件大小（限制读取大文件）
            file_size = os.path.getsize(path)
            if file_size > 5 * 1024 * 1024:  # 5MB 限制
                return {"success": False, "error": "文件过大，超过 5MB 限制"}

            # 检查文件类型
            mime_type, _ = mimetypes.guess_type(path)
            if mime_type and not mime_type.startswith('text/') and not mime_type.startswith('application/json'):
                return {"success": False, "error": f"不支持的文件类型: {mime_type}"}

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.add_to_recent_files(path)
            return {
                "success": True,
                "content": content,
                "size": file_size,
                "mime_type": mime_type,
                "encoding": "utf-8"
            }
        except UnicodeDecodeError:
            try:
                with open(path, 'r', encoding='gbk') as f:
                    content = f.read()
                return {
                    "success": True,
                    "content": content,
                    "size": os.path.getsize(path),
                    "mime_type": mime_type,
                    "encoding": "gbk"
                }
            except:
                return {"success": False, "error": "文件编码不支持"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, path, content):
        """写入文件内容"""
        try:
            # 备份原文件
            if os.path.exists(path):
                backup_path = f"{path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(path, backup_path)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.add_to_recent_files(path)
            return {"success": True, "message": "文件保存成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_item(self, path):
        """删除文件或目录"""
        try:
            if not os.path.exists(path):
                return {"success": False, "error": "路径不存在"}

            if os.path.isfile(path):
                os.remove(path)
                return {"success": True, "message": "文件删除成功"}
            elif os.path.isdir(path):
                shutil.rmtree(path)
                return {"success": True, "message": "目录删除成功"}
            else:
                return {"success": False, "error": "未知的文件类型"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def rename_item(self, old_path, new_name):
        """重命名文件或目录"""
        try:
            if not os.path.exists(old_path):
                return {"success": False, "error": "路径不存在"}

            new_path = os.path.join(os.path.dirname(old_path), new_name)
            if os.path.exists(new_path):
                return {"success": False, "error": "目标名称已存在"}

            os.rename(old_path, new_path)
            return {"success": True, "message": "重命名成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def copy_item(self, source_path, destination_dir):
        """复制文件或目录"""
        try:
            if not os.path.exists(source_path):
                return {"success": False, "error": "源路径不存在"}

            if not os.path.exists(destination_dir):
                return {"success": False, "error": "目标目录不存在"}

            item_name = os.path.basename(source_path)
            destination_path = os.path.join(destination_dir, item_name)

            # 处理重名文件
            counter = 1
            original_destination = destination_path
            while os.path.exists(destination_path):
                if os.path.isfile(source_path):
                    name, ext = os.path.splitext(item_name)
                    destination_path = os.path.join(destination_dir, f"{name}_{counter}{ext}")
                else:
                    destination_path = os.path.join(destination_dir, f"{item_name}_{counter}")
                counter += 1

            if os.path.isfile(source_path):
                shutil.copy2(source_path, destination_path)
            else:
                shutil.copytree(source_path, destination_path)

            return {"success": True, "message": f"复制成功到: {destination_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def move_item(self, source_path, destination_dir):
        """移动文件或目录"""
        try:
            if not os.path.exists(source_path):
                return {"success": False, "error": "源路径不存在"}

            if not os.path.exists(destination_dir):
                return {"success": False, "error": "目标目录不存在"}

            item_name = os.path.basename(source_path)
            destination_path = os.path.join(destination_dir, item_name)

            # 处理重名文件
            counter = 1
            original_destination = destination_path
            while os.path.exists(destination_path):
                if os.path.isfile(source_path):
                    name, ext = os.path.splitext(item_name)
                    destination_path = os.path.join(destination_dir, f"{name}_{counter}{ext}")
                else:
                    destination_path = os.path.join(destination_dir, f"{item_name}_{counter}")
                counter += 1

            shutil.move(source_path, destination_path)
            return {"success": True, "message": f"移动成功到: {destination_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_file_info(self, path):
        """获取文件详细信息"""
        try:
            if not os.path.exists(path):
                return {"success": False, "error": "路径不存在"}

            stat = os.stat(path)
            return {
                "success": True,
                "name": os.path.basename(path),
                "path": os.path.abspath(path),
                "size": stat.st_size,
                "is_directory": os.path.isdir(path),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "extension": os.path.splitext(path)[1].lower(),
                "mime_type": mimetypes.guess_type(path)[0]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_files(self, pattern, search_path=None):
        """搜索文件"""
        try:
            if search_path:
                search_dir = search_path
            else:
                search_dir = self.current_directory

            if not os.path.exists(search_dir):
                return {"success": False, "error": "搜索路径不存在"}

            results = []
            pattern = pattern.lower()

            for root, dirs, files in os.walk(search_dir):
                # 限制搜索深度和结果数量
                if len(results) > 100:
                    break

                for file in files:
                    if pattern in file.lower():
                        file_path = os.path.join(root, file)
                        try:
                            stat = os.stat(file_path)
                            results.append({
                                "name": file,
                                "path": file_path,
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                            })
                        except:
                            continue

            return {
                "success": True,
                "results": results,
                "count": len(results),
                "search_path": search_dir
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_to_recent_files(self, file_path):
        """添加到最近文件列表"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)

        self.recent_files.insert(0, file_path)
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]

    def get_recent_files(self):
        """获取最近文件列表"""
        valid_files = []
        for file_path in self.recent_files:
            if os.path.exists(file_path):
                try:
                    stat = os.stat(file_path)
                    valid_files.append({
                        "name": os.path.basename(file_path),
                        "path": file_path,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except:
                    continue

        return {"success": True, "files": valid_files}

    def get_drive_info(self):
        """获取驱动器信息（Windows）"""
        try:
            if os.name == 'nt':
                import psutil
                drives = []
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        drives.append({
                            "name": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": round((usage.used / usage.total) * 100, 1)
                        })
                    except:
                        continue
                return {"success": True, "drives": drives}
            else:
                return {"success": False, "error": "仅在 Windows 系统支持"}
        except ImportError:
            return {"success": False, "error": "需要安装 psutil 库"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class FileOperationsExample:
    """文件操作示例主类"""

    def __init__(self):
        self.file_manager = FileManager()

    def create_html(self):
        """创建文件管理器界面"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyWebView 文件管理器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            height: 100vh;
            overflow: hidden;
        }

        .container {
            display: flex;
            height: 100vh;
        }

        .sidebar {
            width: 250px;
            background: #2c3e50;
            color: white;
            padding: 20px;
            overflow-y: auto;
        }

        .sidebar h2 {
            margin-bottom: 20px;
            font-size: 1.2em;
            color: #ecf0f1;
        }

        .sidebar-item {
            padding: 10px;
            margin-bottom: 5px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }

        .sidebar-item:hover {
            background: #34495e;
        }

        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .toolbar {
            background: white;
            padding: 15px;
            border-bottom: 1px solid #ddd;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }

        .btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }

        .btn:hover {
            background: #2980b9;
        }

        .btn-secondary {
            background: #95a5a6;
        }

        .btn-secondary:hover {
            background: #7f8c8d;
        }

        .btn-danger {
            background: #e74c3c;
        }

        .btn-danger:hover {
            background: #c0392b;
        }

        .path-bar {
            background: white;
            padding: 10px 15px;
            border-bottom: 1px solid #ddd;
            font-size: 14px;
            color: #555;
        }

        .file-list {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        .file-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 15px;
        }

        .file-item {
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
        }

        .file-item:hover {
            background: #ecf0f1;
            transform: translateY(-2px);
        }

        .file-item.selected {
            background: #e8f4fd;
            border-color: #3498db;
        }

        .file-icon {
            font-size: 32px;
            margin-bottom: 5px;
        }

        .file-name {
            font-size: 12px;
            word-break: break-word;
            color: #333;
        }

        .file-size {
            font-size: 10px;
            color: #777;
            margin-top: 2px;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }

        .modal-content {
            background-color: white;
            margin: 10% auto;
            padding: 20px;
            border-radius: 8px;
            width: 80%;
            max-width: 600px;
            max-height: 70vh;
            overflow-y: auto;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }

        .modal-header h3 {
            color: #2c3e50;
        }

        .close {
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            color: #777;
        }

        .close:hover {
            color: #000;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }

        .form-group input, .form-group textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }

        .form-group textarea {
            min-height: 200px;
            font-family: 'Courier New', monospace;
            resize: vertical;
        }

        .search-box {
            flex: 1;
            max-width: 300px;
        }

        .search-box input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .context-menu {
            display: none;
            position: fixed;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            z-index: 1001;
        }

        .context-menu-item {
            padding: 8px 16px;
            cursor: pointer;
            font-size: 14px;
        }

        .context-menu-item:hover {
            background: #ecf0f1;
        }

        .status-bar {
            background: white;
            padding: 8px 15px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #777;
            display: flex;
            justify-content: space-between;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #777;
        }

        .error {
            color: #e74c3c;
            text-align: center;
            padding: 20px;
        }

        .success {
            color: #27ae60;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>📁 文件管理器</h2>
            <div class="sidebar-item" onclick="navigateToHome()">🏠 主目录</div>
            <div class="sidebar-item" onclick="showRecentFiles()">🕐 最近文件</div>
            <div class="sidebar-item" onclick="showDrives()">💾 驱动器</div>
            <div class="sidebar-item" onclick="showSearch()">🔍 搜索文件</div>

            <h2 style="margin-top: 30px;">⚡ 快速操作</h2>
            <div class="sidebar-item" onclick="showCreateFileModal()">📄 新建文件</div>
            <div class="sidebar-item" onclick="showCreateFolderModal()">📁 新建文件夹</div>
        </div>

        <div class="main-content">
            <div class="toolbar">
                <button class="btn" onclick="navigateToParent()">⬆️ 向上</button>
                <button class="btn" onclick="refreshDirectory()">🔄 刷新</button>
                <button class="btn btn-secondary" onclick="showCreateFileModal()">📄 新建文件</button>
                <button class="btn btn-secondary" onclick="showCreateFolderModal()">📁 新建文件夹</button>
                <button class="btn btn-danger" onclick="deleteSelectedItem()">🗑️ 删除</button>
                <button class="btn btn-secondary" onclick="showRenameModal()">✏️ 重命名</button>

                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="搜索文件..." onkeypress="handleSearchKeyPress(event)">
                </div>
                <button class="btn" onclick="searchFiles()">🔍 搜索</button>
            </div>

            <div class="path-bar" id="pathBar">
                当前路径: 加载中...
            </div>

            <div class="file-list" id="fileList">
                <div class="loading">加载文件列表...</div>
            </div>

            <div class="status-bar">
                <span id="statusText">就绪</span>
                <span id="itemCount">0 个项目</span>
            </div>
        </div>
    </div>

    <!-- 创建文件模态框 -->
    <div id="createFileModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>📄 新建文件</h3>
                <span class="close" onclick="closeModal('createFileModal')">&times;</span>
            </div>
            <div class="form-group">
                <label>文件名:</label>
                <input type="text" id="newFileName" placeholder="例如: document.txt">
            </div>
            <div class="form-group">
                <label>初始内容:</label>
                <textarea id="newFileContent" placeholder="输入文件内容..."></textarea>
            </div>
            <button class="btn" onclick="createFile()">创建</button>
            <button class="btn btn-secondary" onclick="closeModal('createFileModal')">取消</button>
        </div>
    </div>

    <!-- 创建文件夹模态框 -->
    <div id="createFolderModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>📁 新建文件夹</h3>
                <span class="close" onclick="closeModal('createFolderModal')">&times;</span>
            </div>
            <div class="form-group">
                <label>文件夹名:</label>
                <input type="text" id="newFolderName" placeholder="例如: New Folder">
            </div>
            <button class="btn" onclick="createFolder()">创建</button>
            <button class="btn btn-secondary" onclick="closeModal('createFolderModal')">取消</button>
        </div>
    </div>

    <!-- 重命名模态框 -->
    <div id="renameModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>✏️ 重命名</h3>
                <span class="close" onclick="closeModal('renameModal')">&times;</span>
            </div>
            <div class="form-group">
                <label>新名称:</label>
                <input type="text" id="renameInput" placeholder="输入新名称">
            </div>
            <button class="btn" onclick="renameItem()">重命名</button>
            <button class="btn btn-secondary" onclick="closeModal('renameModal')">取消</button>
        </div>
    </div>

    <!-- 文件编辑器模态框 -->
    <div id="editorModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="editorTitle">📝 编辑文件</h3>
                <span class="close" onclick="closeModal('editorModal')">&times;</span>
            </div>
            <div class="form-group">
                <textarea id="editorContent" style="min-height: 400px;"></textarea>
            </div>
            <button class="btn" onclick="saveFile()">保存</button>
            <button class="btn btn-secondary" onclick="closeModal('editorModal')">取消</button>
        </div>
    </div>

    <!-- 右键菜单 -->
    <div id="contextMenu" class="context-menu">
        <div class="context-menu-item" onclick="openItem()">📂 打开</div>
        <div class="context-menu-item" onclick="editItem()">✏️ 编辑</div>
        <div class="context-menu-item" onclick="showRenameModal()">🏷️ 重命名</div>
        <div class="context-menu-item" onclick="copyItem()">📋 复制</div>
        <div class="context-menu-item" onclick="moveItem()">✂️ 移动</div>
        <div class="context-menu-item" onclick="showFileInfo()">ℹ️ 属性</div>
        <div class="context-menu-item" onclick="deleteSelectedItem()">🗑️ 删除</div>
    </div>

    <script>
        let currentDirectory = '';
        let selectedItems = [];
        let currentEditingFile = '';

        // 页面加载时初始化
        window.addEventListener('pywebviewready', function() {
            loadDirectory();

            // 点击空白处关闭右键菜单
            document.addEventListener('click', function() {
                document.getElementById('contextMenu').style.display = 'none';
            });

            // 阻止右键菜单默认事件
            document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
            });
        });

        // 加载目录
        async function loadDirectory(path = null) {
            updateStatus('加载目录中...');
            try {
                const result = await pywebview.api.list_directory(path);
                if (result.success) {
                    currentDirectory = result.directory;
                    displayFiles(result.items);
                    updatePath(result.directory);
                    updateItemCount(result.items.length);
                    updateStatus('就绪');
                } else {
                    showError(result.error);
                }
            } catch (error) {
                showError('加载目录失败: ' + error.message);
            }
        }

        // 显示文件列表
        function displayFiles(items) {
            const fileList = document.getElementById('fileList');

            if (items.length === 0) {
                fileList.innerHTML = '<div class="loading">此文件夹为空</div>';
                return;
            }

            let html = '<div class="file-grid">';
            items.forEach(item => {
                const icon = item.is_directory ? '📁' : getFileIcon(item.extension);
                const size = item.is_directory ? '' : formatFileSize(item.size);

                html += `
                    <div class="file-item" data-path="${item.path}" onclick="selectItem(this, '${item.path}')" ondblclick="openItem('${item.path}')" oncontextmenu="showContextMenu(event, '${item.path}')">
                        <div class="file-icon">${icon}</div>
                        <div class="file-name">${item.name}</div>
                        <div class="file-size">${size}</div>
                    </div>
                `;
            });
            html += '</div>';
            fileList.innerHTML = html;
        }

        // 获取文件图标
        function getFileIcon(extension) {
            const icons = {
                '.txt': '📄',
                '.py': '🐍',
                '.js': '📜',
                '.html': '🌐',
                '.css': '🎨',
                '.json': '📋',
                '.md': '📝',
                '.pdf': '📕',
                '.doc': '📘',
                '.docx': '📘',
                '.xls': '📗',
                '.xlsx': '📗',
                '.ppt': '📙',
                '.pptx': '📙',
                '.jpg': '🖼️',
                '.jpeg': '🖼️',
                '.png': '🖼️',
                '.gif': '🖼️',
                '.mp3': '🎵',
                '.mp4': '🎬',
                '.zip': '📦',
                '.rar': '📦',
                '.exe': '⚙️'
            };
            return icons[extension] || '📄';
        }

        // 格式化文件大小
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
        }

        // 选择项目
        function selectItem(element, path) {
            // 清除之前的选择
            document.querySelectorAll('.file-item').forEach(item => {
                item.classList.remove('selected');
            });

            element.classList.add('selected');
            selectedItems = [path];
        }

        // 打开项目
        async function openItem(path = null) {
            const itemPath = path || selectedItems[0];
            if (!itemPath) return;

            try {
                const result = await pywebview.api.get_file_info(itemPath);
                if (result.success && result.is_directory) {
                    loadDirectory(itemPath);
                } else if (result.success && !result.is_directory) {
                    editFile(itemPath);
                } else {
                    showError(result.error);
                }
            } catch (error) {
                showError('打开失败: ' + error.message);
            }
        }

        // 编辑文件
        async function editFile(path) {
            try {
                const result = await pywebview.api.read_file(path);
                if (result.success) {
                    currentEditingFile = path;
                    document.getElementById('editorTitle').textContent = `📝 编辑: ${result.name || path}`;
                    document.getElementById('editorContent').value = result.content;
                    showModal('editorModal');
                } else {
                    showError(result.error);
                }
            } catch (error) {
                showError('读取文件失败: ' + error.message);
            }
        }

        // 保存文件
        async function saveFile() {
            if (!currentEditingFile) return;

            const content = document.getElementById('editorContent').value;
            try {
                const result = await pywebview.api.write_file(currentEditingFile, content);
                if (result.success) {
                    closeModal('editorModal');
                    showSuccess('文件保存成功');
                    loadDirectory();
                } else {
                    showError(result.error);
                }
            } catch (error) {
                showError('保存文件失败: ' + error.message);
            }
        }

        // 导航到父目录
        async function navigateToParent() {
            try {
                const result = await pywebview.api.navigate_to_parent();
                if (result.success) {
                    loadDirectory();
                } else {
                    showError(result.error);
                }
            } catch (error) {
                showError('导航失败: ' + error.message);
            }
        }

        // 导航到主目录
        function navigateToHome() {
            loadDirectory();
        }

        // 刷新目录
        function refreshDirectory() {
            loadDirectory(currentDirectory);
        }

        // 创建文件
        async function createFile() {
            const name = document.getElementById('newFileName').value;
            const content = document.getElementById('newFileContent').value;

            if (!name) {
                showError('请输入文件名');
                return;
            }

            try {
                const result = await pywebview.api.create_file(name, content);
                if (result.success) {
                    closeModal('createFileModal');
                    showSuccess(result.message);
                    loadDirectory();
                } else {
                    showError(result.error);
                }
            } catch (error) {
                showError('创建文件失败: ' + error.message);
            }
        }

        // 创建文件夹
        async function createFolder() {
            const name = document.getElementById('newFolderName').value;

            if (!name) {
                showError('请输入文件夹名');
                return;
            }

            try {
                const result = await pywebview.api.create_directory(name);
                if (result.success) {
                    closeModal('createFolderModal');
                    showSuccess(result.message);
                    loadDirectory();
                } else {
                    showError(result.error);
                }
            } catch (error) {
                showError('创建文件夹失败: ' + error.message);
            }
        }

        // 删除选中项目
        async function deleteSelectedItem() {
            if (selectedItems.length === 0) {
                showError('请先选择要删除的项目');
                return;
            }

            if (!confirm('确定要删除选中的项目吗？此操作不可恢复！')) {
                return;
            }

            try {
                const result = await pywebview.api.delete_item(selectedItems[0]);
                if (result.success) {
                    showSuccess(result.message);
                    selectedItems = [];
                    loadDirectory();
                } else {
                    showError(result.error);
                }
            } catch (error) {
                showError('删除失败: ' + error.message);
            }
        }

        // 重命名
        async function renameItem() {
            const oldPath = selectedItems[0];
            const newName = document.getElementById('renameInput').value;

            if (!oldPath || !newName) {
                showError('请选择项目并输入新名称');
                return;
            }

            try {
                const result = await pywebview.api.rename_item(oldPath, newName);
                if (result.success) {
                    closeModal('renameModal');
                    showSuccess(result.message);
                    selectedItems = [];
                    loadDirectory();
                } else {
                    showError(result.error);
                }
            } catch (error) {
                showError('重命名失败: ' + error.message);
            }
        }

        // 搜索文件
        async function searchFiles() {
            const pattern = document.getElementById('searchInput').value;
            if (!pattern) {
                showError('请输入搜索关键词');
                return;
            }

            updateStatus('搜索中...');
            try {
                const result = await pywebview.api.search_files(pattern, currentDirectory);
                if (result.success) {
                    displaySearchResults(result.results, pattern);
                    updateStatus(`找到 ${result.count} 个结果`);
                } else {
                    showError(result.error);
                }
            } catch (error) {
                showError('搜索失败: ' + error.message);
            }
        }

        // 显示搜索结果
        function displaySearchResults(results, pattern) {
            const fileList = document.getElementById('fileList');

            if (results.length === 0) {
                fileList.innerHTML = `<div class="loading">没有找到包含 "${pattern}" 的文件</div>`;
                return;
            }

            let html = `
                <div style="margin-bottom: 20px;">
                    <h3>搜索结果: ${results.length} 个文件</h3>
                    <button class="btn btn-secondary" onclick="loadDirectory()">返回文件列表</button>
                </div>
                <div class="file-grid">
            `;

            results.forEach(item => {
                const icon = getFileIcon(item.path.split('.').pop());
                html += `
                    <div class="file-item" data-path="${item.path}" onclick="selectItem(this, '${item.path}')" ondblclick="editItem('${item.path}')">
                        <div class="file-icon">${icon}</div>
                        <div class="file-name">${item.name}</div>
                        <div class="file-size">${formatFileSize(item.size)}</div>
                    </div>
                `;
            });

            html += '</div>';
            fileList.innerHTML = html;
        }

        // 显示右键菜单
        function showContextMenu(event, path) {
            event.preventDefault();
            selectItem(event.currentTarget, path);

            const menu = document.getElementById('contextMenu');
            menu.style.display = 'block';
            menu.style.left = event.pageX + 'px';
            menu.style.top = event.pageY + 'px';
        }

        // 编辑选中项目
        function editItem() {
            if (selectedItems.length > 0) {
                editFile(selectedItems[0]);
            }
            document.getElementById('contextMenu').style.display = 'none';
        }

        // 复制项目（简化版）
        function copyItem() {
            if (selectedItems.length > 0) {
                // 这里可以实现复制到剪贴板的功能
                showSuccess('路径已复制到剪贴板: ' + selectedItems[0]);
            }
            document.getElementById('contextMenu').style.display = 'none';
        }

        // 移动项目（简化版）
        function moveItem() {
            showSuccess('移动功能需要目标文件夹选择');
            document.getElementById('contextMenu').style.display = 'none';
        }

        // 显示文件信息
        async function showFileInfo() {
            if (selectedItems.length === 0) return;

            try {
                const result = await pywebview.api.get_file_info(selectedItems[0]);
                if (result.success) {
                    let info = `文件信息:\\n\\n`;
                    info += `名称: ${result.name}\\n`;
                    info += `路径: ${result.path}\\n`;
                    info += `大小: ${formatFileSize(result.size)}\\n`;
                    info += `类型: ${result.is_directory ? '文件夹' : '文件'}\\n`;
                    info += `创建时间: ${new Date(result.created).toLocaleString('zh-CN')}\\n`;
                    info += `修改时间: ${new Date(result.modified).toLocaleString('zh-CN')}\\n`;

                    if (result.extension) {
                        info += `扩展名: ${result.extension}\\n`;
                    }

                    alert(info);
                } else {
                    showError(result.error);
                }
            } catch (error) {
                showError('获取文件信息失败: ' + error.message);
            }
            document.getElementById('contextMenu').style.display = 'none';
        }

        // 工具函数
        function showModal(modalId) {
            document.getElementById(modalId).style.display = 'block';
        }

        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }

        function showCreateFileModal() {
            document.getElementById('newFileName').value = '';
            document.getElementById('newFileContent').value = '';
            showModal('createFileModal');
        }

        function showCreateFolderModal() {
            document.getElementById('newFolderName').value = '';
            showModal('createFolderModal');
        }

        function showRenameModal() {
            if (selectedItems.length === 0) {
                showError('请先选择要重命名的项目');
                return;
            }
            const oldName = selectedItems[0].split(/[\\/]/).pop();
            document.getElementById('renameInput').value = oldName;
            showModal('renameModal');
        }

        function showRecentFiles() {
            // 这里可以实现显示最近文件的功能
            showSuccess('最近文件功能开发中...');
        }

        function showDrives() {
            // 这里可以实现显示驱动器的功能
            showSuccess('驱动器功能开发中...');
        }

        function showSearch() {
            document.getElementById('searchInput').focus();
        }

        function updatePath(path) {
            document.getElementById('pathBar').textContent = `当前路径: ${path}`;
        }

        function updateStatus(text) {
            document.getElementById('statusText').textContent = text;
        }

        function updateItemCount(count) {
            document.getElementById('itemCount').textContent = `${count} 个项目`;
        }

        function showError(message) {
            alert('错误: ' + message);
            updateStatus('错误');
        }

        function showSuccess(message) {
            alert('成功: ' + message);
            updateStatus('操作完成');
        }

        function handleSearchKeyPress(event) {
            if (event.key === 'Enter') {
                searchFiles();
            }
        }

        // 键盘快捷键
        document.addEventListener('keydown', function(event) {
            if (event.ctrlKey || event.metaKey) {
                switch(event.key) {
                    case 'n':
                        event.preventDefault();
                        showCreateFileModal();
                        break;
                    case 'r':
                        event.preventDefault();
                        refreshDirectory();
                        break;
                    case 'f':
                        event.preventDefault();
                        document.getElementById('searchInput').focus();
                        break;
                }
            }

            if (event.key === 'Delete') {
                deleteSelectedItem();
            }

            if (event.key === 'F2') {
                showRenameModal();
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
            'PyWebView 文件管理器',
            html=html_content,
            width=1200,
            height=800,
            resizable=True,
            min_size=(800, 600),
            js_api=self.file_manager
        )

        print("正在启动 PyWebView 文件管理器...")
        print("这个示例展示了：")
        print("1. 文件和目录浏览")
        print("2. 文件创建和编辑")
        print("3. 文件搜索功能")
        print("4. 右键上下文菜单")
        print("5. 键盘快捷键支持")
        print("6. 文件属性查看")
        print("7. 文件操作（删除、重命名等）")
        print("\\n快捷键：")
        print("• Ctrl+N: 新建文件")
        print("• Ctrl+R: 刷新")
        print("• Ctrl+F: 搜索")
        print("• Delete: 删除选中项目")
        print("• F2: 重命名选中项目")
        print("\\n按 Ctrl+C 或关闭窗口退出应用")

        webview.start()

def main():
    """主函数"""
    app = FileOperationsExample()
    app.run()

if __name__ == '__main__':
    main()