# coding:utf-8
"""
主界面模块
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    ScrollArea, BodyLabel, setFont, TitleLabel
)


class HomeInterface(ScrollArea):
    """主界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        
        # 创建标题
        self.titleLabel = TitleLabel("清风工具箱", self.scrollWidget)
        setFont(self.titleLabel, 24, QFont.Weight.DemiBold)  # 设置大号粗体字体
        
        # 创建欢迎信息
        self.welcomeLabel = BodyLabel(
            "欢迎使用清风工具箱！\n\n"
            "这是一个专为Among Us私服管理设计的工具。\n"
            "您可以使用左侧导航栏访问不同功能。",
            self.scrollWidget
        )
        
        self.InitWidget()

    def InitWidget(self):
        """初始化界面"""
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('homeInterface')
        
        # 设置布局
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.welcomeLabel)
        self.vBoxLayout.addStretch(1)
        
        # 设置样式
        self.scrollWidget.setStyleSheet("QWidget{background:transparent}")
        self.setStyleSheet("HomeInterface{background:transparent}")