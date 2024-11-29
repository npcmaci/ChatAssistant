# Chat Assistant

这是一个基于 Flask和文心一言的学习助手项目，支持以下功能：

1. 大模型基本的聊天问答功能
2. 调用大模型打开语言教程链接。
3. 总结并存储网页内容到本地 Markdown 文件作为笔记。
4. 笔记本查看功能，包括 Markdown 渲染及侧边栏显示文件列表。

---

## 环境配置

### 使用 pip
1. **创建虚拟环境**：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows 使用 venv\Scripts\activate
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

### 使用 Conda
1. **创建环境**：
   ```bash
   conda env create -f environment.yml
   ```

2. **激活环境**：
   ```bash
   conda activate <environment-name>
   ```
   `environment-name` 是 `environment.yml` 文件中的 `name` 字段。

---

## 项目运行

1. **激活虚拟环境**：
   - 使用 pip 创建的虚拟环境：
     ```bash
     source venv/bin/activate  # Windows 使用 venv\Scripts\activate
     ```
   - 使用 Conda 创建的虚拟环境：
     ```bash
     conda activate <environment-name>
     ```

2. **运行项目**：
   ```bash
   python app.py
   ```

3. **访问项目**：
   在浏览器中打开以下地址：
   ```
   http://127.0.0.1:5000/
   ```

---

## 项目结构

```
项目根目录
│
├── app.py                 # 项目主应用
├── requirements.txt       # pip 环境依赖文件
├── environment.yml        # Conda 环境依赖文件
├── notes/                 # 笔记存储目录
│   ├── 示例笔记1.md
│   ├── 示例笔记2.md
│   └── ...
├── templates/
│   ├── index.html         # 主界面模板
│   ├── notes.html         # 笔记本模板
│   └── ...
└── static/                # 静态文件目录
    ├── css/
    ├── js/
    └── ...
```

---

## 功能展示

### 打开语言教程
用户输入「学习 Python」，系统会自动打开菜鸟教程对应的 Python 页面，并返回链接。

### 总结笔记
用户可以选择自动总结网页内容，生成 Markdown 格式的笔记，并存储在 `notes/` 文件夹。

### 查看笔记
访问 `/notes` 页面，可在侧边栏中选择笔记文件，主界面展示对应的 Markdown 内容。

---

## 注意事项

1. **API Key 配置**：
   在 `app.py` 中替换为您自己的 API Key：
   ```python
   API_KEY = 'your_api_key'
   SECRET_KEY = 'your_secret_key'
   ```

2. **项目依赖**：
   请确保按照上述环境配置步骤安装依赖。

3. **数据存储**：
   所有生成的笔记存储在项目根目录下的 `notes/` 文件夹中。
