#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

    def run(self):
        """运行应用"""
        # 使用外部 HTML 文件
        window = webview.create_window(
            'PyWebView 文件管理器',
            'file_operations_example.html',
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
        print("- Ctrl+N: 新建文件")
        print("- Ctrl+R: 刷新")
        print("- Ctrl+F: 搜索")
        print("- Delete: 删除选中项目")
        print("- F2: 重命名选中项目")
        print("\\n按 Ctrl+C 或关闭窗口退出应用")

        webview.start(debug=True)

def main():
    """主函数"""
    app = FileOperationsExample()
    app.run()

if __name__ == '__main__':
    main()