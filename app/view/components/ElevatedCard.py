# coding:utf-8
"""
基于ElevatedCardWidget的功能卡片组件
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout, QLabel
from qfluentwidgets import ElevatedCardWidget, IconWidget, FluentIcon


class ElevatedCard(ElevatedCardWidget):
    """功能卡片"""
    
    clicked = Signal(str)  # 点击信号，传递routeKey
    
    def __init__(self, icon, title, content, routeKey, parent=None):
        super().__init__(parent=parent)
        self.routeKey = routeKey
        
        # 创建组件
        self.iconWidget = IconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(content, self)
        
        # 设置字体
        self.titleLabel.setFont(QFont('Microsoft YaHei', 12, QFont.Weight.DemiBold))
        self.contentLabel.setFont(QFont('Microsoft YaHei', 9))
        
        self.initWidget()

    def initWidget(self):
        """初始化组件"""
        # 设置图标大小
        self.iconWidget.setFixedSize(48, 48)
        
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(24, 24, 24, 24)
        self.vBoxLayout.addWidget(self.iconWidget)
        self.vBoxLayout.addSpacing(16)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        
        # 设置标签属性
        self.titleLabel.setWordWrap(True)
        self.contentLabel.setWordWrap(True)
        self.titleLabel.setAlignment(Qt.AlignTop)
        self.contentLabel.setAlignment(Qt.AlignTop)
        
        # 设置对象名用于样式表
        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')
        
        # 设置卡片固定大小
        self.setFixedSize(200, 160)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        # 不调用父类的mouseReleaseEvent，避免触发父类的clicked信号
        # super().mouseReleaseEvent(event)
        self.clicked.emit(self.routeKey)