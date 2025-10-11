# coding:utf-8
"""
基于FlowLayout的ElevatedCard视图组件
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import FlowLayout, ScrollArea

from .ElevatedCard import ElevatedCard


class ElevatedCardView(ScrollArea):
    """功能卡片视图"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.title = title
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        self.flowLayout = FlowLayout()
        
        # 设置布局
        if title:
            self.vBoxLayout.setContentsMargins(36, 0, 36, 36)
        else:
            self.vBoxLayout.setContentsMargins(36, 36, 36, 36)  # 没有标题时上下边距相同
        
        self.vBoxLayout.setSpacing(10)
        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setHorizontalSpacing(12)
        self.flowLayout.setVerticalSpacing(12)
        self.flowLayout.setAlignment(Qt.AlignHCenter)  # 设置水平居中对齐
        
        # 添加标题和流式布局
        self.titleLabel = None
        if title:
            self.titleLabel = QLabel(title, self.view)
            self.titleLabel.setObjectName('viewTitleLabel')
            self.vBoxLayout.addWidget(self.titleLabel)
        
        self.vBoxLayout.addLayout(self.flowLayout, 1)
        
        # 设置滚动区域
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 设置对象名
        self.view.setObjectName('view')
        if self.titleLabel:
            self.titleLabel.setObjectName('viewTitleLabel')
        
        # 存储卡片列表
        self.cards = []

    def addElevatedCard(self, icon, title, content, routeKey, onClick=None):
        """添加功能卡片"""
        card = ElevatedCard(icon, title, content, routeKey, self.view)
        
        # 连接点击信号
        if onClick:
            card.clicked.connect(onClick)
        
        self.cards.append(card)
        self.flowLayout.addWidget(card)

    def clearCards(self):
        """清除所有卡片"""
        for card in self.cards:
            card.setParent(None)
            card.deleteLater()
        self.cards.clear()