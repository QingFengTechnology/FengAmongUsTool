# coding:utf-8
"""
私服安装界面模块
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, CheckBox, PrimaryPushButton,
    SimpleCardWidget, VBoxLayout, FluentIcon, InfoBarPosition, ScrollArea
)

from ..function.variableConfig import SERVER_CONFIG, INSTALL_CONFIG
from ..function.funcUtils import (
    toggleServerState, installPrivateServer,
    logMessage, showInfoBar
)


class PrivateServerInterface(ScrollArea):
    """私服安装界面类"""
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.serverConfig = SERVER_CONFIG.copy()
        self.serverCheckboxes = {}
        
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        
        self.initWidget()
        
    def initWidget(self):
        """初始化界面"""
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('privateServerInterface')
        
        # 设置布局边距，与其他界面保持一致
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        
        # 标题
        titleLabel = SubtitleLabel('私服安装')
        self.vBoxLayout.addWidget(titleLabel)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.vBoxLayout.addWidget(separator)
        
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
        
        self.vBoxLayout.addWidget(serverCard)
        
        # 按钮区域
        buttonCard = SimpleCardWidget()
        buttonLayout = QHBoxLayout(buttonCard)
        
        self.installButton = PrimaryPushButton('安装私服')
        self.installButton.clicked.connect(self.installPrivateServer)
        buttonLayout.addWidget(self.installButton)
        
        self.vBoxLayout.addWidget(buttonCard)
        self.vBoxLayout.addStretch(1)
        
        # 设置样式，与其他界面保持一致
        self.scrollWidget.setStyleSheet("QWidget{background:transparent}")
        self.setStyleSheet("PrivateServerInterface{background:transparent}")
    
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
                showInfoBar(self.parent(), title, content, position)
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
        
    def addToNavigation(self, mainWindow):
        """添加到导航栏"""
        from qfluentwidgets import NavigationItemPosition
        mainWindow.addSubInterface(
            self, 
            FluentIcon.DOWNLOAD, 
            '私服安装',
            NavigationItemPosition.SCROLL
        )