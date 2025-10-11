# coding:utf-8
import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.module.appManager import AppManager


def main():
    """主函数"""
    # 启用高DPI缩放（PySide6现代方式）
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    
    # 创建应用管理器
    appManagerInstance = AppManager()
    
    # 初始化应用
    window = appManagerInstance.initialize()
    
    # 运行应用
    appManagerInstance.run()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()