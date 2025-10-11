# coding:utf-8
import sys
import os
from PySide6.QtCore import Qt, QResource
from PySide6.QtWidgets import QApplication

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.module.appManager import AppManager


def load_resources():
    """加载Qt资源文件"""
    # 获取资源文件路径
    qrc_file = os.path.join(project_root, 'app', 'resource.qrc')
    
    # 检查资源文件是否存在
    if not os.path.exists(qrc_file):
        print(f"警告: 资源文件不存在: {qrc_file}")
        return False
    
    # 注册资源文件
    if QResource.registerResource(qrc_file):
        print("资源文件加载成功!")
        return True
    else:
        print("资源文件加载失败!")
        return False


def main():
    """主函数"""
    # 启用高DPI缩放（PySide6现代方式）
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    
    # 加载资源文件
    load_resources()
    
    # 创建应用管理器
    appManagerInstance = AppManager()
    
    # 初始化应用
    window = appManagerInstance.initialize()
    
    # 运行应用
    appManagerInstance.run()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()