# -*- coding: utf-8 -*-
import os
import time
import json
import maliang
import subprocess
from tkinter import messagebox
import shutil
# 全局变量存储当前工作目录
CURRENT_WORKING_DIR = os.getcwd()

def get_log_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def cmd(string):
    try:
        result = subprocess.run(string, shell=True, check=True,
                              stderr=subprocess.PIPE,
                              text=True, encoding='utf-8', errors='replace')
        return True
    except subprocess.CalledProcessError as e:
        print(f"{get_log_time()}{string}执行失败")
        print(e.stderr)

        # 对版本冲突进行特判

        if "CONFLICT" in e.stderr:
            messagebox.showerror("错误", "版本冲突，请根据命令行提示逐步解决冲突（纯英文，不会机翻）")
            os.system("git mergetool")
        return False

def init_git(user_name, user_email,https_url):
    if not os.path.exists("repositories"):
        os.mkdir("repositories")
    os.chdir("repositories")
    cmd("git init -b main")
    cmd(f"git config --local user.name '{user_name}'")
    cmd(f"git config --local user.email '{user_email}'")

    code=cmd(f"git remote add origin {https_url}")
    if code:
        print(f"{get_log_time()}添加远程仓库成功")
    else:
        print(f"{get_log_time()}初始化git失败")
        messagebox.showerror("错误", "初始化git失败")
        return
    code=cmd("git lfs install")
    if code:
        print(f"{get_log_time()}安装git-lfs成功")
    else:
        print(f"{get_log_time()}安装git-lfs失败")
        messagebox.showerror("错误", "安装git-lfs失败")
        return
    
    print(f"{get_log_time()}正在远程从Github拉取镜像...")
    code=cmd("git pull origin main")
    if code:
        print(f"{get_log_time()}拉取镜像成功")
    else:
        print(f"{get_log_time()}拉取镜像失败")
        messagebox.showerror("错误", "拉取镜像失败")
        return
    cmd("git checkout -b develop")
    print(f"{get_log_time()}初始化git成功")
    messagebox.showinfo("成功", "初始化git成功")
    
def init_GUI_button_click(name, email, root):
    if not name or not email:
        messagebox.showerror("错误", "请填写完整信息")
        print(f"{get_log_time()}请填写完整信息")
        return
    with open("config.json", "r", encoding='utf-8') as f:
        config = json.load(f)
    try:
        https_url = config.get("https")
    except Exception as e:
        print(f"{get_log_time()}读取配置文件失败：{e}")
        return
    root.destroy()
    init_git(user_name=name, user_email=email, https_url=https_url)
def init_git_gui():
    size = 600, 350
    root = maliang.Tk(size,title="初始化")
    root.center()

    cv = maliang.Canvas(auto_zoom=True, keep_ratio="min", free_anchor=True)
    cv.place(width=600, height=400, x=300, y=200, anchor="center")

    maliang.Text(cv, (0, 0), text="请输入你在他人眼中看到的称呼：", fontsize=24,slant="roman", anchor="nw")

    maliang.Text(cv, (10, 60), text="昵称", anchor="nw")
    name=maliang.InputBox(cv, (0, 100), (600, 40), placeholder="点击输入昵称")
    maliang.Text(cv, (10, 180), text="邮箱", anchor="nw")
    email=maliang.InputBox(cv, (0, 220), (600, 40), placeholder="点击输入邮箱")

    maliang.Button(cv, (600, 350), (100, 50), anchor="se",text="确定",command=lambda:init_GUI_button_click(name=name.get(), email=email.get(), root=root))

    root.mainloop()
def main_gui():
    try:
        size = 800, 500
        root = maliang.Tk(size, title="版本管理")
        root.center()

        cv = maliang.Canvas(auto_zoom=True, keep_ratio="min", free_anchor=True)
        cv.place(width=800, height=500, x=400, y=250, anchor="center")

        # 上方三个按钮
        btn_width = 200
        btn_height = 50
        btn_padding = 20
        
        # 从Github获取最新版本按钮
        maliang.Button(cv, (btn_padding, btn_padding), (btn_width, btn_height), 
                      text="从Github合并最新版本", anchor="nw",
                      command=lambda: fetch_from_github(root=root))
        
        # 保存当前开发版本按钮
        maliang.Button(cv, (btn_padding*2 + btn_width, btn_padding), (btn_width, btn_height),
                      text="保存当前开发版本", anchor="nw",
                      command=lambda: save_current_version(root=root))
        
        # 提交到Github按钮
        maliang.Button(cv, (btn_padding*3 + btn_width*2, btn_padding), (btn_width, btn_height),
                      text="将版本提交到Github", anchor="nw",
                      command=lambda: push_to_github(root=root))
        
        # 还原到Github版本按钮
        maliang.Button(cv, (btn_padding, btn_padding*4), (btn_width, btn_height),
                      text="还原到Github版本", anchor="nw",
                      command=lambda: restore_from_github(root=root))
        # 下方输入框
        maliang.Text(cv, (20, 350), text="自定义GIT指令:", anchor="sw")
        commit_msg = maliang.InputBox(cv, (20, 430), (760, 50), 
                                    placeholder="输入自定义GIT指令")
        maliang.Button(cv, (680, 430), (100, 50), anchor="se", text="执行",
                      command=lambda: cmd(commit_msg.get()))
        root.mainloop()
        return 0
    except Exception as e:
        print(f"{get_log_time()}主界面初始化失败: {e}")
        return 1

def fetch_from_github(root):
    root.destroy()
    with open("config.json", "r", encoding='utf-8') as f:
        config = json.load(f)
    os.chdir("repositories")
    cmd("git branch -D develop")
    print(f"{get_log_time()}正在远程从Github拉取镜像...")
    code=cmd("git pull origin main")
    if code:
        print(f"{get_log_time()}拉取镜像成功")
    else:
        print(f"{get_log_time()}拉取镜像失败")
        messagebox.showerror("错误", "拉取镜像失败")
        return
    print(f"{get_log_time()}拉取镜像成功")
    print(f"{get_log_time()}正在切换到develop分支...")
    cmd("git checkout -b develop")
    print(f"{get_log_time()}成功获取最新版本")

    if config["mc_dir"] != "":
        dir_list=['mods','resourcepacks','config','shaderpacks']
        for dir_name in dir_list:
            full_path = os.path.join(config["mc_dir"],dir_name)
            delete_files_in_directory(full_path)
            copy_and_replace_files(dir_name, full_path)
        
    messagebox.showinfo("成功", "成功获取最新版本")
    os.chdir(CURRENT_WORKING_DIR)
    main_gui()
def save_current_version(root):

    root.destroy()
    with open("config.json", "r", encoding='utf-8') as f:
        config = json.load(f)
    os.chdir("repositories")
    if config["mc_dir"] != "":
        dir_list=['mods','resourcepacks','config','shaderpacks']
        for dir_name in dir_list:
            full_path = os.path.join(config["mc_dir"],dir_name)
            delete_files_in_directory(dir_name)
            copy_and_replace_files(full_path, dir_name)
    
    cmd("git add *")

    massage=input("请输入当前开发版本的提交信息(认真填写): ")
    cmd(f"git commit -m {massage}")
    print(f"{get_log_time()}正在保存当前开发版本...")
    os.chdir(CURRENT_WORKING_DIR)
    print(f"{get_log_time()}当前开发版本已保存")
    messagebox.showinfo("成功", "当前开发版本已保存")
    main_gui()

def push_to_github(root):
    root.destroy()
    os.chdir("repositories")
    print(f"{get_log_time()}正在切换到main分支...")
    cmd("git checkout main")
    print(f"{get_log_time()}正在拉取最新版本...")
    code=cmd("git pull origin main")
    if not code:
        print(f"{get_log_time()}拉取最新版本失败")

    print(f"{get_log_time()}正在合并develop分支...")
    cmd("git merge develop")
    print(f"{get_log_time()}正在提交到Github...")

    
    code=cmd("git push origin main")
    if not code:
        print(f"{get_log_time()}提交到Github失败")
        messagebox.showerror("错误", "提交到Github失败")
        return
    print(f"{get_log_time()}提交到Github成功")
    messagebox.showinfo("成功", "提交到Github成功")
    os.chdir(CURRENT_WORKING_DIR)
    main_gui()

def restore_from_github(root):
    root.destroy()
    os.chdir("repositories")
    print(f"{get_log_time()}正在还原到Github最新版本...")
    code = cmd("git reset --hard origin/main")
    if code:
        print(f"{get_log_time()}还原成功")
        messagebox.showinfo("成功", "已还原到Github最新版本")
    else:
        print(f"{get_log_time()}还原失败")
        messagebox.showerror("错误", "还原到Github版本失败")
    os.chdir(CURRENT_WORKING_DIR)
    main_gui()

def copy_and_replace_files(src_dir, dst_dir):
    """
    复制源目录下的所有文件到目标目录并替换已存在的文件
    :param src_dir: 源目录路径
    :param dst_dir: 目标目录路径
    :return: 成功返回True，失败返回False
    """
    try:
        if not os.path.isdir(src_dir):
            print(f"{get_log_time()}源目录不存在: {src_dir}")
            return False
        
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        
        file_count = 0
        for item in os.listdir(src_dir):
            src_path = os.path.join(src_dir, item)
            dst_path = os.path.join(dst_dir, item)
            
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dst_path)
                file_count += 1
                print(f"{get_log_time()}已复制文件: {src_path} -> {dst_path}")
        
        print(f"{get_log_time()}复制完成，共复制{file_count}个文件")
        return True
    except Exception as e:
        print(f"{get_log_time()}复制文件时出错: {str(e)}")
        return False

def delete_files_in_directory(directory):
    """
    删除指定目录下的所有文件（不删除子目录）
    :param directory: 要删除文件的目录路径
    :return: (成功状态, 删除的文件数量)
    """
    try:
        if not os.path.isdir(directory):
            print(f"{get_log_time()}目录不存在: {directory}")
            return False, 0
        
        deleted_count = 0
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                try:
                    os.remove(item_path)
                    deleted_count += 1
                    print(f"{get_log_time()}已删除文件: {item_path}")
                except Exception as e:
                    print(f"{get_log_time()}删除文件失败 {item_path}: {str(e)}")
                    continue
        
        print(f"{get_log_time()}删除完成，共删除{deleted_count}个文件")
        return True, deleted_count
    except Exception as e:
        print(f"{get_log_time()}删除文件时出错: {str(e)}")
        return False, 0

if __name__ == "__main__":
    #读取配置文件
    with open("config.json", "r", encoding='utf-8') as f:
        config = json.load(f)
    is_init = config.get("is_init", False)
    #判断是否初始化git
    if is_init is False:
        init_git_gui()
        #写入配置文件
        os.chdir(CURRENT_WORKING_DIR)
        config["is_init"] = True
    with open("config.json", "w", encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    main_gui()
    
        
        
    