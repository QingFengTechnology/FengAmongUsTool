# coding:utf-8
"""
主窗口模块
"""
from PySide6.QtCore import Qt, QSize, Signal, QEvent
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QApplication
from qfluentwidgets import (
    FluentWindow, setTheme, Theme, BodyLabel, NavigationItemPosition, FluentIcon as FIF,
    SplashScreen
)

from ..function.variableConfig import WINDOW_CONFIG, THEME_CONFIG
import logging
from ..view.settingInterface import SettingInterface
from ..view.homeInterface import HomeInterface
from ..view.privateServerInterface import PrivateServerInterface


class SplashScreenWithEventCapture(SplashScreen):
    """自定义SplashScreen，捕获所有鼠标事件"""
    splashHidden = Signal()

    def mousePressEvent(self, event):
        event.accept()

    def mouseReleaseEvent(self, event):
        event.accept()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.splashHidden.emit()


class MainWindow(FluentWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        
        # 初始化logger
        self.logger = logging.getLogger("FengAmongUsTool")

        # 设置主题
        setTheme(getattr(Theme, THEME_CONFIG["theme"]))
        self._splashActive = True
        self._eventFilterInstalled = False

        # 初始化窗口
        self.initWindow()

        # 安装应用级事件过滤器，拦截鼠标事件
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
            self._eventFilterInstalled = True

        # 创建启动画面
        self.splashScreen = SplashScreenWithEventCapture(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.splashScreen.titleBar.maxBtn.setHidden(True)
        self.splashScreen.raise_()

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
        # 延迟恢复鼠标事件处理和卡片启用状态，确保SplashScreen动画完成
        def on_splash_finished():
            # 继续保持事件过滤开启，先清空可能排队的用户输入
            try:
                from PySide6.QtCore import QEventLoop, QCoreApplication
                app = QApplication.instance()
                if app is not None:
                    app.processEvents(QEventLoop.AllEvents, 50)
                    app.processEvents(QEventLoop.AllEvents, 50)
                    QCoreApplication.removePostedEvents(None)
            except Exception:
                pass

            # 关闭拦截，恢复正常输入
            self._splashActive = False
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            app = QApplication.instance()
            if app is not None and self._eventFilterInstalled:
                app.removeEventFilter(self)
                self._eventFilterInstalled = False
            # 最后再启用卡片，避免排队事件触发
            self.homeInterface.setCardsEnabled(True)

        self.splashScreen.splashHidden.connect(on_splash_finished)
        self.splashScreen.finish()

    def eventFilter(self, obj, event):
        """在启动画面显示时屏蔽所有鼠标相关事件（包括悬停/移动/滚轮/菜单）"""
        if getattr(self, "_splashActive", False):
            if event.type() in {
                QEvent.MouseButtonPress,
                QEvent.MouseButtonRelease,
                QEvent.MouseButtonDblClick,
                QEvent.MouseMove,
                QEvent.Wheel,
                QEvent.HoverEnter,
                QEvent.HoverLeave,
                QEvent.HoverMove,
                QEvent.ContextMenu,
            }:
                return True
        return super().eventFilter(obj, event)

    def initWindow(self):
        """初始化窗口"""
        self.resize(WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
        self.setWindowTitle(WINDOW_CONFIG["title"])

        # 设置窗口图标 - 使用Qt资源系统
        try:
            self.setWindowIcon(QIcon(":/asset/logo.png"))
            self.logger.debug("成功加载图标文件。")
        except Exception as e:
            self.logger.warning(f"图标文件加载失败: {str(e)}")
            self.setWindowIcon(QIcon())

        # 禁用窗口大小调整
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

        # 添加私服安装界面到导航滚动区
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
        self.logger.debug(f"尝试切换到界面{routeKey}。")

        interface_map = {
            'privateServerInterface': self.privateServerInterface,
            'settingInterface': self.settingInterface
        }

        if routeKey in interface_map:
            try:
                self.switchTo(interface_map[routeKey])
                self.logger.debug(f"成功切换到界面{routeKey}。")
            except Exception as e:
                self.logger.error(f"切换到{routeKey}时出错: {str(e)}")
        elif routeKey == 'homeInterface':
            try:
                self.switchTo(self.homeInterface)
                self.logger.debug(f"成功切换到{routeKey}。")
            except Exception as e:
                self.logger.error(f"切换到{routeKey}时出错: {str(e)}")
        else:
            self.logger.warning(f"未找到{routeKey}，该页面是否存在?")
