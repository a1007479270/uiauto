import win32gui
import win32con
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen

class HighlightWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 设置窗口无边框和背景透明
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()
        
        # 设置边框样式
        self.border_color = Qt.GlobalColor.red  # 改为红色
        self.border_width = 12  # 增加边框宽度使其更醒目
        self.border_style = Qt.PenStyle.DashDotDotLine  # 使用双实线样式
    
    def highlight_element(self, rect, color='red'):
        """显示高亮边框"""
        if not rect:
            self.hide()
            return
            
        # 设置窗口位置和大小
        self.setGeometry(
            rect.left,
            rect.top,
            rect.right - rect.left,
            rect.bottom - rect.top
        )
        
        # 根据传入的颜色设置边框样式
        if color == 'blue':
            self.setStyleSheet('background-color: transparent; border: 2px solid blue;')
        else:
            self.setStyleSheet('background-color: transparent; border: 2px solid red;')
            
        self.show()
        self.update()
    
    def paintEvent(self, event):
        """绘制高亮边框"""
        painter = QPainter(self)
        pen = QPen(self.border_color, self.border_width)
        pen.setStyle(self.border_style)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))