# coding:utf-8
"""
应用管理模块
"""
from .mainWindow import MainWindow


class AppManager:
    """应用管理类"""
    
    def __init__(self):
        self.mainWindow = None
        
    def initialize(self):
        """初始化应用"""
        # 创建主窗口（在MainWindow中会创建所有界面）
        self.mainWindow = MainWindow()
        
        return self.mainWindow
    
    def run(self):
        """运行应用"""
        # 主窗口已经在初始化时显示，这里只需返回True
        if self.mainWindow:
            return True
        return False