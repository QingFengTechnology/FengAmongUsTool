# coding:utf-8
import logging
import os
import sys

from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtWidgets import QApplication

from app.common.config import cfg, loadConfig
from app.view.main_window import MainWindow

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

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

# 加载配置（必须在 QApplication 创建后）
loadConfig()

# internationalization
locale = cfg.get(cfg.language).value
translator = QTranslator()
translator.load(f":/qfluentwidgets/i18n/qfluentwidgets.{locale.name()}.qm")
galleryTranslator = QTranslator()
galleryTranslator.load(locale, "app", ".", ":/app/i18n")

app.installTranslator(translator)
app.installTranslator(galleryTranslator)

# 创建主窗口（但不显示，等待下载完成后再显示）
w = MainWindow()

# 在程序退出时清理缓存
def cleanup_before_exit():
    w.cleanupCache()
    app.quit()

# 连接程序退出信号
app.aboutToQuit.connect(cleanup_before_exit)

app.exec()
