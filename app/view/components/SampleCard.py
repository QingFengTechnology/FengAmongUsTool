# coding:utf-8
"""
功能卡片组件
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QSizePolicy
from qfluentwidgets import IconWidget, FluentIcon, ToolTipFilter, ToolTipPosition


class SampleCard(QFrame):
    """功能卡片"""

    def __init__(self, icon, title, content, routeKey, index, parent=None, onClick=None):
        super().__init__(parent=parent)
        self.onClick = onClick
        self.isPressed = False
        self.timer = QTimer(self)

        self.iconWidget = IconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(content, self)
        self.index = index
        self.routeKey = routeKey

        self.titleLabel.setFont(QFont('Microsoft YaHei', 12, QFont.Weight.DemiBold))
        self.contentLabel.setFont(QFont('Microsoft YaHei', 9))

        self.initWidget()

    def initWidget(self):
        """初始化组件"""
        # 移除所有尺寸限制，让父容器完全控制卡片大小
        self.iconWidget.setFixedSize(48, 48)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(24, 24, 24, 24)
        self.vBoxLayout.addWidget(self.iconWidget)
        self.vBoxLayout.addSpacing(16)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        
        # 设置尺寸策略为固定宽度，高度自适应
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
        # 设置标签的文本换行和自动调整大小
        self.titleLabel.setWordWrap(True)
        self.contentLabel.setWordWrap(True)
        self.titleLabel.setAlignment(Qt.AlignTop)
        self.contentLabel.setAlignment(Qt.AlignTop)
        
        # 允许标签根据内容调整大小
        self.titleLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.contentLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')

        self.installEventFilter(ToolTipFilter(self, 250, ToolTipPosition.TOP))

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.isPressed = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.isPressed:
            self.isPressed = False
            if self.onClick:
                self.onClick(self.routeKey)
        super().mouseReleaseEvent(event)