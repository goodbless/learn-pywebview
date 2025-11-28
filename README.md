# Learn PyWebView

这是一个用于学习 PyWebView 的项目。PyWebView 是一个 Python 库，用于使用 Web 技术构建桌面应用程序。

## 什么是 PyWebView？

PyWebView 是一个轻量级的跨平台库，允许你使用 HTML、CSS 和 JavaScript 创建图形用户界面，同时用 Python 处理后端逻辑。它为你的网页内容创建了一个原生的桌面窗口。

## 特性

- 🌐 使用 Web 技术构建 UI（HTML、CSS、JavaScript）
- 🐍 Python 后端逻辑
- 🖥️ 跨平台支持（Windows、macOS、Linux）
- 📦 轻量级且易于使用
- 🔧 与现有 Web 技术栈无缝集成

## 环境要求

- Python 3.10+（推荐 3.10.2）
- 操作系统：Windows、macOS 或 Linux
- 内存：至少 512MB 可用内存
- 磁盘：100MB 可用空间

## 安装

### 快速开始
```bash
# 1. 克隆项目
git clone https://github.com/goodbless/learn-pywebview.git
cd learn-pywebview

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境（Windows）
.venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行文件管理器示例
python file_operations_example.py
```

### 依赖安装
查看 [INSTALL.md](INSTALL.md) 获取详细的安装说明。

## 依赖包

### 核心依赖
- `pywebview==6.1.0` - 桌面应用框架

### 打包依赖
- `pyinstaller>=6.0.0` - 打包为可执行文件

完整依赖列表请查看 [requirements.txt](requirements.txt)。

## 使用示例
pip install pywebview
```

## 基本用法

### 简单的 "Hello World" 示例

```python
import webview

def main():
    window = webview.create_window('Hello World', 'https://pywebview.flowrl.com')
    webview.start()

if __name__ == '__main__':
    main()
```

### 使用本地 HTML 文件

```python
import webview

def main():
    window = webview.create_window('My App', 'index.html')
    webview.start()

if __name__ == '__main__':
    main()
```

### 添加 JavaScript 函数

```python
import webview

def say_hello():
    return 'Hello from Python!'

window = webview.create_window(
    'JS Bridge Example',
    'index.html',
    js_api=say_hello
)
webview.start()
```

## 项目结构

```
learn-pywebview/
├── README.md              # 项目说明
├── CLAUDE.md              # Claude Code 指导文档
├── examples/              # 示例代码目录
│   ├── 01_basic/          # 基础示例
│   ├── 02_js_bridge/      # JavaScript 桥接示例
│   ├── 03_api_server/     # API 服务器示例
│   └── 04_advanced/       # 高级功能示例
├── templates/             # HTML 模板目录
├── static/                # 静态资源目录
└── requirements.txt       # 依赖文件
```

## 学习路径

### 第一阶段：基础概念
1. 创建简单的窗口
2. 加载本地 HTML 文件
3. 窗口基本配置（大小、标题等）

### 第二阶段：JavaScript 交互
1. Python 与 JavaScript 通信
2. 调用 Python 函数
3. 处理异步操作

### 第三阶段：高级功能
1. 多窗口应用
2. 菜单和工具栏
3. 文件对话框
4. 系统集成

### 第四阶段：实战项目
1. 待办事项应用
2. 文件管理器
3. 简单的 IDE

## 运行示例

每个示例都有独立的运行说明，通常步骤如下：

1. 进入示例目录
2. 安装依赖（如果有）
3. 运行 Python 文件

```bash
cd examples/01_basic
python main.py
```

## 参考资源

- [PyWebView 官方文档](https://pywebview.flowrl.com/)
- [PyWebView GitHub 仓库](https://github.com/r0x0r/pywebview)
- [示例集合](https://github.com/r0x0r/pywebview/tree/master/examples)

## 贡献

欢迎提交新的示例和改进建议！如果你有好的学习示例，欢迎提交 Pull Request。

## 许可证

本项目采用 MIT 许可证。