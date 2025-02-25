import uiautomation as auto
import keyboard
import time
import win32gui
import win32api
import win32con

def get_mouse_position():
    return win32gui.GetCursorPos()

def get_element_under_mouse():
    x, y = get_mouse_position()
    # 先尝试从上一次找到的元素开始查找
    element = auto.ControlFromPoint(x, y)
    if not element:
        return None
    
    def find_deepest_element(current_element, depth=0, max_depth=10):
        if depth >= max_depth:
            return current_element, False
            
        print(f'是否可见: {element.IsVisible()}')
        print(f'是否可用: {element.IsEnabled()}')
            for child in children:
                try:
                    rect = child.BoundingRectangle
                    # 检查鼠标是否在子元素的范围内
                    if (rect.left <= x <= rect.right and 
                        rect.top <= y <= rect.bottom):
                        # 递归查找更深层的元素
                        deeper_element, found_deeper = find_deepest_element(child, depth + 1)
                        if found_deeper:
                            return deeper_element, True
                        # 如果没有更深层的元素，但当前元素可见且可交互，则返回当前元素
                        if not child.IsOffscreen and child.IsEnabled:
                            return child, True
                except Exception:
                    continue
        except Exception:
            pass
            
        # 如果当前元素可见且可交互，返回当前元素
        if not current_element.IsOffscreen and current_element.IsEnabled:
            return current_element, True
        return current_element, False
    
    # 开始深度优先搜索
    result_element, found = find_deepest_element(element)
    return result_element

def generate_uiautomation_code(element):
    if not element:
        return
    
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
            control_type = current.ControlTypeName.replace('Control', '')
            conditions.append(f'ControlType=auto.ControlType.{control_type}')
        
        if conditions:
            hierarchy.insert(0, f'auto.{current.ControlTypeName}({", ".join(conditions)})')
        current = current.GetParentControl()
    
    # 生成完整的定位代码
    if hierarchy:
        code = hierarchy[0]
        for i in range(1, len(hierarchy)):
            code += f'.{hierarchy[i]}'
        return code
    return None

def generate_pywinauto_code(element):
    if not element:
        return
    
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
    code = f"app.window({conditions})"
    return code

def print_element_info(element):
    if element:
        print('\n元素基本信息:')
        print(f'名称: {element.Name}')        
        print(f'类名: {element.ClassName}')
        print(f'控件类型: {element.ControlTypeName}')
        print(f'自动化ID: {element.AutomationId}')
        try:
            print(f'运行时ID: {element.GetRuntimeId()}')            
            print(f'位置: {element.BoundingRectangle}')
            print(f'进程ID: {element.ProcessId}')
            
            # 添加文本内容显示
            try:
                text_content = None
                # 尝试使用TextPattern
                if element.GetPattern(auto.PatternId.TextPattern):
                    text_pattern = element.GetPattern(auto.PatternId.TextPattern)
                    text_content = text_pattern.DocumentRange.GetText(-1)
                # 尝试使用ValuePattern
                elif element.GetPattern(auto.PatternId.ValuePattern):
                    value_pattern = element.GetPattern(auto.PatternId.ValuePattern)
                    text_content = value_pattern.Value
                # 尝试使用LegacyIAccessiblePattern
                elif hasattr(element, 'GetLegacyIAccessiblePattern'):
                    acc_pattern = element.GetLegacyIAccessiblePattern()
                    if acc_pattern:
                        text_content = acc_pattern.Value or acc_pattern.Name
                # 如果都没有获取到，尝试直接获取Name属性
                if text_content is None:
                    text_content = element.Name
                
                if text_content:
                    print(f'文本内容: {text_content}')
            except Exception as e:
                print(f'获取文本内容时出错: {str(e)}')
            
            print('\n元素状态:')
            print(f'是否可见: {element.IsOffscreen == False}')
            print(f'是否可用: {element.IsEnabled}')
            print(f'是否可聚焦: {element.IsKeyboardFocusable}')
            print(f'是否已聚焦: {element.HasKeyboardFocus}')
        except AttributeError as e:
            print(f'获取元素属性时出错: {str(e)}')
        
        print('\n元素层级:')
        print(f'父元素: {element.GetParentControl().Name if element.GetParentControl() else "无"}')
        children = element.GetChildren()
        print(f'子元素数量: {len(children)}')
        if children:
            print('子元素列表:')
            for child in children:
                print(f'  - {child.Name} ({child.ControlTypeName})')
        
        print('\n支持的模式:')
        try:
            if element.GetPattern(auto.PatternId.InvokePattern):
                print('- 可执行操作')
            if element.GetPattern(auto.PatternId.ValuePattern):
                pattern = element.GetPattern(auto.PatternId.ValuePattern)
                print('- 可设置值')
                print(f'当前值: {pattern.Value}')
            if element.GetPattern(auto.PatternId.TextPattern):
                print('- 包含文本')
            if element.GetPattern(auto.PatternId.TogglePattern):
                pattern = element.GetPattern(auto.PatternId.TogglePattern)
                print('- 可切换状态')
                print(f'当前状态: {pattern.ToggleState}')
            if element.GetPattern(auto.PatternId.SelectionPattern):
                print('- 可选择')
            if element.GetPattern(auto.PatternId.RangeValuePattern):
                pattern = element.GetPattern(auto.PatternId.RangeValuePattern)
                print('- 可设置范围值')
                print(f'  当前值: {pattern.Value}')
                print(f'  最小值: {pattern.Minimum}')
                print(f'  最大值: {pattern.Maximum}')
        except Exception as e:
            print(f'获取元素支持的模式时出错: {str(e)}')
        
        print('\n定位代码:')
        uia_code = generate_uiautomation_code(element)
        if uia_code:
            print('UIAutomation定位代码:')
            print(uia_code)
        
        pywinauto_code = generate_pywinauto_code(element)
        if pywinauto_code:
            print('\nPywinauto定位代码:')
            print(pywinauto_code)

def main():
    print('UI元素定位工具')
    print('按F4键获取鼠标位置下的UI元素信息')
    print('按F5键切换动态获取模式（点击获取）')
    print('按Esc键退出程序')
    
    dynamic_mode = False
    last_click_state = False
    
    while True:
        if keyboard.is_pressed('f4'):
            element = get_element_under_mouse()
            print_element_info(element)
            # 等待按键释放
            while keyboard.is_pressed('f4'):
                time.sleep(0.1)
        
        if keyboard.is_pressed('f5'):
            dynamic_mode = not dynamic_mode
            print(f"动态获取模式: {'开启' if dynamic_mode else '关闭'}")
            # 等待按键释放
            while keyboard.is_pressed('f5'):
                time.sleep(0.1)
        
        if dynamic_mode:
            # 检测鼠标左键点击
            click_state = win32api.GetKeyState(win32con.VK_LBUTTON)
            # 检测点击按下的瞬间
            if click_state < 0 and not last_click_state:
                element = get_element_under_mouse()
                print_element_info(element)
            last_click_state = click_state < 0
        
        if keyboard.is_pressed('esc'):
            break
        
        time.sleep(0.1)

if __name__ == '__main__':
    main()