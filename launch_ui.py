import os,threading
import sys
import time
import tempfile
import shutil
import tarfile
import requests
import json

def check_and_update(current_version):
    """
    从 GitHub Releases 检查更新，如有新版本则提示并下载安装，同时保留用户数据。
    
    参数:
        current_version: str, 当前本地版本号（如 "1.2"）
    """
    GITHUB_REPO = "zhaoqianrun/open-xiangcao-cli"
    API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    USER_AGENT = "openxc-updater/1.0"

    try:
        # 获取远程最新版本信息
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(API_URL, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        remote_version = data["tag_name"].lstrip("v")
        release_body = data.get("body", "")

        if remote_version == current_version:
            print("已是最新版本。")
            return

        print(f"发现新版本 {remote_version}（当前 {current_version}）")
        if release_body:
            print("\n更新日志:\n" + release_body)

        choice = input("是否更新代码？(y/n/skip): ").strip().lower()
        if choice == 'skip':
            skip_file = os.path.expanduser("~/.openxc_skip")
            with open(skip_file, "w") as f:
                f.write(current_version)
            print("已跳过此版本，下次启动不再提示。")
            return
        if choice != 'y':
            print("已取消更新。")
            return

        # 下载更新包（使用永久链接）
        download_url = f"https://github.com/{GITHUB_REPO}/releases/download/v{remote_version}/update.tar.gz"
        print("正在下载更新包...")
        with tempfile.TemporaryDirectory() as tmpdir:
            update_file = os.path.join(tmpdir, "update.tar.gz")
            resp = requests.get(download_url, stream=True, timeout=30)
            resp.raise_for_status()
            total = int(resp.headers.get('content-length', 0))
            with open(update_file, 'wb') as f:
                downloaded = 0
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            percent = int(100 * downloaded / total)
                            print(f"\r进度: {percent}%", end="")
            print("\n下载完成。")

            # 备份用户数据
            backup_dir = tempfile.mkdtemp()
            user_data_files = ["chat_history.json"]
            user_data_dirs = ["models"]
            try:
                for fname in user_data_files:
                    if os.path.exists(fname):
                        shutil.copy2(fname, os.path.join(backup_dir, fname))
                for dname in user_data_dirs:
                    if os.path.exists(dname):
                        shutil.copytree(dname, os.path.join(backup_dir, dname))
            except Exception as e:
                print(f"备份用户数据失败: {e}")
                return

            # 解压更新包
            try:
                with tarfile.open(update_file, "r:gz") as tar:
                    tar.extractall(path=".", filter='data')
                print("代码更新完成。")
            except Exception as e:
                print(f"解压失败: {e}")
                shutil.rmtree(backup_dir, ignore_errors=True)
                return

            # 恢复用户数据
            try:
                for fname in user_data_files:
                    backed = os.path.join(backup_dir, fname)
                    if os.path.exists(backed):
                        shutil.copy2(backed, fname)
                for dname in user_data_dirs:
                    backed = os.path.join(backup_dir, dname)
                    if os.path.exists(backed):
                        if os.path.exists(dname):
                            shutil.rmtree(dname)
                        shutil.copytree(backed, dname)
            except Exception as e:
                print(f"恢复用户数据失败: {e}")

            shutil.rmtree(backup_dir, ignore_errors=True)
            print("更新完成！请重启程序。")
            sys.exit(0)

    except Exception as e:
        print(f"更新检查失败: {e}")
        time.sleep(10)
VERSION = "1.2"
check_and_update(VERSION)
# 设置 Termux 字体大小
termux_properties = "/data/data/com.termux/files/home/.termux/termux.properties"
os.makedirs(os.path.dirname(termux_properties), exist_ok=True)
with open(termux_properties, "a+") as f:
    f.seek(0)
    if "font-size" not in f.read():
        f.write("font-size = 10\n")
        os.system("termux-reload-settings")
    else:
        print("无需修改字体大小")

ayo = True

def ui():
    global ayo
    while ayo:
        print("\033[94m" + """
                            \n\n  



                                 #
                             #########
                            ###########
                           ############# 
                          ###############  
                         #################""" + "\033[0m" + r"""
                        /                 \
                       /                   \
                      /                     \
                      _z_q_r_x_i_a_n_g_c_a_o_
                            /\   /\
                           /  \ /  \
                           |       |
                           _x_c_x_c_
                            |      |
                            |      | 
                            |      |
                            |      |l     ooo    a     ddd    
                            ________l    o   o  a a    d  d
                                .   l    o   o aaaaa   d  d
                                .   llll  ooo a     a  ddd    ing
                                .
                               .
                             .
              
              """)
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else "clear")

def fix():
    global ayo
    if os.path.exists("./chat.py"):
        time.sleep(10)
        ayo = False
        time.sleep(5)
        os.system("python ./chat.py")
        exit()
    else:
        ayo = False
        time.sleep(5)
        print("主程序丢失!")
        sys.exit()

t = threading.Thread(target=ui)
t.start()
t1 = threading.Thread(target=fix)
t1.start()
