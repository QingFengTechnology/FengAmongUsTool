# coding:utf-8
import os
import sys

from PyQt5.QtCore import Qt, QTranslator, QLocale, QTimer, QEventLoop, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator, SplashScreen
from qframelesswindow import StandardTitleBar

from app.common.config import cfg
from app.view.main_window import MainWindow
from app.common.signal_bus import getSignalBus

# enable dpi scale
if cfg.get(cfg.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
else:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

# create application
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

# internationalization
locale = cfg.get(cfg.language).value
translator = QTranslator()
translator.load(f":/qfluentwidgets/i18n/qfluentwidgets.{locale.name()}.qm")
galleryTranslator = QTranslator()
galleryTranslator.load(locale, "app", ".", ":/app/i18n")

app.installTranslator(translator)
app.installTranslator(galleryTranslator)

# create main window
w = MainWindow()

# 1. 创建启动页面（无标题和图标，更加简洁）
splashScreen = SplashScreen(QIcon(':/app/images/logo.png'), w)
splashScreen.setIconSize(QSize(120, 120))

# 2. 在创建其他子页面前先显示主界面
w.show()

# 3. 定义隐藏启动页面的函数
def hideSplashScreen():
    splashScreen.finish()

# 4. 连接服务器列表下载完成信号到隐藏启动页面函数
getSignalBus().serversDownloaded.connect(hideSplashScreen)

# 在程序退出时清理缓存
def cleanup_before_exit():
    w.cleanupCache()
    app.quit()

# 连接程序退出信号
app.aboutToQuit.connect(cleanup_before_exit)

app.exec()
