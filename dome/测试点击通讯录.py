"""
Author: Trae AI
Update: 2024-01-16
Version: 1.0.0
"""

import uiautomation as auto
import time
import os

class WeChatAuto:
    VERSION: str = '1.0.0'
    
    def __init__(self, debug: bool = False) -> None:
        """微信UI自动化实例
    
        Args:
            debug (bool, optional): 是否开启调试模式. Defaults to False.
        """
        # 初始化微信主窗口
        self.UiaAPI = auto.WindowControl(
            Name="微信",
            ClassName="WeChatMainWndForPC"
        )
        
        # 初始化主要控件
        self._init_controls()
        print(f'初始化成功，获取到微信窗口')
    
    def _init_controls(self):
        """初始化各个控件"""
        try:
            # 获取左侧导航栏控件
            self.contacts_button = self.UiaAPI.ButtonControl(
                Name="wxauto五群(407)",
                searchDepth=6  # 增加搜索深度以确保能找到按钮
            )
            
            # 验证控件是否存在
            if not self.contacts_button.Exists():
                print("警告：未能正确初始化通讯录按钮")
        except Exception as e:
            print(f"初始化控件时发生错误: {str(e)}")
    def click_contacts(self):
        """点击通讯录按钮"""
        try:
            if self.contacts_button.Exists(3):
                self.contacts_button.Click()
                print("成功点击通讯录按钮")
                return True
            else:
                print("未找到通讯录按钮")
                return False
        except Exception as e:
            print(f"点击通讯录时发生错误: {str(e)}")
            return False

if __name__ == "__main__":
    # 给一些时间切换到微信窗口
    print("请在3秒内切换到微信窗口...")
    time.sleep(3)
    
    # 创建实例并执行点击
    wechat = WeChatAuto()
    wechat.click_contacts()