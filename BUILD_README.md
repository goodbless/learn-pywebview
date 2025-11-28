# PyWebView 文件管理器 - 打包指南

## 快速打包

### 方法一：使用打包脚本（推荐）

```bash
# 运行自动打包脚本
python build.py
```

### 方法二：手动打包

```bash
# 1. 激活虚拟环境
.venv\Scripts\activate

# 2. 安装 PyInstaller（如果未安装）
pip install pyinstaller

# 3. 运行打包命令
pyinstaller file_operations_example.spec

# 4. 可执行文件将在 dist 文件夹中
```

## 配置说明

### spec 文件特性

- **单一可执行文件**: 打包为单个 `.exe` 文件
- **包含所有依赖**: HTML、CSS、JS 文件都打包进 exe
- **隐藏控制台**: `console=False`，不显示黑色控制台窗口
- **应用信息**: 包含版本信息和文件描述
- **自动压缩**: 使用 UPX 压缩减小文件大小

### 输出文件

- **可执行文件名**: `PyWebViewFileManager.exe`
- **输出目录**: `dist/`
- **文件大小**: 约 50-100MB（正常）

## 自定义配置

### 修改应用图标

1. 准备一个 `icon.ico` 文件（256x256 像素）
2. 放在项目根目录下
3. 重新打包

```bash
# 或者指定自定义图标
pyinstaller file_operations_example.spec --icon=my_icon.ico
```

### 修改应用信息

编辑 `file_operations_example.spec` 中的版本信息部分：

```python
StringStruct(u'FileDescription', u'我的文件管理器'),
StringStruct(u'CompanyName', u'我的公司'),
StringStruct(u'FileVersion', u'1.0.0.0'),
```

## 常见问题

### 打包失败

- 确保在虚拟环境中打包
- 检查是否有足够的磁盘空间
- 关闭杀毒软件重试

### 运行时错误

- 首次运行较慢是正常的
- 确保目标系统有足够的权限
- 检查是否缺少系统运行库

### 文件过大

- 可以排除不需要的模块来减小大小
- UPX 压缩可以有效减小文件大小
- 这是 Python 应用的正常现象

## 分发

打包完成后，只需分发 `dist/PyWebViewFileManager.exe` 文件即可：

- ✅ 不需要安装 Python
- ✅ 不需要安装依赖库
- ✅ 不需要虚拟环境
- ✅ 可以直接运行

## 技术细节

### 包含的主要依赖

- `pywebview`: Web 框架
- `bottle`: Web 服务器
- `webview.platforms`: 平台支持
- Windows 系统库和编码支持

### 排除的模块

为了减小文件大小，排除了以下模块：
- 科学计算库（numpy, scipy, pandas）
- 图像处理库（PIL）
- GUI 库（tkinter）
- 测试框架（unittest）

## 支持的平台

- ✅ Windows 10/11（主要目标）
- ⚠️ Linux/macOS（需要修改配置）