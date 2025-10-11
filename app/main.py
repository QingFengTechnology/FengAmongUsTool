# coding:utf-8
import sys
import os
from PySide6.QtCore import Qt, QResource
from PySide6.QtWidgets import QApplication

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.module.appManager import AppManager

def main():
    """主函数"""
    # 初始化日志系统
    from app.function.logManager import logInfo
    logInfo("清风工具箱启动中...")
    
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
        logInfo("Qt资源模块导入成功")
    except ImportError as e:
        logInfo(f"Qt资源模块导入失败: {e}")
    
    # 应用主题设置
    setTheme(cfg.themeMode.value)
    
    # 创建应用管理器
    appManagerInstance = AppManager()
    
    appManagerInstance.initialize()
    
    # 运行应用
    appManagerInstance.run()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()