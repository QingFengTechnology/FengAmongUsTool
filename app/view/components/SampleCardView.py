# coding:utf-8
"""
功能卡片视图组件
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QSpacerItem, QSizePolicy
from qfluentwidgets import ScrollArea

from .SampleCard import SampleCard


class SampleCardView(ScrollArea):
    """功能卡片视图"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.title = title
        self.view = QWidget(self)
        self.gridLayout = QGridLayout(self.view)
        
        # 设置自适应边距，左右边距根据窗口大小自适应
        self.gridLayout.setContentsMargins(36, 0, 36, 36)
        self.gridLayout.setSpacing(12)
        self.gridLayout.setAlignment(Qt.AlignTop)

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用水平滚动
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 允许垂直滚动

        self.view.setObjectName('view')
        self.setObjectName(title)
        
        # 存储卡片列表
        self.cards = []

    def addSampleCard(self, icon, title, content, routeKey, index, onClick=None):
        """添加功能卡片"""
        card = SampleCard(icon, title, content, routeKey, index, self.view, onClick)
        self.cards.append(card)
        self.updateLayout()

    def updateLayout(self):
        """更新布局，根据窗口大小自适应排列卡片"""
        # 清除现有布局
        for i in reversed(range(self.gridLayout.count())):
            item = self.gridLayout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            elif item.spacerItem():
                self.gridLayout.removeItem(item)
        
        if not self.cards:
            return
            
        # 计算每行可以放置的卡片数量（根据窗口宽度和卡片最小宽度）
        view_width = self.view.width()
        if view_width <= 0:
            view_width = 800  # 默认宽度
            
        # 左右边距
        margins = self.gridLayout.contentsMargins()
        available_width = view_width - margins.left() - margins.right()
        
        # 卡片最小宽度（考虑间距）
        min_card_width = 200  # 卡片最小宽度
        spacing = self.gridLayout.spacing()
        
        # 计算每行最大卡片数量
        max_cards_per_row = max(1, int((available_width + spacing) / (min_card_width + spacing)))
        
        # 计算卡片实际宽度（自适应）
        card_width = max(min_card_width, (available_width - (max_cards_per_row - 1) * spacing) // max_cards_per_row)
        
        # 添加卡片到网格布局
        for i, card in enumerate(self.cards):
            row = i // max_cards_per_row
            col = i % max_cards_per_row
            self.gridLayout.addWidget(card, row, col, Qt.AlignTop)
            
            # 只设置卡片的固定宽度，高度由内容自适应
            card.setFixedWidth(card_width)
            
            # 设置卡片的尺寸策略为固定宽度，高度自适应
            card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
        # 设置列的比例，确保卡片均匀分布
        for col in range(max_cards_per_row):
            self.gridLayout.setColumnStretch(col, 1)
            
        # 设置行的比例，确保卡片在垂直方向均匀分布
        total_rows = (len(self.cards) + max_cards_per_row - 1) // max_cards_per_row
        for row in range(total_rows):
            self.gridLayout.setRowStretch(row, 1)

    def resizeEvent(self, event):
        """窗口大小变化时重新布局"""
        super().resizeEvent(event)
        self.updateLayout()