# coding: utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import ScrollArea
from ..common.style_sheet import StyleSheet


class PrivateServerInterface(ScrollArea):
    """ Private Server interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        self.__initWidget()

    def __initWidget(self):
        self.setObjectName('privateServerInterface')
        self.scrollWidget.setObjectName('scrollWidget')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setViewportMargins(0, 100, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 0, 36, 0)