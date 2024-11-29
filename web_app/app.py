import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import requests
import re
import webbrowser
import json


app = Flask(__name__)

# API Key 和 Secret Key
API_KEY = 'c9z0qNKcD8buZ29bn9OU61JN'
SECRET_KEY = 'gJ5fdTraQ8FblGni5HJJgB7ZHK06bYPv'

# 全局变量：记录最近打开的语言和链接
recent_language = {}

# 获取 Access Token
def get_access_token():
    url = 'https://aip.baidubce.com/oauth/2.0/token'
    params = {
        'grant_type': 'client_credentials',
        'client_id': API_KEY,
        'client_secret': SECRET_KEY
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print("获取 Access Token 失败，状态码：", response.status_code)
        raise Exception('获取 Access Token 失败')

# 调用文心一言接口
def call_wenxin(prompt, extract_links=False):
    access_token = get_access_token()
    url = f'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.7,
        'max_tokens': 1024,
        'top_p': 0.95,
        'frequency_penalty': 0,
        'presence_penalty': 0
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json().get('result', '')
        print("大模型返回结果：", result)

        if extract_links:
            # 提取 Markdown 链接格式中的链接部分
            links = re.findall(r'\[.*?\]\((https?://[^\s]+)\)', result)
            print("提取到的链接：", links)
            return links[0] if links else None
        else:
            # 返回自然语言回复并处理换行
            return result.replace("\n", "<br>")
    else:
        print("大模型请求失败，状态码：", response.status_code)
        return None

# 笔记存储函数
def save_note_to_file(title, source_url, content):
    # 替换 HTML 换行符 <br> 为 Markdown 换行符 \n
    content = content.replace("<br>", "\n")

    # 创建 notes 文件夹
    notes_dir = os.path.join(os.getcwd(), "notes")
    os.makedirs(notes_dir, exist_ok=True)

    # 文件路径
    file_name = f"{datetime.now().strftime('%Y-%m-%d')}-{title}.md"
    file_path = os.path.join(notes_dir, file_name)

    # 文件内容
    note_content = f"""# {title}

**日期**: {datetime.now().strftime('%Y-%m-%d')}  
**来源**: {source_url}  

## 总结内容
{content}
"""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(note_content)

    return file_path

# 首页路由
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# 回复路由
@app.route("/reply", methods=["POST"])
def reply():
    user_input = request.json.get("user_input")
    mode = request.json.get("mode", "assistant")  # 默认模式为助手模式

    if user_input:
        if mode == "conversation":
            # 对话模式：直接调用大模型，返回普通对话内容
            prompt = f"用户输入：{user_input}，请根据上下文生成自然语言回复。"
            response = call_wenxin(prompt, extract_links=False)  # 不提取链接
            if response:
                return jsonify({"reply": response})
            else:
                return jsonify({"reply": "抱歉，我无法理解您的问题。"})

        elif mode == "assistant":
            # 判断是否是打开笔记本的需求
            if re.search(r"(打开笔记本|查看笔记|看看笔记)", user_input.strip(), re.IGNORECASE):
                return jsonify({"reply": "<a href='/notes' target='_blank'>点击此处查看笔记本</a>"})

            # 判断是否是记录笔记的需求
            if re.search(r"(总结|帮我总结|生成总结)", user_input.strip(), re.IGNORECASE):
                # 检测是否提供了 URL
                url_match = re.search(r"(https?://[^\s]+)", user_input)
                if url_match:
                    # 用户提供了 URL
                    source_url = url_match.group(1)
                    prompt = f"请总结以下网页内容的核心知识点，生成适合学习的笔记，注意内容要条理清晰且简洁。\n网页链接：{source_url}"
                elif recent_language:
                    # 没有提供 URL，但有最近打开的语言
                    language, source_url = list(recent_language.items())[-1]
                    prompt = f"请总结关于 {language} 的学习知识点，基于以下链接内容生成适合学习的笔记，条理清晰且简洁。\n网页链接：{source_url}"
                else:
                    return jsonify({"reply": "抱歉，我没有找到可以总结的内容。请提供相关链接或先打开教程。"})

                # 调用大模型生成笔记
                note_content = call_wenxin(prompt, extract_links=False)
                if note_content:
                    # 调用大模型生成标题
                    title_prompt = f"根据以下内容生成一个简短的标题，概括核心主题：\n{note_content[:500]}"
                    title = call_wenxin(title_prompt, extract_links=False)
                    if not title:
                        title = "未命名笔记"  # 如果标题生成失败，使用默认值

                    # 保存笔记
                    file_path = save_note_to_file(title.strip(), source_url, note_content)
                    return jsonify({"reply": f"总结已生成并记录成功，存储路径：{file_path}"})
                else:
                    return jsonify({"reply": "生成总结失败，请稍后重试。"})

            # 如果不是记录笔记，执行之前的功能（如打开菜鸟教程）
            languages = [
                "Python", "C", "Java", "JavaScript", "Go", "Ruby", "HTML", "CSS",
                "C++", "C#", "PHP", "Perl", "Swift", "Kotlin", "R", "Scala",
                "Lua", "Rust", "Dart", "TypeScript", "Shell", "SQL", "MATLAB",
                "Fortran", "Assembly"
            ]
            user_input_lower = user_input.lower()
            target_language = next((lang for lang in languages if lang.lower() in user_input_lower), None)

            if target_language:
                # 打开教程
                prompt = f"请提供学习 {target_language} 的菜鸟教程的具体链接，链接应直接跳转到对应语言的教程页面，并以 Markdown 链接格式 [文字](链接) 返回。"
                tutorial_link = call_wenxin(prompt, extract_links=True)  # 提取链接
                if tutorial_link:
                    # 记录最近打开的语言和链接
                    recent_language[target_language] = tutorial_link
                    webbrowser.open(tutorial_link)
                    return jsonify({"reply": f"为您打开 {target_language} 教程：<a href='{tutorial_link}' target='_blank'>{tutorial_link}</a>"})
                else:
                    return jsonify({"reply": f"抱歉，我未能找到 {target_language} 的教程链接。"})

            # 普通对话逻辑
            prompt = f"用户输入：{user_input}，请根据上下文生成自然语言回复。"
            response = call_wenxin(prompt, extract_links=False)
            if response:
                return jsonify({"reply": response})
            else:
                return jsonify({"reply": "抱歉，我无法理解您的问题。"})

    return jsonify({"error": "无效的输入"}), 400

@app.route("/notes", methods=["GET"])
def notes():
    # 获取笔记文件夹中的所有 Markdown 文件
    notes_dir = os.path.join(os.getcwd(), "notes")
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)

    # 获取文件列表
    files = [f for f in os.listdir(notes_dir) if f.endswith(".md")]
    return render_template("notes.html", files=files)


@app.route("/notes/<filename>", methods=["GET"])
def get_note_content(filename):
    # 获取指定文件的内容
    notes_dir = os.path.join(os.getcwd(), "notes")
    file_path = os.path.join(notes_dir, filename)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return jsonify({"content": content})
    else:
        return jsonify({"error": "文件不存在"}), 404

if __name__ == '__main__':
    app.run(debug=True)
