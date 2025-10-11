# coding:utf-8
"""
主窗口模块
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QApplication
from qfluentwidgets import (
    FluentWindow, setTheme, Theme, BodyLabel, NavigationItemPosition, FluentIcon as FIF
)

from ..function.variableConfig import WINDOW_CONFIG, THEME_CONFIG
from ..view.settingInterface import SettingInterface
from ..view.homeInterface import HomeInterface


class MainWindow(FluentWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 设置主题
        setTheme(getattr(Theme, THEME_CONFIG["theme"]))
        
        # 初始化窗口
        self.initWindow()
        
        # 创建子界面
        self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)
        
        # 初始化导航
        self.initNavigation()
        
    def initWindow(self):
        """初始化窗口"""
        self.resize(WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
        self.setWindowTitle(WINDOW_CONFIG["title"])
        
        # 设置窗口图标 - 使用绝对路径确保正确加载
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, '..', 'asset', 'logo.png')
        logo_path = os.path.abspath(logo_path)
        
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
            from ..function.logManager import logInfo
            logInfo(f"图标加载成功: {logo_path}")
        else:
            from ..function.logManager import logWarning
            logWarning(f"图标文件不存在: {logo_path}")
            # 创建一个空的图标作为备用
            self.setWindowIcon(QIcon())
        
        # 创建状态栏
        self.StatusLabel = BodyLabel('就绪')
        self.StatusWidget = QWidget()
        statusLayout = QHBoxLayout(self.StatusWidget)
        statusLayout.addWidget(self.StatusLabel)
        statusLayout.addStretch(1)
        
        # 居中显示窗口
        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        
    def initNavigation(self):
        """初始化导航"""
        # 添加主界面到导航顶部
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')
        
        # 添加设置界面到导航底部
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)
        
        # 设置默认显示主页
        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())
        
    def updateStatus(self, message):
        """更新状态栏消息"""
        self.StatusLabel.setText(message)