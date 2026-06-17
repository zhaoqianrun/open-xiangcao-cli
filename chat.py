# ---- 颜色设置 ----
GREEN = "\033[92m"
BLUE  = "\033[94m"
RESET = "\033[0m"

_orig_print = print
def green_print(*args, sep=' ', end='\n', file=None, flush=False):
    _orig_print(GREEN, end='', file=file, flush=False)
    _orig_print(*args, sep=sep, end='', file=file, flush=False)
    _orig_print(RESET, end=end, file=file, flush=flush)
print = green_print

_orig_input = input
def blue_input(prompt=''):
    _orig_print(BLUE, end='')
    _orig_print(prompt, end='')
    _orig_print(RESET, end='')
    return _orig_input()
input = blue_input
# ---- 结束 ----

print("/exit退出并保存，/help查看帮助，/models管理模型（list/install/del/change）")
import readline  
import json
import requests
import os
import time
import socket
import subprocess
import datetime
import urllib.request

models_dir = "./models/"
os.makedirs(models_dir, exist_ok=True)

mdls = [f for f in os.listdir(models_dir) if f.endswith(".gguf")]
model_name = None
model_path = None

if not mdls:
    print("没有模型哦，请使用 /models install 安装")
else:
    for idx, name in enumerate(mdls, 1):
        print(f"{idx}. {name}")
    choice = int(input("请选择模型序号: ")) - 1
    model_name = mdls[choice]
    model_path = os.path.join(models_dir, model_name)
    print(f"已选择模型: {model_name}\n")

    subprocess.run(["pkill", "-9", "llama-server"], stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    subprocess.Popen(
        ["llama-server", "-m", model_path, "--host", "127.0.0.1", "--port", "5867"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def wait_for_server(host="127.0.0.1", port=5867, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            sock = socket.socket()
            sock.connect((host, port))
            sock.close()
            return True
        except:
            time.sleep(0.3)
    return False

if model_path and not wait_for_server():
    print("服务器启动失败")
    exit(1)

url = "http://127.0.0.1:5867/v1/chat/completions"
save_file = "chat_history.json"
INIT_SYSTEM = "你是一个乐于助人的助手。输入 /exit 退出并保存，/help 查看帮助，/models 管理模型（list/install/del/change）"

# ========== 修复：加载历史，若文件不存在或损坏则创建空数组 ==========
if os.path.exists(save_file):
    try:
        with open(save_file, "r") as f:
            messages = json.load(f)
    except (json.JSONDecodeError, IOError):
        # 文件损坏，重置为空列表
        messages = []
else:
    messages = []

# 确保至少有一条系统消息
if not messages or messages[0].get("role") != "system":
    messages.insert(0, {"role": "system", "content": INIT_SYSTEM})

# 立即写入文件（创建或覆盖）
with open(save_file, "w") as f:
    json.dump(messages, f, indent=2, ensure_ascii=False)
# ============================================================

def get_context_info():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"当前时间：{now}"
def is_server_alive():
    """检查 llama-server 是否还活着"""
    try:
        sock = socket.socket()
        sock.connect(("127.0.0.1", 5867))
        sock.close()
        return True
    except:
        return False

def restart_server():
    """重启 llama-server 并等待就绪"""
    print("检测到服务器无响应，正在重启...")
    subprocess.run(["pkill", "-9", "llama-server"], stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    subprocess.Popen(
        ["llama-server", "-m", model_path, "--host", "127.0.0.1", "--port", "5867"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return wait_for_server()

# 预热模型（可选）
if model_name:
    try:
        requests.post(url, json={"model": model_name, "messages": [{"role": "user", "content": "sys:loading model"}]}, timeout=60)
    except:
        pass

while True:
    user = input("\n你: \n").strip()
    if user == "/exit":
        with open(save_file, "w") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        print("再见")
        break

    if user == "/help":
        print("""
命令说明：
/exit       退出并保存当前对话
/help       显示本帮助
/models     管理模型（进入子菜单）
  /models list       列出本地已有模型
  /models install    安装新模型（交互式输入URL和名称）
  /models del <序号> 删除指定序号的模型（例：/models del 2）
  /models change     切换当前使用的模型（列表选择）
注：首次安装模型后需重启程序才能生效；change命令可即时切换
""")
        continue

    if user.startswith("/models"):
        parts = user.split()
        if len(parts) == 1 or parts[1] == "list":
            mdls = [f for f in os.listdir(models_dir) if f.endswith(".gguf")]
            if not mdls:
                print("本地没有模型，请使用 /models install 安装")
            else:
                print("本地模型列表：")
                for idx, name in enumerate(mdls, 1):
                    print(f"{idx}. {name}")
        elif parts[1] == "install":
            url_input = input("输入.gguf模型文件的url: ")
            name_input = input("输入模型名称: ")
            if not name_input.endswith(".gguf"):
                name_input += ".gguf"
            target_path = os.path.join(models_dir, name_input)
            print("开始下载了...")
            try:
                urllib.request.urlretrieve(url_input, target_path)
                print(f"完成，已保存到 {target_path}")
                print("提示：新模型已下载，请使用 /models list 查看，需要重启程序才能使用")
                mdls = [f for f in os.listdir(models_dir) if f.endswith(".gguf")]
            except Exception as e:
                print(f"下载失败: {e}")
        elif parts[1] == "del" and len(parts) == 3:
            try:
                idx_del = int(parts[2]) - 1
                mdls = [f for f in os.listdir(models_dir) if f.endswith(".gguf")]
                if 0 <= idx_del < len(mdls):
                    to_del = mdls[idx_del]
                    confirm = input(f"确定删除模型 {to_del} 吗？(y/n): ")
                    if confirm.lower() == 'y':
                        os.remove(os.path.join(models_dir, to_del))
                        print(f"已删除 {to_del}")
                        if model_name and to_del == model_name:
                            print("警告：你删除了当前正在使用的模型，程序将退出，请重新启动并选择其他模型")
                            exit(1)
                    else:
                        print("取消删除")
                else:
                    print("序号无效")
            except Exception as e:
                print(f"删除失败: {e}")
        elif parts[1] == "change":
            mdls = [f for f in os.listdir(models_dir) if f.endswith(".gguf")]
            if not mdls:
                print("没有本地模型，请先使用 /models install 安装")
                continue

            print("本地模型列表：")
            for idx, name in enumerate(mdls, 1):
                print(f"{idx}. {name}")

            try:
                choice = int(input("请选择要切换的模型序号: ")) - 1
                if choice < 0 or choice >= len(mdls):
                    print("序号无效")
                    continue
                new_model_name = mdls[choice]
                new_model_path = os.path.join(models_dir, new_model_name)
            except ValueError:
                print("请输入有效数字")
                continue

            # 停止当前服务器
            subprocess.run(["pkill", "-9", "llama-server"], stderr=subprocess.DEVNULL)
            time.sleep(0.5)

            # 更新全局模型变量
            model_name = new_model_name
            model_path = new_model_path

            # 启动新模型服务器
            subprocess.Popen(
                ["llama-server", "-m", model_path, "--host", "127.0.0.1", "--port", "5867"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            if not wait_for_server():
                print("服务器启动失败，请检查模型文件或稍后重试")
                model_name = None
                model_path = None
                continue

            # 预热
            try:
                requests.post(url, json={"model": model_name, "messages": [{"role": "user", "content": "sys:loading model"}]}, timeout=60)
            except:
                pass

            print(f"已切换至模型: {model_name}")
        else:
            print("无效的 /models 子命令。用法：/models list 或 /models install 或 /models del <序号> 或 /models change")
        continue

    if model_name is None:
        print("请先安装模型并使用 /models list 查看，然后重启程序并选择模型")
        continue

    # 正常对话：将原始用户消息加入永久历史（不加时间）
    messages.append({"role": "user", "content": user})

    # 确保服务器存活
    if not is_server_alive():
        if not restart_server():
            print("服务器重启失败，请手动检查")
            messages.pop()  # 移除刚添加的用户消息
            continue

    # ----- 关键：构造临时消息，实时注入时间和天气（不污染历史）-----
    temp_messages = messages.copy()
    # 找到最后一个 user 消息（就是我们刚刚添加的），修改其 content 追加实时信息
    for i in range(len(temp_messages) - 1, -1, -1):
        if temp_messages[i]["role"] == "user":
            context = get_context_info()
            temp_messages[i]["content"] = temp_messages[i]["content"] + f"\n\n[系统实时信息：{context}]"
            break

    payload = {
        "model": model_name,
        "messages": temp_messages,   # 使用临时消息（含实时时间）
        "max_tokens": 512,
        "temperature": 0.7,
        "stream": True
    }
    try:
        resp = requests.post(url, json=payload, stream=True, timeout=120)
        if resp.status_code != 200:
            print(f"错误: {resp.status_code} {resp.text}")
            messages.pop()  # 移除刚才添加的用户消息
            continue
        print("助手: ", flush=True)
        full_reply = ""
        for line in resp.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line == "data: [DONE]":
                    break
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        print(content, end="", flush=True)
                        full_reply += content
        print()
        # 将原始 assistant 回复加入永久历史（不含时间）
        messages.append({"role": "assistant", "content": full_reply})
        # 保存永久历史到文件
        with open(save_file, "w") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
    except requests.exceptions.Timeout:
        print("\n请求超时，模型可能卡住了，尝试重启服务器...")
        restart_server()
        messages.pop()  # 移除未完成的用户消息
    except Exception as e:
        print(f"\nError: {e}")
        messages.pop()
