import pyautogui
import pyperclip
import time
import os
import tkinter as tk
from tkinter import filedialog

# ================= 坐标配置区域 (请务必修改这里) =================
# 你需要使用之前的 get_position.py 脚本获取这两个坐标
SEARCH_BOX_POS = (1450, 230)    # QQ群文件搜索框的位置
DOWNLOAD_BTN_POS = (523, 538)  # 搜索结果列表中，第一个文件的下载按钮位置

# 全局设置
WAIT_TIME = 2.5                 # 搜索后的等待时间(秒)，网速慢请调大
pyautogui.FAILSAFE = True       # 启用安全保护：鼠标甩到左上角强制停止
# ==============================================================

def select_file():
    """弹出窗口选择txt文件，并读取内容"""
    root = tk.Tk()
    root.withdraw() # 隐藏主窗口

    print("请在弹出的窗口中选择包含歌名的 .txt 文件...")
    file_path = filedialog.askopenfilename(
        title="选择歌名列表文件",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )

    if not file_path:
        print("未选择文件，程序退出。")
        return []

    song_list = []
    try:
        # 优先尝试 utf-8 编码读取
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        # 如果失败，尝试 gbk 编码 (Windows记事本默认格式)
        print("检测到 ANSI/GBK 编码，正在尝试重新读取...")
        with open(file_path, 'r', encoding='gbk') as f:
            lines = f.readlines()

    # 清理数据：去除空行和首尾空格
    for line in lines:
        clean_line = line.strip()
        if clean_line:
            song_list.append(clean_line)
    
    print(f"成功读取到 {len(song_list)} 首歌曲。")
    return song_list

def start_automation(songs):
    if not songs:
        return

    print("\n>>> 警告：脚本将在 10 秒后启动 <<<")
    print(">>> 请立即切换到 QQ 群文件界面，并保持不动！ <<<")
    for i in range(10, 0, -1):
        print(f"倒计时: {i}")
        time.sleep(1)

    print("\n开始执行任务...")

    for index, song in enumerate(songs, 1):
        print(f"[{index}/{len(songs)}] 正在搜索: {song}")
        
        # 1. 点击搜索框
        pyautogui.click(SEARCH_BOX_POS)
        time.sleep(0.3)
        
        # 2. 清空搜索框 (Ctrl+A -> Backspace)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.3)
        pyautogui.press('backspace')
        
        # 3. 输入歌名
        pyperclip.copy(song)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        
        # 4. 等待结果
        print(f"  等待搜索结果 ({WAIT_TIME}秒)...")
        time.sleep(WAIT_TIME)
        
        # 5. 点击下载
        # 建议：这里最好稍微移动一下鼠标，模拟人手
        pyautogui.moveTo(DOWNLOAD_BTN_POS, duration=0.2) 
        pyautogui.click()
        
        print(f"  已点击下载位置")
        print("-" * 30)
        
        # 稍微暂停，防止操作过快被风控
        time.sleep(1.5)

    print("\n>>> 所有任务已完成 <<<")

if __name__ == "__main__":
    # 1. 获取歌单
    songs = select_file()
    
    # 2. 如果有歌，开始执行
    if songs:
        start_automation(songs)
    else:
        input("列表为空或读取失败，按回车键退出...")