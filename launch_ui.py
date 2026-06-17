import threading
import time
import os
import sys
import requests
import tarfile
import tempfile
import shutil

VERSION = "1.1"
REMOTE_VERSION_URL = "https://openxc.surge.sh/version.txt"
UPDATE_URL = "https://openxc.surge.sh/update.tar.gz"

def check_and_update():
    """检查更新，如有新版本则提示并更新代码，同时保留用户数据（聊天记录和模型）"""
    try:
        resp = requests.get(REMOTE_VERSION_URL, timeout=100)
        if resp.status_code != 200:
            return
        remote_version = resp.text.strip()
        if remote_version == VERSION:
            return
        print(f"发现新版本 {remote_version}（当前 {VERSION}）")
        choice = input("是否更新代码？(y/n): ")
        if choice.lower() != 'y':
            return

        # 备份用户数据
        backup_dir = tempfile.mkdtemp()
        user_data_files = ["chat_history.json"]
        user_data_dirs = ["models"]

        try:
            # 备份文件
            for fname in user_data_files:
                if os.path.exists(fname):
                    shutil.copy2(fname, os.path.join(backup_dir, fname))
            # 备份目录
            for dname in user_data_dirs:
                if os.path.exists(dname):
                    shutil.copytree(dname, os.path.join(backup_dir, dname))
        except Exception as e:
            print(f"备份用户数据失败: {e}")
            # 可以选择继续或退出
            # 这里我们继续，但风险自负

        # 下载更新包
        with tempfile.TemporaryDirectory() as tmpdir:
            update_file = os.path.join(tmpdir, "update.tar.gz")
            print("正在下载更新...")
            ret = os.system(f"wget -q -O {update_file} {UPDATE_URL}")
            if ret != 0 or not os.path.exists(update_file):
                print("下载失败")
                return

            # 解压更新包（覆盖代码文件）
            print("正在解压...")
            with tarfile.open(update_file, "r:gz") as tar:
                # 这里直接解压全部，因为后面会恢复用户数据
                tar.extractall(path=".", filter='data')

        # 恢复用户数据
        try:
            for fname in user_data_files:
                backed = os.path.join(backup_dir, fname)
                if os.path.exists(backed):
                    shutil.copy2(backed, fname)
            for dname in user_data_dirs:
                backed = os.path.join(backup_dir, dname)
                if os.path.exists(backed):
                    # 如果目标目录已存在，先删除再复制（避免残留）
                    if os.path.exists(dname):
                        shutil.rmtree(dname)
                    shutil.copytree(backed, dname)
        except Exception as e:
            print(f"恢复用户数据失败: {e}")

        # 清理备份目录
        shutil.rmtree(backup_dir, ignore_errors=True)

        print("更新完成！请重启程序。")
        sys.exit(0)

    except Exception as e:
        print(f"更新检查失败: {e}")
        time.sleep(10)

# 执行更新检查
check_and_update()

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
