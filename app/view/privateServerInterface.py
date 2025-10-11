# coding:utf-8
"""
私服安装界面模块
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, CheckBox, PrimaryPushButton,
    SimpleCardWidget, VBoxLayout, FluentIcon, InfoBarPosition
)

from ..function.variableConfig import SERVER_CONFIG, INSTALL_CONFIG
from ..function.funcUtils import (
    toggleServerState, installPrivateServer,
    logMessage, showInfoBar
)


class PrivateServerInterface:
    """私服安装界面类"""
    
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.serverConfig = SERVER_CONFIG.copy()
        self.serverCheckboxes = {}
        self.interface = None
        
    def createInterface(self):
        """创建私服安装界面"""
        self.interface = QWidget()
        self.interface.setObjectName("privateServerInterface")
        
        layout = QVBoxLayout(self.interface)
        
        # 标题
        titleLabel = SubtitleLabel('私服安装')
        layout.addWidget(titleLabel)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 服务器选择区域
        serverCard = SimpleCardWidget()
        serverLayout = VBoxLayout(serverCard)
        
        serverTitle = BodyLabel('选择服务器:')
        serverLayout.addWidget(serverTitle)
        
        # 服务器复选框
        for serverId, config in self.serverConfig.items():
            checkbox = CheckBox(config['name'])
            checkbox.setChecked(config['enabled'])
            checkbox.stateChanged.connect(
                lambda state, sid=serverId: self.toggleServer(sid, state)
            )
            serverLayout.addWidget(checkbox)
            self.serverCheckboxes[serverId] = checkbox
        
        layout.addWidget(serverCard)
        
        # 按钮区域
        buttonCard = SimpleCardWidget()
        buttonLayout = QHBoxLayout(buttonCard)
        
        self.installButton = PrimaryPushButton('安装私服')
        self.installButton.clicked.connect(self.installPrivateServer)
        buttonLayout.addWidget(self.installButton)
        
        layout.addWidget(buttonCard)
        layout.addStretch(1)
        
        return self.interface
    
    def toggleServer(self, serverId, state):
        """切换服务器状态"""
        self.serverConfig = toggleServerState(self.serverConfig, serverId, state)
        logMessage(f"服务器 {self.serverConfig[serverId]['name']} {'启用' if state else '禁用'}")
        
    def installPrivateServer(self):
        """安装私服"""
        success = installPrivateServer(
            self.serverConfig,
            self.log,
            lambda title, content, position=InfoBarPosition.TOP: 
                showInfoBar(self.mainWindow, title, content, position)
        )
        
        if success:
            self.installButton.setEnabled(False)
            # 安装完成后重新启用按钮
            import threading
            def enableButton():
                import time
                time.sleep(INSTALL_CONFIG["steps"] * INSTALL_CONFIG["step_delay"] + 1)
                self.installButton.setEnabled(True)
            
            threading.Thread(target=enableButton).start()
    
    def log(self, message):
        """添加日志"""
        logMessage(message)
        
    def addToNavigation(self, widget):
        """添加到导航栏"""
        if widget:
            self.mainWindow.addSubInterface(
                widget, 
                FluentIcon.SETTING, 
                '私服安装'
            )