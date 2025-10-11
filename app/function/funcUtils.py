# coding:utf-8
"""
工具函数文件
"""
import threading
import time
from datetime import datetime
from PySide6.QtCore import Qt
from qfluentwidgets import InfoBar, InfoBarPosition, SettingCard, ComboBox

from .variableConfig import LOG_CONFIG, INSTALL_CONFIG


class SimpleComboBoxSettingCard(SettingCard):
    """简化的组合框设置卡片"""
    
    def __init__(self, icon, title, content=None, texts=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.comboBox = ComboBox(self)
        
        if texts:
            self.comboBox.addItems(texts)
        
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


def logMessage(message):
    """添加日志到控制台"""
    timestamp = datetime.now().strftime(LOG_CONFIG["timestamp_format"])
    logEntry = f"[{timestamp}] {message}"
    print(logEntry)


def showInfoBar(parent, title, content, position=InfoBarPosition.TOP):
    """显示信息栏"""
    InfoBar.info(title, content, duration=3000, parent=parent, position=position)


def toggleServerState(serverConfig, serverId, state):
    """切换服务器状态"""
    serverConfig[serverId]['enabled'] = (state == Qt.CheckState.Checked.value)
    return serverConfig


def getEnabledServers(serverConfig):
    """获取启用的服务器列表"""
    return [config['name'] for config in serverConfig.values() if config['enabled']]


def installPrivateServer(serverConfig, logCallback, messageCallback):
    """安装私服"""
    enabledServers = getEnabledServers(serverConfig)
    
    if not enabledServers:
        messageCallback('错误', '请至少选择一个服务器！', InfoBarPosition.TOP)
        return False
        
    logCallback(f"开始安装私服，选择的服务器: {', '.join(enabledServers)}")
    
    # 模拟安装过程
    def installThread():
        for i in range(1, INSTALL_CONFIG["steps"] + 1):
            time.sleep(INSTALL_CONFIG["step_delay"])
            logCallback(f"安装进度: {i * (100 // INSTALL_CONFIG['steps'])}%")
            
        logCallback("私服安装完成！")
        
    threading.Thread(target=installThread).start()
    return True