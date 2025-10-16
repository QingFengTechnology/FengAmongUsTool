# coding:utf-8
"""
主窗口模块
"""
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QApplication
from qfluentwidgets import (
    FluentWindow, setTheme, Theme, BodyLabel, NavigationItemPosition, FluentIcon as FIF,
    SplashScreen
)

from ..function.variableConfig import WINDOW_CONFIG, THEME_CONFIG
from ..view.settingInterface import SettingInterface
from ..view.homeInterface import HomeInterface
from ..view.privateServerInterface import PrivateServerInterface


class SplashScreenWithEventCapture(SplashScreen):
    """自定义SplashScreen，捕获所有鼠标事件"""
    def mousePressEvent(self, event):
        """捕获鼠标按下事件"""
        event.accept()

    def mouseReleaseEvent(self, event):
        """捕获鼠标释放事件"""
        event.accept()


class MainWindow(FluentWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 设置主题
        setTheme(getattr(Theme, THEME_CONFIG["theme"]))
        
        # 初始化窗口
        self.initWindow()
        
        # 创建启动画面
        self.splashScreen = SplashScreenWithEventCapture(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.splashScreen.titleBar.maxBtn.setHidden(True)
        self.splashScreen.raise_()
        # 设置主窗口对鼠标事件透明
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # 显示窗口
        self.show()
        QApplication.processEvents()
        
        # 创建子界面
        self.homeInterface = HomeInterface(self)
        self.homeInterface.setCardsEnabled(False)
        self.settingInterface = SettingInterface(self)
        self.privateServerInterface = PrivateServerInterface(self)
        
        # 连接信号
        self.homeInterface.navigateToInterface.connect(self.switchToInterface)
        
        # 初始化导航
        self.initNavigation()
        
        # 完成启动画面
        self.splashScreen.finish()
        # 延迟恢复鼠标事件处理和卡片启用状态，确保SplashScreen动画完成
        def on_splash_finished():
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.homeInterface.setCardsEnabled(True)
        QTimer.singleShot(50, on_splash_finished)
        
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
        
        # 禁用窗口大小调整 - 参考March7thAssistant的实现
        self.titleBar.maxBtn.setHidden(True)
        self.titleBar.maxBtn.setDisabled(True)
        self.titleBar.setDoubleClickEnabled(False)
        self.setResizeEnabled(False)
        
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
        
        # 添加私服安装界面到导航
        self.addSubInterface(
            self.privateServerInterface, FIF.DOWNLOAD, '私服安装', NavigationItemPosition.SCROLL)
        
        # 添加设置界面到导航底部
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)
        
        # 设置默认显示主页
        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())
        
    def updateStatus(self, message):
        """更新状态栏消息"""
        self.StatusLabel.setText(message)
        
    def switchToInterface(self, routeKey):
        """切换到指定界面"""
        from ..function.logManager import logInfo, logWarning
        logInfo(f"尝试切换到界面: {routeKey}")
        
        # 直接使用switchTo方法切换界面
        interface_map = {
            'privateServerInterface': self.privateServerInterface,
            'settingInterface': self.settingInterface
        }
        
        if routeKey in interface_map:
            try:
                self.switchTo(interface_map[routeKey])
                logInfo(f"成功切换到界面: {routeKey}")
            except Exception as e:
                logWarning(f"切换界面时出错: {routeKey}, 错误: {str(e)}")
        elif routeKey == 'homeInterface':
            try:
                self.switchTo(self.homeInterface)
                logInfo(f"成功切换到界面: {routeKey}")
            except Exception as e:
                logWarning(f"切换界面时出错: {routeKey}, 错误: {str(e)}")
        else:
            logWarning(f"未找到对应的界面: {routeKey}")