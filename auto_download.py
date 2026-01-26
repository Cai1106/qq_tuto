import pyautogui
import pyperclip
import time

# ================= 配置区域 =================
# 1. 在这里填入你的歌名列表
music_list = [
    "周杰伦 - 晴天",
    "陈奕迅 - 十年",
    "林俊杰 - 江南",
    "西蒙叔叔"
    # 可以在这里继续添加...
]

# 2. 填入你刚才获取的坐标 (x, y)
SEARCH_BOX_POS = (1161, 216)   # 示例坐标，请修改为你自己的
DOWNLOAD_BTN_POS = (523, 538) # 示例坐标：通常是搜索结果列表的右侧下载图标

# 3. 设置操作间隔时间 (秒)
# 如果网速或电脑慢，请把时间改大，防止脚本操作过快报错
WAIT_TIME = 2 
# ===========================================

def download_music():
    print(">>> 脚本将在 10 秒后启动，请迅速切换到 QQ 群文件窗口！ <<<")
    time.sleep(10)

    for music in music_list:
        print(f"正在尝试搜索: {music}")
        
        # --- 动作 1: 点击搜索框 ---
        pyautogui.click(SEARCH_BOX_POS)
        time.sleep(0.5)
        
        # --- 动作 2: 清除旧内容 (全选 + 删除) ---
        # 这一步是为了防止搜索框里有上一次的残留文字
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('backspace')
        
        # --- 动作 3: 输入歌名 ---
        pyperclip.copy(music)       # 复制到剪贴板
        pyautogui.hotkey('ctrl', 'v') # 粘贴
        time.sleep(0.5)
        pyautogui.press('enter')    # 回车搜索
        
        # --- 动作 4: 等待搜索结果加载 ---
        print("等待结果加载...")
        time.sleep(WAIT_TIME)
        
        # --- 动作 5: 点击下载 ---
        # 这里假设搜索结果的第一项就是你要的目标
        # 注意：你需要确保鼠标点击的位置是准确的“下载”图标或者右键菜单位置
        pyautogui.click(DOWNLOAD_BTN_POS)
        
        # 如果是右键菜单模式，可能还需要增加一次点击“下载”选项的坐标
        # pyautogui.moveRel(20, 50) # 相对移动到菜单的下载选项
        # pyautogui.click()
        
        print(f"已执行下载点击: {music}")
        print("-" * 30)
        
        # 等待一下，防止操作过快被检测或卡顿
        time.sleep(1)

    print(">>> 所有任务执行完毕 <<<")

if __name__ == "__main__":
    # 为了安全，启用防故障功能：将鼠标猛地移到屏幕左上角可强制终止脚本
    pyautogui.FAILSAFE = True
    download_music()