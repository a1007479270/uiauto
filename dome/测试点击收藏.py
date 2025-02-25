import uiautomation as auto
import time

def click_wechat_favorite():
    try:
        # 一句话完成定位和点击
        auto.WindowControl(Name="微信", ClassName="WeChatMainWndForPC").ButtonControl(Name="通讯录").Click()
        print("成功点击收藏按钮")
        return True
            
    except Exception as e:
        print(f"操作失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 给一些时间切换到微信窗口
    print("请在3秒内切换到微信窗口...")
    time.sleep(3)
    
    # 执行点击操作
    click_wechat_favorite()