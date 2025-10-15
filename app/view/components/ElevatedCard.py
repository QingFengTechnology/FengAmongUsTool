# coding:utf-8
"""
基于ElevatedCardWidget的功能卡片组件
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout, QLabel
from qfluentwidgets import ElevatedCardWidget, IconWidget, FluentIcon, isDarkTheme


class ElevatedCard(ElevatedCardWidget):
    """功能卡片"""
    
    clicked = Signal(str)  # 点击信号，传递routeKey
    
    def __init__(self, icon, title, content, routeKey, parent=None):
        super().__init__(parent=parent)
        self.routeKey = routeKey
        self._enabled = True  # 自定义启用状态
        
        # 创建组件
        self.iconWidget = IconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(content, self)
        
        # 设置字体
        self.titleLabel.setFont(QFont('Microsoft YaHei', 12, QFont.Weight.DemiBold))
        self.contentLabel.setFont(QFont('Microsoft YaHei', 9))
        
        self.initWidget()
        self.updateTextColor()

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

    def updateTextColor(self):
        """根据主题更新文字颜色"""
        if isDarkTheme():
            # 深色主题使用白色文字
            self.titleLabel.setStyleSheet("color: white;")
            self.contentLabel.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        else:
            # 浅色主题使用黑色文字
            self.titleLabel.setStyleSheet("color: black;")
            self.contentLabel.setStyleSheet("color: rgba(0, 0, 0, 0.7);")

    def setEnabled(self, enabled):
        """设置组件启用状态"""
        self._enabled = enabled
        super().setEnabled(enabled)
        
    def isEnabled(self):
        """获取组件启用状态"""
        # 确保属性存在，避免初始化过程中的访问错误
        return getattr(self, '_enabled', True)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        # 不调用父类方法，完全控制事件
        pass

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        # 只有在启用状态下才响应点击事件
        if self._enabled:
            self.clicked.emit(self.routeKey)