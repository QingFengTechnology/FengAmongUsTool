# coding:utf-8
"""
工具函数文件
"""

import os
import stat
import platform
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Qt
from qfluentwidgets import InfoBar, InfoBarPosition, SettingCard, ComboBox

# 从新模块导入需要的内容
from .serverManager import (
    ServerLoader, ServerConfigLoader, installPrivateServer,
    fetchAndInstallServers, getEnabledServers, toggleServerState
)
from .variableConfig import LOG_CONFIG, INSTALL_CONFIG
from .logManager import logMessage, logWarning, logError, getLogger


class SimpleComboBoxSettingCard(SettingCard):
    """简化的组合框设置卡片"""
    
    def __init__(self, icon, title, content=None, texts=None, configItem=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.comboBox = ComboBox(self)
        self.configItem = configItem
        
        if texts:
            self.comboBox.addItems(texts)
        
        # 如果提供了配置项，设置当前值
        if configItem:
            self.setValue(configItem.value)
        
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
    
    def setValue(self, value):
        """设置组合框的值"""
        if self.configItem:
            # 根据配置项类型设置值
            if hasattr(self.configItem, 'options'):
                # 选项配置项
                for i, option in enumerate(self.configItem.options):
                    if option == value:
                        self.comboBox.setCurrentIndex(i)
                        break
            else:
                # 普通配置项
                for i in range(self.comboBox.count()):
                    if self.comboBox.itemText(i) == str(value):
                        self.comboBox.setCurrentIndex(i)
                        break
    
    def value(self):
        """获取组合框的值"""
        return self.comboBox.currentText()
    
    def connectValueChanged(self, slot):
        """连接值改变信号"""
        self.comboBox.currentTextChanged.connect(slot)


def showInfoBar(parent, title, content, position=InfoBarPosition.TOP):
    """显示信息栏"""
    InfoBar.info(title, content, duration=3000, parent=parent, position=position)
