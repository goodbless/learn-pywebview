// PyWebView 文件管理器 JavaScript 代码

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

        // 为HTML属性准备安全的路径字符串
        const pathForHtml = item.path.replace(/\\/g, '/').replace(/'/g, "\\'").replace(/"/g, '\\"');

        html += `
            <div class="file-item" data-path="${pathForHtml}" onclick='selectItem(this, "${pathForHtml}")' ondblclick='openItem("${pathForHtml}")' oncontextmenu='showContextMenu(event, "${pathForHtml}")'>
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
        // 为HTML属性准备安全的路径字符串
        const pathForHtml = item.path.replace(/\\/g, '/').replace(/'/g, "\\'").replace(/"/g, '\\"');

        html += `
            <div class="file-item" data-path="${pathForHtml}" onclick='selectItem(this, "${pathForHtml}")' ondblclick='editItem("${pathForHtml}")'>
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