# coding:utf-8
"""主窗口模块"""
import logging
from PySide6.QtCore import Qt, QSize, Signal, QEvent
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
from ..view.toolsInterface import ToolsInterface


class SplashScreenWithEventCapture(SplashScreen):
    """自定义启动画面，在完全隐藏前屏蔽所有鼠标事件"""

    splashHidden = Signal()

    def mousePressEvent(self, event):
        event.accept()

    def mouseReleaseEvent(self, event):
        event.accept()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.splashHidden.emit()


class MainWindow(FluentWindow):
    """应用主窗口"""

    def __init__(self):
        super().__init__()

        # 初始化日志记录器
        self.logger = logging.getLogger("FengAmongUsTool")

        # 按配置应用主题
        setTheme(getattr(Theme, THEME_CONFIG["theme"]))
        self._splashActive = True
        self._eventFilterInstalled = False

        # 初始化窗口尺寸、标题等基础信息
        self.initWindow()

        # 安装事件过滤器，在启动画面期间屏蔽鼠标操作
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
            self._eventFilterInstalled = True

        # 创建并显示启动画面
        self.splashScreen = SplashScreenWithEventCapture(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.splashScreen.titleBar.maxBtn.setHidden(True)
        self.splashScreen.raise_()

        # 先展示窗口，再处理启动动画
        self.show()
        QApplication.processEvents()

        # 创建各个功能界面
        self.homeInterface = HomeInterface(self)
        self.homeInterface.setCardsEnabled(False)
        self.settingInterface = SettingInterface(self)
        self.privateServerInterface = PrivateServerInterface(self)
        self.toolsInterface = ToolsInterface(self)

        # 主页卡片点击后切换到对应界面
        self.homeInterface.navigateToInterface.connect(self.switchToInterface)

        # 初始化导航栏内容
        self.initNavigation()

        # 启动画面结束时恢复输入并启用卡片
        def on_splash_finished():
            self._splashActive = False
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            inner_app = QApplication.instance()
            if inner_app is not None and self._eventFilterInstalled:
                inner_app.removeEventFilter(self)
                self._eventFilterInstalled = False
            self.homeInterface.setCardsEnabled(True)

        self.splashScreen.splashHidden.connect(on_splash_finished)
        self.splashScreen.finish()

    def eventFilter(self, obj, event):
        """在启动画面仍显示时屏蔽鼠标输入事件"""
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
        """初始化窗口尺寸、标题、图标及状态栏"""
        self.resize(WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
        self.setWindowTitle(WINDOW_CONFIG["title"])

        # 设置窗口图标，失败时写日志并使用空图标
        try:
            self.setWindowIcon(QIcon(":/asset/logo.png"))
            self.logger.debug("窗口图标加载成功")
        except Exception as exc:
            self.logger.warning("窗口图标加载失败: %s", exc)
            self.setWindowIcon(QIcon())

        # 锁定窗口尺寸，避免用户拉伸
        self.titleBar.maxBtn.setHidden(True)
        self.titleBar.maxBtn.setDisabled(True)
        self.titleBar.setDoubleClickEnabled(False)
        self.setResizeEnabled(False)

        # 创建状态栏显示文字
        self.StatusLabel = BodyLabel('就绪')
        self.StatusWidget = QWidget()
        status_layout = QHBoxLayout(self.StatusWidget)
        status_layout.addWidget(self.StatusLabel)
        status_layout.addStretch(1)

        # 计算并设置窗口居中位置
        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def initNavigation(self):
        """初始化导航栏内容"""
        # 主页入口位于顶部
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')

        # 私服安装与工具集合展示在滚动区域
        self.addSubInterface(
            self.privateServerInterface, FIF.DOWNLOAD, '私服安装', NavigationItemPosition.SCROLL)

        self.addSubInterface(
            self.toolsInterface, FIF.APPLICATION, '工具集合', NavigationItemPosition.SCROLL)

        # 设置界面放在底部
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

        # 默认显示主页
        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())

    def updateStatus(self, message):
        """更新状态栏文本"""
        self.StatusLabel.setText(message)

    def switchToInterface(self, routeKey):
        """切换到指定功能界面"""
        self.logger.debug("尝试切换到界面 %s", routeKey)

        interface_map = {
            'privateServerInterface': self.privateServerInterface,
            'settingInterface': self.settingInterface,
            'toolsInterface': self.toolsInterface
        }

        if routeKey in interface_map:
            try:
                self.switchTo(interface_map[routeKey])
                self.logger.debug("成功切换到界面 %s", routeKey)
            except Exception as exc:
                self.logger.error("切换到 %s 时出错: %s", routeKey, exc)
        elif routeKey == 'homeInterface':
            try:
                self.switchTo(self.homeInterface)
                self.logger.debug("成功切换到界面 %s", routeKey)
            except Exception as exc:
                self.logger.error("切换到 %s 时出错: %s", routeKey, exc)
        else:
            self.logger.warning("未注册的界面: %s", routeKey)
