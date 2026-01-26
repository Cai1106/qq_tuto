import pyautogui
import time

print("请在 8 秒内将鼠标移动到 QQ 群文件的【搜索框】位置...")
time.sleep(8)
print(f"搜索框坐标: {pyautogui.position()}")

print("\n请在 12 秒内将鼠标移动到搜索结果中【第一个文件的下载按钮/右键位置】...")
time.sleep(12)
print(f"下载操作坐标: {pyautogui.position()}")