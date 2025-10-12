# coding:utf-8
"""
工具函数文件
"""
import threading
import time
import requests
import json
import re
from datetime import datetime
from PySide6.QtCore import Qt, Signal, QObject
from qfluentwidgets import InfoBar, InfoBarPosition, SettingCard, ComboBox

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


class ServerLoader(QObject):
    """服务器加载器"""
    serversLoaded = Signal(dict)  # 服务器加载完成信号
    loadFailed = Signal(str)      # 加载失败信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def loadServers(self):
        """从GitHub加载服务器列表"""
        try:
            # GitHub原始内容URL
            url = "https://raw.githubusercontent.com/YvonneOfficial/Temp-Resources/main/servers.dat"
            
            # 发送GET请求
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析自定义格式数据
            servers_data = self.parseServerConfig(response.text)
            
            # 转换数据格式以匹配现有代码
            server_config = {}
            for i, (name, filename) in enumerate(servers_data.items()):
                server_id = f"server{i+1}"
                server_config[server_id] = {
                    "name": name,
                    "filename": filename,
                    "enabled": False  # 默认不启用任何服务器
                }
            
            # 发出加载完成信号
            self.serversLoaded.emit(server_config)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求错误: {str(e)}"
            logError(error_msg)
            self.loadFailed.emit(error_msg)
        except Exception as e:
            error_msg = f"加载服务器列表时发生未知错误: {str(e)}"
            logError(error_msg)
            self.loadFailed.emit(error_msg)
    
    def parseServerConfig(self, content):
        """解析服务器配置文件"""
        servers = {}
        # 使用正则表达式匹配 "名称" = "文件名" 格式
        pattern = r'"([^"]+)"\s*=\s*"([^"]+)"'
        matches = re.findall(pattern, content)
        
        for name, filename in matches:
            servers[name] = filename
            
        return servers


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