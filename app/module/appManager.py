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
        if self.mainWindow:
            self.mainWindow.show()
            return True
        return False