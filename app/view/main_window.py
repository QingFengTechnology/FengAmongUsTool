# coding: utf-8
import asyncio
import sys
from PyQt5.QtCore import QUrl, QSize, QTimer, QObject, pyqtSignal
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
from ..common.servers_downloader import ServersDownloader


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
            import sys
            if sys.platform.startswith("win"):
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            # 运行异步下载
            data = asyncio.run(downloader.download_servers_json())
            self.download_finished.emit(data)
        except Exception as e:
            print(f"下载 servers.json 时出错: {e}")
            self.download_finished.emit(None)


class MainWindow(SplitFluentWindow):

    def __init__(self):
        super().__init__()
        self.homeInterface = None
        self.privateServerInterface = None
        self.settingInterface = None
        self.download_worker = None
        self.download_thread = None

        self.connectSignalToSlot()

        # 在初始化窗口之前下载servers.json
        self.downloadServersJson()

        self.initWindow()

        # create sub interface
        # 移除主页
        # self.homeInterface = HomeInterface(self)
        self.privateServerInterface = PrivateServerInterface(self)
        self.settingInterface = SettingInterface(self)

        # add items to navigation interface
        self.initNavigation()
        
        # 设置默认页面为私服安装页
        self.switchTo(self.privateServerInterface)
    
    def downloadServersJson(self):
        """在程序启动时下载servers.json文件"""
        try:
            from PyQt5.QtCore import QThread
            
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
            print(f"启动时下载servers.json失败: {e}")
    
    def _onDownloadFinished(self, servers_data):
        """下载完成回调"""
        try:
            if servers_data:
                print("成功下载servers.json")

                # 将数据传递给 PrivateServerCard 并更新 UI
                if self.privateServerInterface and self.privateServerInterface.headerCard:
                    self.privateServerInterface.headerCard.setServersData(servers_data)
            else:
                print("下载servers.json失败")
        except Exception as e:
            print(f"处理servers.json时出错: {e}")
        finally:
            # 无论成功与否，都发送下载完成信号以隐藏 SplashScreen
            getSignalBus().serversDownloaded.emit()
    
    def cleanupCache(self):
        """清理缓存文件夹"""
        try:
            from ..common.servers_downloader import get_temp_cache_dir
            import os
            import shutil
            cache_dir = get_temp_cache_dir()
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                print("已清理缓存文件夹")
        except Exception as e:
            print(f"清理缓存文件夹时出错: {e}")

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
        # 注意：这里不再调用self.show()，因为启动屏幕会处理显示

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())