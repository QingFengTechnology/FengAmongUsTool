# coding:utf-8
import logging
import os
import sys

from PyQt6.QtCore import Qt, QTranslator, QLocale
from PyQt6.QtWidgets import QApplication

from app.common.config import cfg, loadConfig
from app.view.main_window import MainWindow

# 配置日志：控制台 + 文件（每次启动覆盖，使用用户目录以兼容 PyInstaller/Windows）
_log_dir = os.path.join(os.getenv('LOCALAPPDATA') or os.path.expanduser('~'), 'FengAmongUsTool')
_log_file = os.path.join(_log_dir, 'FengAmongUsTool.log')
_handlers: list[logging.Handler] = [logging.StreamHandler()]
try:
    os.makedirs(_log_dir, exist_ok=True)
    _handlers.append(logging.FileHandler(_log_file, mode='w', encoding='utf-8'))
except Exception:
    print(f"Warning: 无法初始化文件日志 '{_log_file}'，已回退到仅控制台输出。")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=_handlers,
)

# enable dpi scale
if cfg.get(cfg.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
else:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

# create application
app = QApplication(sys.argv)
app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

# 加载配置（必须在 QApplication 创建后）
loadConfig()

# 加载 qfluentwidgets 组件库翻译（使系统语言下 On/Off 等控件文字显示为中文）
_translator = QTranslator()
_locale = QLocale.system()
_translator.load(f":/qfluentwidgets/i18n/qfluentwidgets.{_locale.name()}.qm")
app.installTranslator(_translator)

# 创建主窗口
w = MainWindow()

# 在程序退出时清理缓存
def cleanup_before_exit():
    w.cleanupCache()

app.aboutToQuit.connect(cleanup_before_exit)

app.exec()
