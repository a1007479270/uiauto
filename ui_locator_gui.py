import sys
import time
import uiautomation as auto
import win32gui
import win32api
import win32con
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QTreeWidget,
                             QTreeWidgetItem, QTextEdit, QLabel, QCheckBox,
                             QSplitter, QComboBox, QMenu)
from highlight_window import HighlightWindow
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QColor, QDesktopServices, QAction
from PyQt6.QtGui import QColor

class UILocatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('UI元素定位工具')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建高亮窗口
        self.highlight_window = HighlightWindow()
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 顶部工具栏
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(2, 2, 2, 2)  # 减小内边距
        toolbar_layout.setSpacing(5)  # 减小控件之间的间距
        
        # 状态指示器
        self.point_capture_label = QLabel('定点捕获(F4)')
        self.point_capture_label.setFixedHeight(20)  # 设置固定高度
        self.point_capture_label.setToolTip('按F4定点捕获当前鼠标位置信息')
        toolbar_layout.addWidget(self.point_capture_label)
        
        # 添加实时测试按钮（移到定点捕获左边）
        self.test_btn = QPushButton('实时测试')
        self.test_btn.setFixedHeight(20)
        self.test_btn.clicked.connect(self.toggle_test_panel)
        toolbar_layout.insertWidget(0, self.test_btn)
        
        self.click_mode_label = QLabel('左键模式: 关闭(F5)')
        self.click_mode_label.setFixedHeight(20)  # 设置固定高度
        self.click_mode_label.setToolTip('按F5开启/关闭左键点击捕获模式')
        toolbar_layout.addWidget(self.click_mode_label)
        
        self.realtime_mode_label = QLabel('实时捕获: 关闭(F6)')
        self.realtime_mode_label.setFixedHeight(20)  # 设置固定高度
        self.realtime_mode_label.setToolTip('按F6开启/关闭实时捕获模式')
        toolbar_layout.addWidget(self.realtime_mode_label)
        
        # 添加帮助按钮和下拉菜单
        help_btn = QPushButton('帮助')
        help_btn.setFixedHeight(20)
        help_menu = QMenu()
        
        # 添加程序教程菜单项
        tutorial_action = QAction('程序教程', self)
        tutorial_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile('help.html')))
        help_menu.addAction(tutorial_action)
        
        # 添加检测更新菜单项
        update_action = QAction('检测更新', self)
        update_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl('https://github.com/a1007479270')))
        help_menu.addAction(update_action)
        
        # 添加开源地址菜单项
        source_action = QAction('开源地址', self)
        source_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl('https://github.com/a1007479270')))
        help_menu.addAction(source_action)
        
        help_btn.setMenu(help_menu)
        toolbar_layout.addWidget(help_btn)
        
        # 添加一些间距
        toolbar_layout.addSpacing(20)
        
        main_layout.addWidget(toolbar)
        

        
        # 创建实时测试面板
        self.test_panel = QWidget()
        test_panel_layout = QVBoxLayout(self.test_panel)
        
        # 添加定位模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel('定位模式:'))
        self.locator_mode = QComboBox()
        self.locator_mode.addItems(['UIAutomation', 'Pywinauto'])
        mode_layout.addWidget(self.locator_mode)
        test_panel_layout.addLayout(mode_layout)
        
        # 添加代码容器
        code_container = QWidget()
        self.code_container_layout = QVBoxLayout(code_container)
        
        # 添加第一行代码编辑器
        self.add_code_line()
        
        # 添加按钮区域
        buttons_layout = QHBoxLayout()
        add_line_btn = QPushButton('添加代码行')
        add_line_btn.clicked.connect(self.add_code_line)
        run_test_btn = QPushButton('运行测试')
        run_test_btn.clicked.connect(self.test_code)
        buttons_layout.addWidget(add_line_btn)
        buttons_layout.addWidget(run_test_btn)
        
        test_panel_layout.addWidget(code_container)
        test_panel_layout.addLayout(buttons_layout)
        
        # 添加总执行时间标签
        self.total_time_label = QLabel('总执行时间: 0ms')
        test_panel_layout.addWidget(self.total_time_label)
        
        # 默认隐藏测试面板
        self.test_panel.hide()
        main_layout.addWidget(self.test_panel)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧树形结构
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        
        # 应用程序路径输入（移到树形结构上方）
        path_container = QWidget()
        path_layout = QHBoxLayout(path_container)
        path_layout.setContentsMargins(2, 2, 2, 2)
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText('应用程序路径')
        path_layout.addWidget(self.path_input)
        tree_layout.addWidget(path_container)
        
        # 添加展开/折叠按钮
        tree_toolbar = QWidget()
        tree_toolbar_layout = QHBoxLayout(tree_toolbar)
        tree_toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.expand_all_btn = QPushButton('全部展开')
        self.expand_all_btn.setCheckable(True)
        self.expand_all_btn.clicked.connect(self.toggle_tree_expand)
        tree_toolbar_layout.addWidget(self.expand_all_btn)
        tree_toolbar_layout.addStretch()
        
        tree_layout.addWidget(tree_toolbar)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel('元素')
        self.tree.itemClicked.connect(self.on_tree_item_clicked)  # 添加点击事件处理
        tree_layout.addWidget(self.tree)
        
        splitter.addWidget(tree_container)
        
        # 右侧信息面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 元素属性区域
        props_group = QWidget()
        props_layout = QVBoxLayout(props_group)
        props_layout.addWidget(QLabel('元素信息'))
        self.props_text = QTextEdit()
        self.props_text.setReadOnly(True)
        props_layout.addWidget(self.props_text)
        
        # 定位代码区域
        code_group = QWidget()
        code_layout = QVBoxLayout(code_group)
        code_layout.addWidget(QLabel('定位代码'))
        self.code_text = QTextEdit()
        self.code_text.setReadOnly(True)
        code_layout.addWidget(self.code_text)
        
        right_layout.addWidget(props_group)
        right_layout.addWidget(code_group)
        
        splitter.addWidget(right_panel)
        main_layout.addWidget(splitter)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        # 添加版本号标签
        version_label = QLabel('v0.0.0.1')
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        version_label.setStyleSheet('color: gray; padding: 5px;')
        main_layout.addWidget(version_label)
        
        # 初始化定时器用于实时捕获
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.capture_element)
        
        # 初始化点击捕获模式状态
        self.click_capture_mode = False
        self.last_click_state = False
        
        # 启动定时器用于检测快捷键和鼠标点击
        self.key_timer = QTimer()
        self.key_timer.timeout.connect(self.check_hotkeys)
        self.key_timer.start(100)  # 每100ms检查一次
    
    def toggle_realtime_capture(self, checked):
        if checked:
            self.capture_timer.start(100)  # 每100ms捕获一次
            self.realtime_mode_label.setText('实时捕获: 开启')
        else:
            self.capture_timer.stop()
            self.realtime_mode_label.setText('实时捕获: 关闭')
    
    def check_hotkeys(self):
        try:
            # F4: 单次捕获
            if win32api.GetAsyncKeyState(win32con.VK_F4) & 0x8000:
                self.capture_element()
            
            # F5: 切换点击捕获模式
            if win32api.GetAsyncKeyState(win32con.VK_F5) & 0x8000:
                self.click_capture_mode = not self.click_capture_mode
                self.click_mode_label.setText(f"左键模式: {'开启' if self.click_capture_mode else '关闭'}(F5)")
                print(f"点击捕获模式: {'开启' if self.click_capture_mode else '关闭'}")
            
            # F6: 切换实时捕获模式
            if win32api.GetAsyncKeyState(win32con.VK_F6) & 0x8000:
                if self.capture_timer.isActive():
                    self.capture_timer.stop()
                    self.realtime_mode_label.setText('实时捕获: 关闭(F6)')
                else:
                    self.capture_timer.start(100)
                    self.realtime_mode_label.setText('实时捕获: 开启(F6)')
        except KeyboardInterrupt:
            print("检测到键盘中断，继续监听快捷键...")
        except Exception as e:
            print(f"检测快捷键时出错: {str(e)}")
    
    def capture_element(self):
        try:
            x, y = win32gui.GetCursorPos()
            # 使用深度优先搜索查找最深层的可交互元素
            element = auto.ControlFromPoint(x, y)
            if element:
                # 获取并更新应用程序路径
                try:
                    window = element
                    while window and window.ControlTypeName != 'WindowControl':
                        window = window.GetParentControl()
                    if window:
                        process_id = window.ProcessId
                        import psutil
                        try:
                            process = psutil.Process(process_id)
                            exe_path = process.exe()
                            self.path_input.setText(exe_path)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except Exception as e:
                    print(f"获取应用程序路径时出错: {str(e)}")
                    
                def find_deepest_element(current_element, depth=0, max_depth=20):
                    if depth >= max_depth:
                        return current_element, False
                        
                    try:
                        # 获取所有子元素
                        children = current_element.GetChildren()
                        deepest_element = None
                        max_found_depth = -1
                        
                        for child in children:
                            try:
                                rect = child.BoundingRectangle
                                # 检查鼠标是否在子元素的范围内
                                if (rect.left <= x <= rect.right and 
                                    rect.top <= y <= rect.bottom):
                                    # 递归查找更深层的元素
                                    candidate_element, found_deeper = find_deepest_element(child, depth + 1)
                                    
                                    # 更新最深层元素
                                    if found_deeper and candidate_element:
                                        current_depth = 0
                                        temp_element = candidate_element
                                        while temp_element:
                                            current_depth += 1
                                            temp_element = temp_element.GetParentControl()
                                            
                                        if current_depth > max_found_depth:
                                            max_found_depth = current_depth
                                            deepest_element = candidate_element
                                    # 如果当前元素可见且可交互，作为备选
                                    elif not child.IsOffscreen and child.IsEnabled:
                                        if deepest_element is None:
                                            deepest_element = child
                            except Exception:
                                continue
                                
                        # 返回找到的最深层元素
                        if deepest_element:
                            return deepest_element, True
                            
                    except Exception:
                        pass
                    
                    # 如果当前元素可见且可交互，返回当前元素
                    if not current_element.IsOffscreen and current_element.IsEnabled:
                        return current_element, True
                    return current_element, False
                
                # 开始深度优先搜索
                result_element, found = find_deepest_element(element)
                if result_element:
                    self.update_element_info(result_element)
                    # 显示高亮边框
                    self.highlight_window.highlight_element(result_element.BoundingRectangle)
        except Exception as e:
            print(f"捕获元素时出错: {str(e)}")

    def update_element_info(self, element, update_tree=True):
        try:
            # 只在需要时更新树形结构
            if update_tree:
                # 更新树形结构
                self.tree.clear()
                # 创建根节点
                root_item = None
                # 获取元素的层级路径
                current = element
                hierarchy = []
                try:
                    while current:
                        hierarchy.insert(0, current)
                        current = current.GetParentControl()
                except Exception as e:
                    print(f"获取元素层级时出错: {str(e)}")
                
                # 构建树形结构
                for i, elem in enumerate(hierarchy):
                    try:
                        item = QTreeWidgetItem()
                        item.setText(0, f"{elem.Name} ({elem.ControlTypeName})")
                        # 设置当前元素的文本颜色为红色
                        if elem == element:
                            item.setForeground(0, QColor('red'))
                        if i == 0:
                            self.tree.addTopLevelItem(item)
                            root_item = item
                        else:
                            hierarchy[i-1].tree_item.addChild(item)
                        # 存储QTreeWidgetItem引用
                        elem.tree_item = item
                        
                        # 添加当前层级的所有子元素
                        try:
                            children = elem.GetChildren()
                            for child in children:
                                if child not in hierarchy:  # 避免重复添加已在路径中的元素
                                    child_item = QTreeWidgetItem(item)
                                    child_item.setText(0, f"{child.Name} ({child.ControlTypeName})")
                                    # 递归添加子元素的子元素
                                    self.add_children_recursive(child, child_item)
                        except Exception as e:
                            print(f"添加子元素时出错: {str(e)}")
                    except Exception as e:
                        print(f"构建树节点时出错: {str(e)}")
                        continue
                
                # 默认折叠所有节点
                self.tree.collapseAll()
                
                # 展开当前选中元素的路径
                if root_item:
                    current_item = None
                    def find_element_item(item):
                        nonlocal current_item
                        if item:
                            # 从文本中提取名称和控件类型
                            import re
                            match = re.match(r"(.+?) \((.+?)\)", item.text(0))
                            if match:
                                name = match.group(1)
                                control_type = match.group(2)
                                if name == element.Name and control_type == element.ControlTypeName:
                                    current_item = item
                                    return True
                            # 递归查找子节点
                            for i in range(item.childCount()):
                                if find_element_item(item.child(i)):
                                    return True
                        return False
                    
                    # 从根节点开始查找
                    for i in range(self.tree.topLevelItemCount()):
                        if find_element_item(self.tree.topLevelItem(i)):
                            break
                    
                    # 展开找到的节点的路径
                    if current_item:
                        self.tree.setCurrentItem(current_item)
                        while current_item:
                            current_item.setExpanded(True)
                            current_item = current_item.parent()
            
            # 更新属性信息
            props_info = "元素基本信息:\n"
            try:
                # 计算元素深度
                depth = 0
                current = element
                while current:
                    depth += 1
                    current = current.GetParentControl()
                
                # 构建XPath
                xpath = ""
                current = element
                path_components = []
                while current:
                    name = current.Name or ""
                    control_type = current.ControlTypeName or ""
                    component = f"{control_type}[{name}]" if name else control_type
                    path_components.insert(0, component)
                    current = current.GetParentControl()
                xpath = "/" + "/".join(path_components)
                
                props_info += f"名称: {element.Name}\n"
                props_info += f"类名: {element.ClassName}\n"
                props_info += f"控件类型: {element.ControlTypeName}\n"
                props_info += f"自动化ID: {element.AutomationId}\n"
                props_info += f"运行时ID: {element.GetRuntimeId()}\n"
                props_info += f"位置: {element.BoundingRectangle}\n"
                props_info += f"进程ID: {element.ProcessId}\n"
                props_info += f"深度: {depth}\n"
                props_info += f"XPath: {xpath}\n"
            except Exception as e:
                print(f"获取基本属性时出错: {str(e)}")
            
            # 更新定位代码
            code_info = "UIAutomation定位代码:\n"
            code_info += self.generate_uiautomation_code(element)
            
            # 添加简化版定位代码
            code_info += "\n\nUIAutomation简单定位代码:\n"
            # 获取顶层窗口
            top_window = None
            current = element
            while current:
                if current.ControlTypeName == 'WindowControl':
                    top_window = current
                    break
                current = current.GetParentControl()
            
            # 生成简化版定位代码
            if top_window:
                # 获取顶层窗口的定位代码
                window_type = 'WindowControl'
                window_conditions = []
                if top_window.Name:
                    window_conditions.append(f'Name="{top_window.Name}"')
                if top_window.ClassName:
                    window_conditions.append(f'ClassName="{top_window.ClassName}"')
                
                # 获取目标元素的定位代码
                target_type = element.ControlTypeName
                target_conditions = []
                if element.Name:
                    target_conditions.append(f'Name="{element.Name}"')
                if element.ClassName:
                    target_conditions.append(f'ClassName="{element.ClassName}"')
                
                # 组合定位代码为一个链式调用
                if element != top_window:  # 如果目标元素不是顶层窗口
                    code_info += f"auto.{window_type}({', '.join(window_conditions)}).{target_type}({', '.join(target_conditions)})\n"
                else:
                    code_info += f"auto.{window_type}({', '.join(window_conditions)})\n"
            else:
                # 如果找不到顶层窗口，就只生成目标元素的定位代码
                control_type = element.ControlTypeName
                if control_type.endswith('Control'):
                    control_type = control_type[:-7]
                code_info += f"auto.{control_type}(Name=\"{element.Name}\")\n"
            
            code_info += "\n\nPywinauto定位代码:\n"
            code_info += "# 定位目标元素\n"
            code_info += self.generate_pywinauto_code(element)
            
            # 添加Pywinauto简单定位代码
            code_info += "\n\nPywinauto简单定位代码:\n"
            # 获取顶层窗口
            top_window = None
            current = element
            while current:
                if current.ControlTypeName == 'WindowControl':
                    top_window = current
                    break
                current = current.GetParentControl()
            
            # 生成简化版定位代码
            if top_window:
                window_conditions = []
                if top_window.Name:
                    window_conditions.append(f'title="{top_window.Name}"')
                if top_window.ClassName:
                    window_conditions.append(f'class_name="{top_window.ClassName}"')
                
                target_conditions = []
                if element.Name:
                    target_conditions.append(f'title="{element.Name}"')
                if element.ClassName:
                    target_conditions.append(f'class_name="{element.ClassName}"')
                
                if element != top_window:
                    code_info += f"# 连接到应用程序\napp = Application().connect(process={element.ProcessId})\n"
                    code_info += f"# 定位目标窗口\nwindow = app.window({', '.join(window_conditions)})\n"
                    code_info += f"# 定位目标元素\nelement = window.child_window({', '.join(target_conditions)})\n"
                else:
                    code_info += f"# 连接到应用程序\napp = Application().connect(process={element.ProcessId})\n"
                    code_info += f"# 定位目标窗口\nwindow = app.window({', '.join(window_conditions)})\n"
            else:
                code_info += f"# 连接到应用程序\napp = Application().connect(process={element.ProcessId})\n"
                code_info += f"# 定位目标元素\nelement = app.window(title=\"{element.Name}\")\n"
            
            self.props_text.setText(props_info)
            self.code_text.setText(code_info)

            # 强制更新界面
            self.tree.update()
            QApplication.processEvents()
        except Exception as e:
            print(f"更新元素信息时出错: {str(e)}")

    def add_children_recursive(self, parent_element, parent_item, depth=0, max_depth=3):
        if depth >= max_depth:
            return
        try:
            children = parent_element.GetChildren()
            for child in children:
                try:
                    child_item = QTreeWidgetItem(parent_item)
                    child_item.setText(0, f"{child.Name} ({child.ControlTypeName})")
                    # 递归添加子元素
                    self.add_children_recursive(child, child_item, depth + 1, max_depth)
                except Exception:
                    continue
        except Exception:
            pass

    def generate_uiautomation_code(self, element):
        if not element:
            return ""
        
        # 获取元素的完整层级路径
        hierarchy = []
        current = element
        while current:
            conditions = []
            if current.Name:
                conditions.append(f'Name="{current.Name}"')
            if current.ClassName:
                conditions.append(f'ClassName="{current.ClassName}"')
            if current.AutomationId:
                conditions.append(f'AutomationId="{current.AutomationId}"')
            if current.ControlTypeName:
                # 处理特殊的控件类型
                control_type = current.ControlTypeName
                if control_type.endswith('Control'):
                    control_type = control_type[:-7]  # 移除'Control'后缀
                conditions.append(f'ControlType=auto.ControlType.{control_type}')
            
            if conditions:
                # 使用正确的控件类型名称
                control_type = current.ControlTypeName
                if control_type.endswith('Control'):
                    control_type = control_type[:-7]
                hierarchy.insert(0, f'{control_type}({", ".join(conditions)})')
            current = current.GetParentControl()
        
        # 生成完整的定位代码
        if hierarchy:
            # 添加注释
            code = "# 定位目标元素\n"
            code += hierarchy[0] + "\n"
            # 添加层级定位
            for i in range(1, len(hierarchy)):
                code += f".{hierarchy[i]}\n"
            return code
        return ""
    
    def generate_pywinauto_code(self, element):
        if not element:
            return ""
        
        # 添加必要的导入和初始化代码
        code = "from pywinauto.application import Application\n\n"
        
        # 获取应用程序路径
        try:
            import psutil
            process = psutil.Process(element.ProcessId)
            app_path = process.exe()
            code += f"# 连接到已运行的应用程序\napp = Application().connect(process={element.ProcessId})\n\n"
        except Exception:
            code += "# 请确保目标应用程序正在运行\napp = Application()\n\n"
        
        locator_conditions = []
        if element.Name:
            locator_conditions.append(f'title="{element.Name}"')
        if element.ClassName:
            locator_conditions.append(f'class_name="{element.ClassName}"')
        if element.AutomationId:
            locator_conditions.append(f'auto_id="{element.AutomationId}"')
        if element.ControlTypeName:
            locator_conditions.append(f'control_type="{element.ControlTypeName}"')
        
        conditions = ', '.join(locator_conditions)
        code += f"# 定位目标窗口\nwindow = app.window({conditions})\n"
        return code

    def on_tree_item_clicked(self, item, column):
        # 使用QTimer延迟执行元素查找和更新，避免界面卡死
        QTimer.singleShot(0, lambda: self._process_tree_item_click(item))
    
    def _process_tree_item_click(self, item):
        try:
            # 遍历层级路径找到对应的UI元素
            current_item = item
            path = []
            while current_item:
                # 获取元素的名称和控件类型
                item_text = current_item.text(0)
                # 从文本中提取名称和控件类型
                import re
                match = re.match(r"(.+?) \((.+?)\)", item_text)
                if match:
                    name = match.group(1)
                    control_type = match.group(2)
                    path.insert(0, (name, control_type))
                current_item = current_item.parent()
            
            # 从根节点开始查找目标元素
            root_control = auto.GetRootControl()
            target_element = root_control
            
            # 逐层查找目标元素
            for i, (target_name, target_control_type) in enumerate(path):
                found = False
                try:
                    children = target_element.GetChildren()
                    
                    # 遍历直接子元素
                    for child in children:
                        try:
                            # 获取所有可用的匹配属性
                            child_name = child.Name
                            child_type = child.ControlTypeName
                            
                            # 使用精确匹配
                            if child_name == target_name and child_type == target_control_type:
                                target_element = child
                                found = True
                                break
                        except Exception:
                            continue
                    
                    if not found:
                        # 尝试模糊匹配
                        for child in children:
                            try:
                                child_name = child.Name
                                child_type = child.ControlTypeName
                                
                                # 使用部分匹配
                                if ((target_name.lower() in child_name.lower() or 
                                    child_name.lower() in target_name.lower()) and 
                                   child_type == target_control_type):
                                    target_element = child
                                    found = True
                                    break
                            except Exception:
                                continue
                    
                    if not found:
                        return
                except Exception:
                    return
            
            # 找到目标元素后更新界面
            if target_element and target_element != root_control:
                # 更新右侧面板信息
                self.update_element_info(target_element, update_tree=False)
                
                # 先折叠所有节点
                self.tree.collapseAll()
                
                # 展开当前节点的路径
                current_item = item
                while current_item:
                    current_item.setExpanded(True)
                    current_item = current_item.parent()
                
                # 选中当前节点
                self.tree.setCurrentItem(item)
                
                # 使用蓝色高亮框显示选中的元素
                self.highlight_window.highlight_element(target_element.BoundingRectangle, color='blue')
            else:
                print("未找到目标元素")
        except Exception as e:
            print(f"处理树形结构点击事件时出错: {str(e)}")

    def toggle_test_panel(self):
        self.test_panel.setVisible(not self.test_panel.isVisible())

    def toggle_tree_expand(self):
        """切换树形结构的展开/折叠状态"""
        if self.expand_all_btn.isChecked():
            self.tree.expandAll()
            self.expand_all_btn.setText('全部折叠')
        else:
            self.tree.collapseAll()
            self.expand_all_btn.setText('全部展开')
            # 确保当前选中项的路径保持展开
            current_item = self.tree.currentItem()
            if current_item:
                while current_item:
                    current_item.setExpanded(True)
                    current_item = current_item.parent()
    
    def add_code_line(self):
        line_widget = QWidget()
        line_layout = QHBoxLayout(line_widget)
        line_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加代码输入框
        code_edit = QLineEdit()
        code_edit.setPlaceholderText('输入代码')
        line_layout.addWidget(code_edit)
        
        # 添加删除按钮
        delete_btn = QPushButton('删除')
        delete_btn.clicked.connect(lambda: self.code_container_layout.removeWidget(line_widget))
        line_layout.addWidget(delete_btn)
        
        self.code_container_layout.addWidget(line_widget)
    
    def test_code(self):
        # 获取所有代码行
        code_lines = []
        for i in range(self.code_container_layout.count()):
            widget = self.code_container_layout.itemAt(i).widget()
            if widget:
                code_edit = widget.layout().itemAt(0).widget()
                if isinstance(code_edit, QLineEdit):
                    code_lines.append(code_edit.text())
        
        # 添加必要的导入和环境准备代码
        setup_code = """
import uiautomation as auto
from pywinauto.application import Application
import win32gui
import win32api
import win32con
import time

# 初始化全局变量
auto.uiautomation.SetGlobalSearchTimeout(10)
auto.uiautomation.OPERATION_WAIT_TIME = 1

# 初始化应用程序实例
app = Application()
"""
        
        # 创建局部变量字典，用于存储执行过程中的变量
        from pywinauto.application import Application
        local_vars = {
            'auto': auto,
            'Application': Application,
            'win32gui': win32gui,
            'win32api': win32api,
            'win32con': win32con,
            'time': time
        }
        
        # 执行代码并记录时间
        start_time = time.time()
        try:
            # 先执行环境准备代码
            try:
                exec(setup_code, globals(), local_vars)
            except Exception as e:
                error_msg = f'环境初始化错误: {str(e)}'
                self.total_time_label.setText(error_msg)
                self.total_time_label.setStyleSheet('color: red')
                return
            
            # 执行每行代码并记录时间
            for line in code_lines:
                if line.strip():
                    line_start_time = time.time()
                    try:
                        # 尝试执行代码并获取结果
                        try:
                            # 先尝试eval
                            result = eval(line, globals(), local_vars)
                            # 将结果存储到局部变量中，以便后续代码使用
                            if isinstance(result, (auto.Control, Application)):
                                local_vars['result'] = result
                        except (SyntaxError, NameError):
                            # 如果eval失败，尝试exec
                            exec(line, globals(), local_vars)
                            result = local_vars.get('result')
                        
                        line_end_time = time.time()
                        line_time = (line_end_time - line_start_time) * 1000
                        
                        # 更新代码行右侧显示执行时间
                        for j in range(self.code_container_layout.count()):
                            w = self.code_container_layout.itemAt(j).widget()
                            if w and w.layout().itemAt(0).widget().text() == line:
                                time_label = w.layout().itemAt(2).widget() if w.layout().count() > 2 else QLabel()
                                if not time_label:
                                    time_label = QLabel()
                                    w.layout().addWidget(time_label)
                                time_label.setText(f'{line_time:.2f}ms')
                                time_label.setStyleSheet('color: black')
                                break
                        
                        # 如果结果是UI元素，显示高亮
                        if result and hasattr(result, 'BoundingRectangle'):
                            self.highlight_window.highlight_element(result.BoundingRectangle)
                            
                    except Exception as e:
                        error_msg = f'执行代码行出错: {str(e)}'
                        print(error_msg)
                        # 更新错误信息到对应的代码行
                        for j in range(self.code_container_layout.count()):
                            w = self.code_container_layout.itemAt(j).widget()
                            if w and w.layout().itemAt(0).widget().text() == line:
                                time_label = w.layout().itemAt(2).widget() if w.layout().count() > 2 else QLabel()
                                if not time_label:
                                    time_label = QLabel()
                                    w.layout().addWidget(time_label)
                                time_label.setText(error_msg)
                                time_label.setStyleSheet('color: red')
                                break
                        raise
            
            end_time = time.time()
            total_time = (end_time - start_time) * 1000
            self.total_time_label.setText(f'总执行时间: {total_time:.2f}ms')
            self.total_time_label.setStyleSheet('color: black')
        except Exception as e:
            error_msg = f'执行出错: {str(e)}'
            self.total_time_label.setText(error_msg)
            self.total_time_label.setStyleSheet('color: red')


def main():
    app = QApplication(sys.argv)
    window = UILocatorWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()