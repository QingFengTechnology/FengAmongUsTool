# coding: utf-8
import asyncio
import logging
import sys

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QApplication

from qfluentwidgets import NavigationItemPosition, SplitFluentWindow
from qfluentwidgets import FluentIcon as FIF

from .setting_interface import SettingInterface
from .private_server_interface import PrivateServerInterface
from ..common.config import cfg
from ..common.signal_bus import getSignalBus
from ..common.servers_downloader import ServersDownloader

# 导入资源模块以确保资源文件被加载
from ..common import resource as _resource  # noqa: F401

logger = logging.getLogger(__name__)


class DownloadWorker(QObject):
    """下载工作线程类"""
    download_finished = pyqtSignal(object)  # 下载完成信号，传递下载的数据

    def __init__(self):
        super().__init__()

    def download_servers_json(self):
        """在后台线程中下载servers.json"""
        try:
            # 创建下载器实例
            downloader = ServersDownloader()

            # 在 Windows 上需要设置事件循环策略
            if sys.platform.startswith("win"):
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

            # 运行异步下载
            data = asyncio.run(downloader.download_servers_json())
            self.download_finished.emit(data)
        except Exception as e:
            logger.error(f"下载 servers.json 时出错: {e}")
            self.download_finished.emit(None)


class MainWindow(SplitFluentWindow):

    def __init__(self):
        super().__init__()
        self.homeInterface = None
        self.privateServerInterface = None
        self.settingInterface = None
        self.download_worker = None
        self.download_thread = None
        self.splashScreen = None
        self._servers_data = None

        # 基础设置
        self.initWindowBasic()

        # 先显示主窗口（此时内容为空）
        self.show()

        # 连接信号
        self.connectSignalToSlot()

        # 创建并显示 SplashScreen（覆盖在主窗口上）
        self.createSplashScreen()

        # 开始下载（在 SplashScreen 显示时执行）
        self.downloadServersJson()

    def initWindowBasic(self):
        """基础窗口初始化（窗口大小、位置等，但不创建子界面）"""
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/app/images/logo.png'))
        self.setWindowTitle('清风工具箱')

        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        # 注意：这里不调用 self.show()，因为等待下载完成后再显示

    def createSplashScreen(self):
        """创建并显示启动画面"""
        from qfluentwidgets import SplashScreen
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize

        self.splashScreen = SplashScreen(QIcon(':/app/images/logo.png'), self)
        self.splashScreen.setIconSize(QSize(120, 120))
        self.splashScreen.resize(self.size())
        self.splashScreen.show()

    def createInterfaces(self):
        """创建所有子界面"""
        # 移除主页
        # self.homeInterface = HomeInterface(self)
        self.privateServerInterface = PrivateServerInterface(self)
        self.settingInterface = SettingInterface(self)

        # add items to navigation interface
        self.initNavigation()

        # 设置默认页面为私服安装页
        self.switchTo(self.privateServerInterface)

    def finishSplashAndShow(self):
        """关闭 SplashScreen 并显示主窗口"""
        if self.splashScreen:
            self.splashScreen.finish()
            self.splashScreen = None
        self.show()

    def downloadServersJson(self):
        """在程序启动时下载servers.json文件（在 SplashScreen 显示时执行）"""
        try:
            from PyQt6.QtCore import QThread

            # 创建工作线程和工作对象
            self.download_thread = QThread()
            self.download_worker = DownloadWorker()

            # 将工作对象移动到线程中
            self.download_worker.moveToThread(self.download_thread)

            # 连接信号和槽
            self.download_thread.started.connect(self.download_worker.download_servers_json)
            self.download_worker.download_finished.connect(self._onDownloadFinished)
            self.download_worker.download_finished.connect(self.download_thread.quit)
            self.download_worker.download_finished.connect(self.download_worker.deleteLater)
            self.download_thread.finished.connect(self.download_thread.deleteLater)

            # 启动线程
            self.download_thread.start()
        except Exception as e:
            logger.error(f"启动时下载servers.json失败: {e}")
            # 下载失败也要继续初始化界面
            self._downloadComplete(None)

    def _onDownloadFinished(self, servers_data):
        """下载完成回调"""
        try:
            if servers_data:
                logger.info("成功下载servers.json")
                self._servers_data = servers_data
            else:
                logger.warning("下载servers.json失败")
                self._servers_data = None
        except Exception as e:
            logger.error(f"处理servers.json时出错: {e}")
            self._servers_data = None

        self._downloadComplete(self._servers_data)

    def _downloadComplete(self, servers_data):
        """下载完成后的处理，创建界面并显示主窗口"""
        try:
            # 创建界面
            self.createInterfaces()

            # 将数据传递给 PrivateServerCard 并更新 UI
            if servers_data and self.privateServerInterface and self.privateServerInterface.headerCard:
                self.privateServerInterface.headerCard.setServersData(servers_data)

            # 关闭 SplashScreen 并显示主窗口
            self.finishSplashAndShow()
        except Exception as e:
            logger.error(f"下载完成后处理出错: {e}")
            # 出错也要关闭 SplashScreen 并显示主窗口
            self.finishSplashAndShow()

    def cleanupCache(self):
        """清理缓存文件夹"""
        try:
            from ..common.servers_downloader import get_temp_cache_dir
            import os
            import shutil
            cache_dir = get_temp_cache_dir()
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                logger.info("已清理缓存文件夹")
        except Exception as e:
            logger.error(f"清理缓存文件夹时出错: {e}")

    def connectSignalToSlot(self):
        getSignalBus().micaEnableChanged.connect(self.setMicaEffectEnabled)

    def initNavigation(self):
        # self.navigationInterface.setAcrylicEnabled(True)

        # add private server widget
        if self.privateServerInterface:
            self.addSubInterface(self.privateServerInterface, FIF.DOWNLOAD, self.tr('私服安装'))

        # add custom widget to bottom
        if self.settingInterface:
            self.addSubInterface(
                self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)
