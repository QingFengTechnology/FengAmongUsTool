# coding:utf-8
import sys
import os
import logging
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0, project_root)

from app.module.appManager import AppManager
from app.function.updateChecker import startUpdateCheck

def setupLogging():
    """设置标准logging配置"""
    # 在项目根目录创建日志文件
    log_file = Path(project_root) / "FengAmongUsTool.log"
    
    # 配置根日志记录器
    logger = logging.getLogger("FengAmongUsTool")
    logger.setLevel(logging.DEBUG)
    
    # 清除已有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # 文件处理器（追加模式，保留历史日志）
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def main():
    """主函数"""
    # 初始化日志系统
    logger = setupLogging()
    logger.debug("清风工具箱启动中...")
    
    # 启用高DPI缩放（PySide6现代方式）
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    # 加载配置并应用主题和缩放设置
    from app.function.configManager import load_config, cfg, setTheme
    load_config()
    
    # 应用缩放设置
    if cfg.dpiScale.value != "Auto":
        # 将百分比转换为浮点数
        scale_factor = float(cfg.dpiScale.value.rstrip('%')) / 100.0
        os.environ["QT_SCALE_FACTOR"] = str(scale_factor)
    
    app = QApplication(sys.argv)
    
    # 导入Qt资源模块
    try:
        from app.asset import resource_rc
        logger.debug("Qt资源模块导入成功。")
    except ImportError as e:
        logger.error(f"Qt资源模块导入失败: {e}")
    
    # 应用主题设置
    setTheme(cfg.themeMode.value)
    
    # 创建应用管理器
    appManagerInstance = AppManager()
    
    mainWindow = appManagerInstance.initialize()
    startUpdateCheck(mainWindow)
    
    # 运行应用
    appManagerInstance.run()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
