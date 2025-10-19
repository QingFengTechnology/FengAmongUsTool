# coding:utf-8
"""
横幅组件
"""
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from ...function.variableConfig import PROJECT_CONFIG


class BannerWidget(QWidget):
    """横幅组件"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # 不设置固定高度，让高度根据父容器动态调整
        self.vBoxLayout = QVBoxLayout(self)
        self.titleLabel = QLabel(self)
        self.subtitleLabel = QLabel(self)

        self.initWidget()

    def initWidget(self):
        """初始化组件"""
        # 设置标题和副标题
        self.titleLabel.setText(PROJECT_CONFIG["name"])
        self.titleLabel.setFont(QFont('Microsoft YaHei', 28, QFont.Weight.DemiBold))
        self.titleLabel.setStyleSheet("color: white;")
        
        self.subtitleLabel.setText(f"版本 {PROJECT_CONFIG['version']}")
        self.subtitleLabel.setFont(QFont('Microsoft YaHei', 12))
        self.subtitleLabel.setStyleSheet("color: rgba(255, 255, 255, 0.8);")

        # 设置布局 - 增加顶部和底部边距，给背景图片更多空间
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 60, 0, 40)  # 移除左右边距，因为我们在样式表中设置了margin-left
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(10)
        self.vBoxLayout.addWidget(self.subtitleLabel)
        self.vBoxLayout.addStretch(1)  # 只保留底部弹性空间，让标题和副标题靠上显示

        self.titleLabel.setObjectName('titleLabel')
        self.subtitleLabel.setObjectName('subtitleLabel')
        
        # 设置最小高度，确保背景图片有足够展示空间
        self.setMinimumHeight(200)

    def paintEvent(self, event):
        """绘制背景图片"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        try:
            # 加载背景图片文件 - 首先尝试Qt资源系统，如果失败则使用文件路径
            pixmap = QPixmap(":/asset/AmongUs-BG.jpg")
            if pixmap.isNull():
                # 如果资源加载失败，尝试直接加载文件
                bg_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "asset", "AmongUs-BG.jpg")
                pixmap = QPixmap(bg_path)
            
            if not pixmap.isNull():
                # 缩放图片以适应组件大小
                scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                painter.drawPixmap(0, 0, scaled_pixmap)
            else:
                # 如果图片加载失败，绘制白色背景
                painter.fillRect(self.rect(), QColor("white"))
        finally:
            # 确保绘画器被正确结束
            painter.end()