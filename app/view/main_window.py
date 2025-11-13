# coding: utf-8
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import NavigationItemPosition, SplitFluentWindow
from qfluentwidgets import FluentIcon as FIF

from .setting_interface import SettingInterface
from .home_interface import HomeInterface
from .private_server_interface import PrivateServerInterface
from ..common.config import cfg
from ..common.icon import Icon
from ..common.signal_bus import getSignalBus
from ..common import resource


class MainWindow(SplitFluentWindow):

    def __init__(self):
        super().__init__()
        self.homeInterface = None
        self.privateServerInterface = None
        self.settingInterface = None

        self.connectSignalToSlot()

        self.initWindow()

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.privateServerInterface = PrivateServerInterface(self)
        self.settingInterface = SettingInterface(self)

        # add items to navigation interface
        self.initNavigation()

    def connectSignalToSlot(self):
        getSignalBus().micaEnableChanged.connect(self.setMicaEffectEnabled)

    def initNavigation(self):
        # self.navigationInterface.setAcrylicEnabled(True)

        # add home widget
        if self.homeInterface:
            self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('主页'))

        # add private server widget
        if self.privateServerInterface:
            self.addSubInterface(self.privateServerInterface, FIF.DOWNLOAD, self.tr('私服安装'))

        # add custom widget to bottom
        if self.settingInterface:
            self.addSubInterface(
                self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/app/images/logo.png'))
        self.setWindowTitle('清风工具箱')

        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())