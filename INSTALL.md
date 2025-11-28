# 安装指南

## 快速安装

### 1. 创建虚拟环境
```bash
# 使用 Python 3.10+
python -m venv .venv

# Windows 激活
.venv\Scripts\activate

# Linux/Mac 激活
source .venv/bin/activate
```

### 2. 安装依赖
```bash
# 基础运行依赖
pip install -r requirements.txt

# 或安装完整开发依赖
pip install -r requirements-dev.txt
```

### 3. 运行应用
```bash
python file_operations_example.py
```

## 可选：打包为可执行文件

```bash
# 安装打包工具
pip install pyinstaller

# 使用 spec 文件打包
pyinstaller file_operations_example.spec

# 或使用自动化脚本
python build.py
```

## 依赖说明

### 核心依赖
- `pywebview==6.1.0` - 桌面应用框架

### 可选依赖
- `pyinstaller>=6.0.0` - 打包为可执行文件
- `pywin32>=306` - Windows API 访问
- `psutil>=5.9.0` - 系统信息获取

### 开发工具
- `pytest` - 单元测试
- `flake8` - 代码检查
- `black` - 代码格式化

## 系统要求

- **操作系统**: Windows 10/11, Linux, macOS
- **Python**: 3.10 或更高版本
- **内存**: 至少 512MB 可用内存
- **磁盘**: 100MB 可用空间

## 故障排除

### 常见问题

1. **ModuleNotFoundError: No module named 'webview'**
   ```bash
   pip install pywebview
   ```

2. **打包时缺少依赖**
   ```bash
   pip install pyinstaller
   ```

3. **Windows 权限问题**
   - 以管理员身份运行命令提示符

4. **中文显示问题**
   - 确保终端支持 UTF-8 编码

## 更多信息

- 查看 [BUILD_README.md](BUILD_README.md) 了解打包详情
- 查看 [README.md](README.md) 了解项目信息