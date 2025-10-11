# coding:utf-8
"""
应用管理模块
"""
from .mainWindow import MainWindow
from ..view.privateServerInterface import PrivateServerInterface


class AppManager:
    """应用管理类"""
    
    def __init__(self):
        self.mainWindow = None
        self.privateServerInterface = None
        
    def initialize(self):
        """初始化应用"""
        # 创建主窗口
        self.mainWindow = MainWindow()
        
        # 创建私服安装界面
        self.privateServerInterface = PrivateServerInterface(self.mainWindow)
        privateServerWidget = self.privateServerInterface.createInterface()
        
        # 添加到导航栏
        self.privateServerInterface.addToNavigation(privateServerWidget)
        
        return self.mainWindow
    
    def run(self):
        """运行应用"""
        if self.mainWindow:
            self.mainWindow.show()
            return True
        return False