import PyInstaller.__main__

PyInstaller.__main__.run([
    'ui_locator_gui.py',
    '--name=uiauto-UI元素定位工具',
    '--onefile',
    '--windowed',
    '--add-data=help.html;.',
    '--icon=logo.png',
    '--hidden-import=keyboard',
    '--hidden-import=win32api',
    '--hidden-import=win32con',
    '--hidden-import=uiautomation',
    '--clean',
    '--noconfirm'
])